# streamlit_app.py
import os
import sys
import json
from datetime import datetime

import requests
import streamlit as st
import folium
from streamlit_folium import st_folium
from openrouteservice import Client
import pandas as pd

# =========================================================
# Ensure project root is on sys.path (for internal imports)
# =========================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# Project imports
from mapProject.services.route_service import get_route
from data_science.route_analysis import estimate_trip_from_map_payload

# =========================================================
# Paths
# =========================================================
ROUTE_JSON_PATH = os.path.join(BASE_DIR, "route_data.json")
RESULT_JSON_PATH = os.path.join(BASE_DIR, "result_data.json")

# =========================================================
# Constants
# =========================================================
ISTANBUL_DISTRICTS = [
    "ADALAR","ARNAVUTKÖY","ATAŞEHİR","AVCILAR","BAĞCILAR","BAHÇELİEVLER","BAKIRKÖY",
    "BAŞAKŞEHİR","BAYRAMPAŞA","BEŞİKTAŞ","BEYKOZ","BEYLİKDÜZÜ","BEYOĞLU","BÜYÜKÇEKMECE",
    "ÇATALCA","ÇEKMEKÖY","ESENLER","ESENYURT","EYÜPSULTAN","FATİH","GAZİOSMANPAŞA","GÜNGÖREN",
    "KADIKÖY","KAĞITHANE","KARTAL","KÜÇÜKÇEKMECE","MALTEPE","PENDİK","SANCAKTEPE","SARIYER",
    "SİLİVRİ","SULTANBEYLİ","SULTANGAZİ","ŞİLE","ŞİŞLİ","TUZLA","ÜMRANİYE","ÜSKÜDAR","ZEYTİNBURNU"
]
ALLOWED_FUEL_TYPES = {"benzin", "motorin", "lpg"}

# =========================================================
# Helpers: JSON read/write
# =========================================================
def read_json(path: str):
    try:
        if not os.path.exists(path):
            return None
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None

def write_json(path: str, data: dict):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# =========================================================
# Helpers: Fuel normalization
# =========================================================
def normalize_fuel_type(raw: str) -> str:
    s = (raw or "").strip().lower()
    if s in ALLOWED_FUEL_TYPES:
        return s
    if "benz" in s:
        return "benzin"
    if "mot" in s or "diz" in s:
        return "motorin"
    if "lpg" in s:
        return "lpg"
    return "benzin"

# =========================================================
# Helpers: District extraction fallback from address string
# =========================================================
def district_from_address_strong(address: str) -> str:
    """
    If an Istanbul district name appears in the address string, return it.
    Otherwise, fallback to the first comma-separated segment.
    """
    if not address:
        return ""
    up = address.upper()
    for d in ISTANBUL_DISTRICTS:
        if d in up:
            return d
    return address.split(",")[0].strip().upper()

# =========================================================
# Reverse geocode: ORS -> Nominatim fallback
# =========================================================
def reverse_geocode_ors(client: Client, coord):
    """
    coord: [lon, lat]
    returns: (label, district_guess)
    """
    try:
        resp = client.pelias_reverse(point={"lon": coord[0], "lat": coord[1]})
        feats = (resp or {}).get("features", [])
        if not feats:
            return "", ""
        props = feats[0].get("properties", {}) or {}
        label = (props.get("label") or "").strip()

        district = (
            props.get("borough")
            or props.get("localadmin")
            or props.get("locality")
            or props.get("neighbourhood")
            or ""
        )
        return label, (district or "").strip().upper()
    except Exception:
        return "", ""

def reverse_geocode_nominatim(coord):
    """
    coord: [lon, lat]
    returns: (label, district_guess)
    """
    try:
        url = "https://nominatim.openstreetmap.org/reverse"
        params = {
            "format": "jsonv2",
            "lat": coord[1],
            "lon": coord[0],
            "zoom": 18,
            "addressdetails": 1
        }
        headers = {"User-Agent": "fuel-calculator-streamlit/1.0"}
        r = requests.get(url, params=params, headers=headers, timeout=10)
        if r.status_code != 200:
            return "", ""
        data = r.json() or {}
        label = (data.get("display_name") or "").strip()
        addr = data.get("address", {}) or {}
        district = (
            addr.get("city_district")
            or addr.get("district")
            or addr.get("borough")
            or addr.get("suburb")
            or addr.get("town")
            or addr.get("city")
            or ""
        )
        return label, (district or "").strip().upper()
    except Exception:
        return "", ""

def reverse_geocode_best(ors_client: Client, coord):
    label, district = reverse_geocode_ors(ors_client, coord)
    if label or district:
        return label, district
    return reverse_geocode_nominatim(coord)

# =========================================================
# Vehicles CSV (for MAKE/MODEL/YEAR dropdowns)
# =========================================================
@st.cache_data
def load_vehicles_df():
    path = os.path.join(BASE_DIR, "data", "vehicles.csv")
    df = pd.read_csv(path)

    df["MAKE"] = df["MAKE"].astype(str).str.strip()
    df["MODEL"] = df["MODEL"].astype(str).str.strip()
    df["YEAR"] = pd.to_numeric(df["YEAR"], errors="coerce").fillna(0).astype(int)

    df = df[df["YEAR"] > 0].copy()
    return df

# =========================================================
# Page config (English UI)
# =========================================================
st.set_page_config(page_title="Fuel Calculator (Streamlit)", layout="wide")
st.title("Fuel Calculator (Streamlit Frontend)")
st.write("Select start/end on the map → calculate the route → choose vehicle & fuel → compute trip fuel and cost.")

# =========================================================
# ORS API key
# =========================================================
ORS_API_KEY = os.environ.get("ORS_API_KEY", "").strip()
if not ORS_API_KEY:
    st.error("ORS_API_KEY is not set. PowerShell: $env:ORS_API_KEY='...'; then run again.")
    st.stop()

ors_client = Client(key=ORS_API_KEY)

# =========================================================
# Session State init
# =========================================================
if "start_coord" not in st.session_state:
    st.session_state.start_coord = None  # [lon, lat]
if "end_coord" not in st.session_state:
    st.session_state.end_coord = None
if "route_data" not in st.session_state:
    st.session_state.route_data = None

# Persist dropdown selections
if "sel_year" not in st.session_state:
    st.session_state.sel_year = None
if "sel_make" not in st.session_state:
    st.session_state.sel_make = None
if "sel_model" not in st.session_state:
    st.session_state.sel_model = None

# =========================================================
# Layout
# =========================================================
left, right = st.columns([1.2, 0.8], gap="large")

# =========================================================
# LEFT: Map & Route
# =========================================================
with left:
    st.subheader("1) Map Selection")

    click_mode = st.radio("Click mode", ["Select START", "Select END"], horizontal=True)

    # Istanbul center
    m = folium.Map(location=[41.0082, 28.9784], zoom_start=11, control_scale=True)

    # Markers
    if st.session_state.start_coord:
        folium.Marker(
            location=[st.session_state.start_coord[1], st.session_state.start_coord[0]],
            popup="START",
            icon=folium.Icon(icon="play"),
        ).add_to(m)

    if st.session_state.end_coord:
        folium.Marker(
            location=[st.session_state.end_coord[1], st.session_state.end_coord[0]],
            popup="END",
            icon=folium.Icon(icon="stop"),
        ).add_to(m)

    # Route polyline (route_geometry is a LIST [[lon,lat], ...])
    if st.session_state.route_data:
        coords = st.session_state.route_data.get("route_geometry") or []
        if coords:
            latlon = [[c[1], c[0]] for c in coords]  # [lon,lat] -> [lat,lon]
            folium.PolyLine(latlon).add_to(m)

    map_out = st_folium(m, height=520, width=None)

    clicked = (map_out or {}).get("last_clicked")
    if clicked:
        lon = float(clicked["lng"])
        lat = float(clicked["lat"])
        if click_mode == "Select START":
            st.session_state.start_coord = [lon, lat]
            st.session_state.route_data = None
        else:
            st.session_state.end_coord = [lon, lat]
            st.session_state.route_data = None

    b1, b2, b3 = st.columns([1, 1, 1])
    with b1:
        if st.button("Clear START"):
            st.session_state.start_coord = None
            st.session_state.route_data = None
    with b2:
        if st.button("Clear END"):
            st.session_state.end_coord = None
            st.session_state.route_data = None
    with b3:
        if st.button("Reset ALL"):
            st.session_state.start_coord = None
            st.session_state.end_coord = None
            st.session_state.route_data = None

    st.divider()
    st.subheader("2) Route Calculation")

    if st.button("Calculate Route"):
        if not st.session_state.start_coord or not st.session_state.end_coord:
            st.error("Please select both START and END on the map.")
        else:
            route_resp = get_route(ors_client, st.session_state.start_coord, st.session_state.end_coord) or {}

            # Reverse geocode (keep original labels; do not translate addresses)
            start_label, start_dist = reverse_geocode_best(ors_client, st.session_state.start_coord)
            end_label, end_dist = reverse_geocode_best(ors_client, st.session_state.end_coord)

            # District fallback from address text
            if not start_dist and start_label:
                start_dist = district_from_address_strong(start_label)
            if not end_dist and end_label:
                end_dist = district_from_address_strong(end_label)

            route_summery = (route_resp or {}).get("route_summery") or {}
            route_geometry = (route_resp or {}).get("route_geometry") or {}
            geometry_list = (route_geometry or {}).get("geometry") or []  # LIST

            st.session_state.route_data = {
                "start_coord": st.session_state.start_coord,
                "end_coord": st.session_state.end_coord,
                "route_summery": route_summery,
                "route_geometry": geometry_list,  # LIST
                "start_address": start_label or "",
                "end_address": end_label or "",
                "start_district": (start_dist or "").strip().upper(),
                "end_district": (end_dist or "").strip().upper(),
                "_saved_at": datetime.now().isoformat(timespec="seconds"),
            }

            write_json(ROUTE_JSON_PATH, st.session_state.route_data)
            st.success("Route calculated and saved to route_data.json.")

# =========================================================
# RIGHT: Vehicle & Calculate
# =========================================================
with right:
    st.subheader("Vehicle and Trip Cost")

    # =========================
    # DASHBOARD: Route overview (auto)
    # =========================
    st.markdown("### Route Dashboard")

    if st.session_state.route_data and st.session_state.route_data.get("route_summery"):
        s = st.session_state.route_data["route_summery"] or {}

        dist_km = s.get("total_distance_km") or s.get("distance_km") or 0
        dur_min = s.get("total_duration_min") or s.get("duration_min") or 0

        try:
            dist_km = float(dist_km)
        except Exception:
            dist_km = 0.0

        try:
            dur_min = float(dur_min)
        except Exception:
            dur_min = 0.0

        hours = int(dur_min // 60)
        mins = int(round(dur_min % 60))

        c1, c2, c3 = st.columns(3)
        c1.metric("Distance", f"{dist_km:.2f} km")
        c2.metric("Duration", f"{hours} h {mins} min" if dur_min >= 60 else f"{mins} min")
        c3.metric("Avg speed (est.)", f"{(dist_km / (dur_min/60)):.1f} km/h" if dur_min > 0 else "-")

        # Compact route meta (keep addresses as-is)
        with st.expander("Route details", expanded=False):
            st.write("**Start address:**", st.session_state.route_data.get("start_address") or "-")
            st.write("**End address:**", st.session_state.route_data.get("end_address") or "-")
            st.write("**Start district:**", st.session_state.route_data.get("start_district") or "-")
            st.write("**End district:**", st.session_state.route_data.get("end_district") or "-")
    else:
        st.info("No route yet. Select START/END and click 'Calculate Route'.")

    vehicles_df = load_vehicles_df()

    # YEAR dropdown
    year_options = sorted(vehicles_df["YEAR"].unique().tolist())
    if not year_options:
        st.error("Could not read YEAR options from data/vehicles.csv.")
        st.stop()

    if st.session_state.sel_year is None:
        st.session_state.sel_year = 2000 if 2000 in year_options else year_options[0]

    year = st.selectbox(
        "Year",
        year_options,
        index=year_options.index(st.session_state.sel_year) if st.session_state.sel_year in year_options else 0,
        key="ui_year"
    )
    st.session_state.sel_year = year

    # MAKE dropdown filtered by YEAR
    df_year = vehicles_df[vehicles_df["YEAR"] == year]
    make_options = sorted(df_year["MAKE"].unique().tolist())
    if not make_options:
        st.error("No MAKE found for the selected YEAR. Please choose another year.")
        st.stop()

    if st.session_state.sel_make is None or st.session_state.sel_make not in make_options:
        st.session_state.sel_make = make_options[0]

    make = st.selectbox(
        "Make",
        make_options,
        index=make_options.index(st.session_state.sel_make) if st.session_state.sel_make in make_options else 0,
        key="ui_make"
    )
    st.session_state.sel_make = make

    # MODEL dropdown filtered by YEAR+MAKE
    df_make = df_year[df_year["MAKE"] == make]
    model_options = sorted(df_make["MODEL"].unique().tolist())
    if not model_options:
        st.error("No MODEL found for the selected YEAR and MAKE. Please choose another combination.")
        st.stop()

    if st.session_state.sel_model is None or st.session_state.sel_model not in model_options:
        st.session_state.sel_model = model_options[0]

    model = st.selectbox(
        "Model",
        model_options,
        index=model_options.index(st.session_state.sel_model) if st.session_state.sel_model in model_options else 0,
        key="ui_model"
    )
    st.session_state.sel_model = model

    # Fuel dropdown (kept as Turkish keys for backend compatibility; UI label is English)
    fuel_raw = st.selectbox("Fuel type", ["benzin", "motorin", "lpg"], index=0)
    fuel_type = normalize_fuel_type(fuel_raw)

    st.divider()
    st.subheader("District Override (Optional)")

    auto_district = ""
    auto_address = ""
    if st.session_state.route_data:
        auto_district = (st.session_state.route_data.get("start_district") or "").strip().upper()
        auto_address = (st.session_state.route_data.get("start_address") or "").strip()

    st.write("Detected START address:", auto_address or "-")
    st.write("Detected START district:", auto_district or "-")

    use_override = st.checkbox("Manually override district")
    chosen_district = auto_district
    if use_override:
        default_idx = ISTANBUL_DISTRICTS.index(auto_district) if auto_district in ISTANBUL_DISTRICTS else 0
        chosen_district = st.selectbox("Select Istanbul district", ISTANBUL_DISTRICTS, index=default_idx)

    st.divider()
    st.subheader("3) Calculate Fuel & Cost")

    if st.button("Calculate Trip"):
        # Ensure route summary exists (session_state first, then route_data.json)
        route_payload = st.session_state.route_data or read_json(ROUTE_JSON_PATH) or {}
        summary = route_payload.get("route_summery")

        if not summary:
            st.error("Route summary is missing. Please calculate the route first.")
            st.stop()

        # Final district
        district_final = (chosen_district or "").strip().upper()
        if not district_final and route_payload.get("start_address"):
            district_final = district_from_address_strong(route_payload.get("start_address"))

        if not district_final:
            st.error("Start district could not be determined. Please use district override and select a district.")
            st.stop()

        # Build map_payload expected by estimate_trip_from_map_payload()
        dist_km = summary.get("total_distance_km") or summary.get("distance_km") or 0
        try:
            dist_km = float(dist_km)
        except Exception:
            dist_km = 0.0

        map_payload = {
            "distance_km": dist_km,
            "start": {"district": district_final},
        }

        try:
            result = estimate_trip_from_map_payload(
                map_payload=map_payload,
                make=make,
                model=model,
                year=int(year),
                fuel_type=fuel_type,
            )
        except Exception as e:
            st.error(f"Calculation error: {e}")
            st.stop()

        # Save JSON for debugging / traceability (but do not display JSON in UI)
        result_to_save = dict(result) if isinstance(result, dict) else {"result": result}
        result_to_save["_saved_at"] = datetime.now().isoformat(timespec="seconds")
        write_json(RESULT_JSON_PATH, result_to_save)

        st.success("Calculation completed.")

        if not isinstance(result, dict):
            st.write(result)
        else:
            # Flexible key mapping (depending on your implementation)
            fuel_used = result.get("fuel_used", result.get("total_fuel_l", 0))
            total_cost = result.get("total_cost", result.get("cost_tl", 0))
            mixed_cons = result.get("mixed_consumption", result.get("consumption_l_per_100km", 0))

            try:
                fuel_used = float(fuel_used)
            except Exception:
                fuel_used = 0.0
            try:
                total_cost = float(total_cost)
            except Exception:
                total_cost = 0.0
            try:
                mixed_cons = float(mixed_cons)
            except Exception:
                mixed_cons = 0.0

            m1, m2, m3 = st.columns(3)
            m1.metric("Total fuel used", f"{fuel_used:.2f} L")
            m2.metric("Total cost", f"{total_cost:.2f} TL")
            m3.metric("Average consumption", f"{mixed_cons:.2f} L/100km")

            st.write("**Vehicle:**", f"{make} {model} ({year})")
            st.write("**Fuel type:**", fuel_type)
            st.write("**Start district:**", district_final)

            # Optional details if present
            extra_rows = []
            for key, label in [
                ("fuel_price_tl_per_l", "Fuel price (TL/L)"),
                ("distance_km", "Distance (km)"),
                ("trip_duration_min", "Duration (min)"),
            ]:
                if key in result:
                    extra_rows.append((label, result.get(key)))

            if extra_rows:
                st.divider()
                st.write("Details")
                for label, val in extra_rows:
                    st.write(f"- {label}: {val}")


