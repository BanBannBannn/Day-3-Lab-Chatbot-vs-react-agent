from dotenv import load_dotenv
import os
import requests

load_dotenv()

API_KEY =os.environ['VIETMAP_API_KEY']

def _get_coords(address):
    url = f"https://maps.vietmap.vn/api/search/v4?api-version=1.1&apikey={API_KEY}&text={address}"
    response = requests.get(url).json()
    # VietMap returns a list of results; we take the first one
    ref_id = response[0]['ref_id']
    url_place = f"https://maps.vietmap.vn/api/place/v4?apikey={API_KEY}&refid={ref_id}"
    response = requests.get(url_place).json()

    return {
        "lat": response['lat'],
        "lng": response['lng']
    }


def get_distance_between_two_addresses(addr1:str, addr2:str)->dict[str, float]|str:
    r"""Tìm khoảng cách giữa hai địa chỉ
    Args:
        addr1 (str): địa chỉ thứ nhất
        addr1 (str): địa chỉ thứ hai
    Returns:
        A dictionary contains two keys:
            `distance_km`: khoảng cách di chuyển bằng ô tô
            `time_mins`: Thời gian di chuyển ngắn nhất theo phút
        hoặc string nếu lõi
    """
    coords1 = _get_coords(addr1)
    coords2 = _get_coords(addr2)
    
    if coords1 and coords2:
        # Route API request
        route_url = (
            f"https://maps.vietmap.vn/api/route?api-version=1.1&apikey={API_KEY}"
            f"&point={coords1['lat']},{coords1['lng']}&point={coords2['lat']},{coords2['lng']}"
            f"&vehicle=car"
        )
        res = requests.get(route_url).json()
        
        # Distance is returned in meters
        distance_meters = res['paths'][0]['distance']
        time_ms = res['paths'][0]['time']
        
        return {
            "distance_km": distance_meters / 1000,
            "time_mins": time_ms / (1000 * 60)
        }
    return "Location not found."

