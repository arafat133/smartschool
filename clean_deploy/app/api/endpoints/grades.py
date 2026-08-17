from sqlalchemy.orm import selectinload
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from uuid import UUID

from app.core.database import get_db
from app.models.academic import Grade, AcademicHistory
from app.models.user import User
from app.schemas.academic import GradeCreate, GradeResponse
from app.api import deps
from app.services.blockchain import blockchain

router = APIRouter()

@router.post("/", response_model=GradeResponse)
async def submit_grade(
    grade_in: GradeCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    # Fetch the academic history to verify it exists and belongs to the correct school
    result = await db.execute(
        select(AcademicHistory)
        .where(AcademicHistory.id == grade_in.academic_history_id)
        .where(AcademicHistory.school_id == current_user.school_id)
    )
    history = result.scalars().first()
    if not history:
        raise HTTPException(status_code=404, detail="لم يتم العثور على سجل أكاديمي للطالب")

    # Fetch previous grade to get its hash to link the blockchain
    prev_grade_result = await db.execute(
        select(Grade)
        .where(Grade.academic_history_id == grade_in.academic_history_id)
        .order_by(Grade.created_at.desc())
        .limit(1)
    )
    prev_grade = prev_grade_result.scalars().first()
    previous_hash = prev_grade.blockchain_hash if prev_grade else "0"

    # Calculate blockchain hash
    data_to_hash = {
        "student_id": str(history.student_id),
        "subject_id": str(grade_in.subject_id),
        "score": grade_in.score
    }
    current_hash = blockchain.generate_hash(data_to_hash, previous_hash)

    # Store the grade with the hash
    new_grade = Grade(**grade_in.dict(exclude={"school_id"}), school_id=current_user.school_id, blockchain_hash=current_hash)
    db.add(new_grade)
    await db.commit()
    await db.refresh(new_grade)
    
    return new_grade

@router.get("/verify/{academic_history_id}", response_model=bool)
async def verify_grades_integrity(
    academic_history_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    # Fetch all grades for this history in chronological order
    result = await db.execute(
        select(Grade)
        .where(Grade.academic_history_id == academic_history_id)
        .where(Grade.school_id == current_user.school_id)
        .order_by(Grade.created_at.asc())
    )
    grades = result.scalars().all()
    
    previous_hash = "0"
    for grade in grades:
        data_to_hash = {
            "student_id": str(grade.academic_record.student_id),
            "subject_id": str(grade.subject_id),
            "score": grade.score
        }
        if not blockchain.verify_integrity(data_to_hash, previous_hash, grade.blockchain_hash):
            return False # Tampering detected!
        previous_hash = grade.blockchain_hash
        
    return True
