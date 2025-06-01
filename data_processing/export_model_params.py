from pyspark.sql import SparkSession
from pyspark.ml.regression import LinearRegressionModel
import json
import os

# Tạo SparkSession
spark = SparkSession.builder.appName("ExtractModelParams").getOrCreate()

# Tải mô hình đã lưu
model_path = "models/lr_model"
model = LinearRegressionModel.load(model_path)

# Trích xuất hệ số và intercept
coeffs = model.coefficients.toArray().tolist()  # Chuyển sang list để lưu JSON
intercept = model.intercept

# In ra để kiểm tra
print("Coefficients:", coeffs)
print("Intercept:", intercept)

# Lưu vào file JSON
model_params = {"coefficients": coeffs, "intercept": intercept}
os.makedirs("output", exist_ok=True)
with open("output/model_params.json", "w") as f:
    json.dump(model_params, f)

print("Model parameters saved to output/model_params.json")

# Đóng SparkSession
spark.stop()