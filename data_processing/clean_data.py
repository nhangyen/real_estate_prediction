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
        "User-Agent": "MyRealEstateApp/1.0 (abcdefg@example.com)"  # Thay bằng thông tin của bạn
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
    if address in distance_cache:
        print(f"Lấy khoảng cách từ cache cho {address}: {distance_cache[address]:.2f} km")
        return distance_cache[address]
    # Nếu không có trong cache, gọi API
    coords = geocode(address)
    if coords:
        lat, lon = coords
        distance = haversine(lat, lon, hoan_kiem_lat, hoan_kiem_lon)
        # Lưu vào cache
        distance_cache[address] = distance
        print(f"Đã thêm vào cache khoảng cách cho {address}: {distance:.2f} km")
        time.sleep(1)  # Đợi 1 giây để tránh vượt giới hạn API
        return distance
    return None

def extract_district(location):
    """Extract district name from location string"""
    if not location:
        return None
    
    return location.split(',')[0].strip()


client = MongoClient('mongodb://localhost:27017/')
db = client['real_estate']
collection = db['test']

# Statistics counters
total_records = 0
distance_updated = 0
district_updated = 0
missing_location = 0

print("Starting data processing...")

for item in collection.find():
    total_records += 1
    updates = {}
    
    address = item.get("location")
    if address:
        # Update distance if not exists
        if not item.get("distance_to_hoan_kiem"):
            distance = get_distance(address)
            if distance is not None:
                updates["distance_to_hoan_kiem"] = distance
                distance_updated += 1
                print(f"Đã cập nhật khoảng cách cho {address}: {distance:.2f} km")
        
        # Update district if not exists
        if not item.get("district"):
            district = extract_district(address)
            if district:
                updates["district"] = district
                district_updated += 1
                print(f"Đã cập nhật quận/huyện cho {address}: {district}")
    else:
        missing_location += 1
    

    project_name = item.get("project_name")
    # Apply all updates at once
    if updates:
        collection.update_one(
            {"_id": item["_id"]},
            {"$set": updates}
        )
    
    # Sleep to avoid API rate limits
    if address and not item.get("distance_to_hoan_kiem"):
        time.sleep(1)  # Đợi 1 giây để tránh vượt giới hạn

# Print final statistics
print(f"\n=== Processing Statistics ===")
print(f"Total records processed: {total_records}")
print(f"Distance updated: {distance_updated}")
print(f"District updated: {district_updated}")
print(f"Records missing location: {missing_location}")

# Print sample of distinct districts
districts = collection.distinct('district')
print(f"\nFound {len(districts)} distinct districts:")
for district in sorted(filter(None, districts)):
    count = collection.count_documents({'district': district})
    print(f"  {district}: {count} properties")

print("\nData processing completed!")