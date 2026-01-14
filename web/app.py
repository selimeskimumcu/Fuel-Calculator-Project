import os
import sys
import json
import requests
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file
from openrouteservice import Client

<<<<<<< HEAD
# Proje kökünü sys.path'e ekle (mapProject / data_science importları için)
=======
# proje kökünü sys.pathe ekledim sebebi mapproject ve data_science importları için
>>>>>>> b345ac7 (Streamlit frontend implementation and route-based fuel calculation)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

<<<<<<< HEAD
# mapProject servislerini kullan
from mapProject.services.geocode_service import find_coordinates
from mapProject.services.route_service import get_route

# data science hesap
=======
# mapproject servislerini kullandım
from mapProject.services.geocode_service import find_coordinates
from mapProject.services.route_service import get_route

# data science hesaplaması
>>>>>>> b345ac7 (Streamlit frontend implementation and route-based fuel calculation)
from data_science.route_analysis import estimate_trip_from_map_payload

app = Flask(__name__)

<<<<<<< HEAD
# ORS KEY
=======
# bu kısım ors key tarafı o keyi backhendden alacaz
>>>>>>> b345ac7 (Streamlit frontend implementation and route-based fuel calculation)
ORS_API_KEY = os.environ.get("ORS_API_KEY", "BURAYA_ORS_KEY").strip()
if not ORS_API_KEY or ORS_API_KEY == "BURAYA_ORS_KEY":
    print("⚠ ORS_API_KEY ayarlı değil. PowerShell: $env:ORS_API_KEY='...'; python web/app.py")

ors_client = Client(key=ORS_API_KEY)

ALLOWED_FUEL_TYPES = {"benzin", "mazot", "lpg"}

<<<<<<< HEAD
# JSON dosyalarının yazılacağı klasör: Fuel-Calculator-Project/mapProject/
=======
#  json dosyalarının yazıalacağı klasör (proje adı fuel-calculator-project/mapproject/
>>>>>>> b345ac7 (Streamlit frontend implementation and route-based fuel calculation)
MAPPROJECT_DIR = os.path.join(BASE_DIR, "mapProject")
ROUTE_JSON_PATH = os.path.join(MAPPROJECT_DIR, "route_data.json")
RESULT_JSON_PATH = os.path.join(MAPPROJECT_DIR, "result_data.json")


def save_json(path: str, data: dict):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def read_json(path: str):
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


<<<<<<< HEAD
# İstanbul ilçeleri: adres içinden güçlü yakalama için
=======
# istanbulun ilçeleri
>>>>>>> b345ac7 (Streamlit frontend implementation and route-based fuel calculation)
ISTANBUL_DISTRICTS = [
    "ADALAR","ARNAVUTKÖY","ATAŞEHİR","AVCILAR","BAĞCILAR","BAHÇELİEVLER","BAKIRKÖY",
    "BAŞAKŞEHİR","BAYRAMPAŞA","BEŞİKTAŞ","BEYKOZ","BEYLİKDÜZÜ","BEYOĞLU",
    "BÜYÜKÇEKMECE","ÇATALCA","ÇEKMEKÖY","ESENLER","ESENYURT","EYÜPSULTAN",
    "FATİH","GAZİOSMANPAŞA","GÜNGÖREN","KADIKÖY","KAĞITHANE","KARTAL",
    "KÜÇÜKÇEKMECE","MALTEPE","PENDİK","SANCAKTEPE","SARIYER","SİLİVRİ",
    "SULTANBEYLİ","SULTANGAZİ","ŞİLE","ŞİŞLİ","TUZLA","ÜMRANİYE","ÜSKÜDAR",
    "ZEYTİNBURNU"
]


def district_from_address_strong(address: str) -> str:
    """
<<<<<<< HEAD
    Adres label içinde İstanbul ilçelerinden biri geçiyorsa onu döndürür.
    Geçmiyorsa ilk virgül öncesini döndürmeyi dener.
=======
     adres labelin içinde eğer istanbulun ilçerlerinden biri geçerse onu döndüdrüyor.
    geçmezse ilk virgül öncesini döndürmeyi deniyor
>>>>>>> b345ac7 (Streamlit frontend implementation and route-based fuel calculation)
    """
    if not address:
        return ""
    up = address.upper()

    for d in ISTANBUL_DISTRICTS:
        if d in up:
            return d

<<<<<<< HEAD
    # fallback: ilk parça
=======
    # fallback burası ilk parçamız
>>>>>>> b345ac7 (Streamlit frontend implementation and route-based fuel calculation)
    first = address.split(",")[0].strip().upper()
    return first or ""


def reverse_geocode_ors(client, coord):
    """
<<<<<<< HEAD
    ORS Pelias reverse -> (label, district_guess)
=======
    bu kısımda ors pelias reverse geocoding kullanılarak koordinatlardan okunabilir adres ve ilçe bilgisi üretiliyo
    label( koordinatların karşılığı olan insan tarafından okunabilir bir adres bilgisi bunu unutma)(ekranda anlamlı bir adres olarak göstermek) (label)
    district_guess( aynı reverse geocoding çıktısından ilçe biligisinin tahmin edilmesi)(yakıt fiyatı ve hesaplamalarda kullanılmak üzere ilçe bilgisini otomatik tahmin etmek)(district_guess)
>>>>>>> b345ac7 (Streamlit frontend implementation and route-based fuel calculation)
    """
    try:
        resp = client.pelias_reverse(point={"lon": coord[0], "lat": coord[1]})
        feats = resp.get("features") or []
        if not feats:
            return "", ""

        props = feats[0].get("properties") or {}
        label = (props.get("label") or "").strip()

        district = (
            props.get("borough")
            or props.get("localadmin")
            or props.get("county")
            or props.get("locality")
            or props.get("neighbourhood")
            or ""
        )
        district = (district or "").strip().upper()

        if not district and label:
            district = district_from_address_strong(label)

        return label, district
    except Exception:
        return "", ""


def reverse_geocode_nominatim(coord):
    """
<<<<<<< HEAD
    Nominatim reverse -> (label, district_guess)
    Nominatim User-Agent ister.
=======
    reverse geocode haritadan seçilen koordinatların adres ve ilçe gibi anlamlı bilgilere dönüştürlümesidir!!!
    Nominatim reverse -> (label, district_guess)
    Nominatim User-Agent ister.
    bu bölümde openstreetmapin nominatim servisiyle reverse geocodding yapılıyor.
    servisin çalışabilmesi için http isteğinde user agent bilgisi gönderilmesi zorunlu (BUNU UNUTMA)
    burasının önemli olmasının sebebi(user agent gönderilmezse nominatim istediiği cevabı alamaz, uygulama adres içlçe bilgisinide alamaz.)
>>>>>>> b345ac7 (Streamlit frontend implementation and route-based fuel calculation)
    """
    lon, lat = coord[0], coord[1]
    url = "https://nominatim.openstreetmap.org/reverse"
    params = {
        "format": "jsonv2",
        "lat": lat,
        "lon": lon,
        "zoom": 18,
        "addressdetails": 1,
        "accept-language": "tr",
    }
    headers = {"User-Agent": "FuelCalculatorProject/1.0 (local-dev)"}

    try:
        r = requests.get(url, params=params, headers=headers, timeout=10)
        if r.status_code != 200:
            return "", ""
        j = r.json()

        label = (j.get("display_name") or "").strip()
        addr = j.get("address") or {}

        district = (
            addr.get("city_district")
            or addr.get("district")
            or addr.get("borough")
            or addr.get("suburb")
            or addr.get("county")
            or addr.get("town")
            or ""
        )
        district = (district or "").strip().upper()

        if not district and label:
            district = district_from_address_strong(label)

        return label, district
    except Exception:
        return "", ""


def reverse_geocode_best(ors_client, coord):
    """
<<<<<<< HEAD
    Önce ORS reverse, olmazsa Nominatim reverse.
=======
    Önce ORS reverse, olmazsa Nominatim reverse.(adres bilgisini almak için önce orsreverse geocdoing kullanılır,
    eğer başarısız olursa yedek olara k nominatimreverse geocoda geçiliyo)
>>>>>>> b345ac7 (Streamlit frontend implementation and route-based fuel calculation)
    """
    label, district = reverse_geocode_ors(ors_client, coord)
    if label or district:
        return label, district
    return reverse_geocode_nominatim(coord)


@app.route("/")
def index():
    return render_template("index.html")


<<<<<<< HEAD
# route_data.json ve result_data.json'ı HTTP ile servis et
=======
# route_data.json ve result_data.json'ı HTTP ile servis et yani dosyayı diskte tut sonra http üzerinden okunur yap
>>>>>>> b345ac7 (Streamlit frontend implementation and route-based fuel calculation)
@app.get("/route_data.json")
def serve_route_data():
    if not os.path.exists(ROUTE_JSON_PATH):
        return jsonify({"error": "route_data.json henüz oluşturulmadı"}), 404
    return send_file(ROUTE_JSON_PATH, mimetype="application/json")


@app.get("/result_data.json")
def serve_result_data():
    if not os.path.exists(RESULT_JSON_PATH):
        return jsonify({"error": "result_data.json henüz oluşturulmadı"}), 404
    return send_file(RESULT_JSON_PATH, mimetype="application/json")


@app.route("/api/route", methods=["POST"])
def api_route():
    """
<<<<<<< HEAD
    1) address ile: { "start_address": "...", "end_address": "..." }
    2) coord ile:   { "start_coord": [lon,lat], "end_coord": [lon,lat] }
=======
    1)kullanıcı adres girerse  backend bu adresleri önce geocod ile çözer sonra bu koordinatlar üzerinden rota hesapşar
    2) coordinant girerse kordinatlar doğrudan kullanılır ekstra olarak geocod adımı gerekmiyo daha hızlı olur yani
>>>>>>> b345ac7 (Streamlit frontend implementation and route-based fuel calculation)
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

<<<<<<< HEAD
    # ✅ KRİTİK FIX: start/end address + district'i garanti doldur (ORS -> Nominatim fallback)
    start_label, start_dist = reverse_geocode_best(ors_client, start_coord)
    end_label, end_dist = reverse_geocode_best(ors_client, end_coord)

    # route_service bir şey döndürürse onu tercih et, değilse reverse geocode / input address
=======
    # bu düzeltme ors başarırısz olsa bile nominatim yedeği sayesinde başlangıç-bitiş adresi ve ilçe bilgilerini her zaman doldurmasını garanti ediyo.
    start_label, start_dist = reverse_geocode_best(ors_client, start_coord)
    end_label, end_dist = reverse_geocode_best(ors_client, end_coord)

    #  adres bilgisi için önce route servisinin sonucu tercih ediliyo eğer başarısız olursa reverse geocoding veya kullanıcın girdiği adres kullanıyo
>>>>>>> b345ac7 (Streamlit frontend implementation and route-based fuel calculation)
    start_addr_final = (route_data.get("start_address") or start_address or start_label or "").strip()
    end_addr_final = (route_data.get("end_address") or end_address or end_label or "").strip()

    start_district_final = (start_dist or district_from_address_strong(start_addr_final) or "").strip().upper()
    end_district_final = (end_dist or district_from_address_strong(end_addr_final) or "").strip().upper()

<<<<<<< HEAD
    # route_data.json -> mapProject içine yaz
=======
    # route_data.json > mapproject içine yaz
>>>>>>> b345ac7 (Streamlit frontend implementation and route-based fuel calculation)
    try:
        to_save = {
            "start_address": start_addr_final,
            "end_address": end_addr_final,
            "start_district": start_district_final,
            "end_district": end_district_final,
            "start_coord": start_coord,
            "end_coord": end_coord,
            "route_summery": route_data.get("route_summery"),
            "route_geometry": route_data.get("route_geometry"),
            "_saved_at": datetime.now().isoformat(timespec="seconds"),
        }
        save_json(ROUTE_JSON_PATH, to_save)
        print("✅ route_data.json yazıldı ->", ROUTE_JSON_PATH)
    except Exception as e:
        print("⚠ route_data.json kaydedilemedi:", e)

    return jsonify({
        "start_coord": start_coord,
        "end_coord": end_coord,
        "route_summery": route_data.get("route_summery"),
        "route_geometry": route_data.get("route_geometry"),
        "start_address": start_addr_final,
        "end_address": end_addr_final,
        "start_district": start_district_final,
        "end_district": end_district_final,
    })


@app.route("/api/calculate", methods=["POST"])
def api_calculate():
    data = request.get_json(force=True)

    summary = data.get("route_summery")
    vehicle = data.get("vehicle") or {}
    fuel_type = (data.get("fuel_type") or "benzin").strip().lower()

    if fuel_type not in ALLOWED_FUEL_TYPES:
        return jsonify({"error": f"Geçersiz fuel_type: '{fuel_type}'. İzin verilenler: {', '.join(sorted(ALLOWED_FUEL_TYPES))}"}), 400

    # route_summery yoksa son çare route_data.json'dan al
    if not summary:
        rd = read_json(ROUTE_JSON_PATH) or {}
        summary = rd.get("route_summery")

    if not summary:
        return jsonify({"error": "route_summery zorunlu."}), 400

    distance_km = summary.get("total_distance_km")
    urban_percent = summary.get("urban_percent")
    interurban_percent = summary.get("interurban_percent")

    if distance_km is None or urban_percent is None or interurban_percent is None:
        return jsonify({"error": "route_summery alanları eksik: total_distance_km / urban_percent / interurban_percent"}), 400

    city_ratio = float(urban_percent) / 100.0
    highway_ratio = float(interurban_percent) / 100.0

<<<<<<< HEAD
    # district: önce payload, sonra payload start_address, sonra route_data.json
=======
    # ilçe bilgisi öncelikle frontend payloadından alınıyor eğer yoksa adresten çıkarılıyor eğer o da yoksa daha önce üretilmiş route verisi kullanıluyo
>>>>>>> b345ac7 (Streamlit frontend implementation and route-based fuel calculation)
    start_district = (data.get("start_district") or "").strip().upper()
    start_address = (data.get("start_address") or "").strip()

    if not start_district and start_address:
        start_district = district_from_address_strong(start_address)

    if not start_district:
        rd = read_json(ROUTE_JSON_PATH) or {}
        start_district = (rd.get("start_district") or "").strip().upper()
        if not start_district:
            start_address = start_address or (rd.get("start_address") or "").strip()
            if start_address:
                start_district = district_from_address_strong(start_address)

    if not start_district:
        return jsonify({"error": "start_district veya start_address gerekli (route_data.json içinde de yok)."}), 400

    make = (vehicle.get("make") or "").strip()
    model = (vehicle.get("model") or "").strip()
    year = vehicle.get("year")

    if not make or not model or year is None or str(year).strip() == "":
        return jsonify({"error": "vehicle(make, model, year) eksik."}), 400

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
        msg = str(e)
        if "İlçe" in msg or "ilçe" in msg or "district" in msg:
            msg = (
                f"{msg} | Not: Yakıt fiyatı sadece İstanbul ilçeleri için destekleniyor. "
                f"Gönderilen ilçe='{start_district}'."
            )
        return jsonify({"error": msg}), 400

    # result_data.json -> mapProject içine yaz
    try:
        result_to_save = json.loads(json.dumps(result, ensure_ascii=False, default=str))
        result_to_save["_saved_at"] = datetime.now().isoformat(timespec="seconds")

        with open(RESULT_JSON_PATH, "w", encoding="utf-8") as f:
            json.dump(result_to_save, f, ensure_ascii=False, indent=2)

        print("✅ result_data.json yazıldı ->", RESULT_JSON_PATH)
    except Exception as e:
        print(f"⚠ result_data.json kaydedilemedi: {e}")

    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True)
