#adresi kordinatlara çevirmek için kullanacağız.

from utils.normalize import normalize_text

def find_coordinates(client, raw_addres:str):

    addr1= normalize_text(raw_addres)

    addr2= normalize_text(raw_addres.replace("mahallesi", "").replace("mahalle",""))

    parts = raw_addres.split(",")
    if len(parts) >= 3:
        ilce = parts[-2].strip()
        sehir = parts[-1].strip()
        addr3 = normalize_text(f"{ilce}, {sehir}")
    else:
        addr3 = addr2

    search_attempts = [addr1, addr2, addr3]

    for candidate in search_attempts:
        try:
            result = client.pelias_search(text=candidate)

            if result and "features" in result and len(result["features"]) > 0:
                return result["features"][0]["geometry"]["coordinates"]

        except Exception as e:
            print(f"Geocode error ({candidate}):", e)

    return None
