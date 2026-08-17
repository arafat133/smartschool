from pydantic import BaseModel
from datetime import date
from uuid import UUID
from typing import Optional

class AttendanceBase(BaseModel):
    student_id: UUID
    grade_level: str
    academic_year: str
    date: date
    status: str

class AttendanceCreate(AttendanceBase):
    school_id: UUID

class AttendanceResponse(AttendanceBase):
    id: UUID
    school_id: UUID

    class Config:
        orm_mode = True

class AssignmentBase(BaseModel):
    grade_level: str
    academic_year: str
    teacher_id: UUID
    subject_id: UUID
    title: str
    details: str
    due_date: date

class AssignmentCreate(AssignmentBase):
    school_id: UUID

class AssignmentResponse(AssignmentBase):
    id: UUID
    school_id: UUID

    class Config:
        orm_mode = True

class GradeBase(BaseModel):
    academic_history_id: UUID
    subject_id: UUID
    score: float

class GradeCreate(GradeBase):
    school_id: UUID

class GradeResponse(GradeBase):
    id: UUID
    school_id: UUID
    blockchain_hash: str

    class Config:
        orm_mode = True

