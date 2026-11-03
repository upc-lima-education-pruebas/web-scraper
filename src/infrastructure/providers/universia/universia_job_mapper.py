from src.domain.entities.job import Job
from src.domain.value_objects.salary_period import SalaryPeriod
from src.domain.value_objects.compensation_type import CompensationType
from src.domain.value_objects.work_hours import WorkHours
from src.domain.value_objects.currency_type import CurrencyType
from src.domain.value_objects.experience import Experience
from src.domain.value_objects.job_type import JobType
from src.domain.value_objects.origin_page import OriginPage
from src.domain.value_objects.education_level import EducationLevel
from src.infrastructure.processing.parsers.description_parser import DescriptionParser
from src.infrastructure.processing.extractors.skill_extractor import SkillExtractor
from src.infrastructure.processing.normalizers.date_normalizer import normalize_date
from src.infrastructure.processing.normalizers.description_normalizer import normalize_description

from bs4 import BeautifulSoup

def universia_job_mapper(job):
    #Title
    title = job["title"]
    
    #Description
    soup = BeautifulSoup(job["description"], "html.parser")
    description_raw = soup.get_text("\n", strip=True)
    description_cleaned = normalize_description(description_raw)
    parser = DescriptionParser(description_cleaned)
    description = parser.parse_description()
    
    #Details
    job_type = JobType.InPerson.name
    if job["jobLocationType"] == "remote": job_type = JobType.Remote.name
    elif job["jobLocationType"] == "hybrid": job_type = JobType.Hybrid.name
    
    work_hours = WorkHours.FullTime.name
    if job["employmentType"] == "part-time": work_hours = WorkHours.PartTime.name
    
    skill_extractor = SkillExtractor(description_cleaned)
    skills = skill_extractor.extract_skills()
    
    experience = Experience.NoExperienceNeeded.name
    if job["experienceRequirements"]["monthsOfExperience"] == 12: experience = Experience.OneYear.name
    elif job["experienceRequirements"]["monthsOfExperience"] > 12: experience = Experience.TwoOrMoreYears.name
    
    education_level = EducationLevel.Unspecified.name
    university_levels = ["university", "advanced_tech", "intermediate_tech"]
    if job["educationalLevel"] in university_levels: education_level = EducationLevel.University.name
    elif job["educationalLevel"] == "basic_high_school": education_level = EducationLevel.Secondary.name
    
    #Location
    ubigeo = None
    address = None
    location = job.get("jobLocation")
    if location is not None:
        address_raw = location.get("address")
        if address_raw is not None and \
        address_raw.get("streetAddress") is not None and len(address_raw["streetAddress"]) > 0:
            address = address_raw["streetAddress"]
    
    #Payment
    min_salary = None
    max_salary = None
    salary_period = None
    currency = None
    compensation_type = None
    estimated_salary = job.get("estimatedSalary")
    if estimated_salary is not None and estimated_salary[0] is not None:
        min_salary = estimated_salary[0]["minValue"]
        max_salary = estimated_salary[0]["maxValue"]
        if min_salary is not None or max_salary is not None:
            salary_period = SalaryPeriod.Monthly.name
            currency = CurrencyType.PEN.name
            currency_raw = estimated_salary[0]["currency"]
            if currency_raw == "USD": currency = CurrencyType.USD.name
            elif currency_raw == "EUR": currency = CurrencyType.EUR.name
            compensation_type = CompensationType.Fixed.name
    
    #Traceability
    opens_at = normalize_date(job.get("datePosted"))
    closes_at = normalize_date(job.get("validThrough"))
    origin_page = OriginPage.Universia.name
    
    #External
    external_id = job["identifier"]
    external_company_name = None
    external_company_image = None
    
    hiring_org = job.get("hiringOrganization")
    if hiring_org == "confidential":
        external_company_name = "Confidencial"
    elif isinstance(hiring_org, dict):
        external_company_name = hiring_org.get("legalName")
        logo_obj = hiring_org.get("logo")
        if isinstance(logo_obj, dict) and logo_obj.get("url") and len(str(logo_obj["url"]).strip()) > 0:
            external_company_image = str(logo_obj["url"]).strip()
    
    source_url = f"https://www.universia.net/pe/empleo/{external_id}/{job['name']}"
    
    return Job(
       #Details
        title,
        description,
        job_type,
        work_hours,
        #Requirements
        skills,
        experience,
        education_level,
        #Location
        ubigeo,
        address,
        #Salary
        min_salary,
        max_salary,
        currency,
        salary_period,
        compensation_type,
        #Traceability
        opens_at,
        closes_at,
        origin_page,
        source_url,
        #External
        external_id,
        external_company_name,
        external_company_image
    )