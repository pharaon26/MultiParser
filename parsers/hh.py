import re
import time

from parsers.base import get_soup

COLUMNS = [
    {'key': 'title', 'title': 'Название', 'width': 50},
    {'key': 'company', 'title': 'Компания', 'width': 30},
    {'key': 'salary', 'title': 'Зарплата', 'width': 20},
    {'key': 'description', 'title': 'Описание', 'width': 70},
    {'key': 'link', 'title': 'Ссылка', 'width': 60},
]

SALARY_RE = re.compile(r'(от\s+)?(до\s+)?[\d\s]+[-–]?\s*[\d\s]*\s*[₽$€]')
DESCRIPTION_KEYWORDS = ('требования', 'опыт', 'python', 'обязанности')


def parse(query='python', pages=1):
    vacancies = []

    for page in range(pages):
        try:
            soup = get_soup(f'https://hh.ru/search/vacancy?text={query}&page={page}')
        except Exception as e:
            print(f'Ошибка на странице {page + 1}: {e}')
            continue

        items = soup.select('[data-qa="vacancy-serp__vacancy"]')
        print(f'Страница {page + 1}: {len(items)} вакансий')

        for item in items:
            title_el = item.select_one('[data-qa="serp-item__title"]')
            title = title_el.text.strip() if title_el else 'Не указано'
            link = title_el['href'] if title_el else ''

            company_el = item.select_one('[data-qa="vacancy-serp__vacancy-employer"]')
            company = company_el.text.strip() if company_el else 'Не указана'

            salary_match = SALARY_RE.search(item.get_text())
            salary = salary_match.group(0).strip() if salary_match else 'Не указана'

            description = 'Описание отсутствует'
            for tag in item.find_all(['div', 'span']):
                text = tag.get_text(strip=True)
                if len(text) > 50 and any(kw in text.lower() for kw in DESCRIPTION_KEYWORDS):
                    description = text[:300]
                    break

            vacancies.append({
                'title': title,
                'company': company,
                'salary': salary,
                'description': description,
                'link': link,
            })

        time.sleep(2)

    return vacancies
