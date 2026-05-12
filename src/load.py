# Script para ler o arquivo Excel, limpar os dados, exportar para CSV e inserir no banco de dados. O script também cria o schema no banco se ele não existir.
import pandas as pd
from pathlib import Path

from sqlalchemy import text
from utils.db import _LOADget_engine
from utils.config_loader import load_config

BASE_DIR = Path(__file__).resolve().parents[1]
CONFIG_DB = load_config("config/database.yaml")
CONFIG_APP = load_config("config/config.yaml")

ENTRADA = BASE_DIR / CONFIG_APP["paths"]["input"]
SAIDA = BASE_DIR / CONFIG_APP["paths"]["output"]
NOME_SAIDA = CONFIG_APP["CSV"]["nome_saida"]
ARQUIVO_SAIDA = SAIDA / NOME_SAIDA
def main():
    ENGINE = _LOADget_engine()
    SCHEMA = "diarias"

    # =========================
    # 1. LER DADOS
    # =========================
    df = pd.read_excel(ENTRADA)

    # =========================
    # 2. LIMPEZA
    # =========================

    # NOME DO SERVIDOR
    df['nome_do_servidor'] = (
        df['nome_do_servidor']
        .fillna('')
        .astype(str)
        .str.strip()
        .str.replace(r'\s+', ' ', regex=True)
        .str.title()
    )

    # TEXTOS
    colunas_texto = [
        'cargo', 'localidade', 'motivo', 'metas_previstas', 'resultados_obtidos', 'modelo', 'nmorgao'
    ]

    for col in colunas_texto:
        df[col] = (
            df[col]
            .fillna('')
            .astype(str)
            .str.strip()
            .str.replace(r'\s+', ' ', regex=True)
        )

    # DATAS
    colunas_datas = [
        'data_de_liberacao', 'data_de_partida', 'data_de_retorno', 'prestacao_de_contas'
    ]

    for col in colunas_datas:
        df[col] = pd.to_datetime(df[col], dayfirst=True, errors='coerce')


    # NÚMERICOS
    df['qtde_de_diarias'] = pd.to_numeric(df['qtde_de_diarias'], errors='coerce')
    
    def parse_moeda(col: pd.Series) -> pd.Series:
        col = (
            col.astype(str)
            .str.strip()
            .str.lower()
            .replace(['nan', 'none', ''], None)
        )

        col = col.str.replace(r'[^\d,.-]', '', regex=True)
        col = col.replace(['', '-', '.', ','], None)

        # usa na=False sempre
        if col.str.contains(',', na=False).any():
            col = col.str.replace('.', '', regex=False)
            col = col.str.replace(',', '.', regex=False)
            return pd.to_numeric(col, errors='coerce')

        return pd.to_numeric(col, errors='coerce')

    df['valor_das_diarias'] = parse_moeda(df['valor_das_diarias'])
    # INTEIROS
   
    df['idorgao'] =pd.to_numeric(df['idorgao'], errors='coerce').astype('Int64')

    # COLUNA AUXILIAR

    


    df = df.drop_duplicates()

    # =========================
    # 4. EXPORTAR CSV
    # =========================
    df.to_csv(
        ARQUIVO_SAIDA,
        index=False,
        sep=';',
        encoding='utf-8-sig'
    )
    # ========================
    # 5. CRIA O SCHEMA SE NÃO EXISTIR
    # =========================
    with ENGINE.connect() as conn:
        conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {SCHEMA};"))
        conn.commit()


    print(df.shape)
    print(df.head())
    # =========================
    # 6. INSERT NO BANCO (UMA TABELA SÓ)
    # =========================
    df.to_sql(
        "diarias",
        ENGINE,
        schema=SCHEMA,
        if_exists="replace",  # ou "append" se quiser acumular
        index=False,
        method="multi",
        chunksize=1000
    )

    print("✅ Tabela única criada com sucesso")
    print(df['valor_das_diarias'].isna().sum())

if __name__ == "__main__":
    main()