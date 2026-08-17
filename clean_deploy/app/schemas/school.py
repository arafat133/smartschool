from pydantic import BaseModel
from typing import Optional
from uuid import UUID

class SchoolBase(BaseModel):
    name: str
    governorate_district: str
    center_type: str
    directorate_location: str
    school_location: str
    manager_name: str
    manager_phone: str
    it_manager: str
    is_active: bool = True

class SchoolCreate(SchoolBase):
    pass

class SchoolResponse(SchoolBase):
    id: UUID

    class Config:
        orm_mode = True
