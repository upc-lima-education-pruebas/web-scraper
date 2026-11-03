from src.domain.entities.job import Job
from src.domain.value_objects.currency_type import CurrencyType
from src.domain.value_objects.experience import Experience
from src.domain.value_objects.origin_page import OriginPage
from src.domain.value_objects.work_hours import WorkHours
from src.infrastructure.processing.parsers.description_parser import DescriptionParser
from src.infrastructure.processing.extractors.skill_extractor import SkillExtractor
from src.infrastructure.processing.extractors.ubigeo_extractor import ubigeo_resolver
from src.infrastructure.processing.normalizers.date_normalizer import normalize_date
from src.infrastructure.processing.normalizers.description_normalizer import normalize_description
from src.infrastructure.processing.normalizers.url_normalizer import url_normalizer
from bs4 import BeautifulSoup

import re

def laborum_job_mapper(job):
    #Title
    title = job["title"]
    
    #Description    
    description_soup = BeautifulSoup(job["basicEdition"][0]["description"], "html.parser")
    description_raw = description_soup.get_text("\n", strip=True)
    description_cleaned = normalize_description(description_raw)
    parser = DescriptionParser(description_cleaned)
    description = parser.parse_description()

    #Details
    work_hours = None
    work_hours_raw = job.get("Horario")
    if work_hours_raw is not None:
        if work_hours_raw == "Full-time" or work_hours_raw == "Prácticas": work_hours = WorkHours.FullTime.name
    work_hours = parser.parse_work_hours()

    job_type = parser.parse_job_type()
    
    #Requirements
    skill_extractor = SkillExtractor(description_cleaned)
    skills = skill_extractor.extract_skills()

    experience = Experience.NoExperienceNeeded.name
    experience_raw = job.get("experience")
    if experience_raw is not None:
        if experience_raw == 1:
            experience = Experience.OneYear.name
        elif experience_raw >= 2:
            experience = Experience.TwoOrMoreYears.name

    education_level = parser.parse_education_level()

    # Location
    address = None
    ubigeo = None
    location = job.get("Lugar")

    if location:
        street_patterns = r"\b(calle|jiron|jr|jr\.|avenida|av|av\.|pasaje|psj|psj\.|boulevard|blvd)\b"
        if re.search(street_patterns, location, re.IGNORECASE):
            address = location
            location_for_ubigeo = location.split(",")[-1].strip() if "," in location else None
        else:
            location_for_ubigeo = location

        if location_for_ubigeo:
            clean_raw = re.sub(r"\bper[uú]\b", "", location_for_ubigeo, flags=re.IGNORECASE)
            clean_raw = re.sub(r"\b(departamento|provincia)\s+de\s+", "", clean_raw, flags=re.IGNORECASE,)
            parts = [
                p.strip()
                for p in re.split(r"[,|-]+", clean_raw)
                if p.strip() and p.strip().lower() != "peru"
            ]
            if parts:
                if len(parts) == 1 and parts[0].lower() == "lima": ubigeo = ubigeo_resolver("Lima", "Lima")
                if ubigeo is None and len(parts) >= 2: ubigeo = ubigeo_resolver(parts[0], parts[-1])
                if ubigeo is None and len(parts) >= 2: ubigeo = ubigeo_resolver(parts[-1], parts[0])
                if ubigeo is None and len(parts) >= 2: ubigeo = ubigeo_resolver(parts[0], parts[1])
                if ubigeo is None and len(parts) == 1: ubigeo = ubigeo_resolver(parts[0], parts[0])
                if ubigeo is None: ubigeo = ubigeo_resolver(parts[0], "Lima")

    #Salary
    min_salary = None
    max_salary = None
    salary_period = None
    currency = None
    compensation_type = None
    
    salary = parser.parse_salary()
    min_salary = salary["min_salary"]
    max_salary = salary["max_salary"]
    if min_salary is not None and max_salary is not None:
        salary_period = parser.parse_salary_period()
        currency = CurrencyType.PEN.name
        compensation_type = parser.parse_compensation_type()

    #Trazability
    opens_at = normalize_date(job.get("publishDate"))
    closes_at = normalize_date(job.get("expirationDate"))
    origin_page = OriginPage.Laborum.name
    
    #External
    external_id = job.get("job_id")
    detail_company = job.get("detailCompany") or {}
    external_company_name = None
    if detail_company.get("company_name"):
        external_company_name = str(detail_company["company_name"]).strip() or None
    external_company_image = None
    company_logo = detail_company.get("company_logo")
    if company_logo and isinstance(company_logo, str) and company_logo.strip():
        cleaned_logo = company_logo.strip()
        if cleaned_logo != "https://krowdy.s3.amazonaws.com/company/6095c66e43a4b50008b4b834/2021-05-14T12-38-31-768Zempresa.png":
            external_company_image = cleaned_logo
    source_url = f"https://www.laborum.pe/job/{url_normalizer(external_company_name)}/{url_normalizer(job['title'])}/{external_id}"

    return Job(
        title,
        description,
        job_type,
        work_hours,
        skills,
        experience,
        education_level,
        ubigeo,
        address,
        min_salary,
        max_salary,
        currency,
        salary_period,
        compensation_type,
        opens_at,
        closes_at,
        origin_page,
        source_url,
        external_id,
        external_company_name,
        external_company_image
    )