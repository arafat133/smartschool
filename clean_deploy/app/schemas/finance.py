from pydantic import BaseModel
from typing import Optional
from uuid import UUID

class FinancialBase(BaseModel):
    academic_history_id: UUID
    grade_level: str
    academic_year: str
    total_required: float
    amount_paid: float
    payment_status: str

class FinancialCreate(FinancialBase):
    school_id: UUID

class FinancialResponse(FinancialBase):
    id: UUID
    school_id: UUID

    class Config:
        orm_mode = True
