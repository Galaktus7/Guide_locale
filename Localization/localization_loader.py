# localization_loader.py

import os
import json
import yaml
from pathlib import Path

# True - включено, False - Выключено
# Два False - всё выключено, два True - не включать, ебанёт
SYNC_YAML_TO_JSON = False   # Обновлять JSON из YAML
SYNC_JSON_TO_YAML = False  # Обновлять YAML из JSON

SYNC_ENABLED = SYNC_YAML_TO_JSON or SYNC_JSON_TO_YAML



def load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_yaml(path: Path) -> dict:
    if not path.exists():
        return {}
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def save_json(data: dict, path: Path):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def save_yaml(data: dict, path: Path):
    with open(path, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, allow_unicode=True, sort_keys=False)

def sync_yaml_json(json_path: Path, yaml_path: Path) -> dict:
    json_data = load_json(json_path)
    yaml_data = load_yaml(yaml_path)

    if SYNC_YAML_TO_JSON and not SYNC_JSON_TO_YAML:
        # Приоритет YAML: обновляем JSON из YAML
        merged = {**json_data, **yaml_data}
        save_json(merged, json_path)
        save_yaml(merged, yaml_path)

    elif SYNC_JSON_TO_YAML and not SYNC_YAML_TO_JSON:
        # Приоритет JSON: обновляем YAML из JSON
        merged = {**yaml_data, **json_data}
        save_json(merged, json_path)
        save_yaml(merged, yaml_path)

    elif SYNC_YAML_TO_JSON and SYNC_JSON_TO_YAML:
        # Если оба True — синхронизируем так, чтобы файлы стали одинаковы,
        # можно например объединить с приоритетом YAML
        merged = {**json_data, **yaml_data}
        save_json(merged, json_path)
        save_yaml(merged, yaml_path)

    else:
        # Оба False — синхронизация отключена, возвращаем либо JSON либо YAML (json по умолчанию)
        return json_data if json_path.exists() else yaml_data

    return merged

def load_localization_file(path: str) -> dict:
    ext = os.path.splitext(path)[1].lower()
    p = Path(path)

    if ext == ".json":
        yaml_path = p.with_suffix(".yaml")
        if SYNC_ENABLED and yaml_path.exists():
            return sync_yaml_json(p, yaml_path, prefer='json')  # 👈 Добавлено
        return load_json(p)

    elif ext in [".yaml", ".yml"]:
        json_path = p.with_suffix(".json")
        if SYNC_ENABLED and json_path.exists():
            return sync_yaml_json(json_path, p, prefer='json')  # 👈 Добавлено
        return load_yaml(p)


    else:
        raise ValueError(f"Unsupported localization file format: {ext}")
