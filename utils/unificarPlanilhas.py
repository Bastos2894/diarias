import sys
from pathlib import Path
import pandas as pd
import polars as pl
from utils.config_loader import load_config
from utils.stylePlanilhas import style_planilhas

# =========================
# CONFIG 
# =========================
BASE_DIR = Path(__file__).resolve().parents[1]
CONFIG = load_config("config/config.yaml")

ENTRADA_DIR = BASE_DIR / CONFIG["paths"]["input"]
START = CONFIG["paths"]["years"]["start"]
END = CONFIG["paths"]["years"]["end"]
OUTPUT_DIR = BASE_DIR / CONFIG["paths"]["output"]
DADOS = CONFIG["Processamento"]["formatos_aceitos"]

NOME_SAIDA = CONFIG["excel"]["nome_saida"]
ARQUIVO_SAIDA = OUTPUT_DIR / NOME_SAIDA

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# =========================
# MAPA DE MODELO
# =========================
MAPA_MODELO = {
    "1": "diarias dentro do estado",
    "2": "diarias fora do estado",
    "3": "diarias internacionais"
}

# ========================
# Nome e ID do orgão
# ========================
Mapa_orgao = {
    "idorgao": 17601,
    "nmorgao":"FUNDES"
}

# =========================
# FUNÇÕES AUXILIARES
# =========================
def tabela_valida(df: pd.DataFrame) -> bool:
    if df is None or df.empty:
        return False

    df = df.dropna(axis=0, how="all").dropna(axis=1, how="all")

    if df.empty:
        return False

    for _, row in df.iterrows():
        valores = [str(v).strip().lower() for v in row]

        if all(v in ["", "nan", "none"] for v in valores):
            continue

        return True

    return False


def extrair_modelo(nome_arquivo: str):
    try:
        codigo = nome_arquivo.split("_")[-1].split(".")[0]
        return MAPA_MODELO.get(codigo, "desconhecido")
    except:
        return "desconhecido"


def extrair_mes(nome_arquivo: str):
    try:
        return nome_arquivo.split("_")[2]
    except:
        return None


def extrair_ano(path: Path):
    for parte in path.parts:
        if parte.isdigit() and len(parte) == 4:
            return int(parte)
    return None

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

def padronizar_moedas(valor):
    if pd.isna(valor):
        return None
    
    valor = str(valor).strip()

    if "," in valor:
        valor = valor.replace(".", "")
        valor = valor.replace(",", ".")

        try:
            return float(valor)
        except ValueError:
            return None
        
    if valor.isdigit():
        try:
            return float(valor) /100
        except ValueError:  
            return None
    return None


# =========================
# FUNÇÃO PRINCIPAL
# =========================
def unificar_tudo():

    # busca todos os arquivos Excel recursivamente
    arquivos  = []
    for ano in range(START, END + 1):

        pasta_ano = ENTRADA_DIR / str(ano)

        if not pasta_ano.exists():
            print(f"⚠️ Pasta não encontrada: {pasta_ano}")
            continue

        arquivos_ano = list(pasta_ano.rglob("*.xls*"))

        print(f"📂 {ano}: {len(arquivos_ano)} arquivos encontrados.")

        arquivos.extend(arquivos_ano)

    if not arquivos:
        print("Nenhum arquivo encontrado.")
        return None

    print(f"\n📂 Total de arquivos encontrados: {len(arquivos)}")

    dfs_validos = []

    # =========================
    # LOOP PRINCIPAL
    # =========================
    for arquivo in arquivos:

        try:

            # usa a função robusta de leitura
            tabelas = ler_arquivo(arquivo)

            if not tabelas:
                print(f"[IGNORADO] {arquivo.name}")
                continue

            df = None

            # procura primeira tabela válida
            for nome, tabela in tabelas.items():

                if not tabela.empty and tabela_valida(tabela):
                    df = tabela
                    coluna_valor = "Valor das Diarias"
                    if coluna_valor in df.columns:
                        df[coluna_valor] = df[coluna_valor].apply(padronizar_moedas)
                    
                    df[coluna_valor] = pd.to_numeric(df[coluna_valor], errors="coerce")
                    break

            if df is None:
                print(f"[VAZIO] {arquivo.name}")
                continue

            if "Valor das Diarias" in df.columns:
                print(df["Valor das Diarias"].head())

            # =========================
            # LIMPEZA
            # =========================

            # remove cabeçalhos repetidos
            if "Nome do Servidor" in df.columns:
                df = df[df["Nome do Servidor"] != "Nome do Servidor"]

            # remove linhas totalmente vazias
            df = df.dropna(how="all")

            # =========================
            # COLUNAS AUXILIARES
            # =========================

            df["modelo"] = extrair_modelo(arquivo.name)

            df["ano"] = extrair_ano(arquivo)

            df["mes"] = extrair_mes(arquivo.name)

            df["arquivo_origem"] = arquivo.name

            df["Idorgao"] = Mapa_orgao["idorgao"]
            df["NMorgao"] = Mapa_orgao["nmorgao"]

            # adiciona ao consolidado
            dfs_validos.append(df)

            print(f"[OK] {arquivo.name}")

        except Exception as e:

            print(f"[ERRO] {arquivo.name} -> {e}")

    # =========================
    # VALIDAÇÃO FINAL
    # =========================
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
 
    df_final.to_excel(
        ARQUIVO_SAIDA,
        index=False
    )

    # aplica estilo Excel
    style_planilhas(ARQUIVO_SAIDA)

    print(f"\n✅ Consolidado salvo em:")
    print(ARQUIVO_SAIDA)

    print(f"\n📊 Total de linhas: {len(df_final)}")

    return df_final

if __name__ == "__main__":
    unificar_tudo()