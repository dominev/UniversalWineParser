#settings.py
BOT_NAME = 'wine_parser'

SPIDER_MODULES = ['wine_parser.spiders']
NEWSPIDER_MODULE = 'wine_parser.spiders'

# Обязательно
FEED_EXPORT_ENCODING = 'utf-8'
FEED_FORMAT = 'jsonlines'

# Настройки загрузки
DOWNLOAD_DELAY = 2
RANDOMIZE_DOWNLOAD_DELAY = True
CONCURRENT_REQUESTS = 16
CONCURRENT_REQUESTS_PER_DOMAIN = 8

# Повторные попытки
RETRY_ENABLED = True
RETRY_TIMES = 3
RETRY_HTTP_CODES = [500, 502, 503, 504, 408, 429]

# Таймауты
DOWNLOAD_TIMEOUT = 30

# Кеширование
HTTPCACHE_ENABLED = True
HTTPCACHE_EXPIRATION_SECS = 3600
HTTPCACHE_DIR = 'httpcache'

# User Agent
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'

# Пайплайны
ITEM_PIPELINES = {
    'wine_parser.pipelines.WineValidationPipeline': 100,
    'wine_parser.pipelines.DuplicatesPipeline': 200,
    # 'wine_parser.pipelines.WineJsonExportPipeline': 300,  # Закомментируйте если не нужен
}

# Логирование
LOG_LEVEL = 'INFO'