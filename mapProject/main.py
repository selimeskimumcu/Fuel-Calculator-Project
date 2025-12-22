#kullanıcıdan adres alıcaz, service classlarımızı çağırıcak, json üretecek
import json
from openrouteservice import Client
from services.geocode_service import find_coordinates
from services.route_service import get_route

def ask_address(prompt: str):
    raw = input(prompt).strip()
    return raw

def main():
    client = Client(key="eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6ImE3MDU3OTAzNjVjZDQwOTU4MmE3YmY0NzQ3MzE2MjFjIiwiaCI6Im11cm11cjY0In0=")

    print("\n=== ROUTE CALCULATOR  ===\n")

    start_address = ask_address("Enter start address: ")
    end_address = ask_address("Enter end address: ")

    print("\nResolving coordinates...")

    start_coord = find_coordinates(client, start_address)
    end_coord  = find_coordinates(client, end_address)

    if not start_coord:
        print(f"\n[ERROR] Could not geocode start address:\n  {start_address}")
        return

    if not end_coord:
        print(f"\n[ERROR] Could not geocode end address:\n  {end_address}")
        return

    print(f"Start coord: {start_coord}")
    print(f"End coord  : {end_coord}")


    print("\nRequesting route...")

    route_data = get_route(client, start_coord, end_coord)

    if not route_data:
        print("Route data was not found.")
        return


    output = {
        "start_address": start_address,
        "end_address": end_address,
        "start_coord": start_coord,
        "end_coord": end_coord,
        **route_data
    }

    with open("route_data.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=4, ensure_ascii=False)

    print("\nSUCCESS ")
    print("Route data saved to route_data.json \n")


if __name__ == "__main__":
    main()