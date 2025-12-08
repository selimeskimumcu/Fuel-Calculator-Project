# -*- coding: utf-8 -*-
"""
Created on Mon Dec  8 21:09:54 2025

@author: selim
"""
from data_science.fuel_calculator import calculate_trip_cost_with_mixed_consumption

# Example of Map API Gives that distance
distance_km = 20.5

# Sample Rates
city_ratio = 0.6
highway_ratio = 0.4

# Consumption values ​​of the vehicle (L/100km)
city_consumption = 8.0
highway_consumption = 5.5

# Fuel Price (TL/L)
fuel_price = 43

result = calculate_trip_cost_with_mixed_consumption(
    distance_km=distance_km,
    city_ratio=city_ratio,
    highway_ratio=highway_ratio,
    city_consumption=city_consumption,
    highway_consumption=highway_consumption,
    fuel_price=fuel_price
)

print("Karma tüketim (L/100km):", result["mixed_consumption"])
print("Toplam yakıt (L):", result["fuel_used"])
print("Toplam maliyet (TL):", result["total_cost"])


