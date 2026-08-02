from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models import (
    User,
    CompanyProfile,
    StudentProfile,
    Job,
    Application
)
from app.core.dependencies import require_admin

router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)
# ==========================================
# Approve Company
# ==========================================
@router.put(
    "/approve-company/{company_id}"
)
def approve_company(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):

    company = db.query(CompanyProfile).filter(
        CompanyProfile.id == company_id
    ).first()

    if company is None:
        raise HTTPException(
            status_code=404,
            detail="Company not found"
        )

    company.approval_status = "Approved"

    db.commit()
    db.refresh(company)

    return {
        "message": "Company approved successfully",
        "company": company.company_name
    }
# ==========================================
# Dashboard Statistics
# ==========================================
@router.get("/dashboard")
def dashboard_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):

    total_users = db.query(User).count()
    total_students = db.query(StudentProfile).count()
    total_companies = db.query(CompanyProfile).count()
    total_jobs = db.query(Job).count()
    total_applications = db.query(Application).count()

    return {
        "total_users": total_users,
        "total_students": total_students,
        "total_companies": total_companies,
        "total_jobs": total_jobs,
        "total_applications": total_applications
    }