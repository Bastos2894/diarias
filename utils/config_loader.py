import os
import yaml
from dotenv import load_dotenv

def load_config(path):
    load_dotenv(override=True)

    with open(path, "r") as f:
        config = yaml.safe_load(f)

    def resolve_env(value):
        if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
            env_var = value[2:-1]
            env_value = os.getenv(env_var)

            if env_value is None:
                raise ValueError(f"Variável de ambiente '{env_var}' não encontrada")

            return env_value
        return value

    def process_dict(d):
        for k, v in d.items():
            if isinstance(v, dict):
                process_dict(v)
            else:
                d[k] = resolve_env(v)

    process_dict(config)

    return config