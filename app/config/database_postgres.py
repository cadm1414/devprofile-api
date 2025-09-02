from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config.settings import settings
import logging

# Setup logging for database operations
logger = logging.getLogger(__name__)

# PostgreSQL configuration optimized for version 9.6
engine = create_engine(
    settings.DATABASE_URL,    
    echo=False,  # Set to True for SQL debugging
    future=True,
    pool_pre_ping=True,
    pool_recycle=300,
    pool_size=5,
    max_overflow=10
)

Base = declarative_base()

# Import all models to ensure they're registered with Base
from app.context.identity.domain.models.user_model import User
from app.context.user_profile.domain.models.profile_model import Profile
from app.context.user_profile.domain.models.education_model import Education
from app.context.user_profile.domain.models.project_model import Project
from app.context.user_profile.domain.models.skill_model import Skill
from app.context.user_profile.domain.models.social_network_model import SocialNetwork
from app.context.user_profile.domain.models.work_experience_model import WorkExperience
from app.context.user_profile.domain.models.email_model import Email
from app.context.user_profile.domain.models.phone_number_model import PhoneNumber

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    future=True,
)

def test_connection():
    """Test PostgreSQL connection"""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            logger.info(f"✅ PostgreSQL connection successful: {version}")
            return True
    except Exception as e:
        logger.error(f"❌ PostgreSQL connection failed: {e}")
        return False

def init_db():
    """Initialize database tables"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables created successfully")
    except Exception as e:
        logger.error(f"❌ Error creating database tables: {e}")
        raise

def get_db():
    """Database dependency for FastAPI"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
