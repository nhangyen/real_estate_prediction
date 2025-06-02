import requests
import re
from bs4 import BeautifulSoup
from kafka_pipeline.kafka_config import create_kafka_producer
import json
import time
import random
from datetime import datetime

from pymongo import MongoClient
client = MongoClient('mongodb://localhost:27017/')
db = client['real_estate']
collection = db['properties2']

producer = create_kafka_producer()

url = 'https://bds.com.vn/mua-ban-nha-dat-ha-noi'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                '(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

try:
    for i in range(220,1000):
        print("Crawling page "+ str(i))
        response = requests.get(url+"-page"+str(i), headers=headers)

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')

            projects = soup.find_all('div', class_=re.compile(r"item-nhadat\s+bg"))

            for project in projects:
                try:
                    project_name_elem = project.find('a', class_='title-item-nhadat')
                    project_name = project_name_elem.text.strip() if project_name_elem else 'N/A'

                    price_tag = project.find('span', class_='price-item-nhadat')
                    price = price_tag.text.strip() if price_tag else 'N/A'
                    
                    if "tỷ" in price.lower():
                        price_value = float(price.replace(" tỷ", "").replace("tỷ", ""))
                        price_value = price_value * 1000000000
                    if "triệu" in price.lower():
                        price_value = float(price.replace(" triệu", "").replace("triệu", ""))
                        price_value = price_value * 1000000

                    area_tag = price_tag.find_next_sibling()
                    area = area_tag.text.strip() if area_tag else 'N/A'
                    area_value=float(area.replace(" m²", "").replace("m²", ""))

                    location_tag = project.find('span', class_='vaule-item-nhadat')
                    location = location_tag.text.strip() if location_tag else 'N/A'

                    date_tag=location_tag.find_next_sibling()
                    date = date_tag.text.strip() if date_tag else 'N/A'

                    bedroom_tag= project.find('li', class_='phong-ngu')
                    bedroom= (int)(bedroom_tag.text.strip()) if bedroom_tag else 'N/A' 

                    bathroom_tag= project.find('li', class_='phong-tam')
                    bathroom= int(bathroom_tag.text.strip()) if bathroom_tag else 'N/A' 
                except ValueError:
                    continue
                # print(f"Project Name: {project_name}")
                # print(f"Price: {price_value}")
                # print(f"Area: {area_value}")
                # print(f"Location: {location}")
                # print(f"Date: {date}")
                # print(f"Bedroom: {bedroom}")
                # print(f"Bathroom: {bathroom}")
                # print()
                
                try:
                    property_doc = {
                        'project_name': project_name,
                        'price': price_value,
                        'area': area_value,
                        'location': location,
                        'date': date,
                        'bedroom': bedroom,
                        'bathroom': bathroom,
                        # 'crawled_at': datetime.now()
                    }

                    producer.send(
                        'real_estate_data', 
                        value=property_doc
                    )
                    print(f"Sent to Kafka: {project_name}")
                except Exception as e:
                    print(f"Error sending to Kafka: {e}")
                    # try:
                    #     collection.insert_one(property_doc)
                    #     print(f"Saved to MongoDB:{project_name}")
                    # except Exception as mongo_error:
                    #     print(f"Error:{mongo_error}")

        else:
            print(f"Failed to retrieve data. Status code: {response.status_code}")

        # if i <1000:
        #     delay_time = random.uniform(1, 3)
        #     print(f"Waiting {delay_time:.2f} seconds before next request...")
        #     time.sleep(delay_time)

except requests.exceptions.RequestException as e:
    print(f"An error occurred: {e}")
finally:
    client.close()
