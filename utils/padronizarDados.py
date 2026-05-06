import polars as pl
import unicodedata
# Padronmização de dados para facilitar análises e evitar problemas de encoding, acentos, etc.

def _remove_acentos(texto: str) -> str:
    if texto is None:
        return texto
    return unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode("ascii")


def clean_column_names(df: pl.DataFrame) -> pl.DataFrame:
    """
    Padroniza nomes das colunas:
    - remove acentos
    - lowercase
    - troca espaços por underscore
    """
    new_cols = [
        _remove_acentos(col)
        .lower()
        .replace(" ", "_")
        .replace(".", "")
        .replace("-", "_")
        for col in df.columns
    ]
    return df.rename(dict(zip(df.columns, new_cols)))


def strip_string_columns(df: pl.DataFrame) -> pl.DataFrame:
    """
    Remove espaços extras nas colunas texto
    """
    return df.with_columns(
        [
            pl.col(col).str.strip_chars()
            for col, dtype in zip(df.columns, df.dtypes)
            if dtype == pl.Utf8
        ]
    )


def fix_encoding(df: pl.DataFrame) -> pl.DataFrame:
    """
    Remove caracteres quebrados de encoding
    """
    return df.with_columns(
        [
            pl.col(col).map_elements(
                lambda x: _remove_acentos(x) if isinstance(x, str) else x
            )
            for col, dtype in zip(df.columns, df.dtypes)
            if dtype == pl.Utf8
        ]
    )


def clean_dataframe(df: pl.DataFrame) -> pl.DataFrame:
    """
    Pipeline completo de limpeza
    """
    df = clean_column_names(df)
    df = strip_string_columns(df)
    df = fix_encoding(df)
    return df