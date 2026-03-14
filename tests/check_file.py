import json
import sys

filename = sys.argv[1] if len(sys.argv) > 1 else "wines_crawl_localhost_5000_20260314_125801.json"

try:
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
        print(f"Содержимое файла ({len(content)} байт):")
        print("-" * 40)
        print(content)
        print("-" * 40)

        if content.strip():
            data = json.loads(content)
            print(f"\n JSON корректен!")
            print(f"Количество записей: {len(data)}")
            if len(data) > 0:
                print("\nПервая запись:")
                print(json.dumps(data[0], indent=2, ensure_ascii=False))
        else:
            print("!!! Файл пустой!")

except Exception as e:
    print(f"!!! Ошибка: {e}")