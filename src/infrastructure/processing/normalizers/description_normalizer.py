from src.infrastructure.processing.normalizers.constants.noise_patterns import NOISE_PATTERNS
import re

def normalize_description(description: str):
    lines = description.splitlines()
    clean_lines = []
    for line in lines:
        normalized = line.strip().lower()
        if not normalized or any(re.search(pattern, normalized, re.IGNORECASE) for pattern in NOISE_PATTERNS):
            continue
        clean_lines.append(line.strip().replace("\r","").replace("\t",""))
    return "\n".join(clean_lines)