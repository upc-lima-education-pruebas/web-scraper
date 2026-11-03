from src.domain.ports.job_scraper_port import JobScraperPort
from src.domain.value_objects.origin_page import OriginPage
from src.application.dtos.job_response import JobResponse
from src.application.mappers.job_mapper import JobMapper

class TestGetJobsUseCase:
    def __init__(self, scrapers: list[JobScraperPort]):
        self.scrapers = {
            scraper.ORIGIN_PAGE: scraper
            for scraper in scrapers
        }

    def execute(self, platform: OriginPage, max_amount: int|None = None) -> list[JobResponse]:
        scraper = self.scrapers.get(platform)
        if scraper is None:
            raise ValueError(f"Platform {platform} is not supported.")
        jobs = scraper.get_jobs_test(max_amount)
        job_response_list: list[JobResponse] = []
        for job in jobs:
            response = JobMapper.ToResponse(job)
            job_response_list.append(response)
        return job_response_list