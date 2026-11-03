from src.domain.entities.job import Job
from src.domain.value_objects.work_hours import WorkHours
from src.domain.value_objects.currency_type import CurrencyType
from src.domain.value_objects.experience import Experience
from src.domain.value_objects.job_type import JobType
from src.domain.value_objects.origin_page import OriginPage
from src.domain.value_objects.education_level import EducationLevel
from src.infrastructure.processing.parsers.description_parser import DescriptionParser
from src.infrastructure.processing.extractors.skill_extractor import SkillExtractor
from src.infrastructure.processing.normalizers.description_normalizer import normalize_description
from src.infrastructure.processing.normalizers.date_normalizer import normalize_date

def empleosperu_job_mapper(job):
    #Details
    title = job["positionTitle"]
    
    description_raw = job["jobDescription"]
    description_cleaned = normalize_description(description_raw)
    parser = DescriptionParser(description_cleaned)
    description = parser.parse_description()
    
    job_type = JobType.InPerson.name
    
    work_hours = WorkHours.FullTime.name
    if job["hoursPerWeek"]["name"] == "Tiempo parcial": work_hours = WorkHours.PartTime.name
    elif job["hoursPerWeek"]["name"] == "Por horas": work_hours = WorkHours.Hourly.name
    
    #Requirements
    skill_extractor = SkillExtractor(description_cleaned)
    skills = skill_extractor.extract_skills()
    
    experience = Experience.NoExperienceNeeded.name
    extended_details = job["extended"]
    if extended_details.get("yearsOfExperience"):
        if extended_details["yearsOfExperienceType"] == "YEARS":
            if int(extended_details["yearsOfExperience"]) == 1:
                experience = Experience.OneYear.name
            else:
                experience = Experience.TwoOrMoreYears.name
        elif extended_details["yearsOfExperienceType"] == "MONTHS":
            if int(extended_details["yearsOfExperience"]) <= 3:
                experience = Experience.ThreeMonths.name
            elif int(extended_details["yearsOfExperience"]) <= 6:
                experience = Experience.SixMonths.name
            else:
                experience = Experience.OneYear.name
                
    education_level = EducationLevel.Unspecified.name
    if job["educationDegree"]["name"].startswith("Primaria"):
        education_level = EducationLevel.Primary.name
    elif job["educationDegree"]["name"].startswith("Secundaria"):
        education_level = EducationLevel.Secondary.name
    elif job["educationDegree"]["name"].startswith("Técnica"):
        education_level = EducationLevel.Technical.name
    elif job["educationDegree"]["name"].startswith("Universitaria"):
        education_level = EducationLevel.University.name
    elif job["educationDegree"]["name"].startswith("Maestría"):
        education_level = EducationLevel.Master.name
    elif job["educationDegree"]["name"].startswith("Doctorado"):
        education_level = EducationLevel.Doctorate.name
    
    #Location
    ubigeo = None
    if job.get("location"): 
        ubigeo = job["location"]["DISTRICT"]
    address = None
    
    #Payment
    min_salary = None
    max_salary = None
    currency = None
    salary_period = None
    compensation_type = None
    
    if job.get("displaySalary"):
        if job["offeredRemunerationPackages"][0]["minimumAmount"] is not None \
        and job["offeredRemunerationPackages"][0]["maximumAmount"] is not None:
            min_salary = float(job["offeredRemunerationPackages"][0]["minimumAmount"])
            max_salary = float(job["offeredRemunerationPackages"][0]["maximumAmount"])
        if min_salary == 0 and max_salary != 0:
            min_salary = max_salary
    
    if min_salary is not None and max_salary is not None:
        currency = CurrencyType.PEN.name
        salary_period = parser.parse_salary_period()
        compensation_type = parser.parse_compensation_type()
    
    #Traceability
    opens_at = normalize_date(job.get("datePosted"))
    closes_at = normalize_date(job.get("expiration"))
    origin_page = OriginPage.EmpleosPeru.name
    
    #External data
    external_id = job["id"]
    external_company_name = None
    if job.get("companyName"):
        external_company_name = job["companyName"].strip()
    external_company_image = None
    if job.get("companyLogo"):
        external_company_image = f"https://mtpe-candidatos.empleosperu.gob.pe/api/attachments{job["companyLogo"]['url']}"
    source_url = f"https://mtpe-candidatos.empleosperu.gob.pe/search-jobs/description?jobId={external_id}"
        
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
        #Payment
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
        #External data
        external_id,
        external_company_name,
        external_company_image
    )