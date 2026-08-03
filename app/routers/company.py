from typing import Optional

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status
)
from app.core.dependencies import require_company
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.database import get_db
from app.models import User, CompanyProfile
from app.schemas import (
    CompanyProfileCreate,
    CompanyProfileUpdate,
    CompanyProfileResponse
)

from app.core.dependencies import (
    require_company,
    require_admin
)

router = APIRouter(
    prefix="/company",
    tags=["Company Module"]
)


# ============================================================
# Helper Function
# ============================================================

def get_company_profile(db: Session, user_id: int):
    """
    Returns company profile of logged in company
    """

    return (
        db.query(CompanyProfile)
        .filter(CompanyProfile.user_id == user_id)
        .first()
    )


# ============================================================
# Create Company Profile
# ============================================================

@router.post(
    "/profile",
    response_model=CompanyProfileResponse,
    status_code=status.HTTP_201_CREATED
)
def create_company_profile(
    company: CompanyProfileCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_company)
):

    # Check existing profile
    existing = get_company_profile(db, current_user.id)

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Company profile already exists."
        )

    # Check duplicate company email
    duplicate_email = (
        db.query(CompanyProfile)
        .filter(
            CompanyProfile.company_email == company.company_email
        )
        .first()
    )

    if duplicate_email:
        raise HTTPException(
            status_code=400,
            detail="Company email already registered."
        )

    # Check duplicate phone
    duplicate_phone = (
        db.query(CompanyProfile)
        .filter(
            CompanyProfile.company_phone == company.company_phone
        )
        .first()
    )

    if duplicate_phone:
        raise HTTPException(
            status_code=400,
            detail="Company phone already registered."
        )

    new_company = CompanyProfile(
        user_id=current_user.id,
        company_name=company.company_name,
        company_email=company.company_email,
        company_phone=company.company_phone,
        address=company.address,
        industry=company.industry
    )

    try:

        db.add(new_company)
        db.commit()
        db.refresh(new_company)

        return new_company

    except SQLAlchemyError:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Unable to create company profile."
        )


# ============================================================
# Get Logged In Company Profile
# ============================================================

@router.get(
    "/profile",
    response_model=CompanyProfileResponse
)
def get_my_company_profile(
    db: Session =Depends(get_db),
    current_user: User = Depends(require_company)
):

    profile = get_company_profile(
        db,
        current_user.id
    )

    if not profile:

        raise HTTPException(
            status_code=404,
            detail="Company profile not found."
        )

    return profile


# ============================================================
# Update Company Profile
# ============================================================

@router.put(
    "/profile",
    response_model=CompanyProfileResponse
)
def update_company_profile(
    company: CompanyProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_company)
):

    profile = get_company_profile(
        db,
        current_user.id
    )

    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company profile not found."
        )

    # Duplicate email validation
    if company.company_email:

        existing_email = (
            db.query(CompanyProfile)
            .filter(
                CompanyProfile.company_email == company.company_email,
                CompanyProfile.id != profile.id
            )
            .first()
        )

        if existing_email:
            raise HTTPException(
                status_code=400,
                detail="Company email already exists."
            )

    # Duplicate phone validation
    if company.company_phone:

        existing_phone = (
            db.query(CompanyProfile)
            .filter(
                CompanyProfile.company_phone == company.company_phone,
                CompanyProfile.id != profile.id
            )
            .first()
        )

        if existing_phone:
            raise HTTPException(
                status_code=400,
                detail="Company phone already exists."
            )

    update_data = company.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(profile, key, value)

    try:

        db.commit()
        db.refresh(profile)

        return profile

    except SQLAlchemyError:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Unable to update company profile."
        )


# ============================================================
# Delete Company Profile
# ============================================================

@router.delete(
    "/profile",
    status_code=status.HTTP_200_OK
)
def delete_company_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_company)
):

    profile = get_company_profile(
        db,
        current_user.id
    )

    if profile is None:

        raise HTTPException(
            status_code=404,
            detail="Company profile not found."
        )

    try:

        db.delete(profile)
        db.commit()

        return {
            "message": "Company profile deleted successfully."
        }

    except SQLAlchemyError:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Unable to delete company profile."
        )



# ============================================================
# Get All Companies (Admin Only)
# ============================================================

@router.get(
    "/all",
    response_model=list[CompanyProfileResponse]
)
def get_all_companies(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_company)
):

    skip = (page - 1) * limit

    companies = (
        db.query(CompanyProfile)
        .offset(skip)
        .limit(limit)
        .all()
    )

    return companies




# ============================================================
# Search Companies
# ============================================================

@router.get(
    "/search/",
    response_model=list[CompanyProfileResponse]
)
def search_company(
    company_name: Optional[str] = None,
    industry: Optional[str] = None,
    location: Optional[str] = None,
    db: Session = Depends(get_db)
):

    query = db.query(CompanyProfile)

    if company_name:
        query = query.filter(
            CompanyProfile.company_name.ilike(
                f"%{company_name}%"
            )
        )

    if industry:
        query = query.filter(
            CompanyProfile.industry.ilike(
                f"%{industry}%"
            )
        )

    if location:
        query = query.filter(
            CompanyProfile.address.ilike(
                f"%{location}%"
            )
        )

    companies = query.all()

    return companies



# ============================================================
# Approve Company (Admin Only)
# ============================================================

@router.put(
    "/approve/{company_id}",
    response_model=CompanyProfileResponse
)
def approve_company(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_company)
):

    company = (
        db.query(CompanyProfile)
        .filter(
            CompanyProfile.id == company_id
        )
        .first()
    )

    if company is None:
        raise HTTPException(
            status_code=404,
            detail="Company not found."
        )

    company.approval_status = "Approved"

    try:

        db.commit()
        db.refresh(company)

        return company

    except SQLAlchemyError:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Unable to approve company."
        )


# ============================================================
# Reject Company (Admin Only)
# ============================================================

@router.put(
    "/reject/{company_id}",
    response_model=CompanyProfileResponse
)
def reject_company(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_company)
):

    company = (
        db.query(CompanyProfile)
        .filter(
            CompanyProfile.id == company_id
        )
        .first()
    )

    if company is None:
        raise HTTPException(
            status_code=404,
            detail="Company not found."
        )

    company.approval_status = "Rejected"

    try:

        db.commit()
        db.refresh(company)

        return company

    except SQLAlchemyError:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Unable to reject company."
        )
        

# ============================================================
# Get Company By ID (Public)
# ============================================================

@router.get(
    "/{company_id}",
    response_model=CompanyProfileResponse
)
def get_company_by_id(
    company_id: int,
    db: Session = Depends(get_db)
):

    company = (
        db.query(CompanyProfile)
        .filter(
            CompanyProfile.id == company_id
        )
        .first()
    )

    if not company:

        raise HTTPException(
            status_code=404,
            detail="Company not found."
        )

    return company

from typing import Optional
from fastapi import Query
