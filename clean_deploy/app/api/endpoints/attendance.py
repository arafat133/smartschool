from sqlalchemy.orm import selectinload
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from uuid import UUID

from app.core.database import get_db
from app.models.academic import AttendanceRecord
from app.models.user import User
from app.schemas.academic import AttendanceCreate, AttendanceResponse
from app.api import deps

router = APIRouter()

@router.post("/", response_model=AttendanceResponse)
async def create_attendance(
    attendance_in: AttendanceCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    new_record = AttendanceRecord(**attendance_in.dict())
    db.add(new_record)
    await db.commit()
    await db.refresh(new_record)
    return new_record

@router.get("/student/{student_id}", response_model=List[AttendanceResponse])
async def get_student_attendance(
    student_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    result = await db.execute(
        select(AttendanceRecord)
        .where(AttendanceRecord.student_id == student_id)
        .where(AttendanceRecord.school_id == current_user.school_id)
    )
    return result.scalars().all()
