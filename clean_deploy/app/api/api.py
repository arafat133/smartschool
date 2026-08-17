from fastapi import APIRouter
from app.api.endpoints import auth, students, attendance, grades, finance, schools, users

api_router = APIRouter()
api_router.include_router(schools.router, prefix="/schools", tags=["المدارس (Schools)"])
api_router.include_router(users.router, prefix="/users", tags=["المستخدمين الجدد (Users)"])
api_router.include_router(auth.router, prefix="/auth", tags=["التحقق والمستخدمين (Auth)"])
api_router.include_router(students.router, prefix="/students", tags=["الطلاب (Students)"])
api_router.include_router(attendance.router, prefix="/attendance", tags=["الحضور والغياب (Attendance)"])
api_router.include_router(grades.router, prefix="/grades", tags=["الدرجات والبلوكشين (Grades & Blockchain)"])
api_router.include_router(finance.router, prefix="/finance", tags=["الشؤون المالية (Finance)"])
