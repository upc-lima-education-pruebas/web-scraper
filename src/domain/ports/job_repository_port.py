from abc import ABC, abstractmethod
from src.domain.entities.scraped_job import ScrapedJob

class JobRepositoryPort(ABC):

    @abstractmethod
    def exists(self, job: ScrapedJob):
        pass
    
    @abstractmethod
    def exists_many(self, origin_page: str, external_ids: set[str]) -> set[str]:
        pass
    
    @abstractmethod
    def save(self, job: ScrapedJob):
        pass
    
    @abstractmethod
    def save_many(self, jobs: list[ScrapedJob]):
        pass
    
    @abstractmethod
    def touch(self, job: ScrapedJob):
        pass

    @abstractmethod
    def find_expired(self, max_days):
        pass