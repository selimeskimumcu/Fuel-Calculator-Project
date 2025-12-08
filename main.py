# -*- coding: utf-8 -*-
"""
Created on Mon Dec  8 21:09:54 2025

@author: selim
"""
from data_science.fuel_calculator import calculate_fuel_usage, calculate_cost


distance=150 #km
avg_consumption= 6.5 # L/100km
fuel_price = 50 # TL/Litres


fuel = calculate_fuel_usage(distance, avg_consumption)
total_cost = calculate_cost(fuel, fuel_price)

print(f"Average fuel consumption: {fuel} L")
print(f"Cost: {total_cost} TL")