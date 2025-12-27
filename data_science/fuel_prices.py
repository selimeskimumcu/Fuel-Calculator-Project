# -*- coding: utf-8 -*-
"""
Created on Thu Dec 18 17:02:14 2025

@author: selim
"""
# data_science/fuel_prices.py
import requests

PO_ISTANBUL_URL = "https://akaryakit-fiyatlari.vercel.app/api/po/34"

def _norm_tr(s):
    s = (s or "").strip().upper()
    # Türkçe karakter normalize (İ/ı vs.)
    s = s.replace("İ", "I").replace("İ", "I")
    s = s.replace("Ş", "S").replace("Ğ", "G").replace("Ü", "U").replace("Ö", "O").replace("Ç", "C")
    return s

def fetch_istanbul_prices_po():
    r = requests.get(PO_ISTANBUL_URL, timeout=10)
    r.raise_for_status()
    return r.json()

def get_fuel_price_istanbul_by_district(district, fuel_type="benzin"):
    """
    district: 'FATIH', 'KADIKOY' gibi
    fuel_type: 'benzin' | 'mazot' | 'lpg'
    """
    data = fetch_istanbul_prices_po()
    target = _norm_tr(district)

    for item in data.get("fiyatlar", []):
        ilce = _norm_tr(item.get("ilce", ""))
        if ilce == target:
            price = item.get(fuel_type)
            if price is None:
                raise ValueError(f"Yakıt türü bulunamadı: {fuel_type}")
            return float(price)

    # İlçe bulunamazsa genel fallback
    for fallback in ("ISTANBUL (AVRUPA)", "ISTANBUL (ANADOLU)"):
        for item in data.get("fiyatlar", []):
            if _norm_tr(item.get("ilce", "")) == _norm_tr(fallback):
                price = item.get(fuel_type)
                if price is not None:
                    return float(price)

    raise ValueError(f"İlçe fiyatı bulunamadı: {district}")

    
