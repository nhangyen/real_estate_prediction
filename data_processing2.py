from pyspark.sql import SparkSession
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.regression import LinearRegression
from pyspark.ml.evaluation import RegressionEvaluator
from pyspark.ml.feature import StandardScaler
from pyspark.sql.functions import col, split, regexp_replace
# from pyspark.ml import Pipeline
from pyspark.ml.regression import LinearRegression, RandomForestRegressor, GBTRegressor, DecisionTreeRegressor
from pyspark.ml import Pipeline
from pyspark.ml.tuning import ParamGridBuilder, CrossValidator
from pyspark.ml.feature import StringIndexer, OneHotEncoder
from pyspark.ml.regression import RandomForestRegressor
import os


# Khởi tạo Spark Session


spark = SparkSession.builder \
    .appName("RealEstateML") \
    .config("spark.mongodb.input.uri", "mongodb://localhost:27017/real_estate.properties2") \
    .config("spark.mongodb.output.uri", "mongodb://localhost:27017/real_estate.predictions") \
    .config("spark.jars.packages", "org.mongodb.spark:mongo-spark-connector_2.12:3.0.1") \
    .getOrCreate()


# Đọc dữ liệu từ MongoDB

df = spark.read.format("mongo").load()

# district_indexer = StringIndexer(
#     inputCol="district",
#     outputCol="district_index",
#     handleInvalid="keep"
# )

# district_encoder = OneHotEncoder(
#     inputCols=["district_index"],
#     outputCols=["district_encoded"]
# )
# indexed_df = district_indexer.fit(df).transform(df)
# encoded_df = district_encoder.fit(indexed_df).transform(indexed_df)



# selected_features = ["area", "distance_to_hoan_kiem", "price",'bedroom','bathroom']
assembler = VectorAssembler(
    # inputCols=["area", "distance_to_hoan_kiem", "floor","district_encoded"],
    inputCols=["area", "distance_to_hoan_kiem", "bedroom","bathroom"],
    outputCol="features"
)
# vector_df = assembler.transform(encoded_df)
vector_df = assembler.transform(df)


# scaler = StandardScaler(inputCol="features", outputCol="scaled_features")
# scaler_model = scaler.fit(vector_df)
# scaled_df = scaler_model.transform(vector_df)

# Khởi tạo mô hình Linear Regression


lr = LinearRegression(
    featuresCol="features", 
    labelCol="price", 
    maxIter=100, 
    regParam=0.01, 
    elasticNetParam=0.5
)

# rf = RandomForestRegressor(
#     featuresCol="features",
#     labelCol="price",
#     numTrees=100,
#     maxDepth=10,
#     seed=42
# )
# gbt = GBTRegressor(
#     featuresCol="features",
#     labelCol="price",
#     maxIter=100,
#     maxDepth=5,
#     seed=42
# )

# dt = DecisionTreeRegressor(
#     featuresCol="features",
#     labelCol="price",
#     maxDepth=5,
#     seed=42
# )

train_data, test_data = vector_df.randomSplit([0.8, 0.2], seed=42)
# train_data, test_data = scaled_df.randomSplit([0.8, 0.2], seed=42)

# Train mô hình
# model = gbt.fit(train_data)
model = lr.fit(train_data)

# Đánh giá mô hình
predictions = model.transform(test_data)
evaluator = RegressionEvaluator(
    labelCol="price",
    predictionCol="prediction",
    metricName="rmse"
)

rmse = evaluator.evaluate(predictions)
r2 = evaluator.setMetricName("r2").evaluate(predictions)

# In kết quả
print(f"Root Mean Square Error (RMSE): {rmse}")
print(f"R2 Score: {r2}")
print("\nCoefficients:", model.coefficients)
print("Intercept:", model.intercept)

predictions.show(5)
# Lưu predictions vào MongoDB
# predictions.write.format("mongo").mode("overwrite").save()
os.makedirs("models", exist_ok=True)
model.save("models/lr_model")
# Đóng Spark Session
spark.stop()