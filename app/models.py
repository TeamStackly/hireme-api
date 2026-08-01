from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    ForeignKey,
    Text,
    DECIMAL
)
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import Base


# ==========================
# Users Table
# ==========================
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False, index=True)
    phone = Column(String(10), unique=True, nullable=False)
    password = Column(String(255), nullable=False)

    # admin | company | student
    role = Column(String(20), nullable=False)

    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    student_profile = relationship(
        "StudentProfile",
        back_populates="user",
        uselist=False,
        cascade="all, delete"
    )

    company_profile = relationship(
        "CompanyProfile",
        back_populates="user",
        uselist=False,
        cascade="all, delete"
    )


# ==========================
# Student Profiles Table
# ==========================
class StudentProfile(Base):
    __tablename__ = "student_profiles"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False
    )

    education = Column(String(255))
    skills = Column(Text)
    experience = Column(String(100))
    resume_path = Column(String(255))
    location = Column(String(100))

    # Relationships
    user = relationship(
        "User",
        back_populates="student_profile"
    )

    applications = relationship(
        "Application",
        back_populates="student",
        cascade="all, delete"
    )


# ==========================
# Company Profiles Table
# ==========================
class CompanyProfile(Base):
    __tablename__ = "company_profiles"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False
    )

    company_name = Column(String(150), nullable=False)
    company_email = Column(String(100), nullable=False)
    company_phone = Column(String(10), nullable=False)
    address = Column(Text)
    industry = Column(String(100))

    approval_status = Column(
        String(20),
        default="Pending"
    )

    # Relationships
    user = relationship(
        "User",
        back_populates="company_profile"
    )

    jobs = relationship(
        "Job",
        back_populates="company",
        cascade="all, delete"
    )


# ==========================
# Jobs Table
# ==========================
class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)

    company_id = Column(
        Integer,
        ForeignKey("company_profiles.id", ondelete="CASCADE"),
        nullable=False
    )

    job_title = Column(String(150), nullable=False)

    description = Column(Text)

    location = Column(String(100))

    salary = Column(
        DECIMAL(10, 2),
        nullable=False
    )

    required_skill = Column(Text)

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    # Relationships
    company = relationship(
        "CompanyProfile",
        back_populates="jobs"
    )

    applications = relationship(
        "Application",
        back_populates="job",
        cascade="all, delete"
    )


# ==========================
# Applications Table
# ==========================
class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)

    job_id = Column(
        Integer,
        ForeignKey("jobs.id", ondelete="CASCADE"),
        nullable=False
    )

    student_id = Column(
        Integer,
        ForeignKey("student_profiles.id", ondelete="CASCADE"),
        nullable=False
    )

    application_status = Column(
        String(30),
        default="Pending"
    )

    applied_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    # Relationships
    job = relationship(
        "Job",
        back_populates="applications"
    )

    student = relationship(
        "StudentProfile",
        back_populates="applications"
    )
