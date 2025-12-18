#kod tekrarını engelleyecek
import unicodedata

def normalize_text(text: str) -> str:
    if not text:
        return ""
    normalized = unicodedata.normalize("NFKC", text)
    cleaned = ' '.join(c for c in normalized if not unicodedata.combining(c))

    return cleaned.lower().strip()