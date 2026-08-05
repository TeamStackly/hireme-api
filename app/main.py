from fastapi import FastAPI

from app.database import Base, engine
from app.routers import (
    auth,
    company,
    student,
    application,
    admin,
    job 
)

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="HireMe Job Portal API"
)

app.include_router(auth.router)
app.include_router(company.router)
app.include_router(student.router)
app.include_router(application.router)
app.include_router(admin.router)
app.include_router(job.router)


@app.get("/")
def home():
    return {
        "message": "HireMe Job Portal API"
    }