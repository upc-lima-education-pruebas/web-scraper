from src.infrastructure.clients.backend_client import BackendClient
from src.application.use_cases.get_jobs_use_case import GetJobsUseCase
from src.application.dtos.sync_jobs_request import SyncJobsRequest

class SyncJobsToBackendUseCase:
    def __init__(
        self,
        get_jobs_use_case: GetJobsUseCase,
        backend_client: BackendClient
    ):
        self.get_jobs_use_case = get_jobs_use_case
        self.backend_client = backend_client

    def execute(self, request: SyncJobsRequest):
        print("Backend Sync Jobs requested...")
        payload = self.get_jobs_use_case.execute(request)
        print("Payload obtainied")
        if not payload:
            return

        self.backend_client.sync_jobs(payload)