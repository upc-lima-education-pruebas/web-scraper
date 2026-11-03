from src.domain.value_objects.experience import Experience
from src.domain.value_objects.salary_period import SalaryPeriod
from src.domain.value_objects.work_hours import WorkHours
from src.domain.value_objects.education_level import EducationLevel
from src.domain.value_objects.compensation_type import CompensationType
from src.domain.value_objects.job_type import JobType
from src.infrastructure.processing.parsers.constants.job_regex_patterns import JOB_REGEX_PATTERNS
from abc import ABC
import re

class DescriptionParser(ABC):
    def __init__(self, description: str):
        self.description = description
    
    def parse_description(self):
        return self.description
    
    def parse_experience(self):
        exp_match = JOB_REGEX_PATTERNS["experience"].search(self.description)
        if exp_match:
            return self._normalize_experience(exp_match)
        return Experience.NoExperienceNeeded.name
    
    def parse_salary(self):
        text = self.description

        CURRENCY = r'(?:S\/\.?|USD|\$|€|soles|d[oó]lares|euros)'
        KEYWORDS = r'(?:sueldo|salario|remuneraci[oó]n|ganancia|paga|pago|ingreso|gana|obt[eé]n|obtendr[aá]|ofrecemos|b[aá]sico|fijo|m[ií]nimo)'
        NUM = r'(?:\b\d{1,2}(?:[.,\s]\d{3})+(?:[.,]\d{1,2})?\b|\b\d{3,5}(?:[.,]\d{1,2})?\b)'

        range_pattern = rf'(?:{CURRENCY}\s*)?(?P<min>{NUM})\s*(?:[-–—]|\ba\b|\bhasta\b)\s*(?:{CURRENCY}\s*)?(?P<max>{NUM})\s*(?:{CURRENCY})?'

        for match in re.finditer(range_pattern, text, re.IGNORECASE):
            segment = match.group(0)
            if re.search(CURRENCY, segment, re.IGNORECASE) or re.search(KEYWORDS, segment, re.IGNORECASE):
                min_s = self._parse_salary_number(match.group('min'))
                max_s = self._parse_salary_number(match.group('max'))
                if min_s and max_s and min_s < max_s:
                    return {'min_salary': min_s, 'max_salary': max_s}

        single_pattern = rf'(?:{KEYWORDS}.{{0,20}}?)?(?:{CURRENCY}\s*(?P<amt1>{NUM})|(?P<amt2>{NUM})\s*{CURRENCY})'

        for match in re.finditer(single_pattern, text, re.IGNORECASE):
            raw_num = match.group('amt1') or match.group('amt2')
            salary = self._parse_salary_number(raw_num)
            if salary is not None:
                return {'min_salary': salary, 'max_salary': salary}

        fallback_pattern = rf'{KEYWORDS}.{{0,15}}?\b(?P<amt>{NUM})\b'
        fallback_match = re.search(fallback_pattern, text, re.IGNORECASE)
        if fallback_match:
            salary = self._parse_salary_number(fallback_match.group('amt'))
            if salary is not None:
                return {'min_salary': salary, 'max_salary': salary}

        return {'min_salary': None, 'max_salary': None}


    def _parse_salary_number(self, value: str) -> float | None:
        if not value:
            return None

        v = re.sub(r'\s+', '', value.strip())

        if ',' in v and '.' in v:
            if v.rfind('.') > v.rfind(','):
                v = v.replace(',', '')
            else:
                v = v.replace('.', '').replace(',', '.')
        elif ',' in v:
            parts = v.split(',')
            v = (
                v.replace(',', '.')
                if len(parts) == 2 and len(parts[1]) == 2
                else v.replace(',', '')
            )
        elif '.' in v:
            parts = v.split('.')
            if not (len(parts) == 2 and len(parts[1]) == 2):
                v = v.replace('.', '')

        try:
            num = float(v)
            if 500 <= num <= 50000:
                return num
        except ValueError:
            pass

        return None
    
    def parse_salary_period(self):
        salary_period = JOB_REGEX_PATTERNS["salary_period"].search(self.description)
        if salary_period:
            period = salary_period.group().lower()
            if period == "mensual": return SalaryPeriod.Monthly.name
            elif period == "quincenal": return SalaryPeriod.Fortnightly.name
            elif period == "semanal": return SalaryPeriod.Weekly.name
            elif period == "diario": return SalaryPeriod.Daily.name
        return SalaryPeriod.Monthly.name
    
    def parse_compensation_type(self):
        compensation_type = JOB_REGEX_PATTERNS["compensation_type"].search(self.description)
        if compensation_type:
           return CompensationType.Mixed.name
        return CompensationType.Fixed.name
    
    def parse_work_hours(self):
        work_hours_match = JOB_REGEX_PATTERNS["work_hours"].search(self.description)
        if work_hours_match:
            work_hours = work_hours_match.group().lower()
            if re.search(r"comp|full",work_hours): return WorkHours.FullTime.name
            elif re.search(r"med|part", work_hours): return WorkHours.PartTime.name
            elif re.search(r"hor", work_hours): return WorkHours.Hourly.name
        return WorkHours.FullTime.name
        
    def parse_job_type(self):
        job_type_match = JOB_REGEX_PATTERNS["job_type"].search(self.description)
        if job_type_match:
            job_type = job_type_match.group().lower()
            if re.search(r"pre|en o", job_type): return JobType.InPerson.name
            elif re.search(r"vir|rem", job_type): return JobType.Remote.name
            elif re.search(r"h[ií]b", job_type): return JobType.Hybrid.name
        return JobType.InPerson.name
    
    def parse_education_level(self):
        education_level_match = JOB_REGEX_PATTERNS["education_level"].search(self.description)
        if education_level_match:
            education_level = education_level_match.group().lower()
            if re.search(r"^doc", education_level): return EducationLevel.Doctorate.name
            elif re.search(r"^ma", education_level): return EducationLevel.Master.name
            elif re.search(r"^uni|^bac|^tit|^egr", education_level): return EducationLevel.University.name
            elif re.search(r"sec", education_level): return EducationLevel.Secondary.name
            elif re.search(r"pri", education_level): return EducationLevel.Primary.name
        return EducationLevel.Unspecified.name
    
    def _normalize_experience(self, match_object):
        if not match_object:
            return Experience.NoExperienceNeeded.name

        groups = [g for g in match_object.groups() if g is not None]
        if len(groups) < 2:
            return Experience.NoExperienceNeeded.name

        raw_value = groups[0].lower()
        unit = groups[1].lower()

        word_to_num = {
            "un": 1, "dos": 2, "tres": 3, "cuatro": 4, "cinco": 5,
            "una": 1
        }

        try:
            if raw_value in word_to_num:
                value = word_to_num[raw_value]
            else:
                value = int(raw_value)
        except ValueError:
            return Experience.NoExperienceNeeded.name

        if "mes" in unit:
            if value > 12: return Experience.OneYear.name
            if value <= 3:
                return Experience.ThreeMonths.name
            elif value <= 6:
                return Experience.SixMonths.name
            else:
                return Experience.OneYear.name

        if "año" in unit or "year" in unit:
            if value <= 1:
                return Experience.OneYear.name
            elif value >= 2:
                return Experience.TwoOrMoreYears.name

        return Experience.NoExperienceNeeded.name