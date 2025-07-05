import yaml
import json
import sys


def yaml_to_json(yaml_file, json_file):
    with open(yaml_file, "r", encoding="utf-8") as yf:
        data = yaml.safe_load(yf)
    with open(json_file, "w", encoding="utf-8") as jf:
        json.dump(data, jf, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage:"
              "python Localization/convert_yaml_to_json.py Localization/en.yaml Localization/en.json"
              )
    else:
        yaml_to_json(sys.argv[1], sys.argv[2])
