import pandas as pd 
import polars as pl

def tratar_arquivo(caminho_arquivo):
    df = pd.read_excel(caminho_arquivo)

    # padronizar colunas

    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )

    # converte para polars
    df_pl = pl.from_pandas(df)

    # exemplo de tratamento
    df_pl = df_pl.with_columns(
        pl.all().exclude(pl.Utf8).fill_null(0)
    )

    return df_pl
