import pandas as pd
import unicodedata


# =========================
# REMOVE ACENTOS
# =========================
def _remove_acentos(texto: str) -> str:

    if texto is None:
        return texto

    return (
        unicodedata
        .normalize("NFKD", str(texto))
        .encode("ascii", "ignore")
        .decode("ascii")
    )


# =========================
# PADRONIZA NOMES DE COLUNAS
# =========================
def clean_column_names(df: pd.DataFrame) -> pd.DataFrame:

    df.columns = [

        _remove_acentos(col)
        .lower()
        .strip()
        .replace(" ", "_")
        .replace(".", "")
        .replace("-", "_")

        for col in df.columns
    ]

    return df


# =========================
# REMOVE ESPAÇOS EXTRAS
# =========================
def strip_string_columns(df: pd.DataFrame) -> pd.DataFrame:

    colunas_texto = df.select_dtypes(
        include="object"
    ).columns

    for col in colunas_texto:

        df[col] = (
            df[col]
            .astype(str)
            .str.strip()
        )

    return df


# =========================
# CORRIGE ENCODING
# =========================
def fix_encoding(df: pd.DataFrame) -> pd.DataFrame:

    colunas_texto = df.select_dtypes(
        include="object"
    ).columns

    for col in colunas_texto:

        df[col] = df[col].apply(
            lambda x:
                _remove_acentos(x)
                if isinstance(x, str)
                else x
        )

    return df


# =========================
# PIPELINE COMPLETO
# =========================
def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:

    df = clean_column_names(df)

    df = strip_string_columns(df)

    df = fix_encoding(df)

    return df