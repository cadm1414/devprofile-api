# Deployment Configuration for PostgreSQL

## Render Deployment

### Environment Variables to Set in Render Dashboard

**CRITICAL**: Remove any old SQL Server environment variables and set these PostgreSQL variables:

```bash
# API Configuration
API_PREFIX=/api/v1
ORIGINS=*

# PostgreSQL Database (use your Render PostgreSQL service details)
DB_HOST=your-render-postgres-host
DB_PORT=5432
DB_NAME=your-database-name
DB_USER=your-postgres-user
DB_PASSWORD=your-postgres-password

# JWT Configuration
SECRET_KEY=your-super-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

### Steps to Fix Render Deployment:

1. **Go to your Render service dashboard**
2. **Navigate to Environment tab**
3. **DELETE these old SQL Server variables** (if they exist):
   - `DB_DRIVER`
   - `DB_SERVER` 
   - `DB_DATABASE`
   - `DB_USERNAME`
   - Any SQL Server related variables

4. **SET these new PostgreSQL variables**:
   - `DB_HOST` = Your PostgreSQL host
   - `DB_PORT` = 5432
   - `DB_NAME` = Your database name
   - `DB_USER` = Your PostgreSQL username
   - `DB_PASSWORD` = Your PostgreSQL password

5. **Keep these existing variables**:
   - `API_PREFIX` = /api/v1
   - `ORIGINS` = *
   - `SECRET_KEY` = (your JWT secret)
   - `ALGORITHM` = HS256
   - `ACCESS_TOKEN_EXPIRE_MINUTES` = 60

6. **Redeploy the service**

## Fly.io Deployment

### Set Secrets (don't put sensitive data in fly.toml):

```bash
# Set database credentials as secrets
fly secrets set DB_HOST=your-postgres-host
fly secrets set DB_PORT=5432
fly secrets set DB_NAME=your-database-name
fly secrets set DB_USER=your-postgres-user
fly secrets set DB_PASSWORD=your-postgres-password
fly secrets set SECRET_KEY=your-super-secret-key-here

# Deploy
fly deploy
```

## Troubleshooting

### Error: "DB_DRIVER Field required"
This error occurs when:
1. Old environment variables from SQL Server are still set in your deployment platform
2. The deployment is using cached/old code

**Solution**: 
1. Delete ALL old SQL Server environment variables
2. Set new PostgreSQL environment variables
3. Trigger a fresh deployment (not from cache)

### Error: "No module named 'psycopg2'"
**Solution**: The requirements.txt has been updated to include psycopg2-binary. Make sure the deployment is using the latest code.

### Connection Issues
1. Verify PostgreSQL database is accessible from your deployment platform
2. Check if database allows connections from the deployment IP
3. Verify SSL settings match (`sslmode=prefer` in our configuration)

## Local Testing

Before deploying, test locally:

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables in .env file
cp .env-example .env
# Edit .env with your PostgreSQL connection details

# Test connection
python -c "from app.config.database import test_connection; test_connection()"

# Run locally
uvicorn app.main:app --reload
```
