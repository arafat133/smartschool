from sqlalchemy import Column, String, Date, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import TenantModel
from sqlalchemy.orm import relationship

class Student(TenantModel):
    __tablename__ = "students"

    full_name = Column(String, nullable=False, index=True)
    student_number = Column(String, nullable=False, unique=True, index=True)
    
    parent_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    parent2_phone = Column(String, nullable=True)
    
    date_of_birth = Column(Date, nullable=False)
    place_of_birth = Column(String, nullable=False)
    residence = Column(String, nullable=False)
    current_grade_level = Column(String, nullable=False) # e.g., 1st Primary
    father_national_id = Column(String, nullable=False)
    gender = Column(String, nullable=False)
    nationality = Column(String, default="Yemeni")

    school = relationship("School", back_populates="students")
    parent = relationship("User", foreign_keys=[parent_id], back_populates="students_as_parent")
    academic_history = relationship("AcademicHistory", back_populates="student", cascade="all, delete-orphan")
    attendance_records = relationship("AttendanceRecord", back_populates="student", cascade="all, delete-orphan")
