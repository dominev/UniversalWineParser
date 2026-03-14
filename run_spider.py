#!/usr/bin/env python
"""
Запуск паука
"""
import argparse
import subprocess
import sys
import os
from datetime import datetime

def main():
    parser = argparse.ArgumentParser(description='Запуск парсера')

    parser.add_argument('--mode', type=str, default='crawl',
                        choices=['crawl', 'urls'],
                        help='Режим работы: crawl (по умолчанию), urls')

    parser.add_argument('--domain', type=str,
                        help='Домен для парсинга (например: localhost:5000)')

    parser.add_argument('--url', type=str,
                        help='URL для парсинга (одиночный)')

    parser.add_argument('--urls', type=str,
                        help='Список URL через запятую')

    parser.add_argument('--js', action='store_true',
                        help='Использовать Playwright для JS')

    parser.add_argument('--delay', type=float, default=2.0,
                        help='Задержка между запросами (секунд)')

    parser.add_argument('--output', type=str,
                        help='Имя выходного файла')

    parser.add_argument('--limit', type=int, default=0,
                        help='Ограничение на количество товаров')

    args = parser.parse_args()

    print("=" * 60)
    print("🍷 Wine-parser")
    print("=" * 60)

    # Формирование
    if not args.output:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        domain_part = f"_{args.domain.replace(':', '_')}" if args.domain else ""
        js_part = "_js" if args.js else ""
        args.output = f"wines_{args.mode}{domain_part}{js_part}_{timestamp}.json"

    # Wine_hybrid
    cmd = ['scrapy', 'crawl', 'wine_hybrid', '-o', args.output]

    if args.domain:
        cmd.extend(['-a', f'domain={args.domain}'])

    if args.mode == 'urls' and args.urls:
        cmd.extend(['-a', f'urls={args.urls}'])
        cmd.extend(['-a', 'mode=urls'])

    # Параметр use_playwright если включен JS
    if args.js:
        cmd.extend(['-a', 'use_playwright=True'])
        # Также можно передать как строку
        # cmd.extend(['-a', 'use_playwright=1'])

    # Настройки Scrapy
    cmd.extend(['-s', f'DOWNLOAD_DELAY={args.delay}'])
    if args.limit > 0:
        cmd.extend(['-s', f'CLOSESPIDER_ITEMCOUNT={args.limit}'])

    # Для отладки доступно логирование - cmd.extend(['-s', 'LOG_LEVEL=DEBUG'])

    # Вывод информации
    print(f"\n Параметры запуска:")
    print(f"  Режим: {args.mode}")
    print(f"  Домен: {args.domain if args.domain else 'не указан'}")
    print(f"  Задержка: {args.delay} сек")
    print(f"  Лимит: {args.limit if args.limit > 0 else 'без ограничений'}")
    print(f"  JavaScript: {'ВКЛЮЧЕН (Playwright)' if args.js else 'ВЫКЛЮЧЕН'}")
    print(f"  Выходной файл: {args.output}")

    print(f"\n🕷️ Запуск паука...")
    print("-" * 60)
    print(f"Команда: {' '.join(cmd)}")
    print("-" * 60)

    try:
        # Запуск Scrapy
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            print(f"\n Парсинг успешно завершен!")
            print(f"Результаты сохранены в: {args.output}")

            if os.path.exists(args.output):
                size = os.path.getsize(args.output)
                print(f"Размер файла: {size:,} байт")

                try:
                    with open(args.output, 'r', encoding='utf-8') as f:
                        content = f.read().strip()
                        if content.startswith('[') and content.endswith(']'):
                            import json
                            data = json.loads(content)
                            line_count = len(data)
                            print(f"Записей собрано: {line_count}")

                            if line_count > 0:
                                print(f"\n Пример первой записи:")
                                print(json.dumps(data[0], indent=2, ensure_ascii=False)[:200] + "...")
                        else:
                            line_count = len([l for l in content.split('\n') if l.strip()])
                            print(f"Записей собрано: {line_count}")
                except Exception as e:
                    print(f"Ошибка чтения файла: {e}")
        else:
            print(f"\n Ошибка при выполнении:")
            print(result.stderr)
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n\n Парсинг прерван пользователем")
        sys.exit(0)
    except Exception as e:
        print(f"\n Ошибка: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()