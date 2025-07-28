from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func, DateTime
from app.config.database import Base
from sqlalchemy.orm import relationship

class WorkExperience(Base):
    __tablename__ = "work_experiences"

    id = Column(Integer, primary_key=True)
    
    company = Column(String(100))
    role = Column(String(100))
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    description = Column(String(500), nullable=True)
    profile_id = Column(Integer, ForeignKey("profiles.id"))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    profile = relationship("Profile", back_populates="work_experiences")