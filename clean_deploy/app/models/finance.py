from sqlalchemy import Column, String, Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import TenantModel
from sqlalchemy.orm import relationship

class FinancialRecord(TenantModel):
    __tablename__ = "financial_records"

    academic_history_id = Column(UUID(as_uuid=True), ForeignKey("academic_history.id", ondelete="CASCADE"), nullable=False, index=True)
    grade_level = Column(String, nullable=False)
    academic_year = Column(String, nullable=False)
    
    total_required = Column(Float, nullable=False)
    amount_paid = Column(Float, default=0.0)
    payment_status = Column(String, nullable=False) # Paid, Unpaid

    academic_record = relationship("AcademicHistory", back_populates="financial_record")
