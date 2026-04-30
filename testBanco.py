from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

load_dotenv()

engine = create_engine(
    f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)

conn = engine.connect()
print("Conexão bem-sucedida!")
# COLA
# DB_HOST=localhost
# DB_PORT=5433
# DB_NAME=postgres
# DB_USER=XXXXXXX
# DB_PASSWORD=XXXXXX