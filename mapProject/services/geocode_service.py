#adresi kordinatlara çevirmek için kullanacağız.
from utils.normalize import normalize_text

def find_coordinates(client, raw_address: str):


    addr1 = normalize_text(raw_address)


    addr2 = normalize_text(
        raw_address.replace("mahallesi", "")
                   .replace("mahallesi", "")
                   .replace("mahalle", "")
    )


    parts = raw_address.split(",")
    if len(parts) >= 3:
        ilce = parts[-2].strip()
        sehir = parts[-1].strip()
        addr3 = normalize_text(f"{ilce}, {sehir}")
    else:
        addr3 = addr2

    attempts = [addr1, addr2, addr3]

    for candidate in attempts:
        try:
            result = client.pelias_search(text=candidate)

            if result and "features" in result and len(result["features"]) > 0:
                return result["features"][0]["geometry"]["coordinates"]

        except Exception as e:
            print(f"[Geocode ERROR] {candidate} :", e)

    print(f"[Geocode FAIL] {raw_address} could not be founded")
    return None
