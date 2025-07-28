from sqlalchemy import Column, Integer, String, ForeignKey, Date, DateTime, func, Boolean
from app.config.database import Base
from sqlalchemy.orm import relationship

class Education(Base):
    __tablename__ = "educations"

    id = Column(Integer, primary_key=True)
    degree = Column(String(100))
    start_date = Column(Date)
    end_date = Column(Date)
    is_completed = Column(Boolean, default=False)

    institution_id = Column(Integer)    
    title_type_id = Column(Integer, nullable=True)
    profile_id = Column(Integer, ForeignKey("profiles.id"))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    profile = relationship("Profile", back_populates="educations")