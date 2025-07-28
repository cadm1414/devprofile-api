from sqlalchemy import Column, Integer, String, ForeignKey, Text, DateTime, func
from app.config.database import Base
from sqlalchemy.orm import relationship

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True)
    
    title = Column(String(100))
    description = Column(Text)
    url = Column(String(200), nullable=True)
    completion_date = Column(DateTime, nullable=True)
    technologies_id = Column(Integer,  nullable=True)
    profile_id = Column(Integer, ForeignKey("profiles.id"))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    profile = relationship("Profile", back_populates="projects")