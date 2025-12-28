# -*- coding: utf-8 -*-
"""
Created on Mon Dec  8 20:59:20 2025

@author: selim
"""
from data_science.vehicle_data import find_vehicle_consumption
from data_science.fuel_calculator import calculate_trip_cost_with_mixed_consumption
from data_science.fuel_prices import get_fuel_price_istanbul_by_district


def estimate_trip_from_map_payload(
    map_payload,
    make,
    model,
    year,
    fuel_type="benzin",
    city_ratio=0.6,
    highway_ratio=0.4
):
    """
    map_payload beklenen format:
      {
        "distance_km": 59.287,
        "start": {"district": "CEKMEKOY"}
      }

    Araç seçimi CSV'den alınır, yakıt fiyatı İstanbul ilçe bazlı API'den alınır,
    ardından fuel_calculator ile sonuç hesaplanır.
    """

    # 1) Mesafe
    if not isinstance(map_payload, dict):
        raise ValueError("map_payload dict olmalı.")

    if "distance_km" not in map_payload:
        raise ValueError("map_payload içinde 'distance_km' yok.")

    distance_km = float(map_payload["distance_km"])

    # 2) İlçe
    start = map_payload.get("start") or {}
    district = start.get("district")
    if not district:
        raise ValueError("map_payload.start.district yok. (Örn: FATIH / KADIKOY / CEKMEKOY)")

    district = str(district).strip().upper()

    # 3) Oranlar (gelen oranların toplamı 0 olmasın)
    city_ratio = float(city_ratio)
    highway_ratio = float(highway_ratio)
    if (city_ratio + highway_ratio) == 0:
        raise ValueError("city_ratio + highway_ratio 0 olamaz.")

    # 4) Araç tüketimi (CSV)
    city_c, highway_c = find_vehicle_consumption(make, model, year)
    if city_c is None or highway_c is None:
        raise ValueError(
            f"Araç tüketim verisi bulunamadı: MAKE={make}, MODEL={model}, YEAR={year}"
        )

    # 5) Yakıt fiyatı (İstanbul ilçe bazlı)
    fuel_price = get_fuel_price_istanbul_by_district(district, fuel_type=fuel_type)

    # 6) Hesap
    result = calculate_trip_cost_with_mixed_consumption(
        distance_km=distance_km,
        city_ratio=city_ratio,
        highway_ratio=highway_ratio,
        city_consumption=city_c,
        highway_consumption=highway_c,
        fuel_price=fuel_price
    )

    # 7) Frontend için ek meta
    result.update({
        "distance_km": distance_km,
        "district": district,
        "fuel_type": fuel_type,
        "vehicle": {"make": make, "model": model, "year": year},
        "ratios": {"city_ratio": city_ratio, "highway_ratio": highway_ratio},
        "inputs": {
            "city_consumption": city_c,
            "highway_consumption": highway_c,
            "fuel_price": fuel_price
        }
    })

    return result


