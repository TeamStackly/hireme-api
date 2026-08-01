from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    UploadFile,
    File
)

from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, StudentProfile, Job, Application
from app.schemas import (
    StudentProfileCreate,
    StudentProfileUpdate,
    StudentProfileResponse,
    JobResponse,
    ApplicationResponse
)

from app.core.dependencies import require_student

import os
import shutil


router = APIRouter(
    prefix="/student",
    tags=["Student"]
)


@router.post(
    "/profile",
    response_model=StudentProfileResponse,
    status_code=status.HTTP_201_CREATED
)
def create_student_profile(
    profile: StudentProfileCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_student)
):
    existing = db.query(StudentProfile).filter(
        StudentProfile.user_id == current_user.id
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Student profile already exists"
        )

    student = StudentProfile(
        user_id=current_user.id,
        education=profile.education,
        skills=profile.skills,
        experience=profile.experience,
        location=profile.location
    )

    db.add(student)
    db.commit()
    db.refresh(student)

    return student

@router.get(
    "/profile",
    response_model=StudentProfileResponse
)
def get_my_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_student)
):
    profile = db.query(StudentProfile).filter(
        StudentProfile.user_id == current_user.id
    ).first()

    if not profile:
        raise HTTPException(
            status_code=404,
            detail="Profile not found"
        )

    return profile

@router.put(
    "/profile",
    response_model=StudentProfileResponse
)
def update_profile(
    profile: StudentProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_student)
):
    student = db.query(StudentProfile).filter(
        StudentProfile.user_id == current_user.id
    ).first()

    if not student:
        raise HTTPException(
            status_code=404,
            detail="Profile not found"
        )

    for key, value in profile.model_dump(exclude_unset=True).items():
        setattr(student, key, value)

    db.commit()
    db.refresh(student)

    return student

@router.post("/upload-resume")
def upload_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_student)
):

    profile = db.query(StudentProfile).filter(
        StudentProfile.user_id == current_user.id
    ).first()

    if not profile:
        raise HTTPException(
            status_code=404,
            detail="Student profile not found"
        )

    # Create uploads folder if not exists
    os.makedirs("uploads", exist_ok=True)

    file_path = f"uploads/{current_user.id}_{file.filename}"

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    profile.resume_path = file_path

    db.commit()
    db.refresh(profile)

    return {
        "message": "Resume uploaded successfully",
        "resume_path": file_path
    }

@router.get("/jobs", response_model=list[JobResponse])
def get_all_jobs(
    db: Session = Depends(get_db)
):

    jobs = db.query(Job).all()

    return jobs

@router.get("/jobs/{job_id}", response_model=JobResponse)
def get_job(
    job_id: int,
    db: Session = Depends(get_db)
):

    job = db.query(Job).filter(
        Job.id == job_id
    ).first()

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )

    return job

@router.post(
    "/apply/{job_id}",
    response_model=ApplicationResponse,
    status_code=status.HTTP_201_CREATED
)
def apply_for_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_student)
):

    # Check student profile
    student = db.query(StudentProfile).filter(
        StudentProfile.user_id == current_user.id
    ).first()

    if not student:
        raise HTTPException(
            status_code=404,
            detail="Student profile not found"
        )

    # Check job
    job = db.query(Job).filter(
        Job.id == job_id
    ).first()

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )

    # Prevent duplicate application
    existing = db.query(Application).filter(
        Application.job_id == job_id,
        Application.student_id == student.id
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="You have already applied for this job"
        )

    application = Application(
        job_id=job_id,
        student_id=student.id
    )

    db.add(application)
    db.commit()
    db.refresh(application)

    return application

@router.get(
    "/my-applications",
    response_model=list[ApplicationResponse]
)
def my_applications(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_student)
):

    student = db.query(StudentProfile).filter(
        StudentProfile.user_id == current_user.id
    ).first()

    if not student:
        raise HTTPException(
            status_code=404,
            detail="Student profile not found"
        )

    applications = db.query(Application).filter(
        Application.student_id == student.id
    ).all()

    return applications