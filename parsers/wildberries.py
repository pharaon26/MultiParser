import time

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

COLUMNS = [
    {'key': 'title', 'title': 'Название', 'width': 60},
    {'key': 'price', 'title': 'Цена', 'width': 15},
    {'key': 'rating', 'title': 'Рейтинг', 'width': 10},
    {'key': 'link', 'title': 'Ссылка', 'width': 70},
    {'key': 'img_url', 'title': 'Фото (ссылка)', 'width': 70},
]

USER_AGENT = (
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
    '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
)


def _make_driver():
    options = Options()
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument(f'user-agent={USER_AGENT}')
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)


def parse(query='iphone', pages=1):
    url = f'https://www.wildberries.ru/catalog/0/search.aspx?search={query}'
    scrolls = pages * 5
    card_limit = pages * 30

    driver = _make_driver()
    try:
        driver.get(url)
        time.sleep(5)
        for _ in range(scrolls):
            driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
            time.sleep(1)
        html = driver.page_source
    finally:
        driver.quit()

    soup = BeautifulSoup(html, 'html.MultiParser')
    cards = soup.find_all('article', class_='product-card')
    print(f'Найдено карточек: {len(cards)}')

    products = []
    for card in cards[:card_limit]:
        link_el = card.find('a', class_='product-card__link')
        if not link_el:
            continue

        href = link_el.get('href', '')
        title = link_el.get('aria-label', '').strip()

        price_el = card.find('ins', class_='price__lower-price') or card.find('span', class_='price__lower-price')
        price = price_el.text.strip().replace('\xa0', '').replace('₽', '') if price_el else 'Нет цены'

        rating_el = card.find('span', class_='address-rate-mini')
        rating = rating_el.text.strip() if rating_el else 'Нет оценок'

        img_el = card.find('img', class_='j-thumbnail')
        img_url = img_el['src'] if img_el else ''

        products.append({
            'title': title,
            'price': price,
            'rating': rating,
            'link': href,
            'img_url': img_url,
        })

    return products
