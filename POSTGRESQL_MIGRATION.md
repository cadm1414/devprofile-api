# DevProfile API - PostgreSQL Migration

## Database Migration to PostgreSQL 9.6.9

This project has been migrated from SQL Server to **PostgreSQL 9.6.9** to improve cloud platform compatibility and resolve SSL connectivity issues.

### Changes Made:

#### 1. Dependencies Updated
- **Removed**: `pyodbc` (SQL Server)
- **Added**: `psycopg2-binary` (PostgreSQL)

#### 2. Configuration Files
- **settings.py**: Updated database URL format for PostgreSQL
- **database.py**: Removed SQL Server specific configurations, added PostgreSQL optimizations
- **.env-example**: Updated environment variables for PostgreSQL connection

#### 3. Docker Configuration
- **Dockerfile**: Simplified by removing SQL Server driver dependencies
- **fly.toml**: Ready for deployment with PostgreSQL

### PostgreSQL Configuration

#### Environment Variables (.env)
```bash
# PostgreSQL Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=profile_db
DB_USER=your_username
DB_PASSWORD=your_password

# JWT Configuration
SECRET_KEY=your-super-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# API Configuration
API_PREFIX=/api/v1
ORIGINS=http://localhost:3000,http://127.0.0.1:3000,http://localhost:8000
```

#### Connection Features
- **SSL Mode**: `prefer` (compatible with cloud platforms)
- **Connection Pooling**: Optimized for PostgreSQL 9.6.9
- **Application Name**: `devprofile-api` for monitoring
- **Pool Configuration**: 
  - Pool size: 5 connections
  - Max overflow: 10 connections
  - Pool recycle: 300 seconds

### Database Setup

#### Local PostgreSQL Setup
1. Install PostgreSQL 9.6.9 or later
2. Create database:
   ```sql
   CREATE DATABASE profile_db;
   CREATE USER your_username WITH PASSWORD 'your_password';
   GRANT ALL PRIVILEGES ON DATABASE profile_db TO your_username;
   ```

#### Cloud Deployment
The application is now ready for deployment on cloud platforms with managed PostgreSQL services:
- **Fly.io**: PostgreSQL addon available
- **Render**: Managed PostgreSQL service
- **Heroku**: Heroku Postgres
- **Railway**: PostgreSQL service

### Testing the Migration

#### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 2. Configure Environment
```bash
cp .env-example .env
# Edit .env with your PostgreSQL connection details
```

#### 3. Test Database Connection
```bash
python -c "from app.config.database import test_connection; test_connection()"
```

#### 4. Initialize Database Tables
```bash
python -c "from app.config.database import init_db; init_db()"
```

#### 5. Run Application
```bash
uvicorn app.main:app --reload
```

### Migration Benefits

1. **Cloud Compatibility**: Better support across cloud platforms
2. **SSL Handling**: Improved SSL/TLS connection handling
3. **Performance**: PostgreSQL optimization for modern applications
4. **Cost Effective**: Many cloud platforms offer free PostgreSQL tiers
5. **Reliability**: Mature and stable PostgreSQL ecosystem

### Troubleshooting

#### Common Issues
1. **Connection Refused**: Check PostgreSQL service is running
2. **Authentication Failed**: Verify username/password in .env
3. **SSL Errors**: PostgreSQL handles SSL better than SQL Server in cloud environments

#### Logs
Enable SQL logging by setting `echo=True` in `database.py` for debugging queries.

### Next Steps
1. Deploy to chosen cloud platform
2. Configure production PostgreSQL database
3. Update environment variables for production
4. Test all API endpoints with new database
