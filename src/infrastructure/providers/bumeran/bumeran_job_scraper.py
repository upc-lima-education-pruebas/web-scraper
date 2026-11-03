from src.domain.entities.job import Job
from src.domain.value_objects.origin_page import OriginPage
from src.domain.ports.job_scraper_port import JobScraperPort
from src.infrastructure.clients.http_client import HttpClient
from src.infrastructure.processing.normalizers.url_normalizer import url_normalizer
from src.infrastructure.providers.bumeran.bumeran_job_mapper import bumeran_job_mapper
import time
import math

class BumeranJobScraper(JobScraperPort):
    ORIGIN_PAGE = OriginPage.Bumeran
    
    BASE_URL = "https://www.bumeran.com.pe"
    BASE_HEARDERS = {
        "origin": "https://www.bumeran.com.pe",
        "referer": f"https://www.bumeran.com.pe/empleos.html",
        "user-agent": "Mozilla/5.0",
        "x-site-id": "BMPE"
    }
    PAGE_SIZE = 5000
    
    def __init__(self):
        self.client_http = HttpClient()
    
    def get_jobs_test(self, max_amount: str = None) -> list[Job]:
        if max_amount == 0:
            return []
        id_set = self.get_job_ids(max_amount)
        return self._get_job_data(id_set)

    def get_jobs(self, id_set: set[str]) -> list[Job]:
        return self._get_job_data(id_set)
    
    def get_job_ids(self, max_amount: int = None) -> set[str]:
        url = f"{self.BASE_URL}/api/avisos/total"
        total_jobs_raw = self.client_http.get_json(url, self.BASE_HEARDERS)
        total_jobs = total_jobs_raw["total"]
        if max_amount is None or max_amount > total_jobs:
            max_amount = total_jobs
        pages = math.ceil(max_amount / self.PAGE_SIZE)
        id_set = set()
        payload = {
            "filtros": []
        }
        for page in range(pages):
            remaining = max_amount - len(id_set)
            current_page_size = min(self.PAGE_SIZE, remaining)
            url = f"{self.BASE_URL}/api/avisos/searchV2?pageSize={current_page_size}&page={page}&sort=RELEVANTES"
            response = self.client_http.post(url, self.BASE_HEARDERS, payload)
            id_set.update(str(job["id"]) for job in response["content"])
        return id_set
    
    def _get_job_data(self, ids: list[str]) -> list[Job]:
        job_list = []
        for id in ids:
            url = f"{self.BASE_URL}/api/candidates/fichaAvisoNormalizada/{id}"
            try:
                response = self.client_http.get_json(url, self.BASE_HEARDERS)
                job = bumeran_job_mapper(response["aviso"])
                job_list.append(job)
            except Exception as e:
                print(f"Could not get job with id {job.external_id}: {e}\nSleeping for 2 seconds")
                time.sleep(2)
        return job_list