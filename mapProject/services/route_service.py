#kordinatlarımızdan rota çıkarmak için kullanacağız
from openrouteservice import directions

def get_route(client, start_coord, end_coord):
    route = directions.directions(client, coordinates=[start_coord, end_coord],
         profile="driving-car",
          format="geojson")

    props = route["features"][0]["properties"]
    geom = route["features"][0]["geometry"]

    distance_km = props["segments"][0]["distance"]/1000
    distance_min = props["segments"][0]["duration"]/60

    legs = [
        {
            "from": start_coord,
            "to": end_coord,
            "distance": distance_km,
            "duration": distance_min,
        }
    ]

    return {
        "distance": distance_km,
        "duration": distance_min,
        "geometry": geom["coordinates"],
        "legs": legs
    }