# -*- coding: utf-8 -*-
"""
Created on Mon Dec  8 20:59:20 2025

@author: selim
"""
import os
import sys

# data_science/route_analysis.py -> proje kökü
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from .vehicle_data import find_vehicle_consumption
from .fuel_calculator import calculate_trip_cost_with_mixed_consumption
from .fuel_prices import get_fuel_price_istanbul_by_district


ALLOWED_FUEL_TYPES = {"benzin", "mazot", "lpg"}


def estimate_trip_from_map_payload(
    map_payload,
    make,
    model,
    year,
    fuel_type="benzin",

    city_ratio=0.6,
    highway_ratio=0.4,

    force_city_ratio=0.90,
    # Istanbul traffic reality
    traffic_multiplier_city=1.45,
    traffic_multiplier_highway=1.08
):

    # fuel_type verification
    fuel_type = (fuel_type or "benzin").strip().lower()
    if fuel_type not in ALLOWED_FUEL_TYPES:
        raise ValueError(
            f"Geçersiz fuel_type: '{fuel_type}'. İzin verilenler: {', '.join(sorted(ALLOWED_FUEL_TYPES))}"
        )

    # Distance
    if not isinstance(map_payload, dict):
        raise ValueError("map_payload dict olmalı.")
    if "distance_km" not in map_payload:
        raise ValueError("map_payload içinde 'distance_km' yok.")

    distance_km = float(map_payload["distance_km"])
    if distance_km <= 0:
        raise ValueError("distance_km 0'dan büyük olmalı.")

    # District
    start = map_payload.get("start") or {}
    district = start.get("district")
    if not district:
        raise ValueError("map_payload.start.district can not be founded. (Example: FATIH / KADIKOY / CEKMEKOY)")
    district = str(district).strip().upper()

    # Odds
    if force_city_ratio is not None:
        city_ratio = float(force_city_ratio)
        if not (0.0 <= city_ratio <= 1.0):
            raise ValueError("force_city_ratio 0 ile 1 arasında olmalı. Örn: 0.90")
        highway_ratio = 1.0 - city_ratio
    else:
        city_ratio = float(city_ratio)
        highway_ratio = float(highway_ratio)
        total = city_ratio + highway_ratio
        if total == 0:
            raise ValueError("city_ratio + highway_ratio 0 olamaz.")
        city_ratio /= total
        highway_ratio /= total

    # Vehicle (CSV)
    city_c, highway_c = find_vehicle_consumption(make, model, year)
    if city_c is None or highway_c is None:
        raise ValueError(
            f"Araç tüketim verisi bulunamadı: MAKE={make}, MODEL={model}, YEAR={year}"
        )

    # Designing Traffic
    city_c_adj = float(city_c) * float(traffic_multiplier_city)
    highway_c_adj = float(highway_c) * float(traffic_multiplier_highway)

    # Fuel Price (District of Istanbul)
    try:
        fuel_price = get_fuel_price_istanbul_by_district(district, fuel_type=fuel_type)
    except Exception as e:
        raise ValueError(
            f"Yakıt fiyatı bulunamadı. İlçe='{district}', fuel_type='{fuel_type}'. "
            "Başlangıç noktasının İstanbul ilçesi olduğundan emin ol."
        ) from e

    # Calculate
    result = calculate_trip_cost_with_mixed_consumption(
        distance_km=distance_km,
        city_ratio=city_ratio,
        highway_ratio=highway_ratio,
        city_consumption=city_c_adj,
        highway_consumption=highway_c_adj,
        fuel_price=fuel_price
    )

    # Frontend
    result.update({
        "distance_km": distance_km,
        "district": district,
        "fuel_type": fuel_type,
        "vehicle": {"make": make, "model": model, "year": year},
        "ratios": {"city_ratio": city_ratio, "highway_ratio": highway_ratio},
        "inputs": {
            "city_consumption_raw": city_c,
            "highway_consumption_raw": highway_c,
            "city_consumption_adjusted": city_c_adj,
            "highway_consumption_adjusted": highway_c_adj,
            "fuel_price": fuel_price,
            "force_city_ratio": force_city_ratio,
            "traffic_multiplier_city": traffic_multiplier_city,
            "traffic_multiplier_highway": traffic_multiplier_highway
        }
    })

    return result
