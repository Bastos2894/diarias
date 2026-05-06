from sqlalchemy import create_engine
from utils.config_loader import load_config
# função para criar a engine de conexão com o banco de dados, usando as informações do arquivo de configuração
def _LOADget_engine():
    config = load_config("config/database.yaml")  
    db = config["database"]

    required_keys = ["driver", "host", "port", "name", "user", "password"]

    for key in required_keys:
        if key not in db:
            raise ValueError(f"Falta a chave '{key}' no config")

    connection_string = (
        f"{db['driver']}://{db['user']}:{db['password']}"
        f"@{db['host']}:{db['port']}/{db['name']}"
    )

   

    return create_engine(connection_string)