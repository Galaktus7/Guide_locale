import os
import json
import yaml
import pathlib


REFERENCE_LOCALE = "ru"
BASE_DIR = pathlib.Path(__file__).resolve().parent
LOCALE_ROOT = BASE_DIR
SUPPORTED_EXT = [".json", ".yaml", ".yml"]


def load_file(path):
    with open(path, encoding="utf-8") as f:
        if path.endswith(".json"):
            return json.load(f)
        elif path.endswith((".yaml", ".yml")):
            return yaml.safe_load(f)
    return {}


def compare_keys(ref_keys, test_keys):
    return ref_keys - test_keys, test_keys - ref_keys

def find_locale_files():
    files_by_folder = {}
    for root, _, files in os.walk(LOCALE_ROOT):
        relevant_files = [f for f in files if any(f.endswith(ext) for ext in SUPPORTED_EXT)]
        if not relevant_files:
            continue

        group = {}
        for f in relevant_files:
            lang = f.split('.')[0]
            group[lang] = os.path.join(root, f)
        files_by_folder[root] = group
    return files_by_folder


def main():
    all_groups = find_locale_files()

    for folder, group in all_groups.items():
        if REFERENCE_LOCALE not in group:
            print(f"\n⚠️ Пропущена папка {folder} — нет файла для {REFERENCE_LOCALE}")
            continue

        ref_data = load_file(group[REFERENCE_LOCALE])
        if not isinstance(ref_data, dict):
            print(f"❌ Ошибка: файл {group[REFERENCE_LOCALE]} не содержит словарь.")
            continue

        ref_keys = set(ref_data.keys())
        rel_path = os.path.relpath(folder, LOCALE_ROOT)
        print(f"\n📁 Проверка: {rel_path or '/'}")

        for lang, path in group.items():
            if lang == REFERENCE_LOCALE:
                continue

            try:
                data = load_file(path)
            except Exception as e:
                print(f"❌ Не удалось прочитать {path}: {e}")
                continue

            if not isinstance(data, dict):
                print(f"❌ Ошибка: файл {path} не содержит словарь.")
                continue

            keys = set(data.keys())
            missing, extra = compare_keys(ref_keys, keys)

            print(f" 🔸 {lang}.{'yaml' if path.endswith('.yaml') else 'json'}:")
            if not missing and not extra:
                print("   ✅ Ключи совпадают")
            else:
                if missing:
                    print(f"   ❗ Отсутствуют ключи: {sorted(missing)}")
                if extra:
                    print(f"   ⚠️ Лишние ключи: {sorted(extra)}")


if __name__ == "__main__":
    main()
