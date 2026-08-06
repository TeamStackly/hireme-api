from datetime import timedelta

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status
)


from fastapi.security import OAuth2PasswordRequestForm

from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.schemas import (
    UserCreate,
    UserResponse,
    UserLogin,
    Token
)

from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token
)

from app.core.dependencies import get_current_user

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

ACCESS_TOKEN_EXPIRE_MINUTES = 30


# ==========================================================
# Register User
# ==========================================================

@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
def register_user(
    user: UserCreate,
    db: Session = Depends(get_db)
):

    # -------------------------
    # Check Email
    # -------------------------

    existing_email = (
        db.query(User)
        .filter(User.email == user.email)
        .first()
    )

    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered."
        )

    # -------------------------
    # Check Phone
    # -------------------------

    existing_phone = (
        db.query(User)
        .filter(User.phone == user.phone)
        .first()
    )

    if existing_phone:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phone number already registered."
        )

    # -------------------------
    # Validate Role
    # -------------------------

    allowed_roles = [
        "student",
        "company",
        "admin"
    ]

    if user.role.lower() not in allowed_roles:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role must be student, company or admin."
        )

    # -------------------------
    # Hash Password
    # -------------------------

    hashed_password = get_password_hash(
        user.password
    )

    # -------------------------
    # Create User
    # -------------------------

    new_user = User(
        full_name=user.full_name,
        email=user.email,
        phone=user.phone,
        password=hashed_password,
        role=user.role.lower()
    )

    try:

        db.add(new_user)

        db.commit()

        db.refresh(new_user)

        return new_user

    except Exception:

        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to register user."
        )
        


# ==========================================================
# Login User
# ==========================================================

@router.post(
    "/login",
    response_model=Token,
    status_code=status.HTTP_200_OK
)
def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Login using email as username.
    """

    # Find user
    user = (
        db.query(User)
        .filter(User.email == form_data.username)
        .first()
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password."
        )

    # Verify password
    if not verify_password(
        form_data.password,
        user.password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password."
        )

    # Check active status
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive."
        )

    # Create JWT Token
    access_token = create_access_token(
        data={
            "sub": user.email
        },
        expires_delta=timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


# ==========================================================
# Current Logged-in User
# ==========================================================

@router.get(
    "/me",
    response_model=UserResponse
)
def get_logged_in_user(
    current_user: User = Depends(get_current_user)
):
    """
    Returns the currently authenticated user.
    """
    return current_user
# ==========================================================
# Logout
# ==========================================================

@router.post("/logout")
def logout():
    """
    JWT logout is handled by the client by deleting the token.
    """
    return {
        "message": "Logout successful. Please remove the token from the client."
    }
    
# ==========================================================
# User Profile
# ==========================================================

@router.get(
    "/profile",
    response_model=UserResponse
)
def profile(
    current_user: User = Depends(get_current_user)
):
    return current_user

# ==========================================================
# Verify Token
# ==========================================================

@router.get("/verify")
def verify(
    current_user: User = Depends(get_current_user)
):
    return {
        "authenticated": True,
        "email": current_user.email,
        "role": current_user.role
    }