from requests import Session
from fastapi import FastAPI, HTTPException , Depends
from cloud_functions import schedule_job, delete_job, logging, send_email
from db import *
from app_db import SessionLocal
from crud import insert_active_promotion, delete_active_promotion, get_promotions
from dotenv import load_dotenv
from models import Base
import schema
from agents.weather_recommendation_agent import recommend_products_by_weather
from agents.social_media_agent import post_products_to_instagram
from agents.personalized_recommendation_agent import recommend_personalized_products
from pydantic import BaseModel
import json

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
class EmailRequest(BaseModel):
    to: str
    subject: str
    body: str

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/schedule-job/{merchant_id}/{job_name}")
def create_scheduled_job(merchant_id: int, job_name: str, db: Session = Depends(get_db)):
    """
    Endpoint to create a new Cloud Scheduler job.
    """
    if job_name not in endpoints:
        raise HTTPException(status_code=404, detail=f"Promotion '{job_name}' not found.")
    logging.info(f"Received request to create job: {job_name} from merchant: {merchant_id}")
    url = f"{endpoints[job_name]['url']}/{merchant_id}" 
    schedule = endpoints[job_name]['schedule']
    job_id = f"{job_name}-{merchant_id}"
    status = schedule_job(job_id, url, schedule)
    if status:
        print(insert_active_promotion(db, merchant_id, job_name))
        return {"message": f"Cloud Scheduler job '{job_name}' created."}
    else:
         raise HTTPException(status_code=500, detail=f"Error creating job.")

@app.get("/delete-job/{merchant_id}/{job_name}")
def delete_scheduled_job(merchant_id: str, job_name: str, db: Session = Depends(get_db)):
    """
    Endpoint to delete a cloud Scheduled job.
    """
    if job_name not in endpoints:
        raise HTTPException(status_code=404, detail=f"Promotion '{job_name}' not found.")
    logging.info(f"Received request to delete job: {job_name} from merchant: {merchant_id}")
    delete_job(merchant_id, job_name)
    delete_active_promotion(db, merchant_id, job_name)
    return {"message": f"Cloud Scheduler job '{job_name}' deleted."}
    
#In FastAPI, static paths must be declared before dynamic ones.  
@app.get("/promotions/know-your-customer")
def know_your_customer():
    """
    Endpoint to be called from the scheduler to apply send google form to the user to know more information
    """
    # which_customer ?
    email_body = "We’d love to know more about you."
    # notify_users
    logging.info("Emails will be send")
    try:
         send_email(
         "ssadik@deloitte.com",
         "Tell Us a Little About Yourself!",
          body = email_body,
          form_link="https://forms.gle/dBwmSPf4vPuoYxMG7")
         return {"status": "success", "message": "Email sent successfully"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    
@app.get("/promotions/happy-hour/{merchant_id}")
def happy_hour(merchant_id: int):
    """
    Endpoint to be called from the scheduler to apply happy-hour promotion
    """
    happy_hour = get_hour_with_least_orders(merchant_id)
    emails = get_users_email_by_merchant_id(merchant_id)
    email_body = f"Exclusive Happy Hour! Get 20% off from {happy_hour}:00 to {happy_hour + 1}:00 today only! Enjoy your day!"
    # notify_users
    logging.info("Emails will be send")
    for email in emails:
      send_email(
      to_email=email,
      subject="Happy hour Promotion",
      body=email_body)

@app.get("/promotions/birthday/{merchant_id}")
def birthday(merchant_id: int):
    """
    Endpoint to be called from the scheduler to apply birthday promotion
    """
    users = get_birthdays_last_month_by_merchant(merchant_id)
    emails = get_users_email_by_merchant_id(merchant_id)
    email_body = f"It’s your special day 🎉 Enjoy 1 free item from our hand-picked birthday selection!"
    # notify_users
    logging.info("Emails will be send")
    for email in emails:
      send_email(
      to_email=email,
      subject="Birthday Promotion",
      body=email_body)
        
@app.get("/promotions/{merchant_id}", response_model=list[schema.PromotionWithStatus])
def read_promotions_for_merchant(merchant_id: str, db: Session = Depends(get_db)):
    rows = get_promotions(db, merchant_id)
    return [dict(row._mapping) for row in rows]

@app.get("/recommendations/weather/{merchant_id}")
def weather_recommendation(merchant_id: int):
    notification_message = recommend_products_by_weather(merchant_id)
    notification_message = notification_message.strip("`\n ")
    if notification_message.startswith("json"):
        notification_message = notification_message[4:].strip()
    notification_message = json.loads(notification_message)
    emails = ['nhelmy@deloitte.com', 'ssadik@deloitte.com'] # relaced with the actual emails from db
    for email in emails:
      send_email(
      to_email=email,
      subject=notification_message['subject'],
      body=notification_message['message'])

@app.get("/recommendations/social-media/{merchant_id}")
def post_to_instagram(merchant_id: int):
    post_products_to_instagram(merchant_id)
    return

@app.get("/recommendations/personalized/{merchant_id}")
def personalized_recommendation(merchant_id: int):
    recommend_personalized_products(merchant_id)

# just for testing
@app.post("/send-email")
def send_email_endpoint(request: EmailRequest):
    try:
        send_email(request.to, request.subject, request.body)
        return {"status": "success", "message": "Email sent successfully"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
