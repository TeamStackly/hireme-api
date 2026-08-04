from fastapi import FastAPI

from app.database import Base, engine
<<<<<<< HEAD
from app.routers import (
    auth,
    application,
    admin
)
=======
from app.routers import company
from app.routers import auth
>>>>>>> company-module

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="HireMe Job Portal API"
)

app.include_router(auth.router)
app.include_router(company.router)
app.include_router(application.router)
app.include_router(admin.router)


@app.get("/")
def home():
    return {
        "message": "HireMe Job Portal API"
    }