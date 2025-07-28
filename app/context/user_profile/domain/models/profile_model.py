from sqlalchemy import Column, Integer, String, ForeignKey, Date, DateTime, func
from app.config.database import Base
from sqlalchemy.orm import relationship

class Profile(Base):
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True)    
    title = Column(String(255))
    bio = Column(String)
    address = Column(String(255))
    city = Column(String(100))
    country = Column(String(100))
    birthday = Column(Date, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)

    user = relationship("User", back_populates="profile")
    social_networks = relationship("SocialNetwork", back_populates="profile", cascade="all, delete-orphan")
    emails = relationship("Email", back_populates="profile", cascade="all, delete-orphan")
    phones = relationship("PhoneNumber", back_populates="profile", cascade="all, delete-orphan")
    work_experiences = relationship("WorkExperience", back_populates="profile", cascade="all, delete-orphan")
    skills = relationship("Skill", back_populates="profile", cascade="all, delete-orphan")
    educations = relationship("Education", back_populates="profile", cascade="all, delete-orphan")
    projects = relationship("Project", back_populates="profile", cascade="all, delete-orphan")