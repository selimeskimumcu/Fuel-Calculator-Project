# -*- coding: utf-8 -*-
"""
Created on Thu Dec 18 17:02:14 2025

@author: selim
"""
# data_science/fuel_prices.py
import requests

PO_ISTANBUL_URL = "https://akaryakit-fiyatlari.vercel.app/api/po/34"

def fetch_istanbul_prices_po():
    """
    Petrol Ofisi kaynağından İstanbul fiyatlarını çeker.
    Dönen örnek: {"sonYenileme": "...", "fiyatlar":[{"ilce":"ISTANBUL (AVRUPA)", "benzin":..., "mazot":..., "lpg":...}, ...]}
    """
    r = requests.get(PO_ISTANBUL_URL, timeout=10)
    r.raise_for_status()
    return r.json()

def get_fuel_price_istanbul(fuel_type="benzin", region="AVRUPA"):
    """
    fuel_type: "benzin" | "mazot" | "lpg"
    region: "AVRUPA" | "ANADOLU"
    Çıktı: TL/L (float)
    """
    data = fetch_istanbul_prices_po()
    target = f"ISTANBUL ({region.strip().upper()})"

    for item in data.get("fiyatlar", []):
        if str(item.get("ilce", "")).strip().upper() == target:
            price = item.get(fuel_type)
            if price is None:
                raise ValueError(f"Yakıt türü bulunamadı: {fuel_type}")
            return float(price)

    raise ValueError(f"İstanbul bölgesi bulunamadı: {target}")

    
