# wine_hybrid_spider.py
import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from urllib.parse import urlparse
import re
from datetime import datetime


class WineHybridSpider(CrawlSpider):

    name = 'wine_hybrid'

    def __init__(self, *args, **kwargs):
        self.mode = kwargs.get('mode', 'crawl')
        self.custom_urls = kwargs.get('urls', '').split(',') if kwargs.get('urls') else []
        self.domain = kwargs.get('domain', '')
        self.use_playwright = kwargs.get('use_playwright', False) or kwargs.get('js', False)

        # Start_urls
        if self.mode == 'urls' and self.custom_urls:
            self.start_urls = [url.strip() for url in self.custom_urls if url.strip()]
        elif self.domain:
            self.start_urls = [f'http://{self.domain}']
        else:
            self.start_urls = ['http://localhost:5000']

        print(f"\n{'=' * 60}")
        print("WINE HYBRID SPIDER STARTED")
        print(f"{'=' * 60}")
        print(f"Mode: {self.mode}")
        print(f"Domain: {self.domain if self.domain else 'N/A'}")
        print(f"Start URLs: {self.start_urls}")
        print(f"Playwright: {'ON' if self.use_playwright else 'OFF'}")
        print(f"{'=' * 60}\n")

        # Правила для crawl режима
        self.rules = ()
        super().__init__(*args, **kwargs)

    def start_requests(self):
        """Поддержка Playwright"""
        for url in self.start_urls:
            yield scrapy.Request(
                url,
                callback=self.parse,
                meta={'playwright': self.use_playwright},
                errback=self.handle_error
            )

    def handle_error(self, failure):

        self.logger.error(f"Error request: {failure.request.url}")
        self.logger.error(f"Reason: {failure.value}")

    def parse(self, response):

        playwright_used = response.meta.get('playwright', False)
        self.logger.info(f"Loading: {response.url}")

        # Пропускаем JSON и другие не-HTML ответы
        content_type = response.headers.get('Content-Type', '').decode('latin1')
        if 'text/html' not in content_type:
            return

        # Если это страница товара - парсим
        if '/product/' in response.url:
            yield from self.parse_wine_item(response)
            return

        # Ищем ссылки на товары
        product_links = []

        # Способ 1: onclick
        for div in response.css('div.product'):
            onclick = div.css('::attr(onclick)').get()
            if onclick and 'location.href' in onclick:
                match = re.search(r"location\.href='([^']+)'", onclick)
                if match:
                    url = match.group(1)
                    absolute_url = response.urljoin(url)
                    product_links.append(absolute_url)
                    self.logger.info(f"Found product link: {absolute_url}")

        # Способ 2: absolute links
        for link in response.css('a[href*="/product/"]::attr(href)').getall():
            absolute_url = response.urljoin(link)
            product_links.append(absolute_url)
            self.logger.info(f"Found product link (a tag): {absolute_url}")

        # Отправляем запросы на все найденные товары
        for url in set(product_links):
            yield scrapy.Request(
                url,
                callback=self.parse_wine_item,
                meta={'playwright': self.use_playwright}
            )

        # Ищем ссылки на следующие страницы
        pagination_links = []
        for link in response.css('a.page-link::attr(href)').getall():
            absolute_url = response.urljoin(link)
            pagination_links.append(absolute_url)
            self.logger.info(f"Found pagination: {absolute_url}")

        # Ищем ссылки на страницы каталога
        for link in response.css('a[href*="catalog?page="]::attr(href)').getall():
            absolute_url = response.urljoin(link)
            pagination_links.append(absolute_url)

        # Переходим по страницам пагинации
        for url in set(pagination_links):
            yield scrapy.Request(
                url,
                callback=self.parse,
                meta={'playwright': self.use_playwright}
            )

    def parse_wine_item(self, response):
        """Парсинг карточки винного товара"""

        self.logger.info(f"PARSING PRODUCT: {response.url}")

        # Проверяем, что это действительно страница товара
        if '/product/' not in response.url:
            return

        # Название - берем из H1
        name = response.css('h1::text').get()
        if not name:
            self.logger.warning(f"No H1 at {response.url}")
            return

        name = name.strip()
        self.logger.info(f"Name: {name}")

        # Винтаж - ищем год в названии
        vintage = None
        match = re.search(r'\b(19|20)\d{2}\b', name)
        if match:
            vintage = int(match.group())
            self.logger.info(f"Vintage: {vintage}")

        # Цена
        price = None
        currency = None

        # Пробуем meta теги
        price_meta = response.css('meta[itemprop="price"]::attr(content)').get()
        if price_meta:
            try:
                price = float(price_meta)
                currency = response.css('meta[itemprop="priceCurrency"]::attr(content)').get()
                self.logger.info(f"Price (meta): {price} {currency}")
            except:
                pass

        # Если нет в meta, ищем в тексте
        if price is None:
            text = response.css('body').get('')
            patterns = [
                (r'(\d+[.,]\d+|\d+)\s*€', 'EUR'),
                (r'(\d+[.,]\d+|\d+)\s*\$', 'USD'),
                (r'(\d+[.,]\d+|\d+)\s*£', 'GBP'),
                (r'(\d+[.,]\d+|\d+)\s*₽', 'RUB'),
            ]

            for pattern, curr in patterns:
                match = re.search(pattern, text)
                if match:
                    price_str = match.group(1).replace(',', '.')
                    try:
                        price = float(price_str)
                        currency = curr
                        self.logger.info(f"Price (text): {price} {currency}")
                        break
                    except:
                        pass

        # Наличие
        availability = 'in_stock'
        text_lower = response.css('body').get('').lower()
        if 'out of stock' in text_lower or 'нет в наличии' in text_lower:
            availability = 'out_of_stock'
        self.logger.info(f"Availability: {availability}")

        # Изображение
        image = response.css('meta[property="og:image"]::attr(content)').get()
        if not image:
            image = response.css('img::attr(src)').get()
        if image and not image.startswith('http'):
            image = response.urljoin(image)
        self.logger.info(f"Image: {image}")

        # Объем
        volume = '750ml'
        vol_match = re.search(r'(\d+)\s*(ml|мл|l|л)', text_lower)
        if vol_match:
            val = vol_match.group(1)
            unit = vol_match.group(2)
            if unit in ['l', 'л']:
                volume = f"{float(val) * 1000}ml"
            else:
                volume = f"{val}ml"
            self.logger.info(f"Volume: {volume}")

        item = {
            'name': name,
            'vintage': vintage,
            'availability': availability,
            'image_url': image,
            'price': price,
            'currency': currency,
            'bottle_volume': volume,
            'bottle_quantity': 1,
            'url': response.url,
            'domain': urlparse(response.url).netloc,
            'scraped_at': datetime.now().isoformat(),
            'parser_mode': self.mode,
            'used_playwright': self.use_playwright
        }

        self.logger.info(f"COLLECTED: {name}")
        yield item