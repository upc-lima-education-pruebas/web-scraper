from src.domain.entities.job import Job
from src.domain.ports.job_scraper_port import JobScraperPort
from src.domain.value_objects.origin_page import OriginPage
from src.infrastructure.clients.http_client import HttpClient
from src.infrastructure.providers.empleosperu.empleosperu_job_mapper import empleosperu_job_mapper
import time

class EmpleosPeruJobScraper(JobScraperPort):
    ORIGIN_PAGE = OriginPage.EmpleosPeru
    
    BASE_URL = "https://mtpe-candidatos.empleosperu.gob.pe/api/jobs"
    BASE_HEADERS = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "es-PE,es-419;q=0.9,es;q=0.8,en;q=0.7",
        "Connection": "keep-alive",
        "Content-Type": "application/json",
        "Host": "mtpe-candidatos.empleosperu.gob.pe",
        "Sec-Ch-Ua": '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
    }
    
    def __init__(self):
        self.client = HttpClient()
    
    def get_jobs_test(self, max_amount: str = None) -> list[Job]:
        if max_amount == 0: return []
        id_set = self.get_job_ids(max_amount)
        return self.get_jobs(id_set)
    
    def get_jobs(self, id_set: set[str]) -> list[Job]:       
        job_list = []
        for id in id_set:
            job_detail = None
            try:
                headers = self.BASE_HEADERS.copy()
                headers["Referer"] = f"{self.BASE_URL}/search-jobs/description?jobId={id}"
                job_detail = self.client.get_json(f"{self.BASE_URL}/{id}", headers)
                job = empleosperu_job_mapper(job_detail)
                job_list.append(job)
            except Exception as e:
                print(f"Could not get job with id {id}: {e}\nSleeping for 0.3 seconds")
                time.sleep(0.3)
        return job_list
    
    def get_job_ids(self, max_amount: int = None) -> set[str]:
        if max_amount == 0:
            return []
        
        base_data = self.client.get_json(f"{self.BASE_URL}?limit=0", self.BASE_HEADERS)
        total_count = int(base_data["totalCount"])
        if max_amount is None or max_amount > total_count:
            max_amount = total_count
        url = f"{self.BASE_URL}?limit={max_amount}"
        data = self.client.get_json(url)
        data_list = data["data"]
        id_set = set()
        for data in data_list:
            jobId = data["id"]
            id_set.add(jobId)
            if len(id_set) >= max_amount:
                break
        return id_set