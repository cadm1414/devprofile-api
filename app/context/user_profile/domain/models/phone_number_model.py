from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, func, DateTime
from app.config.database import Base
from sqlalchemy.orm import relationship

class PhoneNumber(Base):
    __tablename__ = "phones"

    id = Column(Integer, primary_key=True)    
    number = Column(String(20), nullable=False)
    anext = Column(String(20), nullable=True)
    is_principal = Column(Boolean, default=False)
    profile_id = Column(Integer, ForeignKey("profiles.id"))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    profile = relationship("Profile", back_populates="phones")