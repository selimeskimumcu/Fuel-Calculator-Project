# -*- coding: utf-8 -*-
"""
Created on Mon Dec  8 20:59:20 2025

@author: selim
"""
from data_science.vehicle_data import find_vehicle_consumption
from data_science.fuel_calculator import calculate_trip_cost_with_mixed_consumption
from data_science.fuel_prices import get_fuel_price_istanbul

def estimate_trip_istanbul_with_live_fuel_price(
    distance_km,
    make,
    model,
    year,
    fuel_type="benzin",        # "benzin" | "mazot" | "lpg"
    region="AVRUPA",           # "AVRUPA" | "ANADOLU"
    city_ratio=0.6,
    highway_ratio=0.4
):
    city_c, highway_c = find_vehicle_consumption(make, model, year)
    if city_c is None or highway_c is None:
        raise ValueError("Seçilen araç için yakıt tüketim verisi bulunamadı.")

    fuel_price = get_fuel_price_istanbul(fuel_type=fuel_type, region=region)

    return calculate_trip_cost_with_mixed_consumption(
        distance_km=distance_km,
        city_ratio=city_ratio,
        highway_ratio=highway_ratio,
        city_consumption=city_c,
        highway_consumption=highway_c,
        fuel_price=fuel_price
    )
