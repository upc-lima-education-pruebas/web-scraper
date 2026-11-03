from abc import ABC, abstractmethod
from src.domain.entities.job import Job
from src.domain.value_objects.origin_page import OriginPage

class JobScraperPort(ABC):  
    ORIGIN_PAGE: OriginPage
    
    #Method for testing if the provider's scraper functions correctly
    @abstractmethod
    def get_jobs_test(self, max_amount: int = None) -> list[Job]: 
        pass
    
    #Retrieves the jobs with the provided ids
    @abstractmethod
    def get_jobs(self, id_set: set[str]) -> list[Job]:
        pass
    
    #Retrieves the ids of the jobs
    @abstractmethod
    def get_job_ids(self, max_amount: int = None) -> set[str]:
        pass