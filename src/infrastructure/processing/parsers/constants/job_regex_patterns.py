import re

JOB_REGEX_PATTERNS = {
    "experience": re.compile(
        r"(\d+|un|dos|tres|cuatro|cinco)\s+(año|mes|year)",
        re.IGNORECASE
    ),
    "skills": re.compile(
        r"(?:experiencia|conocimiento|habilidad|actitud|aptitud|capacidad|competencia|dominio|manejo|conoce|comprende|requisito|deseable).*",
        re.IGNORECASE
    ),
    "salary_range": re.compile(
        r"sueldo.*?s\/?\.?\s?([\d,.]+).*?(?:a|-).*?s\/?\.?\s?([\d,.]+)|remuneraci[oó]n.*?s\/?\.?\s?([\d,.]+).*?(?:a|-).*?s\/?\.?\s?([\d,.]+)|salario.*?s\/?\.?\s?([\d,.]+).*?(?:a|-).*?s\/?\.?\s?([\d,.]+)",
        re.IGNORECASE
    ),
    "salary_single": re.compile(
        r"s\/?\.\s?\d{3,6}(?:[.,]\d{3})*|sueldo:(.*[^bono|^comisi[oó]n])|salario:(.*[^bono|^comisi[oó]n])|remuneraci[oó]n:(.*[^bono|^comisi[oó]n])",
        re.IGNORECASE
    ),
    "salary_period": re.compile(
        r"pago.*(mensual)|pago.*(quincenal)|pago.*(semanal)|pago.*(diario)",
        re.IGNORECASE
    ),
    "compensation_type": re.compile(
        r"(comisi[oó]n|comisiones)",
        re.IGNORECASE
    ),
    "work_hours": re.compile(
        r"\b(tiempo completo|jornada completa|full[- ]?time|medio tiempo|media jornada|part[- ]?time|por horas)\b",
        re.IGNORECASE
    ),
    "job_type": re.compile(
      r"modalidad(virtual|remoto|h[ií]brid[ao]|presencial|en oficina)|trabajo(virtual|remoto|h[ií]brid[ao]|presencial|en oficina)",
      re.IGNORECASE
    ),
    "education_level": re.compile(
        r"(universidad|universitari[oa]|bachiller|bachillerato|t[ií]tulo|titulado|egresado|maestr[ií]a|master|doctorado|t[eé]cnico)|(primaria|secundaria) completa| (primaria|secundaria) i[nm]completa",
        re.IGNORECASE
    )
}