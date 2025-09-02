from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config.settings import settings

# Debug logs para ver la URL generada
print(f"🔍 DATABASE_URL generada: {settings.DATABASE_URL}")
print(f"🔍 DB_HOST: {settings.DB_HOST}")
print(f"🔍 DB_PORT: {settings.DB_PORT}")
print(f"🔍 DB_USER: {settings.DB_USER}")
print(f"🔍 DB_NAME: {settings.DB_NAME}")

def create_database_if_not_exists():
    try:        
        master_url = settings.DATABASE_URL.replace(f"/{settings.DB_NAME}", "/master")
        temp_engine = create_engine(master_url, echo=True)
        
        with temp_engine.connect() as conn:            
            result = conn.execute(text(f"SELECT database_id FROM sys.databases WHERE name = '{settings.DB_NAME}'"))
            if not result.fetchone():
                print(f"🔍 Creando base de datos: {settings.DB_NAME}")
                conn.execute(text(f"CREATE DATABASE [{settings.DB_NAME}]"))
                conn.commit()
                print(f"✅ Base de datos {settings.DB_NAME} creada exitosamente")
            else:
                print(f"✅ Base de datos {settings.DB_NAME} ya existe")
        
        temp_engine.dispose()
    except Exception as e:
        print(f"❌ Error al crear/verificar base de datos: {e}")
        print("🔍 Continuando con la conexión existente...")


create_database_if_not_exists()

engine = create_engine(
    settings.DATABASE_URL,    
    echo=True,
    future=True,
    pool_pre_ping=True,
    pool_recycle=3600
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
