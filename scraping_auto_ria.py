import json
import random
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import re

url = 'https://auto.ria.com/uk/search/?page=2'
all_data = []


def safe_find_text(parent, tag, attrs):
    el = parent.find(tag, attrs)
    return el.text.strip() if el else None


# Обробка кожної URL по черзі
def scrape():
    driver = webdriver.Chrome()

    driver.get(url)
    time.sleep(2)

    html_code = driver.page_source
    soup = BeautifulSoup(html_code, 'html.parser')
    all_cars = soup.find_all('div', {'class': 'content'})
    print(len(all_cars))

    for car in all_cars:
        try:
            title_car = safe_find_text(car, 'span', {"class": "blue bold"})
            year_raw = safe_find_text(car, 'div', {"class": "item ticket-title"})
            year_car = year_raw[-4:] if year_raw else None
            price_usd = safe_find_text(car, 'span', {"class": "bold size22 green"}) + '$'
            run_car = safe_find_text(car, 'li', {"class": "item-char js-race"})
            location = safe_find_text(car, 'li', {"class": "item-char view-location js-location"})
            # Генерація унікального числового ID за допомогою хешування
            unique_id = random.randint(1000, 9999)  # 4-значне випадкове число

            # Посилання на авто
            link_tag = car.find('a', class_='address')
            link_url = link_tag['href'] if link_tag and 'href' in link_tag.attrs else None

            # Фото
            img_block = car.find_previous_sibling('div',
                                                  class_='ticket-photo')  # або подивитися всередині батьків
            img_url = None
            if img_block:
                img_tag = img_block.find('img')
                if img_tag and 'src' in img_tag.attrs:
                    img_url = img_tag['src']
            else:
                print('⚠️ No image found for this car block')

            li_items = car.find_all('li', class_='item-char')
            engine = None
            transmissions = None

            for li in li_items:
                if not transmissions and li.find('i', class_='icon-akp'):
                    transmissions = li.text.strip()

                if not engine and li.find('i', class_='icon-fuel'):
                    engine = li.text.strip()
                    #
                    # # Знаходимо фото без all_foto — напряму в блоці car
                    # img_block = car.find_previous_sibling('div',
                    #                                       class_='ticket-photo')  # або подивитися всередині батьків
                    # img_url = None
                    # if img_block:
                    #     img_tag = img_block.find('img')
                    #     if img_tag and 'src' in img_tag.attrs:
                    #         img_url = img_tag['src']
                    # else:
                    #     print('⚠️ No image found for this car block')

            car_data = {
                'id': unique_id,
                'title': title_car,
                'year': year_car,
                'price_usd': price_usd,
                'odometer': run_car,
                'engine': engine,
                'transmissions': transmissions,
                'location': location,
                'image_url': img_url,
                'link': link_url,
            }
            all_data.append(car_data)

        except Exception as e:
            print(f"Error processing one car block: {e}")


    driver.quit()
scrape()

with open('cars.json', 'w', encoding='utf-8') as f:
    json.dump(all_data, f, ensure_ascii=False, indent=4)


