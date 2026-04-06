import requests
from requests.structures import CaseInsensitiveDict
from dotenv import load_dotenv
import os
load_dotenv() 


shop_api= os.getenv("GEOAPIFY_API_KEY")
print("API KEY:", shop_api)

def search_shop(user_location):
    headers = CaseInsensitiveDict()
    headers["Accept"] = "application/json"

    #step 1 : get lat and long of user location
    api_location_trans = f"https://api.geoapify.com/v1/geocode/search?text={user_location}&apiKey={shop_api}"

    resp = requests.get(api_location_trans, headers=headers)
    if resp.status_code != 200:
        return f"Error: Unable to fetch location data for {user_location}"
    data = resp.json()
    if not data.get("features"):
        return f"Error: No location data found for {user_location}"

    lat = data["features"][0]["properties"]["lat"]
    lon = data["features"][0]["properties"]["lon"]

    #step 2 : search for shops near the lat and long
    api_get_shop= f"https://api.geoapify.com/v2/places?categories=catering.restaurant&filter=circle:{lon},{lat},1000&limit=20&apiKey={shop_api}"
    resp = requests.get(api_get_shop, headers=headers)
    if resp.status_code != 200:
        return f"Error: Unable to fetch shop data for location {user_location}"
    data = resp.json()
    if not data.get("features"):
        return f"Error: No shop data found for location {user_location}"
    shops = []
    for feature in data["features"]:
        shop_info = {
            "name": feature["properties"].get("name", "N/A"),
            "address": feature["properties"].get("formatted", "N/A")
        }
        shops.append(shop_info)
    return shops

