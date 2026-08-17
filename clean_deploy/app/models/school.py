from sqlalchemy import Column, String, Boolean
from app.models.base import BaseModel
from sqlalchemy.orm import relationship

class School(BaseModel):
    __tablename__ = "schools"

    name = Column(String, nullable=False, index=True)
    governorate_district = Column(String, nullable=False)
    center_type = Column(String, nullable=False) # Boys/Girls/Mixed
    directorate_location = Column(String, nullable=False)
    school_location = Column(String, nullable=False)
    manager_name = Column(String, nullable=False)
    manager_phone = Column(String, nullable=False)
    it_manager = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)

    users = relationship("User", back_populates="school", cascade="all, delete-orphan")
    students = relationship("Student", back_populates="school", cascade="all, delete-orphan")
