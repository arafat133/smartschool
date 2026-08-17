from sqlalchemy import Column, String, Boolean, Enum
import enum
from app.models.base import TenantModel
from sqlalchemy.orm import relationship

class UserRole(str, enum.Enum):
    SUPER_ADMIN = "super_admin"
    SCHOOL_ADMIN = "school_admin"
    TEACHER = "teacher"
    HR = "hr"
    FINANCE = "finance"
    ATTENDANCE = "attendance"
    PARENT = "parent"

class User(TenantModel):
    __tablename__ = "users"

    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, nullable=False) # Storing string value of UserRole
    phone = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)

    school = relationship("School", back_populates="users")
    students_as_parent = relationship("Student", foreign_keys="[Student.parent_id]", back_populates="parent")
