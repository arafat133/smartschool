from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List, Dict, Any
from uuid import UUID

from app.core.database import get_db
from app.models.academic import Grade, AcademicHistory, SubjectCatalog, AttendanceRecord
from app.models.student import Student
from app.models.finance import FinancialRecord
from app.models.user import User
from app.schemas.finance import FinancialResponse
from app.api import deps
from app.services.blockchain import blockchain

router = APIRouter()

@router.get("/report/{academic_history_id}", response_model=Dict[str, Any])
async def get_masked_academic_report(
    academic_history_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """
    Granular Masking Policy:
    Check financial status before showing grades.
    """
    # 1. Fetch Financial Record
    fin_result = await db.execute(
        select(FinancialRecord)
        .where(FinancialRecord.academic_history_id == academic_history_id)
        .where(FinancialRecord.school_id == current_user.school_id)
    )
    fin_record = fin_result.scalars().first()

    if not fin_record:
        raise HTTPException(status_code=404, detail="لم يتم العثور على سجل مالي لهذا العام الدراسي")

    # 2. Fetch Grades with subject names
    grades_result = await db.execute(
        select(Grade)
        .options(selectinload(Grade.subject))
        .where(Grade.academic_history_id == academic_history_id)
        .where(Grade.school_id == current_user.school_id)
    )
    grades = grades_result.scalars().all()

    # 3. Apply Policy
    report = {
        "status": "success",
        "financial_status": fin_record.payment_status,
        "total_required": fin_record.total_required,
        "amount_paid": fin_record.amount_paid,
        "message": "",
        "grades": []
    }

    if fin_record.payment_status.lower() != "paid":
        report["message"] = "تنبيه: الطالب متعثر مالياً. تم حجب الدرجات حتى يتم سداد القسط المتبقي."
        # Mask grades
        for g in grades:
            report["grades"].append({
                "subject_name": g.subject.name if g.subject else str(g.subject_id),
                "subject_id": str(g.subject_id),
                "score": "***"  # MASKED
            })
    else:
        report["message"] = "الرصيد مسدد بالكامل."
        for g in grades:
            report["grades"].append({
                "subject_name": g.subject.name if g.subject else str(g.subject_id),
                "subject_id": str(g.subject_id),
                "score": g.score,
                "blockchain_hash": g.blockchain_hash
            })

    return report


@router.get("/dashboard/students", response_model=List[Dict[str, Any]])
async def get_dashboard_students(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """
    يعيد قائمة كاملة بالطلاب مع معلومات السجل الأكاديمي والحالة المالية.
    مخصص للوحة التحكم (Dashboard) في الواجهة الأمامية.
    """
    # Fetch students for this school
    students_result = await db.execute(
        select(Student)
        .where(Student.school_id == current_user.school_id)
    )
    students = students_result.scalars().all()

    result = []
    for student in students:
        # Get academic history
        acad_result = await db.execute(
            select(AcademicHistory)
            .where(AcademicHistory.student_id == student.id)
            .where(AcademicHistory.school_id == current_user.school_id)
            .order_by(AcademicHistory.academic_year.desc())
            .limit(1)
        )
        acad = acad_result.scalars().first()

        financial_status = "غير متوفر"
        academic_history_id = None
        if acad:
            academic_history_id = str(acad.id)
            fin_result = await db.execute(
                select(FinancialRecord)
                .where(FinancialRecord.academic_history_id == acad.id)
            )
            fin = fin_result.scalars().first()
            if fin:
                financial_status = "مسدد" if fin.payment_status.lower() == "paid" else "متعثر"

        result.append({
            "id": str(student.id),
            "full_name": student.full_name,
            "student_number": student.student_number,
            "grade_level": student.current_grade_level,
            "financial_status": financial_status,
            "academic_history_id": academic_history_id,
        })

    return result


@router.get("/dashboard/student/{student_id}", response_model=Dict[str, Any])
async def get_student_full_report(
    student_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """
    يعيد التقرير الكامل للطالب: بيانات شخصية + درجات (مع تطبيق البوابة المالية) + حضور.
    """
    # 1. Student info
    stu_result = await db.execute(
        select(Student)
        .where(Student.id == student_id)
        .where(Student.school_id == current_user.school_id)
    )
    student = stu_result.scalars().first()
    if not student:
        raise HTTPException(status_code=404, detail="لم يتم العثور على الطالب")

    # 2. Academic History
    acad_result = await db.execute(
        select(AcademicHistory)
        .where(AcademicHistory.student_id == student_id)
        .where(AcademicHistory.school_id == current_user.school_id)
        .order_by(AcademicHistory.academic_year.desc())
        .limit(1)
    )
    acad = acad_result.scalars().first()

    report = {
        "student": {
            "id": str(student.id),
            "full_name": student.full_name,
            "student_number": student.student_number,
            "grade_level": student.current_grade_level,
            "date_of_birth": str(student.date_of_birth),
            "gender": student.gender,
            "nationality": student.nationality,
        },
        "grades": [],
        "attendance": [],
        "financial": {},
        "financial_message": "",
        "blockchain_verified": False,
    }

    if not acad:
        return report

    # 3. Financial Record
    fin_result = await db.execute(
        select(FinancialRecord)
        .where(FinancialRecord.academic_history_id == acad.id)
    )
    fin = fin_result.scalars().first()

    is_paid = fin and fin.payment_status.lower() == "paid"
    report["financial"] = {
        "total_required": fin.total_required if fin else 0,
        "amount_paid": fin.amount_paid if fin else 0,
        "payment_status": fin.payment_status if fin else "غير متوفر",
        "remaining": (fin.total_required - fin.amount_paid) if fin else 0,
    }

    # 4. Grades with blockchain + masking
    grades_result = await db.execute(
        select(Grade)
        .options(selectinload(Grade.subject))
        .where(Grade.academic_history_id == acad.id)
        .where(Grade.school_id == current_user.school_id)
        .order_by(Grade.created_at.asc())
    )
    grades = grades_result.scalars().all()

    if is_paid:
        report["financial_message"] = "✅ الرصيد مسدد بالكامل."
        for g in grades:
            report["grades"].append({
                "subject": g.subject.name if g.subject else "غير معروف",
                "score": g.score,
                "hash": g.blockchain_hash[:16] + "...",
            })
    else:
        report["financial_message"] = "⚠️ تنبيه: الطالب متعثر مالياً. تم حجب الدرجات الرسمية إلى حين سداد القسط المتبقي."
        for g in grades:
            report["grades"].append({
                "subject": g.subject.name if g.subject else "غير معروف",
                "score": "***",
                "hash": "محجوب",
            })

    # 5. Blockchain Verification
    previous_hash = "0"
    blockchain_ok = True
    for grade in grades:
        data_to_hash = {
            "student_id": str(acad.id),
            "subject_id": str(grade.subject_id),
            "score": grade.score,
        }
        if not blockchain.verify_integrity(data_to_hash, previous_hash, grade.blockchain_hash):
            blockchain_ok = False
            break
        previous_hash = grade.blockchain_hash
    report["blockchain_verified"] = blockchain_ok

    # 6. Attendance
    att_result = await db.execute(
        select(AttendanceRecord)
        .where(AttendanceRecord.student_id == student_id)
        .where(AttendanceRecord.school_id == current_user.school_id)
        .order_by(AttendanceRecord.date.desc())
    )
    attendance = att_result.scalars().all()
    status_map = {"present": "حاضر", "absent": "غائب", "late": "متأخر", "excused": "معذور"}
    for a in attendance:
        report["attendance"].append({
            "date": str(a.date),
            "status": status_map.get(a.status, a.status),
        })

    return report
