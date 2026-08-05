import argparse

from parsers import hh, labirint, wildberries
from parsers.base import save_to_excel

PARSERS = {
    'wb': (wildberries.parse, wildberries.COLUMNS, 'wb_result.xlsx'),
    'labirint': (labirint.parse, labirint.COLUMNS, 'labirint_result.xlsx'),
    'hh': (hh.parse, hh.COLUMNS, 'hh_result.xlsx'),
}


def main():
    parser = argparse.ArgumentParser(description='Парсер маркетплейсов и hh.ru')
    parser.add_argument('source', choices=PARSERS.keys(), help='Источник: wb, labirint или hh')
    parser.add_argument('query', help='Поисковый запрос')
    parser.add_argument('--pages', type=int, default=1, help='Количество страниц')
    parser.add_argument('--output', help='Имя выходного .xlsx файла')

    args = parser.parse_args()

    parse_func, columns, default_output = PARSERS[args.source]
    rows = parse_func(args.query, args.pages)
    save_to_excel(rows, columns, args.output or default_output)


if __name__ == '__main__':
    main()
