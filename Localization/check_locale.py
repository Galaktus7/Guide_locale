import os
import json
import yaml
import pathlib
import difflib
import re

ALLOW_IDENTICAL_TRANSLATIONS = {
    'uk': True
}

ALLOW_SIMILAR_TRANSLATIONS = {
    'uk': 0.98
}

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

def extract_numbers(text):
    return re.findall(r"\d+(?:\.\d+)?%?", text)

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
        print(f"\n📁 Проверка текста: {rel_path or '/'}")

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

            # Словарь для хранения проблемных ключей:
            # key -> list of (lang, similarity, target_value)
            outdated_by_key = {}
            same_text_keys = []

            for k in ref_keys & set(data.keys()):
                ref_value = str(ref_data[k]).strip()
                target_value = str(data[k]).strip()

                if ref_value == target_value:
                    if not ALLOW_IDENTICAL_TRANSLATIONS.get(lang, False):
                        same_text_keys.append(k)
                    continue

                similarity = difflib.SequenceMatcher(None, ref_value, target_value).ratio()
                threshold = ALLOW_SIMILAR_TRANSLATIONS.get(lang, 0.9)

                ref_numbers = extract_numbers(ref_value)
                target_numbers = extract_numbers(target_value)
                numbers_differ = (ref_numbers != target_numbers) and ref_numbers and target_numbers

                if similarity < 0.85:
                    continue  # игнорируем очень разные переводы

                if numbers_differ:
                    outdated_by_key.setdefault(k, []).append((lang, similarity, target_value))
                    continue  # если числа не совпадают, считаем подозрительным

                if similarity > threshold or (lang == 'uk' and similarity > 0.9):
                    continue  # слишком похожие — норм

                # если попали сюда — схожесть от 0.85 до порога, и числа совпадают
                outdated_by_key.setdefault(k, []).append((lang, similarity, target_value))

            # Вывод результатов сгруппировано по ключам
            if not same_text_keys and not outdated_by_key:
                print(f" 🔸 {lang}.{'yaml' if path.endswith('.yaml') else 'json'}:")
                print("   ✅ Всё хорошо: переводы различаются, как и должно быть")
                continue

            # Сначала подозрительно идентичные переводы (если есть)
            if same_text_keys:
                print(f" 🔸 {lang}.{'yaml' if path.endswith('.yaml') else 'json'}:")
                print(f"   ⚠️ Подозрительно идентичные переводы ({len(same_text_keys)}):")
                for key in sorted(same_text_keys):
                    print(f"     🔸 {key} = '{ref_data[key]}'")

            # Затем подозрение на устаревшие переводы по ключам
            if outdated_by_key:
                for key, lang_data_list in sorted(outdated_by_key.items()):
                    print(f"\n     🔸 {key}")
                    print(f"        ru: {ref_data[key][:80]}{'…' if len(ref_data[key]) > 80 else ''}")
                    for lang_, score, val in sorted(lang_data_list, key=lambda x: x[1], reverse=True):
                        print(f"   🟣 {lang_}.json: (схожесть {score:.1%})")
                        print(f"        ▪️ {lang_}: {val[:80]}{'…' if len(val) > 80 else ''}")

if __name__ == "__main__":
    main()
