#kordinatlarımızdan rota çıkarmak için kullanacağız
from openrouteservice import directions, convert


def get_route(client, start_coord, end_coord):

    try:
        route = directions.directions(
            client,
            coordinates=[start_coord, end_coord],
            profile="driving-car",
            format="geojson",
            instructions=True,
            instructions_format="text"
        )
    except Exception as e:
        print("Route API ERROR:", e)
        return None


    feature = route["features"][0]
    props = feature["properties"]
    geom = feature["geometry"]


    segment = props["segments"][0]


    distance_km = segment["distance"] / 1000.0
    duration_min = segment["duration"] / 60.0

    urban_km =0.0
    interurban_km = 0.0

    toll_km = 0.0


    steps = []
    for step in segment.get("steps", []):

        distance_m = step.get("distance", 0)
        duration_s = step.get("duration", 0)



        if duration_s >0:
            speed_kmh = (distance_m / 1000) / (duration_s / 3600)
        else:
            speed_kmh = 0


        if speed_kmh < 50:
            road_type = "urban"
            urban_km += distance_m / 1000
        else:
            road_type = "interurban"
            interurban_km += distance_m / 1000

        is_toll = False
        if speed_kmh >= 80 and distance_m >= 1000:
            is_toll = True
            toll_km += distance_m / 1000

        steps.append({
            "instruction": step.get("instruction"),
            "distance_m": step.get("distance"),
            "duration_s": step.get("duration"),
            "speed_kmh": round(speed_kmh,2),
            "road_type": road_type,
            "is_toll": is_toll,
            "type": step.get("type"),
            "way_points": step.get("way_points")
        })

    def percent(part,whole):
        return round((part / whole) * 100, 2) if whole > 0 else 0
    urban_percent = percent(urban_km, distance_km)
    interurban_percent = percent(interurban_km, distance_km)
    toll_percent = percent(toll_km, distance_km)

    try:
        decoded = convert.decode_polyline(geom)
        decoded_geometry = decoded.get("coordinates", [])
    except:
        decoded_geometry = geom.get("coordinates", [])



    return {
        "route_summery": {
        "total_distance_km": round(distance_km, 3),
        "total_duration_min": round(duration_min, 2),
        "urban_km": round(urban_km, 3),
        "interurban_km": round(interurban_km, 3),
        "toll_km": round(toll_km, 3),
        "urban_percent": urban_percent,
        "interurban_percent": interurban_percent,
        "toll_percent": toll_percent
        },
        "route_geometry": {
        "geometry": geom.get("coordinates", []),
        "geometry_decoded": decoded_geometry
        },
        "route_legs": [
            {
                "from": start_coord,
                "to": end_coord,
                "distance_km": round(distance_km, 3),
                "duration_min": round(duration_min, 2),
                "steps": steps
            }
        ]
    }
