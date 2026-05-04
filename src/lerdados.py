import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

import polars as pl
import pandas as pd

from utils.style_planilhas import style_planilhas
from utils.data_padrao import clean_dataframe
from utils.config_loader import load_config

# =========================
# CONFIG
# =========================
BASE_DIR = Path(__file__).resolve().parents[1]
CONFIG = load_config()

ENTRADA_DIR = BASE_DIR / CONFIG["paths"]["input"]
OUTPUT_DIR = BASE_DIR / CONFIG["paths"]["output"]

ENTIDADE = CONFIG["filtro"]["entidade"]

PROCESSAMENTO = CONFIG["Processamento"]

FORMATOS = [f.lower() for f in PROCESSAMENTO["formatos_aceitos"]]
DELETAR = PROCESSAMENTO["deletar_apos_processamento"]
REMOVER_DUPLICADOS = PROCESSAMENTO["remover_duplicados"]
COLUNA_CHAVE = PROCESSAMENTO["coluna_chave"]

NOME_SAIDA = CONFIG["excel"]["nome_saida"]
ARQUIVO_SAIDA = OUTPUT_DIR / NOME_SAIDA

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# =========================
# FUNÇÕES
# =========================

def listar_arquivos():
    arquivos = [
        f for f in ENTRADA_DIR.iterdir()
        if f.is_file() and f.suffix.lower() in FORMATOS
    ]

    if not arquivos:
        print(f"Nenhum arquivo encontrado em: {ENTRADA_DIR}")

    print(f"Arquivos encontrados: {len(arquivos)}")
    return arquivos


def ler_arquivo(caminho: Path) -> pl.DataFrame:
    try:
        if caminho.suffix == ".html":
            df_pd = pd.read_html(caminho)[0]
            return pl.from_pandas(df_pd)

        elif caminho.suffix in [".xlsx", ".xls"]:
            try:
                return pl.read_excel(caminho)

            except Exception:
                print(f"⚠️ Lendo como HTML: {caminho.name}")
                df_pd = pd.read_html(caminho)[0]
                return pl.from_pandas(df_pd)

        elif caminho.suffix == ".csv":
            return pl.read_csv(caminho)

        else:
            raise ValueError(f"Formato não suportado: {caminho.name}")

    except Exception as e:
        raise RuntimeError(f"Erro ao ler arquivo {caminho.name}: {e}")


def aplicar_filtro(df: pl.DataFrame) -> pl.DataFrame:
    if ENTIDADE:
        if "Entidade" not in df.columns:
            raise ValueError("Coluna 'Entidade' não encontrada.")

        df = df.filter(pl.col("Entidade") == ENTIDADE)

    return df

def processar_arquivo(caminho: Path) -> pl.DataFrame:
   

    df = ler_arquivo(caminho)
    df = aplicar_filtro(df)
    df = clean_dataframe(df)

    # 🔥 padroniza tipos 
    df = df.with_columns([
        pl.col(col).cast(pl.Utf8) for col in df.columns
    ])
    print(f"Shape antes limpeza: {df.shape}")


    df = df.with_columns([
        pl.lit(caminho.name).alias("arquivo_origem")
    ])
    
    print(f"Processando: {caminho.name}")
    print(f"Shape depois limpeza: {df.shape}")
    

    return df


def salvar_excel(df: pl.DataFrame):
    
    
    df.write_excel(ARQUIVO_SAIDA)
    style_planilhas(ARQUIVO_SAIDA)
    print(f"Arquivo salvo em: {ARQUIVO_SAIDA}")
    print("Resumo final:")
    print(f"Linhas: {df.height}")
    print(f"Colunas: {df.width}")
    print(df.head(3))


# =========================
# MAIN
# =========================

def main():
    print("🚀 SCRIPT INICIADO")

    print(f"Entrada: {ENTRADA_DIR.resolve()}")
    print(f"Formatos: {FORMATOS}")



    if not ENTRADA_DIR.exists():
        raise FileNotFoundError(f"Pasta não encontrada: {ENTRADA_DIR}")

    arquivos = listar_arquivos()
    dfs = []
    
    arquivos_processados = []

    for arquivo in arquivos:
        try:
            df = processar_arquivo(arquivo)
            if df.height > 0:
                dfs.append(df)
            else:
                print(f"DataFrame vazio ignorado: {arquivo.name}")

            arquivos_processados.append(arquivo)

        except Exception as e:
            print(f"Erro ao processar {arquivo.name}: {e}")

    if dfs:
        try:
            df_final = pl.concat(dfs, how="diagonal")

            if REMOVER_DUPLICADOS:
                if COLUNA_CHAVE in df_final.columns:
                    df_final = df_final.unique(subset=[COLUNA_CHAVE])

            salvar_excel(df_final)

            
            if DELETAR:
                for arquivo in arquivos_processados:
                    arquivo.unlink()
                    print(f"Arquivo deletado: {arquivo.name}")
                
                    if arquivo.suffix == ".py":
                        print(f"⚠️ Ignorando arquivo Python: {arquivo.name}")
                        continue
                
                

        except Exception as e:
            print(f"Erro ao consolidar/salvar: {e}")
            print("⚠️ Nenhum arquivo foi deletado.")

    else:
        print("Nenhum arquivo processado com sucesso.")
if __name__ == "__main__":
    main()

print(ENTRADA_DIR.resolve())
print(FORMATOS)
print(list(ENTRADA_DIR.iterdir()))