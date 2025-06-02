from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
import time
import random
import re
import json
from datetime import datetime
from pymongo import MongoClient
from kafka_pipeline.kafka_config import create_kafka_producer

client = MongoClient('mongodb://localhost:27017/')
db = client['real_estate']
collection = db['properties2']

producer = create_kafka_producer()

def clean_price(price_text):
    """Convert price text to numeric value in billions"""
    if not price_text or price_text == "N/A" or price_text == "Giá thỏa thuận":
        return None
    try:
        match = re.search(r'([\d,\.]+)\s*(tỷ|triệu)', price_text)
        if match:
            value = float(match.group(1).replace(',', '.'))
            unit = match.group(2)
            if unit == 'tỷ':
                return value*1000000000
            elif unit == 'triệu':
                return value *1000000
    except:
        pass
    return None

def clean_area(area_text):
    """Extract area value in m²"""
    if not area_text or area_text == "N/A":
        return None
    try:
        match = re.search(r'([\d,\.]+)\s*m²', area_text)
        if match:
            return float(match.group(1).replace(',', '.'))
    except:
        pass
    return None

def extract_room_count(config_text, room_type):
    """Extract room count from config text"""
    if not config_text or config_text == "N/A":
        return 0
    try:
        if room_type == 'bedroom':
            pattern = r'(\d+)\s*(?:Phòng ngủ|PN)'
        else:  # bathroom
            pattern = r'(\d+)\s*(?:WC|Phòng tắm|phòng vệ sinh)'
            
        match = re.search(pattern, config_text, re.IGNORECASE)
        return int(match.group(1)) if match else 0
    except:
        return 0

def get_data():
    edge_driver_path = "C:/Users/nhang/Downloads/edgedriver_win64/msedgedriver.exe"  # Đường dẫn đến msedgedriver.exe

    # Thiết lập trình duyệt Edge
    options = Options()
    # options.add_argument("--headless")  # Bỏ ghi chú nếu muốn chạy ẩn
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--start-maximized")

    driver = webdriver.Edge(service=Service(edge_driver_path), options=options)

    data = []

    try:
        for i in range(2200, 3000):
            print("Scrawling page",i)
            url = f"https://batdongsan.com.vn/nha-dat-ban-ha-noi/p{i}" if i > 1 else "https://batdongsan.com.vn/nha-dat-ban-ha-noi"
            driver.get(url)
            time.sleep(random.uniform(4, 6))  # Chờ trang load

            # Tìm tất cả các card bất động sản
            cards = driver.find_elements(By.CLASS_NAME, 'js__card')

            if not cards:
                print("Không tìm thấy dữ liệu. Có thể selector đã thay đổi.")
                continue

            for card in cards:
                try:
                    # Project name
                    title = card.find_element(By.CSS_SELECTOR, '.re__card-title .pr-title').text.strip()
                    
                    # Price and area from config section
                    config = card.find_element(By.CLASS_NAME, 're__card-config').text
                    price = re.search(r'([\d,\.]+\s*tỷ|Giá thỏa thuận)', config)
                    price = price.group(1) if price else "N/A"
                    
                    area = re.search(r'([\d,\.]+\s*m²)', config)
                    area = area.group(1) if area else "N/A"
                    
                    # Location
                    location = card.find_element(By.CLASS_NAME, 're__card-location').text
                    location = location.replace('·', '').strip()
                    
                    # Extract bedroom and bathroom counts using text content
                    bedrooms = 0
                    bathrooms = 0
                    
                    try:
                        bedroom_span = card.find_element(By.CSS_SELECTOR, '[aria-label*="Phòng ngủ"]')
                        bedrooms = int(re.search(r'\d+', bedroom_span.text).group())
                    except:
                        bedrooms = extract_room_count(config, 'bedroom')
                        
                    try:
                        bathroom_span = card.find_element(By.CSS_SELECTOR, '[aria-label*="WC"]')
                        bathrooms = int(re.search(r'\d+', bathroom_span.text).group())
                    except:
                        bathrooms = extract_room_count(config, 'bathroom')                    # Extract date
                    try:
                        date_element = card.find_element(By.CLASS_NAME, 're__card-published-info-published-at')
                        date = date_element.get_attribute('aria-label')
                    except:
                        date = "N/A"

                    item = {
                        'project_name': title,
                        'price': clean_price(price),
                        'area': clean_area(area),
                        'location': location,
                        'date': date,
                        'bedroom': bedrooms,
                        'bathroom': bathrooms,
                        # 'crawled_at': datetime.now()
                    }
                    
                    # Send to Kafka first
                    try:
                        producer.send(
                            'real_estate_data', 
                            value=item
                        )
                        print(f"Sent to Kafka: {item['project_name']}")
                    except Exception as kafka_error:
                        print(f"Error sending to Kafka: {kafka_error}")
                        # Fallback to MongoDB if Kafka fails
                        try:
                            collection.insert_one(item)
                            print(f"Saved to MongoDB (fallback): {item['project_name']}")
                        except Exception as mongo_error:
                            print(f"Error saving to MongoDB: {mongo_error}")

                    # print("\nExtracted property:")
                    # print(f"Project: {item['project_name']}")
                    # print(f"Price: {item['price']}")
                    # print(f"Area: {item['area']}")
                    # print(f"Location: {item['location']}")
                    # print(f"Bedrooms: {item['bedroom']}")
                    # print(f"Bathrooms: {item['bathroom']}")
                    # print(f"Date: {item['date']}")
                    # print("-" * 50)

                    data.append(item)                
                except Exception as e:
                    print(f"Error processing card: {str(e)}")
                    continue

            time.sleep(random.uniform(1, 2))  # Giả lập người dùng

    finally:
        driver.quit()
        client.close()

    return data

if __name__ == "__main__":
    results = get_data()
    print(f"🎯 Total items found: {len(results)}")
