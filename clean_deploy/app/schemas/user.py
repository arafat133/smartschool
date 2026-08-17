from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from app.models.user import UserRole

class UserBase(BaseModel):
    username: str
    phone: Optional[str] = None
    role: UserRole

class UserCreate(UserBase):
    password: str
    school_id: UUID

class UserResponse(UserBase):
    id: UUID
    school_id: UUID
    is_active: bool

    class Config:
        orm_mode = True
