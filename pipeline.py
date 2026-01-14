# -*- coding: utf-8 -*-
"""
Created on Fri Dec 26 00:12:06 2025

@author: selim
"""
import json

from data_science.route_analysis import estimate_trip_from_map_payload


def _norm_district(s):
<<<<<<< HEAD
    # The district name is being aligned with the fuel price API.
    return (s or "").strip().upper()

def extract_district(route_data: dict) -> str:
    # It safely extracts the starting district from the map printout.
=======
    # İstanbul ilçe adını API ile uyumlu hale getirmek için:
    # büyük harf + trim yeterli (fuel_prices içinde ayrıca normalize var)
    return (s or "").strip().upper()


def extract_district(route_data: dict) -> str:
    """
    Öncelik:
      1) start_district alanı (harita modülü bunu yazarsa en temiz)
      2) start_address alanından ilçe çıkarma (ilk parça)
    """
>>>>>>> b345ac7 (Streamlit frontend implementation and route-based fuel calculation)
    if "start_district" in route_data and route_data["start_district"]:
        return _norm_district(route_data["start_district"])

    start_address = route_data.get("start_address")
    if start_address:
<<<<<<< HEAD
        # "Çekmeköy, Istanbul, Türkiye" -> "Çekmeköy"
        district_guess = str(start_address).split(",")[0]
        return _norm_district(district_guess)

    raise ValueError("In route_data.json, start_district or start_address can not be founded.")

# It reads the map JSON and generates a simple payload for Data Science.
=======
        # Örnek: "Çekmeköy, Istanbul, Türkiye" -> "Çekmeköy"
        district_guess = str(start_address).split(",")[0]
        return _norm_district(district_guess)

    raise ValueError("route_data.json içinde start_district veya start_address bulunamadı.")


>>>>>>> b345ac7 (Streamlit frontend implementation and route-based fuel calculation)
def load_route_payload(route_data_path="route_data.json") -> dict:
    with open(route_data_path, "r", encoding="utf-8") as f:
        data = json.load(f)

<<<<<<< HEAD
    summary = data.get("route_summery")
    if not summary:
        raise ValueError("In route_data.json, 'route_summery' can not be founded.")

    distance_km = summary.get("total_distance_km")
    if distance_km is None:
        raise ValueError("In route_summery, 'total_distance_km' can not be founded.")
=======
    # Harita tarafında ana özet: route_summery (yazım bu şekilde)
    summary = data.get("route_summery")
    if not summary:
        raise ValueError("route_data.json içinde 'route_summery' alanı bulunamadı.")

    distance_km = summary.get("total_distance_km")
    if distance_km is None:
        raise ValueError("route_summery içinde 'total_distance_km' yok.")
>>>>>>> b345ac7 (Streamlit frontend implementation and route-based fuel calculation)

    urban_percent = summary.get("urban_percent")
    interurban_percent = summary.get("interurban_percent")
    if urban_percent is None or interurban_percent is None:
<<<<<<< HEAD
        raise ValueError("In route_summery, 'urban_percent' or 'interurban_percent' can not be founded.")

    # Odd
=======
        raise ValueError("route_summery içinde 'urban_percent' veya 'interurban_percent' yok.")

    # yüzde -> oran
>>>>>>> b345ac7 (Streamlit frontend implementation and route-based fuel calculation)
    city_ratio = float(urban_percent) / 100.0
    highway_ratio = float(interurban_percent) / 100.0

    district = extract_district(data)

    payload = {
        "distance_km": float(distance_km),
        "city_ratio": city_ratio,
        "highway_ratio": highway_ratio,
        "start": {"district": district}
    }
    return payload

<<<<<<< HEAD
    # If the frontend has written the tool selection to JSON,
    # it automatically retrieves it.
def load_vehicle_selection(route_data: dict) -> dict | None:

=======

def load_vehicle_selection(route_data: dict) -> dict | None:
    """
    Frontend isterse route_data.json içine şu objeyi ekleyebilir:
      "vehicle_selection": {"make": "...", "model": "...", "year": 2018, "fuel_type": "benzin"}
    """
>>>>>>> b345ac7 (Streamlit frontend implementation and route-based fuel calculation)
    vs = route_data.get("vehicle_selection")
    if isinstance(vs, dict):
        return vs
    return None


def save_result(result: dict, path="result_data.json") -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)


def main():
<<<<<<< HEAD
    # route_data.json reading
    with open("route_data.json", "r", encoding="utf-8") as f:
        route_data = json.load(f)

    # Make Map Payload
    map_payload = load_route_payload("route_data.json")

    # Choose of Vehicle
=======
    # 1) route_data.json oku
    with open("route_data.json", "r", encoding="utf-8") as f:
        route_data = json.load(f)

    # 2) Harita payload üret
    map_payload = load_route_payload("route_data.json")

    # 3) Araç seçimi: JSON'da varsa oradan al, yoksa CLI ile sor (demo için)
>>>>>>> b345ac7 (Streamlit frontend implementation and route-based fuel calculation)
    vs = load_vehicle_selection(route_data)
    if vs is None:
        print("vehicle_selection bulunamadı. Demo için terminalden alıyorum.")
        make = input("MAKE (örn: ACURA): ").strip()
        model = input("MODEL (örn: 1.6EL): ").strip()
        year = int(input("YEAR (örn: 2000): ").strip())
        fuel_type = input("fuel_type (benzin/mazot/lpg) [benzin]: ").strip() or "benzin"
    else:
        make = vs.get("make", "").strip()
        model = vs.get("model", "").strip()
        year = int(vs.get("year"))
        fuel_type = (vs.get("fuel_type") or "benzin").strip()

<<<<<<< HEAD
    # Calculate
=======
    # 4) Hesapla (oranları haritadan alıyoruz!)
>>>>>>> b345ac7 (Streamlit frontend implementation and route-based fuel calculation)
    result = estimate_trip_from_map_payload(
        map_payload={
            "distance_km": map_payload["distance_km"],
            "start": {"district": map_payload["start"]["district"]}
        },
        make=make,
        model=model,
        year=year,
        fuel_type=fuel_type,
        city_ratio=map_payload["city_ratio"],
        highway_ratio=map_payload["highway_ratio"]
    )

<<<<<<< HEAD
    # Frontend
=======
    # Ek bilgi (frontend için güzel)
>>>>>>> b345ac7 (Streamlit frontend implementation and route-based fuel calculation)
    result["route_summary"] = {
        "distance_km": map_payload["distance_km"],
        "city_ratio": map_payload["city_ratio"],
        "highway_ratio": map_payload["highway_ratio"],
        "start_district": map_payload["start"]["district"]
    }

    save_result(result, "result_data.json")
    print("OK -> result_data.json yazıldı")


if __name__ == "__main__":
    main()

