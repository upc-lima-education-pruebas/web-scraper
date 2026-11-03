from src.domain.entities.job import Job
from src.domain.value_objects.currency_type import CurrencyType
from src.domain.value_objects.origin_page import OriginPage
from src.domain.value_objects.work_hours import WorkHours
from src.domain.value_objects.job_type import JobType
from src.domain.value_objects.salary_period import SalaryPeriod
from src.infrastructure.processing.parsers.description_parser import DescriptionParser
from src.infrastructure.processing.extractors.skill_extractor import SkillExtractor
from src.infrastructure.processing.extractors.ubigeo_extractor import ubigeo_resolver
from src.infrastructure.processing.normalizers.description_normalizer import normalize_description
from src.infrastructure.processing.normalizers.date_normalizer import normalize_date

from bs4 import BeautifulSoup     

def bumeran_job_mapper(job):
    #Title
    title = job["titulo"]
    
    #Description
    description_soup = BeautifulSoup(job["descripcion"], "html.parser")
    description_raw = description_soup.get_text("\n", strip=True)
    description_cleaned = normalize_description(description_raw)
    parser = DescriptionParser(description_cleaned)
    description = parser.parse_description()

    #Details
    job_type = JobType.InPerson.name
    job_type_raw = job["modalidadTrabajo"]["stringId"]
    if job_type_raw == "remoto": job_type = JobType.Remote.name
    elif job_type_raw == "hibrido": job_type = JobType.Hybrid.name
    
    work_hours = WorkHours.FullTime.name
    work_hours_raw = job["tipoTrabajo"]["stringId"]
    part_time_list = ["part-time", "fines-de-semana"]
    hourly_list = ["por horas"]
    if work_hours_raw in part_time_list: work_hours = WorkHours.PartTime.name
    elif work_hours_raw in hourly_list: work_hours = WorkHours.Hourly.name
    
    #Requirements
    skill_extractor = SkillExtractor(description_cleaned)
    skills = skill_extractor.extract_skills()
    
    experience = parser.parse_experience()
    education_level = parser.parse_education_level()
    
    #Location
    address = job["localizacion"]["direccion"] or None
    
    location = job["localizacion"]
    ubigeo = None
    if location.get("localidadDetalle") and location.get("provinciaDetalle"):
        ubigeo = ubigeo_resolver(job["localizacion"]["localidadDetalle"], job["localizacion"]["provinciaDetalle"])
    
    #Payment
    min_salary = None
    max_salary = None
    salary_period = None
    currency = None
    compensation_type = None
    
    if job["requisitos"]["salario"]:
        min_salary = job["requisitos"]["salario"]["salarioMinimo"] or None
        max_salary = job["requisitos"]["salario"]["salarioMaximo"] or None
        frecuency = job["requisitos"]["salario"]["frecuenciaPago"]
        period = ""
        if frecuency:
            period = str(frecuency.get("nombre")).lower()
        if period:
            if "mes" in period: salary_period = SalaryPeriod.Monthly.name
            elif "semana" in period: salary_period = SalaryPeriod.Weekly.name
            elif "dia" in period: salary_period = SalaryPeriod.Daily.name
            elif "quincena" in period: salary_period = SalaryPeriod.Fortnightly.name
            elif "hora" in period: salary_period = SalaryPeriod.ForFees.name
    
    if max_salary and not min_salary:
        min_salary = max_salary
    if max_salary is None and min_salary is None:
            salary = parser.parse_salary()
            min_salary = salary["min_salary"]
            max_salary = salary["max_salary"]
    if min_salary is not None and max_salary is not None:
        if salary_period is None:
            salary_period = parser.parse_salary_period()
        currency = CurrencyType.PEN.name
        compensation_type = parser.parse_compensation_type()
    
    #Traceability
    opens_at = normalize_date(job.get("fechaPublicacion"))
    closes_at = normalize_date(job.get("fechaFinalizacion"))
    origin_page = OriginPage.Bumeran.name
    
    #External
    external_id = str(job["id"])
    external_company_name = None
    external_company_image = None
    if not job["empresa"]["confidencial"]:
        external_company_name = job["empresa"]["denominacion"]
        image = job["empresa"].get("logoURL")
        if image is not None and len(image) > 0:
            external_company_image = image
    source_url = f"https://www.bumeran.com.pe{job['seoFriendlyUrl']}"
    
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