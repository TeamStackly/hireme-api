from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional
from datetime import datetime


# ==========================================
# User Schemas
# ==========================================

class UserCreate(BaseModel):
    full_name: str = Field(..., min_length=3, max_length=100)
    email: EmailStr
    phone: str = Field(..., min_length=10, max_length=10)
    password: str = Field(..., min_length=8)
    role: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    phone: str
    role: str
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ==========================================
# Student Profile Schemas
# ==========================================

class StudentProfileCreate(BaseModel):
    education: str
    skills: str
    experience: str
    location: str


class StudentProfileUpdate(BaseModel):
    education: Optional[str] = None
    skills: Optional[str] = None
    experience: Optional[str] = None
    location: Optional[str] = None


class StudentProfileResponse(BaseModel):
    id: int
    user_id: int
    education: str
    skills: str
    experience: str
    resume_path: Optional[str]
    location: str

    model_config = ConfigDict(from_attributes=True)


# ==========================================
# Company Profile Schemas
# ==========================================

class CompanyProfileCreate(BaseModel):
    company_name: str
    company_email: EmailStr
    company_phone: str
    address: str
    industry: str


class CompanyProfileUpdate(BaseModel):
    company_name: Optional[str] = None
    company_email: Optional[EmailStr] = None
    company_phone: Optional[str] = None
    address: Optional[str] = None
    industry: Optional[str] = None


class CompanyProfileResponse(BaseModel):
    id: int
    user_id: int
    company_name: str
    company_email: EmailStr
    company_phone: str
    address: str
    industry: str
    approval_status: str

    model_config = ConfigDict(from_attributes=True)


# ==========================================
# Job Schemas
# ==========================================

class JobCreate(BaseModel):
    job_title: str
    description: str
    location: str
    salary: float
    required_skill: str


class JobUpdate(BaseModel):
    job_title: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    salary: Optional[float] = None
    required_skill: Optional[str] = None


class JobResponse(BaseModel):
    id: int
    company_id: int
    job_title: str
    description: str
    location: str
    salary: float
    required_skill: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ==========================================
# Application Schemas
# ==========================================

class ApplicationCreate(BaseModel):
    job_id: int


class ApplicationResponse(BaseModel):
    id: int
    job_id: int
    student_id: int
    application_status: str
    applied_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ==========================================
# JWT Token Schemas
# ==========================================

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None
