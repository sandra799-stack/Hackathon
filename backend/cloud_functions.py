from google.cloud import scheduler_v1
import google.auth
from google.api_core.exceptions import NotFound
import logging, os
from dotenv import load_dotenv
load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
PROJECT_ID = os.getenv("PROJECT_ID")
LOCATION_ID = os.getenv("LOCATION_ID")

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
        credentials, project = google.auth.default(
            scopes=['https://www.googleapis.com/auth/cloud-platform']
        )
        logging.info(f"Credentials loaded successfully for project: {project}")

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
        response = client.create_job(request={"parent": parent, "job": job})
        logging.info(f"Job created {job_name}")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")

def delete_job(job_name: str):
    """
    Deletes a Cloud Scheduler job.
    
    Args:
        job_name (str): The name of the job to delete.
    """
    try:
        logging.info("Loading Application Default Credentials...")
        credentials, project = google.auth.default(
            scopes=['https://www.googleapis.com/auth/cloud-platform']
        )
        print(f"Credentials loaded successfully for project: {project}")

        client = scheduler_v1.CloudSchedulerClient(credentials=credentials)
        job_name = f"projects/{PROJECT_ID}/locations/{LOCATION_ID}/jobs/{job_name}"
        
        logging.info(f"Attempting to delete job: {job_name}...")
        client.delete_job(request={"name": job_name})

        logging.info(f"Job {job_name} deleted successfully!")

    except NotFound:
        logging.error(f"Error: Job '{job_name}' not found. It may have already been deleted.")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")