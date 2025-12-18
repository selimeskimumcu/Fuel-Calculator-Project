#kullanıcıdan adres alıcaz, service classlarımızı çağırıcak, json üretecek
import json
from openrouteservice import Client
from services.geocode_service import find_coordinates
from services.route_service import get_route

API_KEY = "eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6ImE3MDU3OTAzNjVjZDQwOTU4MmE3YmY0NzQ3MzE2MjFjIiwiaCI6Im11cm11cjY0In0="

def main():
    start_point = input("Enter start address: ")
    end_point = input("Enter end address: ")

    client = Client(API_KEY)


    start_coord = find_coordinates(client, start_point)
    end_coord = find_coordinates(client, end_point)

    if start_coord is None or end_coord is None:
        print("No address found, please try again.")
        return

    print("Start coord:", start_coord)
    print("End coord:", end_coord)


    route_data = get_route(client, start_coord, end_coord)


    output = {
        "start_address": start_point,
        "end_address": end_point,
        "start_coord": start_coord,
        "end_coord": end_coord,
        **route_data
    }

    with open("output.json", "w") as f:
        json.dump(output, f, indent=4)

    print("\n✓ Route data written to output.json")

if __name__ == "__main__":
    main()
