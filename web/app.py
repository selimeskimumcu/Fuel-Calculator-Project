import os
import sys

# ✅ Proje kökünü sys.path'e ekle (mapProject / data_science importları için)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from flask import Flask, render_template, request, jsonify
from openrouteservice import Client

# mapProject servislerini kullan
from mapProject.services.geocode_service import find_coordinates
from mapProject.services.route_service import get_route

# data science hesap
from data_science.route_analysis import estimate_trip_from_map_payload

app = Flask(__name__)

# ✅ ORS KEY: önce ortam değişkeninden (önerilen), yoksa placeholder
ORS_API_KEY = os.environ.get("ORS_API_KEY", "BURAYA_ORS_KEY").strip()

if not ORS_API_KEY or ORS_API_KEY == "BURAYA_ORS_KEY":
    # Uygulama yine açılır ama route endpointi çalışmayabilir.
    # İstersen burada raise da edebilirsin.
    print("⚠ ORS_API_KEY ayarlı değil. PowerShell: $env:ORS_API_KEY='...'; python web/app.py")

ors_client = Client(key=ORS_API_KEY)

ALLOWED_FUEL_TYPES = {"benzin", "mazot", "lpg"}


def district_from_start_address(start_address: str) -> str:
    # "Çekmeköy, İstanbul, Türkiye" -> "ÇEKMEKÖY"
    if not start_address:
        return ""
    return start_address.split(",")[0].strip().upper()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/route", methods=["POST"])
def api_route():
    """
    İki kullanım:
    1) address ile: { "start_address": "...", "end_address": "..." }
    2) coord ile:   { "start_coord": [lon,lat], "end_coord": [lon,lat] }
    """
    data = request.get_json(force=True)

    start_address = data.get("start_address")
    end_address = data.get("end_address")
    start_coord = data.get("start_coord")
    end_coord = data.get("end_coord")

    # Address geldiyse coord'a çevir
    if start_address and end_address:
        sc = find_coordinates(ors_client, start_address)
        ec = find_coordinates(ors_client, end_address)
        if not sc or not ec:
            return jsonify({"error": "Adreslerden koordinat bulunamadı. Yazımı kontrol edin."}), 400
        start_coord, end_coord = sc, ec

    if not start_coord or not end_coord:
        return jsonify({"error": "start_coord ve end_coord gerekli (veya start_address/end_address)."}), 400

    try:
        route_data = get_route(ors_client, start_coord, end_coord)
    except Exception as e:
        return jsonify({"error": f"Rota servisi hatası: {str(e)}"}), 400

    if not route_data:
        return jsonify({"error": "Rota bulunamadı."}), 400

    return jsonify({
        "start_coord": start_coord,
        "end_coord": end_coord,
        "route_summery": route_data.get("route_summery"),
        "route_geometry": route_data.get("route_geometry"),
        # Harita ekibin yazdıysa: start_address da döndürmek iyi olur
        "start_address": route_data.get("start_address"),
        "end_address": route_data.get("end_address"),
    })


@app.route("/api/calculate", methods=["POST"])
def api_calculate():
    """
    Beklenen JSON:
    {
      "route_summery": {...},
      "start_address": "Çekmeköy, İstanbul, Türkiye"  (veya start_district)
      "vehicle": {"make":"ACURA","model":"1.6EL","year":2000},
      "fuel_type": "benzin" | "mazot" | "lpg"
    }
    """
    data = request.get_json(force=True)

    summary = data.get("route_summery")
    vehicle = data.get("vehicle") or {}
    fuel_type = (data.get("fuel_type") or "benzin").strip().lower()

    # ✅ fuel_type doğrulama (dokunuş 1)
    if fuel_type not in ALLOWED_FUEL_TYPES:
        return jsonify({
            "error": f"Geçersiz fuel_type: '{fuel_type}'. İzin verilenler: {', '.join(sorted(ALLOWED_FUEL_TYPES))}"
        }), 400

    if not summary:
        return jsonify({"error": "route_summery zorunlu."}), 400

    # route bilgileri
    distance_km = summary.get("total_distance_km")
    urban_percent = summary.get("urban_percent")
    interurban_percent = summary.get("interurban_percent")

    if distance_km is None or urban_percent is None or interurban_percent is None:
        return jsonify({"error": "route_summery alanları eksik: total_distance_km / urban_percent / interurban_percent"}), 400

    city_ratio = float(urban_percent) / 100.0
    highway_ratio = float(interurban_percent) / 100.0

    # district: önce start_district, yoksa start_address'ten çıkar
    start_district = (data.get("start_district") or "").strip().upper()
    if not start_district:
        start_address = data.get("start_address", "")
        start_district = district_from_start_address(start_address)

    if not start_district:
        return jsonify({"error": "start_district veya start_address gerekli."}), 400

    make = (vehicle.get("make") or "").strip()
    model = (vehicle.get("model") or "").strip()
    year = vehicle.get("year")

    if not make or not model or year is None or str(year).strip() == "":
        return jsonify({"error": "vehicle(make, model, year) eksik."}), 400

    # DataScience hesap
    try:
        result = estimate_trip_from_map_payload(
            map_payload={"distance_km": float(distance_km), "start": {"district": start_district}},
            make=make,
            model=model,
            year=int(year),
            fuel_type=fuel_type,
            city_ratio=city_ratio,
            highway_ratio=highway_ratio
        )
    except Exception as e:
        # ✅ daha açıklayıcı hata (dokunuş 2) - ilçeye göre yakıt fiyatı bulunamazsa vs.
        msg = str(e)
        if "İlçe" in msg or "ilçe" in msg or "district" in msg:
            msg = (
                f"{msg} | Not: Yakıt fiyatı sadece İstanbul ilçeleri için destekleniyor. "
                f"Gönderilen ilçe='{start_district}'."
            )
        return jsonify({"error": msg}), 400

    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True)
