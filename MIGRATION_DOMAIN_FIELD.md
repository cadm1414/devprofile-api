# Migration: Add Domain Field to User Model

## Overview
Added `domain` field to User model to enable public profile URLs (e.g., `myprofile.com/domain`).

## Changes Made

### 1. Database Model Update
**File:** `app/context/identity/domain/models/user_model.py`
```python
domain = Column(String(50), unique=True, nullable=True, index=True)
```
- Max length: 50 characters
- Unique constraint: No duplicate domains
- Nullable: Can be set later (not required at registration)
- Indexed: For fast lookups

### 2. Pydantic Schemas Updated
**File:** `app/context/identity/api/schemas/user_schema.py`

**UserUpdate schema:**
```python
domain: Optional[str] = Field(
    None, 
    max_length=50, 
    pattern=r'^[a-zA-Z0-9]+$', 
    description="Unique domain for public profile URL (alphanumeric only, no spaces or special characters)"
)
```

**UserOut schema:**
```python
domain: Optional[str] = None
```

**Validation Rules:**
- Alphanumeric only (no spaces, no special characters)
- Maximum 50 characters
- Optional (nullable)
- Unique across all users

### 3. Database Migration Created
**File:** `migrations/versions/001_add_domain_to_users.py`

**Migration Details:**
- Revision ID: `001`
- Adds `domain` column to `users` table
- Creates unique index `ix_users_domain`
- Safe for existing data (nullable column)

**Upgrade:**
```python
def upgrade() -> None:
    op.add_column('users', sa.Column('domain', sa.String(length=50), nullable=True))
    op.create_index(op.f('ix_users_domain'), 'users', ['domain'], unique=True)
```

**Downgrade (rollback):**
```python
def downgrade() -> None:
    op.drop_index(op.f('ix_users_domain'), table_name='users')
    op.drop_column('users', 'domain')
```

### 4. Alembic Infrastructure
**Files Created:**
- `alembic.ini` - Main configuration
- `migrations/env.py` - Environment setup with Base import
- `migrations/script.py.mako` - Template for new migrations
- `migrations/versions/001_add_domain_to_users.py` - Initial migration

**Configuration:**
- Connected to `app.config.database.Base` for autogenerate support
- Uses `settings.DATABASE_URL` from environment

### 5. Docker Deployment Updated
**File:** `start.sh` (NEW)
```bash
#!/bin/bash
alembic upgrade head
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**File:** `Dockerfile`
- Modified CMD to use `/app/start.sh`
- Added COPY and chmod for start.sh
- Migrations now run automatically on container startup

## Testing Locally (Optional)

### Run Migration Manually
```bash
# From project root
alembic upgrade head
```

### Verify Column Added
```sql
-- Connect to PostgreSQL
\d users;
-- Should show 'domain' column with varchar(50), nullable, unique index
```

### Test API
```bash
# Update user with domain
curl -X PUT http://localhost:8000/api/v1/identity/me \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"domain": "johndoe123"}'

# Should return 200 OK with domain field
```

## Deployment Process

### Automatic Migration on AWS
When you push to GitHub:

1. **GitHub Actions builds new Docker image**
2. **Image deployed to EC2**
3. **Container starts and runs:**
   ```bash
   alembic upgrade head  # Runs migration
   uvicorn app.main:app  # Starts API
   ```
4. **Migration adds domain column** (if not exists)
5. **API starts with new schema**

### Expected Behavior
- ✅ Existing users: `domain = NULL`
- ✅ New registrations: `domain = NULL` (set later via profile update)
- ✅ Domain validation: Alphanumeric only, max 50 chars
- ✅ Unique constraint: Cannot have duplicate domains
- ✅ Index: Fast lookups for public profile URLs

## Validation Rules

### Valid Domains
- `johndoe123` ✅
- `user2024` ✅
- `MyCoolProfile` ✅
- `dev` ✅

### Invalid Domains (will be rejected)
- `john-doe` ❌ (special characters)
- `john doe` ❌ (spaces)
- `user@123` ❌ (special characters)
- `123456789012345678901234567890123456789012345678901` ❌ (>50 chars)

## API Endpoints Affected

### Update User Profile
```http
PUT /api/v1/identity/me
Authorization: Bearer <token>
Content-Type: application/json

{
  "domain": "myuniquehandle"
}
```

**Response:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "name": "John",
  "last_name": "Doe",
  "full_name": "John Doe",
  "domain": "myuniquehandle"
}
```

### Get User Profile
```http
GET /api/v1/identity/me
Authorization: Bearer <token>
```

**Response includes:**
```json
{
  "domain": "myuniquehandle"  // or null if not set
}
```

## Error Handling

### Duplicate Domain
```json
{
  "detail": "UNIQUE constraint failed: users.domain"
}
```
**Solution:** Use a different domain name

### Invalid Characters
```json
{
  "detail": [
    {
      "loc": ["body", "domain"],
      "msg": "string does not match regex \"^[a-zA-Z0-9]+$\"",
      "type": "value_error.str.regex"
    }
  ]
}
```
**Solution:** Use only letters and numbers

## Next Steps

### 1. Commit and Push Changes
```bash
git add .
git commit -m "Add domain field to User model with Alembic migration"
git push origin main
```

### 2. Monitor Deployment
- Watch GitHub Actions workflow
- Check EC2 logs: `docker logs -f devprofile-api`
- Verify migration runs: Look for "Running upgrade -> 001"

### 3. Test on Production
```bash
# Health check
curl http://23.20.131.20/health

# Update your profile with domain
curl -X PUT http://23.20.131.20/api/v1/identity/me \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"domain": "yourhandle"}'
```

### 4. Future Enhancement: Public Profile Endpoint
Create endpoint for public profile access:
```python
@router.get("/profile/{domain}", response_model=UserOut)
def get_public_profile(domain: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.domain == domain).first()
    if not user:
        raise HTTPException(status_code=404, detail="Profile not found")
    return user
```

## Rollback (If Needed)

### Downgrade Migration
```bash
# SSH to EC2
docker exec -it devprofile-api bash
alembic downgrade -1
```

This will:
- Drop the unique index `ix_users_domain`
- Remove the `domain` column from `users` table

## Files Modified Summary
```
✅ app/context/identity/domain/models/user_model.py (SQLAlchemy model)
✅ app/context/identity/api/schemas/user_schema.py (Pydantic schemas)
✅ alembic.ini (NEW - Alembic config)
✅ migrations/env.py (NEW - Alembic environment)
✅ migrations/script.py.mako (NEW - Migration template)
✅ migrations/versions/001_add_domain_to_users.py (NEW - Migration)
✅ start.sh (NEW - Startup script with migration)
✅ Dockerfile (Modified - Uses start.sh)
```

## Database Schema After Migration

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    hashed_password VARCHAR(100) NOT NULL,
    domain VARCHAR(50) UNIQUE,  -- NEW FIELD
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE UNIQUE INDEX ix_users_domain ON users(domain);  -- NEW INDEX
CREATE UNIQUE INDEX ix_users_email ON users(email);
CREATE INDEX ix_users_id ON users(id);
```

## Success Criteria
- ✅ Migration runs without errors on container startup
- ✅ Domain field is nullable and unique
- ✅ Validation enforces alphanumeric-only constraint
- ✅ Existing users have `domain = NULL`
- ✅ Users can update their domain via PUT /api/v1/identity/me
- ✅ API returns domain field in responses
- ✅ No duplicate domains allowed (unique constraint enforced)
