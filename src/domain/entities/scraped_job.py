from dataclasses import dataclass
from datetime import datetime

@dataclass
class ScrapedJob:
    origin_page: str
    external_id: str
    first_seen_at: datetime
    last_seen_at: datetime