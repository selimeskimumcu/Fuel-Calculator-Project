# -*- coding: utf-8 -*-
"""
Created on Mon Dec  8 20:58:33 2025

@author: selim
"""
# data_science/fuel_calculator.py

def calculate_fuel_usage(distance_km, consumption_per_100km):
    """
    distance_km: total distance (km)
    consumption_per_100km: fuel consumption in L/100km
    """
    return distance_km * consumption_per_100km / 100


def calculate_cost(fuel_usage_litre, fuel_price_per_litre):
    """
    fuel_usage_litre: fuel consumed (L)
    fuel_price_per_litre: price per liter of fuel (TL)
    """
    return fuel_usage_litre * fuel_price_per_litre


def calculate_mixed_consumption(city_ratio, highway_ratio, city_consumption, highway_consumption):
    """
    city_ratio: city ratio (0-1)
    highway_ratio: highway ratio (0-1)
    city_consumption: city consumption (L/100km)
    highway_consumption: highway consumption (L/100km)
    """
    total = city_ratio + highway_ratio
    if total == 0:
        raise ValueError("city_ratio + highway_ratio can not be 0")

    city_ratio = city_ratio / total
    highway_ratio = highway_ratio / total

    return (city_ratio * city_consumption) + (highway_ratio * highway_consumption)


def calculate_trip_cost_with_mixed_consumption(
    distance_km,
    city_ratio,
    highway_ratio,
    city_consumption,
    highway_consumption,
    fuel_price
):
    """
    Total cost calculation using Map API + vehicle consumption data.
    """

    mixed_consumption = calculate_mixed_consumption(
        city_ratio,
        highway_ratio,
        city_consumption,
        highway_consumption
    )

    fuel_used = calculate_fuel_usage(distance_km, mixed_consumption)
    total_cost = calculate_cost(fuel_used, fuel_price)

    return {
        "mixed_consumption": mixed_consumption,  # L/100km
        "fuel_used": fuel_used,                  # L
        "total_cost": total_cost                 # TL
    }
