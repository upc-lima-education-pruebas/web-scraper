import json
from pathlib import Path
import unicodedata

CURRENT_DIR = Path(__file__).parent
UBIGEO_PATH = CURRENT_DIR / "data" / "ubigeo.json"

with open(UBIGEO_PATH, 'r', encoding='utf-8') as f:
    ubigeos_data = json.load(f)

UBIGEO_INDEX = {
    (item['Distrito'].upper(), item['Departamento'].upper()): item['Ubigeo']
    for item in ubigeos_data
}

def ubigeo_resolver(district: str, department: str) -> str | None:
    if not district or not department:
        return None

    normalized_district = normalize_for_ubigeo(district)
    normalized_department = normalize_for_ubigeo(department)

    # Aliases y reglas especiales
    if normalized_district == "CERCADO DE LIMA":
        normalized_district = "LIMA"

    if "CALLAO" in normalized_department:
        normalized_department = "CALLAO"

    if "CALLAO" in normalized_district and normalized_department == "LIMA":
        normalized_department = "CALLAO"

    key = (normalized_district, normalized_department)

    return UBIGEO_INDEX.get(key)

def normalize_for_ubigeo(text: str) -> str:
    if not text:
        return ""

    text = text.replace("Ñ", "__N_ENYE__").replace("ñ", "__n_enye__")

    text = "".join(
        c
        for c in unicodedata.normalize("NFD", text)
        if unicodedata.category(c) != "Mn"
    )

    text = text.replace("__N_ENYE__", "Ñ").replace("__n_enye__", "ñ")

    return (
        text.replace(".", "")
        .replace("-", "")
        .strip()
        .upper()
    )