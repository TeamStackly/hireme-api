from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import (
    User,
    Application,
    Job,
    StudentProfile,
    CompanyProfile
)
from app.schemas import (
    ApplicationCreate,
    ApplicationResponse
)
from app.core.dependencies import (
    get_current_user,
    require_student,
    require_company
)

router = APIRouter(
    prefix="/applications",
    tags=["Applications"]
)
# ==========================================
# Apply for Job
# ==========================================
@router.post(
    "/apply",
    response_model=ApplicationResponse,
    status_code=status.HTTP_201_CREATED
)
def apply_job(
    application: ApplicationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_student)
):

    # Check student profile
    student = db.query(StudentProfile).filter(
        StudentProfile.user_id == current_user.id
    ).first()

    if student is None:
        raise HTTPException(
            status_code=404,
            detail="Student profile not found"
        )

    # Check job exists
    job = db.query(Job).filter(
        Job.id == application.job_id
    ).first()

    if job is None:
        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )

    # Prevent duplicate application
    existing_application = db.query(Application).filter(
        Application.job_id == application.job_id,
        Application.student_id == student.id
    ).first()

    if existing_application:
        raise HTTPException(
            status_code=400,
            detail="You have already applied for this job"
        )

    new_application = Application(
        job_id=application.job_id,
        student_id=student.id
    )

    db.add(new_application)
    db.commit()
    db.refresh(new_application)

    return new_application
# ==========================================
# Get My Applications
# ==========================================
@router.get(
    "/my-applications",
    response_model=list[ApplicationResponse]
)
def get_my_applications(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_student)
):

    student = db.query(StudentProfile).filter(
        StudentProfile.user_id == current_user.id
    ).first()

    if student is None:
        raise HTTPException(
            status_code=404,
            detail="Student profile not found"
        )

    applications = db.query(Application).filter(
        Application.student_id == student.id
    ).all()

    return applications
# ==========================================
# Get Applicants for a Job
# ==========================================
@router.get(
    "/job/{job_id}",
    response_model=list[ApplicationResponse]
)
def get_applicants(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_company)
):

    company = db.query(CompanyProfile).filter(
        CompanyProfile.user_id == current_user.id
    ).first()

    if company is None:
        raise HTTPException(
            status_code=404,
            detail="Company profile not found"
        )

    job = db.query(Job).filter(
        Job.id == job_id,
        Job.company_id == company.id
    ).first()

    if job is None:
        raise HTTPException(
            status_code=404,
            detail="Job not found or access denied"
        )

    applications = db.query(Application).filter(
        Application.job_id == job_id
    ).all()

    return applications
# ==========================================
# Update Application Status
# ==========================================
@router.put(
    "/{application_id}/status",
    response_model=ApplicationResponse
)
def update_application_status(
    application_id: int,
    status_value: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_company)
):

    application = db.query(Application).filter(
        Application.id == application_id
    ).first()

    if application is None:
        raise HTTPException(
            status_code=404,
            detail="Application not found"
        )

    if status_value.lower() not in ["accepted", "rejected", "pending"]:
        raise HTTPException(
            status_code=400,
            detail="Status must be Accepted, Rejected or Pending"
        )

    application.application_status = status_value.capitalize()

    db.commit()
    db.refresh(application)

    return application
# ==========================================
# Accept Application
# ==========================================
@router.put(
    "/{application_id}/accept",
    response_model=ApplicationResponse
)
def accept_application(
    application_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_company)
):

    application = db.query(Application).filter(
        Application.id == application_id
    ).first()

    if application is None:
        raise HTTPException(
            status_code=404,
            detail="Application not found"
        )

    application.application_status = "Accepted"

    db.commit()
    db.refresh(application)

    return application
# ==========================================
# Reject Application
# ==========================================
@router.put(
    "/{application_id}/reject",
    response_model=ApplicationResponse
)
def reject_application(
    application_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_company)
):

    application = db.query(Application).filter(
        Application.id == application_id
    ).first()

    if application is None:
        raise HTTPException(
            status_code=404,
            detail="Application not found"
        )

    application.application_status = "Rejected"

    db.commit()
    db.refresh(application)

    return application