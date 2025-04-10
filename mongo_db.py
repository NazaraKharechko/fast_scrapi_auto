import json
from pymongo import MongoClient
from datetime import datetime

# Підключення до MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['auto_ria_db']
collection = db['cars']

# Завантаження з файлу
with open('cars.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

    # Якщо масив — вставляємо всі
    if isinstance(data, list):
        collection.insert_many(data)
    else:
        collection.insert_one(data)

# Якщо вставляєш по одному запису під час парсингу:
car_data = {
    "title": title_car,
    "year": int(year_car) if year_car else None,
    "price_usd": int(price_usd.replace(' ', '').replace('$', '')),
    "odometer": run_car,
    "engine": engine,
    "transmission": transmissions,
    "location": location,
    "image_url": url_foto,
    "ad_url": url_ad,
    "timestamp": datetime.now().isoformat()
}

collection.insert_one(car_data)
