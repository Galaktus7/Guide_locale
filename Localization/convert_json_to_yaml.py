import json
import yaml
import sys


def json_to_yaml(json_file, yaml_file):
    with open(json_file, "r", encoding="utf-8") as jf:
        data = json.load(jf)
    with open(yaml_file, "w", encoding="utf-8") as yf:
        yaml.dump(data, yf, allow_unicode=True, sort_keys=False)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage:"
              "python Localization/convert_json_to_yaml.py Localization/Unique_weapons/ru.json Localization/Unique_weapons/ru.yaml"
              )
    else:
        json_to_yaml(sys.argv[1], sys.argv[2])
