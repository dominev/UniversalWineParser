# playwright_middleware.py
"""
Поддержка Playwright
"""
from scrapy import signals
from scrapy.http import HtmlResponse
import asyncio
from playwright.async_api import async_playwright
import logging


class PlaywrightMiddleware:

    def __init__(self):
        self.playwright = None
        self.browser = None
        self.context = None
        self.logger = logging.getLogger(__name__)

    @classmethod
    def from_crawler(cls, crawler):
        middleware = cls()
        crawler.signals.connect(middleware.spider_opened, signals.spider_opened)
        crawler.signals.connect(middleware.spider_closed, signals.spider_closed)
        return middleware

    async def spider_opened(self, spider):
        """Инициализация"""
        self.logger.info("🚀 Запуск Playwright...")
        self.playwright = await async_playwright().start()

        # Настройки браузера
        self.browser = await self.playwright.chromium.launch(
            headless=True,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-web-security',
                '--disable-features=IsolateOrigins,site-per-process',
                '--disable-site-isolation-trials',
            ]
        )

        # Создаем контекст с реалистичными настройками
        self.context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            locale='ru-RU',
            timezone_id='Europe/Moscow',
            geolocation={'longitude': 37.6176, 'latitude': 55.7558},
            permissions=['geolocation'],
            extra_http_headers={
                'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
        )

        self.logger.info("✅ Playwright успешно запущен")

    async def spider_closed(self, spider):
        """Закрытие Playwright"""
        self.logger.info("🛑 Остановка Playwright...")
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        self.logger.info("👋 Playwright остановлен")

    async def process_request(self, request, spider):
        """
        Обработка запроса через Playwright
        """
        # Проверяем, нужно ли использовать Playwright для этого URL
        use_playwright = self._should_use_playwright(request, spider)

        if not use_playwright:
            return None

        self.logger.info(f"🌐 Загрузка через Playwright: {request.url}")

        try:
            # Создаем новую страницу
            page = await self.context.new_page()

            # Устанавливаем таймаут
            page.set_default_timeout(30000)  # 30 секунд

            # Перехватываем запросы для блокировки ненужных ресурсов
            await page.route("**/*", self._handle_route)

            # Переходим на страницу
            response = await page.goto(
                request.url,
                wait_until='networkidle',
                timeout=30000
            )

            if not response:
                await page.close()
                return None

            # Ждем загрузки контента
            await self._wait_for_content(page)

            # Прокручиваем страницу для загрузки lazy-контента
            await self._scroll_page(page)

            # Получаем HTML
            content = await page.content()

            # Закрываем страницу
            await page.close()

            # Создаем Scrapy Response
            return HtmlResponse(
                url=request.url,
                status=response.status,
                headers=response.headers,
                body=content.encode('utf-8'),
                request=request,
                encoding='utf-8'
            )

        except Exception as e:
            self.logger.error(f"!!! Ошибка Playwright для {request.url}: {str(e)}")
            return None

    def _should_use_playwright(self, request, spider):
        """
        Определяет, нужно ли использовать Playwright для URL
        """
        # Если в мета явно указано
        if request.meta.get('playwright', False):
            return True

        # Если паук имеет атрибут use_playwright
        if getattr(spider, 'use_playwright', False):
            return True

        # Проверяем по расширению файла
        if request.url.endswith(('.js', '.css', '.png', '.jpg', '.gif', '.pdf', '.svg', '.ico')):
            return False

        # Проверяем по признакам JavaScript-сайта
        js_indicators = getattr(spider, 'js_sites', [])
        for indicator in js_indicators:
            if indicator in request.url:
                return True

        return False

    async def _handle_route(self, route, request):
        """
        Обработка маршрутов
        """
        # Блокируем изображения, шрифты, стили для ускорения
        if request.resource_type in ['image', 'media', 'font', 'stylesheet']:
            await route.abort()
        else:
            await route.continue_()

    async def _wait_for_content(self, page):
        """
        Ожидание загрузки основного контента
        """
        try:
            # Ждем появления основных селекторов
            await page.wait_for_selector('body', timeout=5000)

            # Ждем окончания загрузки jQuery/Ajax если есть
            await page.wait_for_function('''
                () => {
                    if (window.jQuery) {
                        return jQuery.active == 0;
                    }
                    if (window.fetch) {
                        return true;
                    }
                    return document.readyState === 'complete';
                }
            ''', timeout=5000)

        except Exception as e:
            self.logger.debug(f"Ожидание контента прервано: {e}")

    async def _scroll_page(self, page):
        """
        Прокрутка страницы для загрузки контента
        """
        try:
            # Получаем высоту страницы
            height = await page.evaluate('document.body.scrollHeight')

            # Прокручиваем постепенно
            for i in range(0, height, 500):
                await page.evaluate(f'window.scrollTo(0, {i})')
                await asyncio.sleep(0.1)

            # Прокрутка вверх-вниз для активации всего
            await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
            await asyncio.sleep(0.5)
            await page.evaluate('window.scrollTo(0, 0)')

        except Exception as e:
            self.logger.debug(f"Ошибка при прокрутке: {e}")