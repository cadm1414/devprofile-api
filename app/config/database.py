from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config.settings import settings

engine = create_engine(
    settings.DATABASE_URL,    
    echo=True,
    future=True,
)

Base = declarative_base()

#MODELOS
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

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
