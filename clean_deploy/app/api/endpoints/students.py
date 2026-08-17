from sqlalchemy.orm import selectinload
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from uuid import UUID

from app.core.database import get_db
from app.models.student import Student
from app.models.user import User
from app.schemas.student import StudentCreate, StudentResponse
from app.api import deps

router = APIRouter()

allow_create = deps.RoleChecker(["super_admin", "school_admin"])

@router.post("/", response_model=StudentResponse)
async def create_student(
    student_in: StudentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(allow_create)
):
    # Depending on user role, we could enforce school_id
    new_student = Student(**student_in.dict())
    db.add(new_student)
    await db.commit()
    await db.refresh(new_student)
    return new_student

@router.get("/", response_model=List[StudentResponse])
async def read_students(
    skip: int = 0, limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    # Enforce Row-Level Security / Multi-tenancy by filtering school_id
    # If RLS is configured at DB level, this automatically filters
    result = await db.execute(select(Student).where(Student.school_id == current_user.school_id).offset(skip).limit(limit))
    return result.scalars().all()
