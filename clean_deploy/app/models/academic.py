from sqlalchemy import Column, String, Integer, Date, ForeignKey, Float
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import TenantModel
from sqlalchemy.orm import relationship

class AcademicHistory(TenantModel):
    __tablename__ = "academic_history"

    student_id = Column(UUID(as_uuid=True), ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)
    grade_level = Column(String, nullable=False) # الصف الدراسي
    academic_year = Column(String, nullable=False) # السنة الدراسية
    status = Column(String, nullable=False) # pass or fail

    student = relationship("Student", back_populates="academic_history")
    grades = relationship("Grade", back_populates="academic_record", cascade="all, delete-orphan")
    financial_record = relationship("FinancialRecord", uselist=False, back_populates="academic_record", cascade="all, delete-orphan")

class SubjectCatalog(TenantModel):
    __tablename__ = "subjects_catalog"

    name = Column(String, nullable=False)
    grade_level = Column(String, nullable=False) # الصف المخصص له

class Grade(TenantModel):
    __tablename__ = "grades"

    academic_history_id = Column(UUID(as_uuid=True), ForeignKey("academic_history.id", ondelete="CASCADE"), nullable=False, index=True)
    subject_id = Column(UUID(as_uuid=True), ForeignKey("subjects_catalog.id", ondelete="CASCADE"), nullable=False)
    score = Column(Float, nullable=False)
    blockchain_hash = Column(String, nullable=False) # البصمة الرقمية

    academic_record = relationship("AcademicHistory", back_populates="grades")
    subject = relationship("SubjectCatalog")

class DailyAssignment(TenantModel):
    __tablename__ = "daily_assignments"

    grade_level = Column(String, nullable=False)
    academic_year = Column(String, nullable=False)
    teacher_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    subject_id = Column(UUID(as_uuid=True), ForeignKey("subjects_catalog.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)
    details = Column(String, nullable=False)
    due_date = Column(Date, nullable=False)

    teacher = relationship("User")
    subject = relationship("SubjectCatalog")

class AttendanceRecord(TenantModel):
    __tablename__ = "attendance_records"

    student_id = Column(UUID(as_uuid=True), ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)
    grade_level = Column(String, nullable=False)
    academic_year = Column(String, nullable=False)
    date = Column(Date, nullable=False)
    status = Column(String, nullable=False) # present, absent, late, excused

    student = relationship("Student", back_populates="attendance_records")
