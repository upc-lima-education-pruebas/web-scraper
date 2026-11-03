from src.domain.entities.job import Job
from src.domain.value_objects.work_hours import WorkHours
from src.domain.value_objects.currency_type import CurrencyType
from src.domain.value_objects.job_type import JobType
from src.domain.value_objects.origin_page import OriginPage
from src.domain.value_objects.education_level import EducationLevel
from src.domain.value_objects.experience import Experience
from src.infrastructure.processing.parsers.description_parser import DescriptionParser
from src.infrastructure.processing.extractors.skill_extractor import SkillExtractor
from src.infrastructure.processing.extractors.ubigeo_extractor import ubigeo_resolver
from src.infrastructure.processing.normalizers.description_normalizer import normalize_description
from src.infrastructure.processing.normalizers.date_normalizer import normalize_date

def computrabajo_job_mapper(job, jobId, company_image):
    #Title
    title = job["ltr"]

    #Details
    description_raw = job["ld"]
    description_cleaned = normalize_description(description_raw)
    parser = DescriptionParser(description_cleaned)
    description = parser.parse_description()
    
    job_type = JobType.InPerson.name
    if job["iwt"] == 2: job_type = JobType.Remote.name
    elif job["iwt"] == 3: job_type = JobType.Hybrid.name
    
    work_hours = WorkHours.FullTime.name
    if job["lset"] == "Tiempo parcial": work_hours = WorkHours.PartTime.name
    elif job["lset"] == "Por horas": work_hours = WorkHours.Hourly.name
    
    #Requirements
    skill_extractor = SkillExtractor(description_cleaned)
    skills = skill_extractor.extract_skills()
    
    experience = Experience.NoExperienceNeeded.name
    if job.get("ey"):    
        if job["ey"] == 1: experience = Experience.OneYear.name
        elif job["ey"] >= 2: experience = Experience.TwoOrMoreYears.name
    else:
        experience = parser.parse_experience()
    
    education_level = EducationLevel.Unspecified.name
    if job["me"] == "Educación Primaria": education_level = EducationLevel.Primary.name
    elif job["me"] == "Educación Secundaria": education_level = EducationLevel.Secondary.name
    elif job["me"] == "Técnico": education_level = EducationLevel.Technical.name
    elif job["me"] == "Universitario": education_level = EducationLevel.University.name
    elif job["me"] == "Maestría": education_level = EducationLevel.Master.name
    elif job["me"] == "Doctorado": education_level = EducationLevel.Doctorate.name
    
    #Location
    ubigeo = None
    if job["c"] and job["l"]:
        ubigeo = ubigeo_resolver(job["c"], job["l"])
    address = None
    
    #Payment
    min_salary = None
    max_salary = None
    currency = None
    salary_period = None
    compensation_type = None
    
    min_s = float(job["smin"])
    max_s = float(job["smax"])
    if min_s == 0 and max_s == 0:
        salary = float(job["s"])
        if salary != 0:
            min_salary = salary
            max_salary = salary
        else:
            salary = parser.parse_salary()
            if min_salary is not None and max_salary is not None:
                min_salary = float(salary.get("min_salary"))
                max_salary = float(salary.get("max_salary"))
    else:
        min_salary = min_s
        max_salary = max_s
    
    if min_salary is not None and max_salary is not None:
        currency = CurrencyType.PEN.name
        salary_period = parser.parse_salary_period()
        compensation_type = parser.parse_compensation_type()
    
    #Traceability
    opens_at = normalize_date(job.get("dlu"))
    closes_at = normalize_date(job.get("et"))
    origin_page = OriginPage.Computrabajo.name
    
    #External
    external_id = jobId
    external_company_name = job["cn"]
    external_company_image = None
    if company_image is not None:
       external_company_image = f"https://ii.ct-stc.com/3/{company_image}"
    source_url = f"https://pe.computrabajo.com/empleos-en-mi-ubicacion#{jobId}"
    
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
        #External
        external_id,
        external_company_name,
        external_company_image
    )