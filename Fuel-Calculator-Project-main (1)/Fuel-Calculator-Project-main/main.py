from flask import Flask, request, jsonify
# -*- coding: utf-8 -*-
"""
Created on Mon Dec  8 21:09:54 2025

@author: selim
"""
from data_science.fuel_prices import get_fuel_price_istanbul_by_district
print(get_fuel_price_istanbul_by_district("FATIH", "benzin"))
app = Flask(__name__)

@app.route("/")
def home():
    return "Backend çalışıyor"

@app.route("/calculate", methods=["POST"])
def calculate():
    data = request.json
    print("Frontend'den gelen veri:", data)
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(debug=True)
@app.route("/")
def home():
    return "Backend çalışıyor"

@app.route("/calculate", methods=["POST"])
def calculate():
    data = request.json

    fuel_type = data["fuel"]

    fuel_prices = {
        "benzin": 52.18,
        "mazot": 50.00,
        "lpg": 25.00
    }

    price = fuel_prices.get(fuel_type, 0)

    distance_km = 100
    consumption_per_100km = 7

    cost = (distance_km / 100) * consumption_per_100km * price

    return jsonify({
        "distance_km": distance_km,
        "fuel_price": price,
        "total_cost": round(cost, 2)
    })



