import json
import glob
from collections import defaultdict


def check_results():

    """Проверяет все тестовые файлы"""

    print("=" * 60)
    print("🔍 ПРОВЕРКА РЕЗУЛЬТАТОВ ТЕСТИРОВАНИЯ")
    print("=" * 60)

    all_files = glob.glob("test_results/*.json")

    if not all_files:
        print("!!! Нет файлов для проверки!")
        return

    stats = defaultdict(lambda: {"count": 0, "files": []})

    for file in all_files:
        try:
            with open(file, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if content.startswith('[') and content.endswith(']'):
                    data = json.loads(content)
                    count = len(data)
                else:
                    # JSON lines format
                    lines = [json.loads(line) for line in content.split('\n') if line.strip()]
                    data = lines
                    count = len(lines)

                stats[file]["count"] = count
                stats[file]["size"] = len(content)
                stats[file]["sample"] = data[0] if count > 0 else None

        except Exception as e:
            print(f"!!! Ошибка в {file}: {e}")

    # Вывод статистики
    print("\n СТАТИСТИКА ПО ФАЙЛАМ:")
    print("-" * 60)

    for file, info in stats.items():
        status = "✅" if info["count"] > 0 else "⚠️"
        print(f"{status} {file}: {info['count']} записей, {info['size']} байт")

        if info["sample"]:
            print(f"   Пример: {json.dumps(info['sample'], ensure_ascii=False)[:100]}...")

    print("\n" + "=" * 60)

    # Проверка обязательных полей
    required_fields = ['name', 'url', 'price']
    print("\n🔎 ПРОВЕРКА ОБЯЗАТЕЛЬНЫХ ПОЛЕЙ:")

    for file, info in stats.items():
        if info["sample"]:
            missing = [f for f in required_fields if f not in info["sample"]]
            if missing:
                print(f"⚠️ {file}: отсутствуют поля {missing}")
            else:
                print(f"✅ {file}: все поля присутствуют")


if __name__ == "__main__":
    check_results()