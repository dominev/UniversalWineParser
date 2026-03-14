# test_server.py
"""
Простой тестовый сервер с винной продукцией для отладки парсера
Запуск: python test_server.py
"""

from flask import Flask, render_template_string, jsonify
import random
from datetime import datetime

app = Flask(__name__)

# Тестовые данные о винах
wines = [
    {
        "id": 1,
        "name": "Château Margaux",
        "vintage": 2015,
        "price": 850.0,
        "currency": "EUR",
        "volume": "750ml",
        "in_stock": True,
        "image": "/static/images/margaux.jpg",
        "description": "Grand Cru Classé, Bordeaux"
    },
    {
        "id": 2,
        "name": "Sassicaia",
        "vintage": 2018,
        "price": 320.0,
        "currency": "EUR",
        "volume": "750ml",
        "in_stock": True,
        "image": "/static/images/sassicaia.jpg",
        "description": "Bolgheri Sassicaia DOC, Tuscany"
    },
    {
        "id": 3,
        "name": "Dom Pérignon",
        "vintage": 2012,
        "price": 190.0,
        "currency": "EUR",
        "volume": "750ml",
        "in_stock": False,
        "image": "/static/images/dom.jpg",
        "description": "Champagne Vintage"
    },
    {
        "id": 4,
        "name": "Opus One",
        "vintage": 2016,
        "price": 350.0,
        "currency": "USD",
        "volume": "750ml",
        "in_stock": True,
        "image": "/static/images/opus.jpg",
        "description": "Napa Valley Bordeaux Blend"
    },
    {
        "id": 5,
        "name": "Vega Sicilia Único",
        "vintage": 2010,
        "price": 450.0,
        "currency": "EUR",
        "volume": "750ml",
        "in_stock": True,
        "image": "/static/images/vega.jpg",
        "description": "Ribera del Duero"
    },
    {
        "id": 6,
        "name": "Penfolds Grange",
        "vintage": 2017,
        "price": 800.0,
        "currency": "AUD",
        "volume": "750ml",
        "in_stock": True,
        "image": "/static/images/grange.jpg",
        "description": "South Australia Shiraz"
    }
]

# Категории вин
categories = [
    {"id": 1, "name": "Bordeaux", "count": 5},
    {"id": 2, "name": "Burgundy", "count": 3},
    {"id": 3, "name": "Champagne", "count": 2},
    {"id": 4, "name": "Italian", "count": 4},
    {"id": 5, "name": "Spanish", "count": 3},
    {"id": 6, "name": "New World", "count": 4}
]

# HTML шаблоны
INDEX_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Wine Shop - Тестовый магазин вин</title>
    <meta charset="utf-8">
    <style>
        body { font-family: Arial; margin: 0; padding: 20px; background: #f5f5f5; }
        .header { background: #8B0000; color: white; padding: 20px; margin-bottom: 20px; }
        .container { max-width: 1200px; margin: 0 auto; }
        .categories { background: white; padding: 15px; margin-bottom: 20px; border-radius: 5px; }
        .category { display: inline-block; margin: 0 10px; color: #8B0000; cursor: pointer; }
        .products { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; }
        .product { background: white; padding: 15px; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
        .product img { max-width: 100%; height: 200px; object-fit: cover; }
        .price { font-size: 20px; color: #8B0000; font-weight: bold; }
        .stock { color: green; }
        .out-of-stock { color: red; }
        .pagination { margin-top: 20px; text-align: center; }
        .page-link { display: inline-block; padding: 5px 10px; margin: 0 5px; background: white; text-decoration: none; color: #8B0000; }
        .footer { margin-top: 40px; text-align: center; color: #666; }
    </style>
</head>
<body>
    <div class="header">
        <div class="container">
            <h1>🍷 Тестовый винный магазин</h1>
            <p>Для отладки парсера - все данные вымышленные</p>
        </div>
    </div>

    <div class="container">
        <div class="categories">
            <h3>Категории:</h3>
            {% for cat in categories %}
            <span class="category">{{ cat.name }} ({{ cat.count }})</span>
            {% endfor %}
        </div>

        <div class="products">
            {% for wine in wines %}
            <div class="product" onclick="location.href='/product/{{ wine.id }}'">
                <img src="{{ wine.image }}" alt="{{ wine.name }}" onerror="this.src='https://via.placeholder.com/300x200?text=Wine'">
                <h3>{{ wine.name }} {{ wine.vintage }}</h3>
                <p>{{ wine.description[:50] }}...</p>
                <div class="price">{{ wine.price }} {{ wine.currency }}</div>
                <div class="{% if wine.in_stock %}stock{% else %}out-of-stock{% endif %}">
                    {% if wine.in_stock %}✓ В наличии{% else %}✗ Нет в наличии{% endif %}
                </div>
                <small>{{ wine.volume }}</small>
            </div>
            {% endfor %}
        </div>

        <div class="pagination">
            <a href="/catalog?page=1" class="page-link">1</a>
            <a href="/catalog?page=2" class="page-link">2</a>
            <a href="/catalog?page=3" class="page-link">3</a>
            <a href="/catalog?page=4" class="page-link">4</a>
            <a href="/catalog?page=5" class="page-link">5</a>
        </div>

        <div class="footer">
            <p>Тестовые данные для проверки парсера | Все цены и наличие вымышленные</p>
            <p><a href="/sitemap.xml">Sitemap</a> | <a href="/catalog">Каталог</a> | <a href="/api/wines">API</a></p>
        </div>
    </div>
</body>
</html>
"""

PRODUCT_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>{{ wine.name }} {{ wine.vintage }} - Тестовый магазин</title>
    <meta property="og:title" content="{{ wine.name }} {{ wine.vintage }}">
    <meta property="og:image" content="{{ wine.image }}">
    <meta property="og:url" content="/product/{{ wine.id }}">
    <meta itemprop="name" content="{{ wine.name }}">
    <meta itemprop="price" content="{{ wine.price }}">
    <meta itemprop="priceCurrency" content="{{ wine.currency }}">
    <meta itemprop="availability" content="{% if wine.in_stock %}InStock{% else %}OutOfStock{% endif %}">
    <meta itemprop="image" content="{{ wine.image }}">
    <style>
        body { font-family: Arial; padding: 20px; background: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }
        .product-image { max-width: 400px; height: auto; }
        .price { font-size: 28px; color: #8B0000; }
        .stock { padding: 10px; border-radius: 5px; }
        .in-stock { background: #d4edda; color: #155724; }
        .out-of-stock { background: #f8d7da; color: #721c24; }
        .specs { margin-top: 20px; border-top: 1px solid #ddd; padding-top: 20px; }
        .back-link { display: block; margin-top: 20px; color: #8B0000; }
    </style>
</head>
<body>
    <div class="container">
        <h1>{{ wine.name }} <span class="vintage">{{ wine.vintage }}</span></h1>

        <img src="{{ wine.image }}" class="product-image" onerror="this.src='https://via.placeholder.com/400x400?text=Wine'">

        <div class="price">{{ wine.price }} {{ wine.currency }}</div>

        <div class="stock {% if wine.in_stock %}in-stock{% else %}out-of-stock{% endif %}">
            {% if wine.in_stock %}
                <span class="availability">В наличии</span>
            {% else %}
                <span class="availability">Нет в наличии</span>
            {% endif %}
        </div>

        <div class="specs">
            <h3>Характеристики:</h3>
            <ul>
                <li class="volume">Объем: {{ wine.volume }}</li>
                <li>Винтаж: {{ wine.vintage }}</li>
                <li>Страна: {{ wine.description.split(',')[0] }}</li>
                <li class="min-order">Минимальный заказ: 1 бутылка</li>
            </ul>
        </div>

        <a href="/" class="back-link">← Назад к каталогу</a>
    </div>
</body>
</html>
"""

SITEMAP_TEMPLATE = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    {% for wine in wines %}
    <url>
        <loc>http://localhost:5000/product/{{ wine.id }}</loc>
        <lastmod>{{ now }}</lastmod>
        <changefreq>monthly</changefreq>
        <priority>0.8</priority>
    </url>
    {% endfor %}
    <url>
        <loc>http://localhost:5000/catalog</loc>
        <lastmod>{{ now }}</lastmod>
        <changefreq>daily</changefreq>
        <priority>0.5</priority>
    </url>
</urlset>
"""


@app.route('/')
def index():
    """Главная страница с каталогом"""
    page = int(request.args.get('page', 1))
    per_page = 6
    start = (page - 1) * per_page
    end = start + per_page
    paginated_wines = wines[start:end]

    return render_template_string(
        INDEX_TEMPLATE,
        wines=paginated_wines,
        categories=categories,
        page=page
    )


@app.route('/catalog')
def catalog():
    """Страница каталога"""
    return index()


@app.route('/product/<int:product_id>')
def product(product_id):
    """Страница товара"""
    wine = next((w for w in wines if w['id'] == product_id), None)
    if wine:
        return render_template_string(PRODUCT_TEMPLATE, wine=wine)
    return "Wine not found", 404


@app.route('/sitemap.xml')
def sitemap():
    """Sitemap для тестирования"""
    from flask import request, make_response
    now = datetime.now().date().isoformat()

    sitemap_content = render_template_string(SITEMAP_TEMPLATE, wines=wines, now=now)
    response = make_response(sitemap_content)
    response.headers['Content-Type'] = 'application/xml'
    return response


@app.route('/api/wines')
def api_wines():
    """API для получения списка вин"""
    return jsonify(wines)


@app.route('/api/wine/<int:product_id>')
def api_wine(product_id):
    """API для получения конкретного вина"""
    wine = next((w for w in wines if w['id'] == product_id), None)
    if wine:
        return jsonify(wine)
    return jsonify({"error": "Not found"}), 404


@app.route('/static/images/<path:filename>')
def static_images(filename):
    """Заглушка для изображений"""
    from flask import send_file
    from io import BytesIO
    from PIL import Image, ImageDraw, ImageFont

    # Создаем заглушку изображения
    img = Image.new('RGB', (300, 200), color='#8B0000')
    d = ImageDraw.Draw(img)
    d.text((150, 100), filename.replace('.jpg', '').replace('.png', ''), fill='white', anchor='mm')

    img_io = BytesIO()
    img.save(img_io, 'JPEG')
    img_io.seek(0)

    return send_file(img_io, mimetype='image/jpeg')


if __name__ == '__main__':
    from flask import request

    print("\n" + "=" * 50)
    print("🍷 ТЕСТОВЫЙ ВИННЫЙ МАГАЗИН ЗАПУЩЕН")
    print("=" * 50)
    print("\n📌 Доступные URL:")
    print("  • Главная: http://localhost:5000/")
    print("  • Каталог: http://localhost:5000/catalog")
    print("  • Sitemap: http://localhost:5000/sitemap.xml")
    print("  • API: http://localhost:5000/api/wines")
    print("\n🍷 Примеры товаров:")
    for wine in wines[:3]:
        print(f"  • {wine['name']} {wine['vintage']}: http://localhost:5000/product/{wine['id']}")
    print("\n" + "=" * 50)
    print("🚀 Для остановки нажмите Ctrl+C")
    print("=" * 50 + "\n")

    app.run(debug=True, port=5000)