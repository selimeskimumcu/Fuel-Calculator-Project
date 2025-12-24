# -*- coding: utf-8 -*-
"""
Created on Mon Dec  8 21:09:54 2025

@author: selim
"""
from data_science.route_analysis import estimate_trip_istanbul_with_live_fuel_price

result = estimate_trip_istanbul_with_live_fuel_price(
    distance_km=25.4,
    make="ACURA",
    model="1.6EL",
    year=2000,
    fuel_type="benzin",
    region="AVRUPA",
    city_ratio=0.7,
    highway_ratio=0.3
)

print(result)





