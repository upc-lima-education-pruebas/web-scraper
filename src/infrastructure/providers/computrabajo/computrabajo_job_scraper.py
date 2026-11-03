from src.domain.entities.job import Job
from src.domain.value_objects.origin_page import OriginPage
from src.domain.ports.job_scraper_port import JobScraperPort
from src.infrastructure.clients.http_client import HttpClient
from src.infrastructure.processing.normalizers.url_normalizer import url_normalizer
from src.infrastructure.providers.computrabajo.computrabajo_job_mapper import computrabajo_job_mapper

from bs4 import BeautifulSoup
import math
import time


class ComputrabajoJobScraper(JobScraperPort):
    ORIGIN_PAGE = OriginPage.Computrabajo
    
    BASE_URL = "https://pe.computrabajo.com"
    API_URL = "https://oferta.computrabajo.com"
    PAGE_SIZE = 20
    
    def __init__(self):
        self.client = HttpClient()

    def get_jobs_test(self, max_amount: str = None) -> list[Job]:
        if max_amount == 0: return []
        id_set = self.get_job_ids(max_amount)
        return self._get_job_data(id_set)

    def get_jobs(self, id_set: set[str]) -> list[Job]:
        return self._get_job_data(id_set)


    def get_job_ids(self, max_amount=None) -> set[str]:
        if max_amount == 0: return []
        url = f"{self.BASE_URL}/empleos-en-mi-ubicacion"
        html = self.client.get_text(url)
        soup = BeautifulSoup(html, "html.parser")
        title_page = soup.find("h1",class_="title_page")
        if title_page:
            total_jobs = int(title_page.find("span").text.replace(".", "").strip())
            if total_jobs == 0:
                return []
        else: return []

        if max_amount is None: max_amount = total_jobs
        else: max_amount = min(max_amount, total_jobs)

        number_of_pages = math.ceil(max_amount / self.PAGE_SIZE)
        id_set = set()
        
        sleep_counter = 0
        for page in range(number_of_pages):
            page_url = f"{url}?p={page+1}"
            try:
                html = self.client.get_text(page_url)
                sleep_counter += 1
                if sleep_counter == 50:
                    time.sleep(1)
                    sleep_counter = 0
            except Exception as e:
                print(f"Could not get {page+1}: {e}\nSleeping for 1 minute")
                time.sleep(60)
                sleep_counter = 0
                continue
            soup = BeautifulSoup(html, "html.parser")
            articles = soup.find_all("article")
            for article in articles:
                job_id = article.get("data-id")
                if job_id:
                    id_set.add(job_id)
                    if len(id_set) >= max_amount:
                        return id_set
        return id_set


    def _get_job_data(self, id_set: set[str]) -> list[Job]:
        job_list = []
        for job_id in id_set:
            try:
                api_url = (f"{self.API_URL}/offer/{job_id}/d/j?ipo=3&iapo=1")
                response = self.client.get_json(api_url)
                job_data = response["o"]
                company_image = None
                company_data = response["c"]
                if company_data.get("lp") is not None and len(company_data["lp"]) > 0:
                    company_image = company_data["lp"]
                job = computrabajo_job_mapper(job_data, job_id, company_image)
                job_list.append(job)
            except:
                time.sleep(1)

        return job_list