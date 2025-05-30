import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
from pyspark.sql import SparkSession
from pyspark.ml.feature import StringIndexer, OneHotEncoder, VectorAssembler, StandardScaler
from math import sqrt
import numpy as np

# Initialize Spark Session
spark = SparkSession.builder \
    .appName("RealEstateML") \
    .config("spark.mongodb.input.uri", "mongodb://localhost:27017/real_estate.properties2") \
    .config("spark.mongodb.output.uri", "mongodb://localhost:27017/real_estate.predictions") \
    .config("spark.jars.packages", "org.mongodb.spark:mongo-spark-connector_2.12:3.0.1") \
    .getOrCreate()

# Read data from MongoDB
df = spark.read.format("mongo").load()

# Feature Engineering
district_indexer = StringIndexer(
    inputCol="district",
    outputCol="district_index",
    handleInvalid="keep"
)

district_encoder = OneHotEncoder(
    inputCols=["district_index"],
    outputCols=["district_encoded"]
)

indexed_df = district_indexer.fit(df).transform(df)
encoded_df = district_encoder.fit(indexed_df).transform(indexed_df)

assembler = VectorAssembler(
    inputCols=["area", "bedroom", "bathroom", "district_encoded"],
    outputCol="features"
)
vector_df = assembler.transform(encoded_df)

scaler = StandardScaler(inputCol="features", outputCol="scaled_features")
scaler_model = scaler.fit(vector_df)
scaled_df = scaler_model.transform(vector_df)

# Convert Spark DataFrame to Pandas
pandas_df = scaled_df.select("scaled_features", "price").toPandas()

# Prepare Features and Labels
X = pandas_df["scaled_features"].tolist()
y = pandas_df["price"]

# Train-Test Split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train XGBoost Model
xgb_model = xgb.XGBRegressor(
    max_depth=6,
    n_estimators=100,
    learning_rate=0.1,
    random_state=42
)
xgb_model.fit(X_train, y_train)

# Evaluate Model
y_pred = xgb_model.predict(X_test)
mse = mean_squared_error(y_test, y_pred)  # Compute Mean Squared Error
rmse = sqrt(mse)  # Compute Root Mean Squared Error
print(f"Root Mean Square Error (RMSE): {rmse}")

# Tính RMSE theo %
mean_y_test = np.mean(y_test)
rmse_percent = (rmse / mean_y_test) * 100

# Tính R^2
r2 = r2_score(y_test, y_pred)
print(f"RMSE (% of mean true value): {rmse_percent:.2f}%")
print(f"Root Mean Square Error (RMSE): {rmse:.2f}")

print(f"R^2 Score: {r2:.4f}")

# Optional: Feature Importance
importance = xgb_model.feature_importances_
print("Feature Importances:", importance)