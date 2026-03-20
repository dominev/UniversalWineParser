#! 🍷 Wine Parser - Универсальный парсер для винных магазинов

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Scrapy](https://img.shields.io/badge/Scrapy-2.8+-green.svg)](https://scrapy.org/)
[![Playwright](https://img.shields.io/badge/Playwright-1.40+-orange.svg)](https://playwright.dev/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)


## Описание

Профессиональный парсер для сбора информации о винах с любых интернет-магазинов по всему миру. Поддерживает два режима обхода, автоматическое определение структуры сайта, работает с JavaScript.

### Ключевые возможности

- Два режима работы: обход сайта (crawl) и парсинг конкретных URL (urls)
- Поддержка JavaScript через Playwright
- Автоматическое извлечение: название, винтаж, цена, валюта, наличие, изображение, объем
- Экспорт в JSON
- Устойчивость к блокировкам (задержки, повторные попытки)

# Архитектура проекта
```bash
wine_parser/                            # Корневая папка проекта
├── scrapy.cfg                          # Конфигурация Scrapy
├── run_spider.py                       # Скрипт для запуска парсера
├── requirements.txt                    # Зависимости проекта
├── README.MD                           # Документация
│
├── wine_parser/                        # Основной парсер
│   ├── __init__.py
│   ├── items.py                        # Модели данных
│   ├── pipelines.py                    # Обработка и валидация данных
│   ├── settings.py                     # Настройки проекта
│   │
│   ├── spiders/                        
│   │   ├── __init__.py
│   │   └── wine_spider.py              # 🕷️ Основной паук (crawl и urls режимы)
│   │
│   └── middlewares/                    
│       ├── __init__.py
│       └── playwright_middleware.py    # Поддержка JavaScript
│
└── tests/                              # Тесты
    ├── test_server.py                  # Локальный сайт
    ├── test_parser.py
    ├── test_requirements.txt           # Тест парсера
    ├── check_file.py                   # Проверка файлов
    └── check_results.py                # Тест результатов

```
### Установка

```bash
# Клонирование репозитория
git clone <repository-url>
cd wine_spyder
# Установка зависимостей
pip install -r requirements.txt

# Зависимости для теста (на локальном сервере)
cd tests
pip install -r test_requirements.txt

# Для поддержки JavaScript (опционально)
pip install playwright
playwright install chromium
```

# Быстрый старт

```bash
# Режим обхода сайта
python run_spider.py --mode crawl --domain example.com

# Режим прямых ссылок
python run_spider.py --mode urls --urls "https://example.com/product/1,https://example.com/product/2"

# Парсинг конкретных URL
python run_spider.py --mode urls --urls "https://example.com/wine1,https://example.com/wine2"

# С поддержкой JavaScript
python run_spider.py --mode crawl --domain example.com --js
```

### !!!Для тестирования на локальным сервере.!!!
* обязательно установить нужные зависимости -
  (test_requirements.txt)

```bash
# 1. Запуск тестового сервера (в отдельном терминале)
python tests/test_server.py

# 2. Обычный режим (без JS)
python run_spider.py --mode crawl --domain localhost:5000 --output wines.json

# 3. Режим с Playwright
python run_spider.py --mode crawl --domain localhost:5000 --js --output wines_js.json

# 4. Режим прямых ссылок
python run_spider.py --mode urls --urls "http://localhost:5000/product/1,http://localhost:5000/product/2" --output specific.json

# 5. С ограничениями
python run_spider.py --mode crawl --domain localhost:5000 --limit 3 --delay 1 --output limited.json
```

# Режимы работы

1. Crawl Mode (режим обхода) - ПО УМОЛЧАНИЮ

Автоматически находит все страницы товаров, следуя по ссылкам. Использует правила обхода для навигации по категориям и пагинации.

2. URLs Mode (режим списка URL) - 

Парсит только указанные URL (полезно для тестирования или точечного сбора).

# Параметры командной строки

* --mode | Режим работы: crawl/sitemap/urls |	--mode sitemap
* --domain | Домен для парсинга |	--domain winshop.com
* --urls |	Список URL через запятую |	--urls url1,url2,url3
* --js |	Включить поддержку JavaScript |	--js
* --delay |	Задержка между запросами (сек) |	--delay 3
* --output |	Имя выходного файла	| --output my_wines.json
* --limit |	Лимит товаров	| --limit 100

### Выходные данные (Пример)

```bash
  [
  {
    "name": "Château Margaux",
    "vintage": null,
    "availability": "in_stock",
    "image_url": "http://localhost:5000/static/images/margaux.jpg",
    "price": 850.0,
    "currency": "EUR",
    "bottle_volume": "750ml",
    "bottle_quantity": 1,
    "url": "http://localhost:5000/product/1",
    "domain": "localhost:5000",
    "scraped_at": "2024-01-15T10:30:45.123456",
    "parser_mode": "crawl",
    "used_playwright": false
  }
]
```

## 🛠️ Возможные проблемы и решения

Частые проблемы и решения: 
1. Блокировка сайтом - HTTP 403, 429, капча

Решение:
- Увеличьте `--delay` до 5-10 секунд
- Включите ротацию User-Agent
- Используйте прокси (настройка в settings.py)
- Добавьте случайные задержки
2. Не загружается JavaScript - Пустые страницы, нет данных

Решение:
- Установите Playwright: `playwright install`
- Проверьте настройки в `playwright_middleware.py`
- Увеличьте таймауты: `--delay 5 --js`
- Включите отладку: `LOG_LEVEL=DEBUG`
4. Слишком медленно - Низкая скорость сбора

Решение:
- Используйте sitemap вместо crawl
- Уменьшите `DOWNLOAD_DELAY` (осторожно!)
- Увеличьте `CONCURRENT_REQUESTS`
- Отключите кеширование для продакшена

5. Ошибка кодировки в Windows

Решение:
- Убедитесь, что в settings.py указано FEED_EXPORT_ENCODING = 'utf-8'

6. Пустой JSON файл

Решение:
- Проверьте доступность сайта и селекторы под его структуру

##  Краткий комментарий о сложностях и решениях

Основные сложности при разработке:
1. *Структура сайта и навигация*

Ссылки на товары были реализованы через JavaScript, а не через стандартные теги. 

Обычный LinkExtractor не видел эти ссылки.
Вместо CrawlSpider использовал обычный Spider с ручным извлечением URL из атрибутов через регулярные выражения.

2. Пагинация

Ссылки на следующие страницы каталога имели класс page-link, но могли отсутствовать на некоторых страницах.
Реализовал рекурсивный обход всех найденных ссылок, что гарантирует сбор товаров со всех страниц каталога независимо от их количества.

3. Извлечение данных из разных форматов

Цены могли быть представлены в разных форматах:
Мета-теги, блоки с символами валют, разные разделители.
Реализовал многоуровневую систему извлечения: сначала проверяются мета-теги, затем текст страницы с универсальными регулярными выражениями под разные валюты и форматы чисел.

4. Отсутствие винтажа в данных

В тестовых данных год винтажа был частью названия только для некоторых позиций, а для других отсутствовал.
Поиск года через регулярное выражение в названии товара. Если год не найден — поле остается null.

5. Обработка дубликатов

При обходе пагинации некоторые товары могли попадаться повторно.
Использовал встроенный механизм Scrapy для фильтрации дубликатов по URL.

6. Кодировка и спецсимволы

Названия содержали символы вроде "é" и эмодзи, что вызывало ошибки в Windows-консоли.
Явно указал FEED_EXPORT_ENCODING = 'utf-8' в настройках и убрал все не-ASCII символы из отладочного вывода.

7. JSON vs HTML ответы

Сайт отдавал JSON по некоторым URL, и паук пытался применить к ним CSS-селекторы.
Добавил проверку Content-Type и пропускаю все не-HTML ответы.

*Итог:* Все сложности успешно решены, паук стабильно собирает данные, корректно обрабатывает различные форматы представления информации и устойчив к типичным проблемам парсинга (пагинация, дубликаты, разные типы контента).

### *// Проект сделан в рамках технического задания.//*

# 🎯 Контакты:
* Email : ipicuous@gmail.com
* Recovery email: amilastie@gmail.com
* Telegram : @dominev
