from sqlalchemy.orm import selectinload
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List

from app.core.database import get_db
from app.models.school import School
from app.schemas.school import SchoolCreate, SchoolResponse

router = APIRouter()

@router.post("/", response_model=SchoolResponse)
async def create_school(
    school_in: SchoolCreate,
    db: AsyncSession = Depends(get_db)
):
    # In a real app, only SuperAdmin can create schools. For testing, we keep it open.
    new_school = School(**school_in.dict())
    db.add(new_school)
    await db.commit()
    await db.refresh(new_school)
    return new_school

@router.get("/", response_model=List[SchoolResponse])
async def read_schools(
    skip: int = 0, limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(School).offset(skip).limit(limit))
    return result.scalars().all()
