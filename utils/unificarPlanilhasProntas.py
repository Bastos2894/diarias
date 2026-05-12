import sys
from pathlib import Path
import pandas as pd

from utils.config_loader import load_config
from utils.padronizarDados import clean_dataframe

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
# FUNÇÕES AUXILIARES
# =========================


def ler_arquivo(caminho: Path):

    try:

        # HTML
        if caminho.suffix == ".html":

            tabelas_html = pd.read_html(
                caminho,
                decimal=",",
                thousands="."
            )

            return {
                f"Tabela_{i}": df
                for i, df in enumerate(tabelas_html)
            }

        # Excel
        elif caminho.suffix in [".xlsx", ".xls"]:

            try:

                return pd.read_excel(
                    caminho,
                    sheet_name=None,
                    engine="xlrd" if caminho.suffix == ".xls" else "openpyxl"
                )

            except Exception:

                print(f"⚠️ Lendo como HTML: {caminho.name}")

                tabelas_html = pd.read_html(caminho)

                return {
                    f"Tabela_{i}": df
                    for i, df in enumerate(tabelas_html)
                }

        # CSV
        elif caminho.suffix == ".csv":

            df = pd.read_csv(caminho)

            return {"CSV": df}

        else:

            raise ValueError(f"Formato não suportado: {caminho.name}")

    except Exception as e:

        raise RuntimeError(f"Erro ao ler arquivo {caminho.name}: {e}")



# =========================
# FUNÇÃO PRINCIPAL
# =========================
def unificar_tudo():

    # busca todos os arquivos Excel recursivamente
    arquivos = list(
        ENTRADA_DIR.rglob("*.*")
    )

    if not arquivos:
        print("Nenhum arquivo encontrado.")
        return None
   
    print(f"\n📂 total de arquivos: {len(arquivos)}.")

    dfs_validos = []

    for arquivo in arquivos:

        try:

            # usa a função robusta de leitura
            conteudo = ler_arquivo(arquivo)

            if not conteudo:
                print(f"[IGNORADO] {arquivo.name}")
                continue

            df = None

            # procura primeira tabela válida
            for nome, tabela in conteudo.items():

                if tabela.empty:
                    continue

                df = tabela
                break
            if df is None:
                print(f"[VAZIO] {arquivo.name}")
                continue

            # adiciona ao consolidado
            dfs_validos.append(df)

            print(f"[OK] {arquivo.name}")

        except Exception as e:

            print(f"[ERRO] {arquivo.name} -> {e}")

    if not dfs_validos:
        print("Nenhuma tabela válida encontrada.")
        return None
    
   
    # =========================
    # CONCATENA
    # =========================
    df_final = pd.concat(
        dfs_validos,
        ignore_index=True
    )

    # =========================
    # EXPORTA
    # =========================
    df_final = clean_dataframe(df_final)
    
    df_final.to_excel(
        ARQUIVO_SAIDA,
        index=False
    )

    # aplica estilo Excel
  

    print(f"\n✅ Consolidado salvo em:")
    print(ARQUIVO_SAIDA)

    print(f"\n📊 Total de linhas: {len(df_final)}")

    return df_final

if __name__ == "__main__":
    unificar_tudo()