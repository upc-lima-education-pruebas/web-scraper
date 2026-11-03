from src.domain.entities.job import Job
from src.domain.ports.job_scraper_port import JobScraperPort
from src.domain.value_objects.origin_page import OriginPage
from src.infrastructure.providers.laborum.laborum_job_mapper import laborum_job_mapper
import requests
from bs4 import BeautifulSoup
import urllib.parse

class LaborumJobScraper(JobScraperPort):
    ORIGIN_PAGE = OriginPage.Laborum
    BASE_URL = "https://www.laborum.pe"
    API_ENDPOINT = "https://www.laborum.pe/api/v1/beesearch/laborExchange/5e0a767b2aab660056457c2b/jobs"
    BASE_HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/128.0.0.0 Safari/537.36"
        ),
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "es-ES,es;q=0.9",
        "Origin": BASE_URL,
        "Referer": f"{BASE_URL}/",
        "Content-Type": "application/json;charset=UTF-8",
    }
    PAGE_SIZE = 20

    def __init__(self):
        self._cached_jobs: dict[str, Job] = {}

    def get_jobs_test(self, max_amount: int = None) -> list[Job]:
        if max_amount == 0:
            return []
        ids = self.get_job_ids(max_amount)
        return self.get_jobs(ids)
    
    def get_jobs(self, id_set: set[str]) -> list[Job]:
        str_id_set = {str(i) for i in id_set}
        jobs = [
            job for ext_id, job in self._cached_jobs.items() 
            if ext_id in str_id_set
        ]
        self._cached_jobs.clear()
        return jobs
    
    def get_job_ids(self, max_amount: int = None) -> set[str]:
        if max_amount == 0:
            return set()

        self._cached_jobs.clear()
        areas = self._get_areas()

        for area in areas:
            page = 1
            has_next = True

            while has_next:
                data = self._fetch_api_page(area_name=area, page=page, limit=self.PAGE_SIZE)
                docs = data.get("docs", [])
                info = data.get("info", {})

                for doc in docs:
                    job_entity = laborum_job_mapper(doc)
                    self._cached_jobs[job_entity.external_id] = job_entity

                    if max_amount and len(self._cached_jobs) >= max_amount:
                        return set(self._cached_jobs.keys())

                has_next = info.get("hasNextPage", False)
                page += 1

        return set(self._cached_jobs.keys())

    def _get_areas(self) -> list[str]:
        try:
            response = requests.get(
                self.BASE_URL, 
                headers={"User-Agent": self.BASE_HEADERS["User-Agent"]}, 
                timeout=10
            )
            if response.status_code != 200:
                return []

            soup = BeautifulSoup(response.text, "html.parser")
            area_links = soup.find_all(
                "a", href=lambda h: h and h.startswith("/search-jobs?fromAreas=available")
            )

            areas = []
            for link in area_links:
                href = link.get("href")
                parsed_url = urllib.parse.urlparse(href)
                query_params = urllib.parse.parse_qs(parsed_url.query)
                if "q" in query_params:
                    areas.append(query_params["q"][0])

            return list(set(areas))
        except Exception:
            return []

    def _fetch_api_page(self, area_name: str, page: int = 1, limit: int = 20) -> dict:
        payload = {
            "fromAreas": "available",
            "limit": limit,
            "page": page,
            "search": area_name,
        }
        try:
            response = requests.post(
                self.API_ENDPOINT, 
                json=payload, 
                headers=self.BASE_HEADERS, 
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    return data.get("data", {})
        except Exception:
            pass
        return {}