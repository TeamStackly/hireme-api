from fastapi import FastAPI

from app.database import Base, engine

from app.routers import auth
from app.routers import student

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="HireMe Job Portal API"
)

app.include_router(auth.router)
app.include_router(student.router)


@app.get("/")
def home():
    return {
        "message": "HireMe Job Portal API"
    }