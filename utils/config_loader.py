import yaml
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]


def load_config():
    config_path = BASE_DIR / "config" / "config.yaml"
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)