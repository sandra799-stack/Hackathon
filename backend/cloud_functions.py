from google.cloud import scheduler_v1
from google.oauth2 import service_account
from google.api_core.exceptions import NotFound
import logging, os
from fastapi import HTTPException
from dotenv import load_dotenv
import os, ssl, smtplib
from email.message import EmailMessage
load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
PROJECT_ID = os.getenv("PROJECT_ID")
LOCATION_ID = os.getenv("LOCATION_ID")
KEY_PATH = os.getenv("KEY_PATH")

def schedule_job(job_name: str, target_url: str, cron_schedule: str):
    """
    Creates a Cloud Scheduler job using Application Default Credentials.

    Args:
        job_name (str): The name of the job to be created.
        target_url (str): The endpoint to be called.
        cron_schedule(str): CRON expression of the job.
    """
    # Load credentials from the environment. This will use the credentials
    # saved by `gcloud auth application-default login`.
    try:
        logging.info("Loading Application Default Credentials...")
        credentials = service_account.Credentials.from_service_account_file(KEY_PATH)
        logging.info(f"Credentials loaded successfully")

        # Create a client with the loaded credentials
        client = scheduler_v1.CloudSchedulerClient(credentials=credentials)
        parent = f"projects/{PROJECT_ID}/locations/{LOCATION_ID}"

        # Define the job details
        job = scheduler_v1.Job(
            name=f"{parent}/jobs/{job_name}",
            http_target=scheduler_v1.HttpTarget(
                    uri=target_url,
                    http_method=scheduler_v1.HttpMethod.GET
            ),
            schedule=cron_schedule,
            time_zone="America/New_York",
        )

        logging.info(f"Attempting to create job: {job_name}...")
        client.create_job(request={"parent": parent, "job": job})
        logging.info(f"Job created {job_name}")
        return True
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        raise HTTPException(status_code=500, detail=f"Error creating job. {e}")

def delete_job(merchant_id: int, job_name: str):
    """
    Deletes a Cloud Scheduler job.
    
    Args:
        job_name (str): The name of the job to delete.
    """
    try:
        logging.info("Loading Application Default Credentials...")
        credentials = service_account.Credentials.from_service_account_file(KEY_PATH)
        print(f"Credentials loaded successfully")

        client = scheduler_v1.CloudSchedulerClient(credentials=credentials)
        job_name = f"projects/{PROJECT_ID}/locations/{LOCATION_ID}/jobs/{job_name}-{merchant_id}"
        
        logging.info(f"Attempting to delete job: {job_name}...")
        client.delete_job(request={"name": job_name})
        logging.info(f"Job {job_name} deleted successfully!")
        return True
    except NotFound:
        raise HTTPException(status_code=404, detail=f"Error: Job '{job_name}' not found. It may have already been deleted.")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        raise HTTPException(status_code=500, detail=f"Error deleting job.")
    
def send_email(to_email: str, subject: str, body: str , form_link: str | None = None) -> None:
    user = os.environ["GMAIL_USER"]
    app_pw = os.environ["GMAIL_APP_PASSWORD"]

    msg = EmailMessage()
    msg["From"] = user
    msg["To"] = to_email
    msg["Subject"] = subject
       # Always include plain text
    msg.set_content(body if not form_link else f"{body}\n\n{form_link}")
    if form_link:
        html_body = f"""
        <html>
            <body>
                <p>{body}</p>
                <p><a href="{form_link}">Click here to fill out the form</a></p>
            </body>
        </html>
        """
        msg.add_alternative(html_body, subtype="html")
        
    context = ssl.create_default_context()
    with smtplib.SMTP("smtp.gmail.com", 587) as s:
        s.starttls(context=context)
        s.login(user, app_pw)
        s.send_message(msg)
