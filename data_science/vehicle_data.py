# -*- coding: utf-8 -*-
"""
Created on Thu Dec 18 16:19:10 2025

@author: selim
"""
import csv
import os

DATA_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "data",
    "vehicles.csv"
)

def _norm(s):
    return (str(s) if s is not None else "").strip().lower()

def _to_float(x):
    if x is None:
        return None
    s = str(x).strip().replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return None

def find_vehicle_consumption(make, model, year=None, csv_path=DATA_PATH):
    """
    It finds vehicle fuel consumption values from a CSV file.
    If there are multiple rows for the same MAKE+MODEL+YEAR, it takes the AVERAGE.
    Return:
        (avg_city, avg_highway)
      If it can't find anything: (None, None)
    """

    make_n = _norm(make)
    model_n = _norm(model)
    year_n = _norm(year) if year is not None else None

    city_values = []
    highway_values = []

    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            if _norm(row.get("MAKE")) != make_n:
                continue
            if _norm(row.get("MODEL")) != model_n:
                continue
            if year_n is not None and _norm(row.get("YEAR")) != year_n:
                continue

            city = _to_float(row.get("FUEL CONSUMPTION"))      # şehir içi
            highway = _to_float(row.get("HWY (L/100 km)"))     # şehir dışı
            combined = _to_float(row.get("COMB (L/100 km)"))   # karma

            # Priority: Add city+highway if available
            if city is not None and highway is not None:
                city_values.append(city)
                highway_values.append(highway)
                continue

            # Fallback: If combined, use this instead of city/highway
            if combined is not None:
                city_values.append(combined)
                highway_values.append(combined)

    if not city_values or not highway_values:
        return None, None

    avg_city = sum(city_values) / len(city_values)
    avg_highway = sum(highway_values) / len(highway_values)

    return avg_city, avg_highway
