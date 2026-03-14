import scrapy

class WineItem(scrapy.Item):
    """Модель данных для винного товара"""
    name = scrapy.Field()
    vintage = scrapy.Field()
    availability = scrapy.Field()
    image_url = scrapy.Field()
    price = scrapy.Field()
    currency = scrapy.Field()
    bottle_volume = scrapy.Field()
    bottle_quantity = scrapy.Field()
    url = scrapy.Field()
    scraped_at = scrapy.Field()