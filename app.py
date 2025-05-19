from flask import Flask, request, jsonify, render_template
from pyspark.sql import SparkSession
from pyspark.ml.regression import LinearRegressionModel
from pyspark.ml.feature import VectorAssembler
from pyspark.sql.functions import lit
from pyspark.sql.types import DoubleType, StringType, StructType, StructField
import os
from pymongo import MongoClient
import re
import clean_data
app = Flask(__name__)

# Kết nối MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['real_estate']
history_collection = db['prediction_history']

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
        address = float(data['address'])
        area = float(data['area'])
        bedroom = float(data['bedroom'])
        bathroom = float(data['bathroom'])
        
        # Trích xuất quận và tính khoảng cách đến trung tâm
        #distance_to_hoan_kiem = clean_data.get_distance(address)
        
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
                float(address),
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

if __name__ == '__main__':
    app.run(debug=True)