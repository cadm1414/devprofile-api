from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, func, DateTime
from app.config.database import Base
from sqlalchemy.orm import relationship

class Email(Base):
    __tablename__ = "emails"

    id = Column(Integer, primary_key=True)    
    email = Column(String(100), nullable=False)
    is_principal = Column(Boolean, default=False)
    profile_id = Column(Integer, ForeignKey("profiles.id"))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    profile = relationship("Profile", back_populates="emails")