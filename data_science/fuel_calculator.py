# -*- coding: utf-8 -*-
"""
Created on Mon Dec  8 20:58:33 2025

@author: selim
"""
def calculate_fuel_usage(distance_km, consumption_per_100km):
    return distance_km * consumption_per_100km / 100


def calculate_cost(fuel_usage_litre, fuel_price_per_litre):
    return fuel_usage_litre * fuel_price_per_litre

    
def calculate_mixed_consumption(city_ratio, highway_ratio, city_consumption, highway_consumption):
    """
    Parameters
    city_ratio: The route's urban ratio (between 0 and 1)
    highway_ratio: The route's extra-urban ratio (between 0 and 1)
    city_consumption: The vehicle's urban consumption (L/100km)
    highway_consumption: The vehicle's extra-urban consumption (L/100km)

    """
    total = city_ratio + highway_ratio
    if total == 0:
        raise ValueError("city_ratio + highway_ratio cant be 0.")
            
    city_ratio_norm = city_ratio / total
    highway_ratio_norm = highway_ratio / total
    
    mixed = (city_ratio * city_consumption) + (highway_ratio * highway_consumption)
    return mixed   # L/100km

def calculate_trip_cost_with_mixed_consumption(distance_km,city_ratio,highway_ratio,city_consumption,highway_consumption,fuel_price):
    mixed_consumption = calculate_mixed_consumption(
        city_ratio, highway_ratio, city_consumption, highway_consumption)
    
    fuel_used = calculate_fuel_usage(distance_km, mixed_consumption)
    total_cost = calculate_cost(fuel_used, fuel_price)
    
    return {
        "mixed_consumption": mixed_consumption,
        "fuel_used": fuel_used,
        "total_cost":total_cost
        }




    
        
    
