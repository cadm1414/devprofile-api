# Domain Field - Deployment Guide

## ✅ All Changes Complete - Ready to Deploy!

### Summary
Added `domain` field to User model to enable public profile URLs (e.g., `myprofile.com/{domain}`).

### Files Modified/Created
```
✅ app/context/identity/domain/models/user_model.py
✅ app/context/identity/api/schemas/user_schema.py  
✅ app/context/identity/application/usecases/update_user_use_case.py
✅ alembic.ini
✅ migrations/env.py
✅ migrations/script.py.mako
✅ migrations/versions/001_add_domain_to_users.py
✅ start.sh
✅ Dockerfile
✅ MIGRATION_DOMAIN_FIELD.md (documentation)
```

## Quick Deploy

### 1. Commit and Push
```bash
git add .
git commit -m "feat: Add domain field for public profile URLs with Alembic migration"
git push origin main
```

### 2. Monitor Deployment
```bash
# Watch GitHub Actions
# URL: https://github.com/YOUR_USERNAME/devprofile-api/actions

# After deployment, check logs
ssh -i "your-key.pem" ubuntu@23.20.131.20
docker logs -f devprofile-api
```

**Look for:** `Running upgrade -> 001, add_domain_to_users`

### 3. Test API
```bash
# Health check
curl http://23.20.131.20/health

# Update profile with domain (after login)
curl -X PUT http://23.20.131.20/api/v1/identity/me \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"domain": "myhandle123"}'
```

## What Happens on Deployment

1. **GitHub Actions builds new Docker image**
2. **Deploys to EC2**
3. **Container starts:**
   - Runs `alembic upgrade head` (adds domain column)
   - Starts FastAPI server
4. **Migration completes:**
   - Adds `domain` column (String 50, nullable, unique)
   - Creates unique index `ix_users_domain`
   - Existing users get `domain = NULL`

## Features

### Validation Rules
- ✅ Alphanumeric only (no spaces, no special chars)
- ✅ Maximum 50 characters
- ✅ Unique across all users
- ✅ Optional (nullable)

### Valid Examples
- `johndoe123` ✅
- `DevProfile2024` ✅
- `myhandle` ✅

### Invalid Examples
- `john-doe` ❌ (hyphen not allowed)
- `john doe` ❌ (space not allowed)
- `user@123` ❌ (@ not allowed)

### Error Handling
- Invalid format: Returns 422 with validation error
- Duplicate domain: Returns 400 with "El dominio ya está en uso"

## Rollback (if needed)
```bash
# SSH to EC2
docker exec -it devprofile-api bash
alembic downgrade -1
```

## Full Documentation
See `MIGRATION_DOMAIN_FIELD.md` for complete technical details.

## Status: ✅ READY TO DEPLOY
All code complete. Migrations tested. Ready for production.
