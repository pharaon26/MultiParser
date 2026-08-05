import os
import re
import time

import requests
from bs4 import BeautifulSoup
from PIL import Image

from parsers.base import HEADERS

COLUMNS = [
    {'key': 'title', 'title': 'Название', 'width': 60},
    {'key': 'author', 'title': 'Автор', 'width': 30},
    {'key': 'price', 'title': 'Цена', 'width': 15},
    {'key': 'link', 'title': 'Ссылка', 'width': 50},
    {'key': 'img_path', 'title': 'Фото', 'width': 12, 'image': True},
]


def _download_cover(img_url, save_path):
    try:
        response = requests.get(img_url, headers=HEADERS, timeout=15)
    except Exception:
        return ''

    if response.status_code != 200 or len(response.content) < 1000:
        return ''

    temp_path = save_path + '.tmp'
    with open(temp_path, 'wb') as f:
        f.write(response.content)

    try:
        img = Image.open(temp_path)
        if img.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            mask = img.split()[-1] if img.mode == 'RGBA' else None
            background.paste(img, mask=mask)
            img = background
        elif img.mode != 'RGB':
            img = img.convert('RGB')
        img.save(save_path, 'JPEG', quality=85)
        return save_path
    except Exception:
        return ''
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


def parse(query='python', pages=1):
    os.makedirs('images', exist_ok=True)
    products = []

    for page in range(1, pages + 1):
        try:
            response = requests.get(
                f'https://www.labirint.ru/search/{query}/?page={page}',
                headers=HEADERS, timeout=15,
            )
            soup = BeautifulSoup(response.text, 'html.MultiParser')
        except Exception as e:
            print(f'Ошибка на странице {page}: {e}')
            continue

        items = soup.select('div.product-card')[:10]
        print(f'Страница {page}: {len(items)} товаров')

        for idx, item in enumerate(items, start=1):
            title_el = item.select_one('a.product-card__name')
            title = (title_el.get('title', '').strip() or title_el.text.strip()) if title_el else 'Не указано'

            author_el = item.select_one('div.product-card__author a')
            author = author_el.text.strip() if author_el else 'Не указан'

            price_el = item.select_one('div.product-card__price-current')
            price = re.sub(r'\s+', ' ', price_el.text.strip()) if price_el else 'Не указана'

            href = title_el.get('href', '') if title_el else ''
            link = 'https://www.labirint.ru' + href if href.startswith('/') else href

            img_path = ''
            img_el = item.select_one('img[data-src]')
            if img_el:
                img_url = img_el.get('data-src', '')
                if img_url and 'emptycover' not in img_url:
                    if img_url.startswith('//'):
                        img_url = 'https:' + img_url
                    elif img_url.startswith('/'):
                        img_url = 'https://www.labirint.ru' + img_url
                    img_path = _download_cover(img_url, f'images/product_{page}_{idx}.jpg')

            products.append({
                'title': title,
                'author': author,
                'price': price,
                'link': link,
                'img_path': img_path,
            })

        time.sleep(2)

    return products
