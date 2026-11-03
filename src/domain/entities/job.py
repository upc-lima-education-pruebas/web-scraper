from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class Job:
    #Title
    title: str
    #Details
    description: str
    job_type: str
    work_hours: str
    # Requirements
    skills: list[str]
    experience: str
    education_level: str
    #Location
    ubigeo: Optional[str]
    address: Optional[str]
    #Payment
    min_salary: Optional[float]
    max_salary: Optional[float]
    currency: Optional[str]
    salary_period: Optional[str]
    compensation_type: Optional[str]
    #Traceability
    opens_at: Optional[datetime]
    closes_at: Optional[datetime]
    origin_page: str
    source_url: str
    #External data
    external_id: str
    external_company_name: Optional[str]
    external_company_image: Optional[str]