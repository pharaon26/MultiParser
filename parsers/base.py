import os

import requests
from bs4 import BeautifulSoup
from openpyxl import Workbook
from openpyxl.drawing.image import Image as XLImage
from openpyxl.styles import Alignment, Font

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}


def get_soup(url, timeout=15):
    response = requests.get(url, headers=HEADERS, timeout=timeout)
    response.raise_for_status()
    return BeautifulSoup(response.text, 'html.MultiParser')


def save_to_excel(rows, columns, filename):
    if not rows:
        print('Нет данных для сохранения')
        return

    wb = Workbook()
    ws = wb.active
    ws.title = 'Результат'

    ws.append([c['title'] for c in columns])
    for cell in ws[1]:
        cell.font = Font(bold=True, size=12)
        cell.alignment = Alignment(horizontal='center')

    has_images = any(c.get('image') for c in columns)

    for row_idx, row in enumerate(rows, start=2):
        for col_idx, c in enumerate(columns, start=1):
            if c.get('image'):
                continue
            ws.cell(row=row_idx, column=col_idx, value=row.get(c['key'], ''))
        if has_images:
            ws.row_dimensions[row_idx].height = 85

    for col_idx, c in enumerate(columns, start=1):
        letter = ws.cell(row=1, column=col_idx).column_letter
        ws.column_dimensions[letter].width = c.get('width', 20)

        if c.get('image'):
            for row_idx, row in enumerate(rows, start=2):
                path = row.get(c['key'])
                if path and os.path.exists(path):
                    img = XLImage(path)
                    img.width, img.height = 60, 80
                    ws.add_image(img, f'{letter}{row_idx}')

    wb.save(filename)
    print(f'Сохранено {len(rows)} строк в {filename}')
