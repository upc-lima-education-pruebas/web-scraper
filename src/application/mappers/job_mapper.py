from src.domain.entities.job import Job
from src.domain.entities.scraped_job import ScrapedJob
from src.application.dtos.job_response import JobResponse

from datetime import datetime, UTC

class JobMapper:
    @staticmethod
    def ToResponse(job: Job) -> JobResponse:
        return JobResponse(
            job.title,
            job.description,
            job.job_type,
            job.work_hours,
            job.skills,
            job.experience,
            job.education_level,
            job.ubigeo,
            job.address,
            job.min_salary,
            job.max_salary,
            job.currency,
            job.salary_period,
            job.compensation_type,
            job.opens_at,
            job.closes_at,
            job.origin_page,
            job.source_url,
            job.external_company_name,
            job.external_company_image
        )
    
    @staticmethod
    def ToScrapedJob(job: Job) -> ScrapedJob:
        return ScrapedJob(
            job.origin_page,
            job.external_id,
            datetime.now(UTC).isoformat(),
            datetime.now(UTC).isoformat()
        )