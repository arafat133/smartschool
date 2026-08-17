from pydantic import BaseModel
from datetime import date
from typing import Optional
from uuid import UUID

class StudentBase(BaseModel):
    full_name: str
    student_number: str
    parent_id: Optional[UUID] = None
    parent2_phone: Optional[str] = None
    date_of_birth: date
    place_of_birth: str
    residence: str
    current_grade_level: str
    father_national_id: str
    gender: str
    nationality: str = "Yemeni"

class StudentCreate(StudentBase):
    school_id: UUID

class StudentResponse(StudentBase):
    id: UUID
    school_id: UUID

    class Config:
        orm_mode = True
