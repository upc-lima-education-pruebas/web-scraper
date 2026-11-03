from src.domain.value_objects.origin_page import OriginPage
from src.application.use_cases.test_get_job_ids_use_case import TestGetJobIdsUseCase
from src.application.use_cases.test_get_jobs_use_case import TestGetJobsUseCase
from src.application.use_cases.sync_jobs_to_backend_use_case import SyncJobsToBackendUseCase
from src.application.use_cases.get_jobs_use_case import GetJobsUseCase
from src.application.dtos.sync_jobs_request import SyncJobsRequest
from src.infrastructure.clients.backend_client import BackendClient
from src.infrastructure.persistence.sqlite_job_repository import SqliteJobRepository
from src.infrastructure.providers.bumeran.bumeran_job_scraper import BumeranJobScraper
from src.infrastructure.providers.computrabajo.computrabajo_job_scraper import ComputrabajoJobScraper
from src.infrastructure.providers.empleosperu.empleosperu_job_scraper import EmpleosPeruJobScraper
from src.infrastructure.providers.universia.universia_job_scraper import UniversiaJobScraper
from src.infrastructure.providers.laborum.laborum_job_scraper import LaborumJobScraper

from fastapi import APIRouter, BackgroundTasks, status

router = APIRouter(
    prefix="/jobs",
    tags=["jobs"]
)

scrapers = [
    EmpleosPeruJobScraper(),
    ComputrabajoJobScraper(),
    BumeranJobScraper(),
    UniversiaJobScraper(),
    LaborumJobScraper()
]

sqlite_job_repository = SqliteJobRepository()

#Testing use cases
test_get_jobs_use_case = TestGetJobsUseCase(scrapers)
test_get_job_ids_use_case = TestGetJobIdsUseCase(scrapers)

#Sync use case
get_jobs_use_case = GetJobsUseCase(scrapers, sqlite_job_repository)
sync_jobs_to_backend_use_case = SyncJobsToBackendUseCase(get_jobs_use_case, BackendClient())


@router.get("/test/get-jobs", status_code=status.HTTP_200_OK)
async def get_jobs_from_one_platform(platform: OriginPage, max_amount: int = None):
    return test_get_jobs_use_case.execute(platform, max_amount)

@router.get("test/get-job-ids", status_code=status.HTTP_200_OK)
async def get_jobs_ids_from_one_platform(platform: OriginPage, max_amount: int = None):
    return test_get_job_ids_use_case.execute(platform, max_amount)

@router.post("/sync-async", status_code=status.HTTP_202_ACCEPTED)
async def trigger_sync(request: SyncJobsRequest, background_tasks: BackgroundTasks):
    background_tasks.add_task(sync_jobs_to_backend_use_case.execute, request)
    return {
        "status": "Accepted",
        "message": "Backend sync proccess initiated"
    }