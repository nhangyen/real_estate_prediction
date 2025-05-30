import requests,time,re
from math import radians, sin, cos, sqrt, atan2
from pymongo import MongoClient

distance_cache= {}

# Tọa độ Hồ Hoàn Kiếm
hoan_kiem_lat = 21.0285  # Latitude
hoan_kiem_lon = 105.8542  # Longitude

# Hàm geocoding sử dụng OpenStreetMap Nominatim
def geocode(address):
    url = f"https://nominatim.openstreetmap.org/search?format=json&q={address}"
    headers = {
        "User-Agent": "MyRealEstateApp/1.0 (your.email@example.com)"  # Thay bằng thông tin của bạn
    }
    
    url = f"https://nominatim.openstreetmap.org/search?format=json&q={address}"
    response = requests.get(url, headers=headers)
    data = response.json()
    if data:
        return float(data[0]['lat']), float(data[0]['lon'])
    return None

# Hàm tính khoảng cách Haversine
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Bán kính Trái Đất (km)
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c

def get_distance(address):
    # Kiểm tra trong cache trước
    # if address in distance_cache:
    #     print(f"Lấy khoảng cách từ cache cho {address}: {distance_cache[address]:.2f} km")
    #     return distance_cache[address]
    
    # Nếu không có trong cache, gọi API
    coords = geocode(address)
    if coords:
        lat, lon = coords
        distance = haversine(lat, lon, hoan_kiem_lat, hoan_kiem_lon)
        # Lưu vào cache
        # distance_cache[address] = distance
        # print(f"Đã thêm vào cache khoảng cách cho {address}: {distance:.2f} km")
        # time.sleep(1)  # Đợi 1 giây để tránh vượt giới hạn API
        return distance
    return None


def extract_floor(project_name):
    if "tầng" in project_name.lower():
        floors = re.findall(r'(\d+)\s*tầng', project_name.lower())
        floors = int(floors[0]) if floors else None
        if floors != None:
            return floors
    if "đất" in project_name.lower():
        return 0
    return 1

# client = MongoClient('mongodb://localhost:27017/')
# db = client['real_estate']
# collection = db['properties2']

# for item in collection.find():
#     address = item.get("location")
#     if address:
#         distance = get_distance(address)
#         if distance is not None:
#             collection.update_one(
#                 {"_id": item["_id"]},
#                 {"$set": {"distance_to_hoan_kiem": distance}}
#             )
#             print(f"Đã cập nhật khoảng cách cho {address}: {distance:.2f} km")


        #time.sleep(1)  # Đợi 1 giây để tránh vượt giới hạn
    # project_name= item.get("project_name")
    # if project_name:
    #     collection.update_one(
    #         {"_id": item["_id"]},
    #         {"$set": {"floor":extract_floor(project_name)} }
    #     )
        # print(f"Đã cập nhật floor cho {project_name}")