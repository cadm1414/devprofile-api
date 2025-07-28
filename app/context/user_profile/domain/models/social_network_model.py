from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func, Boolean
from sqlalchemy.orm import relationship
from app.config.database import Base

class SocialNetwork(Base):
    __tablename__ = "social_networks"

    id = Column(Integer, primary_key=True)
    url = Column(String(255), nullable=False)
    is_public = Column(Boolean, default=True) 
    platform_id = Column(Integer, nullable=False)
    profile_id = Column(Integer, ForeignKey("profiles.id"))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    
    profile = relationship("Profile", back_populates="social_networks")