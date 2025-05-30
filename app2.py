from math import radians, sin, cos, sqrt, atan2
from flask import Flask, request, jsonify, render_template
import numpy as np
import json
import os
import requests
# from pymongo import MongoClient

app2 = Flask(__name__)

# Kết nối MongoDB với error handling
# mongodb_available = False
# try:
#     client = MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=2000)
#     client.server_info()
#     db = client['real_estate']
#     history_collection = db['prediction_history']
#     mongodb_available = True
#     print("MongoDB connection successful")
# except Exception as e:
#     print(f"MongoDB connection failed: {e}")
#     print("App will run without MongoDB functionality")
#     client = None
#     db = None
#     history_collection = None

# Load model parameters
model_params_path = "output/model_params.json"
if not os.path.exists(model_params_path):
    raise FileNotFoundError(f"Model parameters not found at {model_params_path}. Run data_processing2.py first.")

with open(model_params_path, "r") as f:
    model_params = json.load(f)

coefficients = np.array(model_params["coefficients"])
intercept = model_params["intercept"]
feature_names = model_params["feature_names"]

print(f"Model loaded successfully: {len(coefficients)} coefficients, intercept={intercept}")

@app2.route('/')
def index():
    return render_template('index.html')

@app2.route('/login')
def login():
    return render_template('login.html')

@app2.route('/predict', methods=['GET', 'POST'])
def predict():
    if request.method == 'GET':
        return render_template('predict.html')
    else:
        try:
            # Nhận dữ liệu từ form
            data = request.get_json()
            if not data:
                return jsonify({"status": "error", "message": "No data received"}), 400
                
            address = str(data['address'])
            area = float(data['area'])
            bedroom = float(data['bedroom'])
            bathroom = float(data['bathroom'])
            
            # Tính khoảng cách đến Hoàn Kiếm
            try:
                distance_to_hoan_kiem = get_distance(address)
                if distance_to_hoan_kiem is None:
                    distance_to_hoan_kiem = 10.0  # Giá trị mặc định
            except Exception as e:
                print(f"Error calculating distance: {e}")
                distance_to_hoan_kiem = 10.0
                
            # Tạo feature vector
            features = np.array([area, distance_to_hoan_kiem, bedroom, bathroom])
            
            # Dự đoán giá bằng NumPy (dot product + intercept)
            predicted_price = np.dot(features, coefficients) + intercept
            
            # Lưu kết quả vào MongoDB nếu có thể
            # if mongodb_available:
            #     try:
            #         prediction_record = {
            #             "address": address,
            #             "area": area,
            #             "bedroom": bedroom,
            #             "bathroom": bathroom,
            #             "distance_to_hoan_kiem": distance_to_hoan_kiem,
            #             "predicted_price": float(predicted_price)
            #         }
            #         history_collection.insert_one(prediction_record)
                #     print(f"Prediction saved to MongoDB")
                # except Exception as e:
                #     print(f"Failed to save to MongoDB: {e}")
            
            return jsonify({
                "status": "success",
                "predicted_price": float(predicted_price),
                "distance": distance_to_hoan_kiem
            })
            
        except Exception as e:
            print(f"Error during prediction: {e}")
            return jsonify({"status": "error", "message": str(e)}), 500

hoan_kiem_lat = 21.0285  # Latitude
hoan_kiem_lon = 105.8542  # Longitude

# Hàm geocoding sử dụng OpenStreetMap Nominatim
def geocode(addr):
    url = f"https://nominatim.openstreetmap.org/search?format=json&q={addr}"
    headers = {
        "User-Agent": "MyRealEstateApp/1.0 (your.email@example.com)"  # Thay bằng thông tin của bạn
    }
    
    url = f"https://nominatim.openstreetmap.org/search?format=json&q={addr}"
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

def get_distance(addr):
    coords = geocode(addr)
    if coords:
        lat, lon = coords
        distance = haversine(lat, lon, hoan_kiem_lat, hoan_kiem_lon)
        return distance
    return None



if __name__ == '__main__':
    app2.run(debug=True)