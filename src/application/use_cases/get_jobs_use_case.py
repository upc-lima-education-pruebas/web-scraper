from src.domain.entities.job import Job
from src.domain.entities.scraped_job import ScrapedJob
from src.domain.ports.job_scraper_port import JobScraperPort
from src.domain.ports.job_repository_port import JobRepositoryPort
from src.application.dtos.sync_jobs_request import SyncJobsRequest
from src.application.dtos.job_response import JobResponse
from src.application.mappers.job_mapper import JobMapper

from datetime import datetime, UTC
from concurrent.futures import ThreadPoolExecutor

class GetJobsUseCase:
    def __init__(self, scrapers: list[JobScraperPort], job_repository: JobRepositoryPort):
        self.scrapers = scrapers
        self.job_repository = job_repository

    def execute(self, request: SyncJobsRequest) -> list[JobResponse]:
        ids_per_platform = {}
        with ThreadPoolExecutor(max_workers=len(self.scrapers)) as executor:
            futures = {
                executor.submit(scraper.get_job_ids, request.max_amount): scraper
                for scraper in self.scrapers
            }
            for future, scraper in futures.items():
                ids_per_platform[scraper.ORIGIN_PAGE] = future.result()

        ids_to_scrape = {}

        for scraper in self.scrapers:
            ids = ids_per_platform[scraper.ORIGIN_PAGE]
            existing = self.job_repository.exists_many(scraper.ORIGIN_PAGE.name, ids)
            ids_to_scrape[scraper.ORIGIN_PAGE] = ids - existing

        job_list: list[Job]  = []
        with ThreadPoolExecutor(max_workers=len(self.scrapers)) as executor:
            futures = {
                executor.submit(scraper.get_jobs, ids_to_scrape[scraper.ORIGIN_PAGE]): scraper
                for scraper in self.scrapers
            }
            for future in futures:
                job_list.extend(future.result())

        self.job_repository.find_expired(30)
        job_response_list: list[JobResponse] = []
        scraped_job_list: list[ScrapedJob] = []
        
        for job in job_list:
            response = JobMapper.ToResponse(job)
            job_response_list.append(response)
            scraped_job = ScrapedJob(
                job.origin_page,
                job.external_id,
                datetime.now(UTC).isoformat(),
                datetime.now(UTC).isoformat()
            )
            scraped_job_list.append(scraped_job)
        
        self.job_repository.save_many(scraped_job_list)
        return job_response_list
            
        
    
    def _remove_duplicates(self, jobs: list[Job]) -> list[Job]:
        unique = {}

        for job in jobs:
            key = (job.origin_page,job.external_id)
            unique[key] = job
        
        return list(unique.values())