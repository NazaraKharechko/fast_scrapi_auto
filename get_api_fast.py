import json
import os
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Query
from typing import List
from pydantic import BaseModel
from typing import Optional


# Створюємо екземпляр FastAPI
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # або ["http://localhost:63342"] для безпеки
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Модель продукту для валідації даних
class CarModel(BaseModel):
    id: int
    title: str
    year: int
    price_usd: int
    odometer: str
    engine: str
    transmissions: Optional[str] = None  # ← дозволяє null
    location: str
    image_url: str
    link: str



    class Config:
        orm_mode = True


# Функція для зчитування даних з файлу JSON
def clean_car_data(car):
    # Ціна: чистимо від пробілів, символів
    raw_price = car.get("price_usd", "0")
    try:
        price = int(raw_price.replace("\xa0", "").replace("$", "").replace(" ", "").strip())
    except:
        price = 0

    # Рік: перетворення у int
    try:
        year = int(car.get("year", 0))
    except:
        year = 0

    return {
        "id": car.get("id", ""),
        "title": car.get("title", ""),
        "year": year,
        "price_usd": price,
        "odometer": car.get("odometer", ""),
        "engine": car.get("engine", ""),
        "transmissions": car.get("transmissions", "Unknown"),
        "location": car.get("location", ""),
        "image_url": car.get("image_url", ""),
        "link": car.get("link", "")
    }

def load_cars():
    try:
        if not os.path.exists('cars.json'):
            raise FileNotFoundError("cars.json file not found")

        with open('cars.json', 'r', encoding='utf-8') as file:
            raw_data = json.load(file)
            if not raw_data:
                raise ValueError("cars.json file is empty")
            return [clean_car_data(car) for car in raw_data]
    except FileNotFoundError as e:
        print(f"Error: {e}")
        raise e
    except json.JSONDecodeError:
        print("Error: Invalid JSON in cars.json")
        raise
    except Exception as e:
        print(f"Error loading data: {e}")
        raise e

@app.get("/cars/{car_id}", response_model=CarModel)
async def get_car_by_id(car_id: int):
    try:
        cars = load_cars()  # Завантажуємо всі автомобілі
        # Шукаємо автомобіль з відповідним ID
        car = next((car for car in cars if car["id"] == car_id), None)

        if car:
            return car
        else:
            return {"detail": "Car not found"}

    except Exception as e:
        print(f"Error: {e}")
        return {"detail": "Internal Server Error"}


# Ендпоінт для отримання списку авто з пагінацією
@app.get("/cars", response_model=List[CarModel])
async def get_cars(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, le=100)
):
    # Завантажуємо дані про авто
    cars = load_cars()

    # Пагінація: повертаємо лише частину списку, відповідно до skip та limit
    return cars[skip:skip + limit]

@app.get("/cars/title/{title}", response_model=List[CarModel])
async def get_cars_by_title(title: str):
    try:
        cars = load_cars()  # Load cars from the data source

        # Debugging print to check the loaded cars
        print(f"Loaded cars: {cars}")

        # Filter cars based on the title (case-insensitive)
        filtered_cars = [car for car in cars if title.lower() in car["title"].lower()]

        # Debugging print to check the filtered cars
        print(f"Filtered cars: {filtered_cars}")

        return filtered_cars
    except Exception as e:
        print(f"Error: {e}")
        return {"detail": "Internal Server Error"}

@app.get("/cars/year/{year}", response_model=List[CarModel])
async def get_cars_by_year(year: int):
    try:
        cars = load_cars()  # Завантажуємо автомобілі з джерела даних

        print(f"Loaded cars: {cars}")

        # Фільтрація автомобілів за роком
        filtered_cars = [car for car in cars if car["year"] == year]

        print(f"Filtered cars: {filtered_cars}")

        return filtered_cars
    except Exception as e:
        print(f"Error: {e}")
        return {"detail": "Internal Server Error"}


def save_cars(cars):
    with open('cars.json', 'w', encoding='utf-8') as file:
        json.dump(cars, file, ensure_ascii=False, indent=4)


# Оновлення автомобіля за ID
@app.put("/cars/{id}", response_model=CarModel)
async def update_car(id: int, car: CarModel):
    # Зчитуємо всі автомобілі
    cars = load_cars()

    # Шукаємо автомобіль за ID
    car_to_update = next((car for car in cars if car["id"] == id), None)

    if not car_to_update:
        raise HTTPException(status_code=404, detail="Car not found")

    # Оновлюємо дані автомобіля
    car_to_update["title"] = car.title
    car_to_update["year"] = car.year
    car_to_update["price_usd"] = car.price_usd
    car_to_update["odometer"] = car.odometer
    car_to_update["engine"] = car.engine
    car_to_update["transmissions"] = car.transmissions or "Unknown"
    car_to_update["location"] = car.location
    car_to_update["image_url"] = car.image_url

    # Зберігаємо оновлені дані назад у файл
    save_cars(cars)

    return car_to_update

# Видалення автомобіля за ID
@app.delete("/cars/{id}", response_model=CarModel)
async def delete_car(id: int):
    # Зчитуємо всі автомобілі
    cars = load_cars()

    # Шукаємо автомобіль за ID
    car_to_delete = next((car for car in cars if car["id"] == id), None)

    if not car_to_delete:
        raise HTTPException(status_code=404, detail="Car not found")

    # Видаляємо автомобіль із списку
    cars.remove(car_to_delete)

    # Зберігаємо оновлений список в файл
    save_cars(cars)

    return car_to_delete