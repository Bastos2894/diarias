import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

import polars as pl
import pandas as pd


from utils.padronizarDados import clean_dataframe
from utils.config_loader import load_config
# =========================
# CONFIG
# =========================
BASE_DIR = Path(__file__).resolve().parents[1]
CONFIG = load_config("config/config.yaml")

ENTRADA_DIR = BASE_DIR / CONFIG["paths"]["input"]
OUTPUT_DIR = BASE_DIR / CONFIG["paths"]["output"]







NOME_SAIDA = CONFIG["excel"]["nome_saida"]
ARQUIVO_SAIDA = OUTPUT_DIR / NOME_SAIDA

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# =========================
# FUNÇÕES
# =========================




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




def processar_arquivo(caminho: Path) -> pl.DataFrame:
   

    df = ler_arquivo(caminho)
    
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



    if not ENTRADA_DIR.exists():
        raise FileNotFoundError(f"Pasta não encontrada: {ENTRADA_DIR}")

    arquivos = list(ENTRADA_DIR.glob("*.*"))
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

           

            salvar_excel(df_final)

            
           
                

        except Exception as e:
            print(f"Erro ao consolidar/salvar: {e}")
            print("⚠️ Nenhum arquivo foi deletado.")

    else:
        print("Nenhum arquivo processado com sucesso.")
if __name__ == "__main__":
    main()

print(ENTRADA_DIR.resolve())
print(list(ENTRADA_DIR.iterdir()))