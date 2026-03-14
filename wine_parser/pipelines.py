# pipelines.py
import json
import logging
from scrapy.exceptions import DropItem
from datetime import datetime
from urllib.parse import urlparse


class WineValidationPipeline:
    """Проверяет качество данных"""

    def __init__(self):
        self.items_validated = 0
        self.items_dropped = 0
        self.logger = logging.getLogger(__name__)

    def process_item(self, item, spider):
        if not item.get('name'):
            self.items_dropped += 1
            raise DropItem(f"Пропущен товар без названия: {item.get('url')}")

        if not item.get('price'):
            spider.logger.warning(f"Товар без цены: {item.get('name')}")

        # Добавляем домен если нет
        if not item.get('domain') and item.get('url'):
            item['domain'] = urlparse(item['url']).netloc

        # Добавляем время если нет
        if not item.get('scraped_at'):
            item['scraped_at'] = datetime.now().isoformat()

        self.items_validated += 1
        return item

    def close_spider(self, spider):
        spider.logger.info(f"Принято: {self.items_validated}, Отброшено: {self.items_dropped}")


class DuplicatesPipeline:
    """Удаляет дубликаты по URL"""

    def __init__(self):
        self.urls_seen = set()
        self.duplicates = 0

    def process_item(self, item, spider):
        url = item.get('url')
        if url in self.urls_seen:
            self.duplicates += 1
            raise DropItem(f"Дубликат URL: {url}")
        else:
            self.urls_seen.add(url)
            return item

    def close_spider(self, spider):
        spider.logger.info(f"Дубликатов удалено: {self.duplicates}")


class WineJsonExportPipeline:
    """Экспорт в JSON"""

    def open_spider(self, spider):
        filename = getattr(spider, 'output_file', f'wines_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
        self.file = open(filename, 'w', encoding='utf-8')
        self.file.write('[')
        self.first_item = True

    def close_spider(self, spider):
        self.file.write(']')
        self.file.close()
        spider.logger.info(f"Данные сохранены в JSON файл")

    def process_item(self, item, spider):
        if not self.first_item:
            self.file.write(',\n')
        else:
            self.first_item = False

        line = json.dumps(dict(item), ensure_ascii=False, indent=2)
        self.file.write(line)
        return item