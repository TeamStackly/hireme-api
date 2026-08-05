from fastapi import APIRouter, HTTPException

router = APIRouter(
    prefix="/jobs",
    tags=["Jobs"]
)

# Temporary in-memory storage
jobs = []


@router.get("/")
def get_all_jobs():
    return {"jobs": jobs}


@router.post("/")
def create_job(title: str, company: str, location: str):
    job = {
        "id": len(jobs) + 1,
        "title": title,
        "company": company,
        "location": location
    }
    jobs.append(job)
    return {
        "message": "Job created successfully",
        "job": job
    }


@router.get("/{job_id}")
def get_job(job_id: int):
    for job in jobs:
        if job["id"] == job_id:
            return job
    raise HTTPException(status_code=404, detail="Job not found")


@router.delete("/{job_id}")
def delete_job(job_id: int):
    for job in jobs:
        if job["id"] == job_id:
            jobs.remove(job)
            return {"message": "Job deleted successfully"}
    raise HTTPException(status_code=404, detail="Job not found")