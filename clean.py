import requests
from math import radians, sin, cos, sqrt, atan2
import datetime

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


def convert_price(price_str):
    price_str = price_str.replace(" tỷ", "").replace(",", ".")
    return float(price_str) * 1000000000

# Hàm chuyển đổi diện tích
def convert_area(area_str):
    return float(area_str.replace(" m²", ""))

# Hàm chuyển đổi ngày
def convert_date(date_str):
    return datetime.strptime(date_str, "%d/%m/%Y")

# Hàm tính khoảng cách Haversine
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Bán kính Trái Đất (km)
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c



# Ví dụ sử dụng
address = " Đông Anh, Hà Nội"
coords = geocode(address)

if coords:
    lat, lon = coords
    distance = haversine(lat, lon, hoan_kiem_lat, hoan_kiem_lon)
    print(f"Khoảng cách từ {address} đến Hồ Hoàn Kiếm: {distance:.2f} km")
else:
    print(f"Không thể tìm tọa độ cho địa chỉ: {address}")