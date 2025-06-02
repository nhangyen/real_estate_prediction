from flask import Flask, request, jsonify, render_template
from pyspark.sql import SparkSession
from pyspark.ml.regression import LinearRegressionModel
from pyspark.ml.feature import VectorAssembler
from pyspark.sql.functions import lit
from pyspark.sql.types import DoubleType, StringType, StructType, StructField
import os
import requests
from math import radians, sin, cos, sqrt, atan2
# from pymongo import MongoClient
import re
import data_processing.clean_data as clean_data
app = Flask(__name__)

# Kết nối MongoDB
# client = MongoClient('mongodb://localhost:27017/')
# db = client['real_estate']
# history_collection = db['prediction_history']

# Khởi tạo Spark Session
spark = SparkSession.builder \
    .appName("RealEstateAPI") \
    .config("spark.jars.packages", "org.mongodb.spark:mongo-spark-connector_2.12:3.0.1") \
    .getOrCreate()

# Tải mô hình đã lưu
model_path = "models/lr_model"
model = LinearRegressionModel.load(model_path)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/predict', methods=['GET', 'POST'])
def predict():
    if request.method == 'GET':
        return render_template('predict.html')
    else:
        # Nhận dữ liệu từ form
        data = request.get_json()
        address = str(data['address'])
        area = float(data['area'])
        bedroom = float(data['bedroom'])
        bathroom = float(data['bathroom'])
        
        distance_to_hoan_kiem = float(get_distance(address))
        
        # Tạo DataFrame từ dữ liệu đầu vào
        schema = StructType([
            StructField("area", DoubleType(), True),
            StructField("distance_to_hoan_kiem", DoubleType(), True),
            StructField("bedroom", DoubleType(), True),
            StructField("bathroom", DoubleType(), True)
        ])
        
        data_row = [
            (
                float(area),
                float(distance_to_hoan_kiem),
                float(bedroom),
                float(bathroom)
            )
        ]
        input_df = spark.createDataFrame(data_row, schema)
        
        # Tạo vector features
        assembler = VectorAssembler(
            inputCols=["area", "distance_to_hoan_kiem", "bedroom", "bathroom"],
            outputCol="features"
        )
        
        vector_df = assembler.transform(input_df)
        
        # Dự đoán giá
        prediction = model.transform(vector_df)
        predicted_price = prediction.select("prediction").first()[0]
        
        # Lưu kết quả dự đoán vào MongoDB
        # prediction_record = {
        #     "address": address,
        #     "area": area,
        #     "bedroom": bedroom,
        #     "bathroom": bathroom,
        #     "distance_to_hoan_kiem": distance_to_hoan_kiem,
        #     "predicted_price": predicted_price
        # }
        #history_collection.insert_one(prediction_record)
        
        return jsonify({
            "status": "success",
            "predicted_price": predicted_price,
        })


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
    app.run(debug=True)