
from kafka_config import create_kafka_consumer
from pymongo import MongoClient
import json

def start_consumer():
    # MongoDB connection
    client = MongoClient('mongodb://localhost:27017/')
    db = client['real_estate']
    collection = db['test']
    
    # Create Kafka consumer
    consumer = create_kafka_consumer()
    
    print("Starting Kafka consumer...")
    try:
        for message in consumer:
            property_data = message.value
            
            try:
                # Insert into MongoDB
                collection.insert_one(property_data)
                print(f"Saved to MongoDB: {property_data['project_name']}")
            except Exception as e:
                print(f"Error saving to MongoDB: {e}")
                
    except KeyboardInterrupt:
        print("Stopping consumer...")
    finally:
        consumer.close()
        client.close()

if __name__ == "__main__":
    start_consumer()