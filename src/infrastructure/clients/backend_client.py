from src.application.dtos.job_response import JobResponse
from dataclasses import asdict
import requests
import os

class BackendClient:
    
    def __init__(self):
        self.url = os.getenv("AZURE_BACKEND_URL", "http://localhost:5000/api/v1/job/sync")
        self.headers = {
            "Content-Type": "application/json",
            "X-Scraper-Key": os.getenv('BACKEND_API_KEY', 'llanqui-scraper-secret-key-2026')
        }
    
    def sync_jobs(self, jobs: list[JobResponse]):
        print("Syncing jobs...")
        payload = [asdict(job) for job in jobs]
        response = requests.post(
            self.url,
            json=payload,
            headers=self.headers,
            timeout=120
        )
        response.raise_for_status()
        print("Jobs synced!")