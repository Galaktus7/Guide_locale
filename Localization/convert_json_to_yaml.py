import json
import yaml
import sys
import os

def json_to_yaml(json_file, yaml_file):
    with open(json_file, "r", encoding="utf-8") as jf:
        data = json.load(jf)
    with open(yaml_file, "w", encoding="utf-8") as yf:
        yaml.dump(data, yf, allow_unicode=True, sort_keys=False)
    print(f"[✓] Converted: {json_file} → {yaml_file}")

def batch_convert_json_to_yaml(directory):
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".json"):
                json_path = os.path.join(root, file)
                yaml_path = json_path[:-5] + ".yaml"
                try:
                    json_to_yaml(json_path, yaml_path)
                except Exception as e:
                    print(f"[!] Failed: {json_path} → {e}")

if __name__ == "__main__":
    if len(sys.argv) == 3:
        # Ручной режим
        json_to_yaml(sys.argv[1], sys.argv[2])
    elif len(sys.argv) == 2:
        # Автоматическая пакетная конвертация из указанной директории
        batch_convert_json_to_yaml(sys.argv[1])

        #   ru    uk    en
        #   Abilities   Boss_fight  Buttons     Dungeons    Effect  Items   Melee_weapons   No_topic    Range_weapons
        #   Spellcaster   Unique_weapons
        #   python Localization/convert_json_to_yaml.py Localization/Unique_weapons/
