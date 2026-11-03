from src.domain.value_objects.origin_page import OriginPage
from src.domain.ports.job_scraper_port import JobScraperPort

class TestGetJobIdsUseCase:
    def __init__(self, scrapers: list[JobScraperPort]):
        self.scrapers = {
            scraper.ORIGIN_PAGE: scraper
            for scraper in scrapers
        }

    def execute(self, platform: OriginPage, max_amount: int|None = None) -> set[str]:
        scraper = self.scrapers.get(platform)
        if scraper is None:
            raise ValueError(f"Platform {platform} is not supported.")
        job_id_set: set[str] = scraper.get_job_ids(max_amount)
        return job_id_set