from requests import Session
from applicationDb import SessionLocal
from fastapi import FastAPI, HTTPException , Depends
from cloud_functions import schedule_job, logging
from db import *
from dotenv import load_dotenv
from models import Base
import crud, schema
load_dotenv()

app = FastAPI()
API_BASE_URL = os.getenv("API_BASE_URL")

endpoints = {
    'happy-hour': {
        "url": f"{API_BASE_URL}/promotions/happy-hour",
        "schedule": "0 0 * * *" # Runs every day at midnight UTC
    },
    "birthday": {
        "url": f"{API_BASE_URL}/promotions/birthday",
        "schedule": "0 0 * * *"
    }
}

@app.get("/schedule-job/{merchant_id}/{job_name}")
def create_scheduled_job(job_name: str, merchant_id: int):
    """
    Endpoint to create a new Cloud Scheduler job.
    """
    if job_name not in endpoints:
        raise HTTPException(status_code=404, detail=f"Promotion '{job_name}' not found.")
    logging.info(f"Received request to create job: {job_name} from merchant: {merchant_id}")
    url = endpoints[job_name]['url']
    schedule = endpoints[job_name]['schedule']
    job_name = f"{job_name}-{merchant_id}"
    status = schedule_job(job_name, url, schedule)
    if status:
        return {"message": f"Cloud Scheduler job '{job_name}' created."}
    else:
         raise HTTPException(status_code=500, detail=f"Error creating job.")

@app.get("/delete-job/{merchant_id}/{job_name}")
def delete_scheduled_job(job_name: str, merchant_id: int):
    """
    Endpoint to delete a cloud Scheduled job.
    """
    if job_name not in endpoints:
        raise HTTPException(status_code=404, detail=f"Promotion '{job_name}' not found.")
    logging.info(f"Received request to create job: {job_name} from merchant: {merchant_id}")
    delete_job(merchant_id, job_name)
    return {"message": f"Cloud Scheduler job '{job_name}' deleted."}

@app.get("/promotions/happy-hour/{merchant_id}")
def happy_hour(merchant_id: int):
    """
    Endpoint to be called from the scheduler to apply happy-hour promotion
    """
    happy_hour = get_hour_with_least_orders(merchant_id)
    emails = get_users_email_by_merchant_id(merchant_id)
    email_body = f"Exclusive Happy Hour! Get 20% off from {happy_hour}:00 to {happy_hour + 1}:00 today only! Enjoy your day!"
    # notify_users

@app.get("/promotions/birthday/{merchant_id}")
def happy_hour(merchant_id: int):
    """
    Endpoint to be called from the scheduler to apply birthday promotion
    """
    users = get_birthdays_last_month_by_merchant(merchant_id)
    emails = get_users_email_by_merchant_id(merchant_id)
    email_body = f"It’s your special day 🎉 Enjoy 1 free item from our hand-picked birthday selection!"
    # notify_users

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
@app.get("/promotions/{merchant_id}", response_model=list[schema.PromotionWithStatus])
def read_promotions_for_merchant(merchant_id: str, db: Session = Depends(get_db)):
    rows = crud.get_promotions(db, merchant_id)
    return [dict(row._mapping) for row in rows]