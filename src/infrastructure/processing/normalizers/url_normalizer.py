import unicodedata
import re

def url_normalizer(text: str):
    if not text: return ""
    text = text.strip().lower()
    text = ''.join(
        c for c in unicodedata.normalize('NFD', text)
        if unicodedata.category(c) != 'Mn'
    )
    text = re.sub(r'[^a-z0-9]+', '-', text)
    text = text.strip('-')
    return text