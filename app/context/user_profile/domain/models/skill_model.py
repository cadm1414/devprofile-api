from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from app.config.database import Base
from sqlalchemy.orm import relationship

class Skill(Base):
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True)    
    name = Column(String(100))
    category = Column(String(100), nullable=True)
    years_experience = Column(Integer, nullable=True)
    skill_level_id = Column(Integer, nullable=True)
    profile_id = Column(Integer, ForeignKey("profiles.id"))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    profile = relationship("Profile", back_populates="skills")