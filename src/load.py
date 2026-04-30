from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

load_dotenv()

def get_engine():
    return create_engine(
        f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@"
        f"{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    )

def salvar(df_polars, tabela):

    engine = get_engine()

    df_pandas = df_polars.to_pandas()

    df_pandas.to_sql(
        tabela,
        engine,
        if_exists = "append",
        index = False
    )

    print(f"[OK] Dados salvos na tabela {tabela}.")