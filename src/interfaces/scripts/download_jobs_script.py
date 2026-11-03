from src.application.use_cases.get_jobs_use_case import GetJobsUseCase
from src.application.dtos.sync_jobs_request import SyncJobsRequest

from src.infrastructure.providers.empleosperu.empleosperu_job_scraper import EmpleosPeruJobScraper
from src.infrastructure.providers.computrabajo.computrabajo_job_scraper import ComputrabajoJobScraper
from src.infrastructure.providers.bumeran.bumeran_job_scraper import BumeranJobScraper
from src.infrastructure.providers.laborum.laborum_job_scraper import LaborumJobScraper
from src.infrastructure.providers.universia.universia_job_scraper import UniversiaJobScraper

from src.infrastructure.persistence.sqlite_job_repository import SqliteJobRepository

import json


def main():
    
    scrapers = [
        EmpleosPeruJobScraper(),
        ComputrabajoJobScraper(),
        BumeranJobScraper(),
        LaborumJobScraper(),
        UniversiaJobScraper()
    ]

    use_case = GetJobsUseCase(scrapers,SqliteJobRepository())
    request = SyncJobsRequest(max_amount=10000)
    print("Started scraping")
    jobs = use_case.execute(request)

    print(f"Collected {len(jobs)} jobs")

    with open("dataset/jobs_dataset.json", "w", encoding="utf-8") as f:
        json.dump(
            [job.__dict__ for job in jobs],
            f,
            ensure_ascii=False,
            indent=2
        )

if __name__ == "__main__":
    main()