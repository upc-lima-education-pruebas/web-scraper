from src.domain.entities.job import Job
from src.domain.ports.job_scraper_port import JobScraperPort
from src.domain.value_objects.origin_page import OriginPage
from src.infrastructure.clients.http_client import HttpClient
from src.infrastructure.processing.normalizers.url_normalizer import url_normalizer
from src.infrastructure.providers.universia.universia_job_mapper import universia_job_mapper
import math

class UniversiaJobScraper(JobScraperPort):
    ORIGIN_PAGE = OriginPage.Universia
    
    BASE_URL = "https://api-manager.universia.net/orientacion-job-posting/v1/api/job-posting"
    BOARDS = "boards=00000000-0000-0000-0000-000000000007"
    BASE_HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "es-PE,es;q=0.9",
        "Origin": "https://www.universia.net",
        "Referer": "https://www.universia.net/pe/empleo",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
    }
    PAGE_SIZE = 100
        
    def __init__(self):
        self.client = HttpClient()
        self._cached_jobs = {}
    
    def get_jobs_test(self, max_amount: str = None) -> list[Job]:
        if max_amount == 0: return []
        ids = self.get_job_ids(max_amount)
        return self.get_jobs(ids)
    
    def get_jobs(self, id_set: set[str]) -> list[Job]:
        str_id_set = {str(i) for i in id_set}
        jobs_to_return = [
            job for ext_id, job in self._cached_jobs.items() 
            if ext_id in str_id_set
        ]
        self._cached_jobs.clear()
        return jobs_to_return
    
    def get_job_ids(self, max_amount: int = None) -> set[str]:
        if max_amount == 0:
            return set()
            
        self._cached_jobs.clear()

        initial_url = f"{self.BASE_URL}?limit=1&{self.BOARDS}"
        base_data = self.client.get_json(initial_url, self.BASE_HEADERS)
        total_count = base_data.get("total", 0)
        
        if max_amount is None or max_amount > total_count:
            max_amount = total_count
            
        total_pages = math.ceil(max_amount / self.PAGE_SIZE)
        fetched_count = 0

        for page_index in range(total_pages):
            remaining = max_amount - fetched_count
            if remaining <= 0:
                break
                
            current_limit = min(self.PAGE_SIZE, remaining)
            current_offset = page_index * self.PAGE_SIZE
            
            url = f"{self.BASE_URL}?offset={current_offset}&limit={current_limit}&{self.BOARDS}"
            
            response = self.client.get_json(url, self.BASE_HEADERS)
            
            for result in response.get("results", []):
                external_id = str(result["identifier"])
                self._cached_jobs[external_id] = universia_job_mapper(result)
                fetched_count += 1

        return set(self._cached_jobs.keys())