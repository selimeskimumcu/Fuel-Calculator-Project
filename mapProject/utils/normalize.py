#kod tekrarını engelleyecek
import unicodedata
import re

def normalize_text(text: str):
    if not text:
        return ""

    text = text.lower().strip()


    text = (
        text.replace("ı", "i").replace("ğ", "g")
            .replace("ü", "u").replace("ş", "s")
            .replace("ö", "o").replace("ç", "c")
    )


    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))


    text = re.sub(r"\s+", " ", text)

    return text
