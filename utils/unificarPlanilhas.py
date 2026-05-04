import sys
from pathlib import Path
import pandas as pd
from utils.config_loader import load_config

# =========================
# CONFIG 
# =========================
BASE_DIR = Path(__file__).resolve().parents[1]
CONFIG = load_config()

ENTRADA_DIR = BASE_DIR / CONFIG["paths"]["input"]
OUTPUT_DIR = BASE_DIR / CONFIG["paths"]["output"]

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

# =========================
# FUNÇÕES AUXILIARES
# =========================
def tabela_valida(df: pd.DataFrame) -> bool:
    if df is None or df.empty:
        return False

    # remove linhas/colunas totalmente vazias
    df = df.dropna(axis=0, how="all").dropna(axis=1, how="all")

    if df.empty:
        return False

    # 🔥 verifica se existe pelo menos 1 linha com dado real
    for _, row in df.iterrows():
        valores = [str(v).strip().lower() for v in row]

        # ignora linhas que são só cabeçalho repetido
        if all(v in ["", "nan", "none"] for v in valores):
            continue

        # se tiver QUALQUER valor útil → é válida
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


# =========================
# FUNÇÃO PRINCIPAL
# =========================
def unificar_tudo():
    arquivos = list(ENTRADA_DIR.rglob("*.xls*"))

    if not arquivos:
        print("Nenhum arquivo encontrado.")
        return None

    dfs_validos = []

    for arquivo in arquivos:
        try:
            tabelas = pd.read_html(arquivo)

            if not tabelas:
                print(f"[IGNORADO] {arquivo.name}")
                continue

            df = None

            for tabela in tabelas:
                if tabela_valida(tabela):
                    df = tabela
                    break

            if df is None:
                print(f"[VAZIO] {arquivo.name}")
                continue
            
            # remove linhas duplicadas de cabeçalho
            if "Nome do Servidor" in df.columns:
                df = df[df["Nome do Servidor"] != "Nome do Servidor"]

            # adiciona colunas
            df["modelo"] = extrair_modelo(arquivo.name)
            df["ano"] = arquivo.parent.name
            df["mes"] = extrair_mes(arquivo.name)

            dfs_validos.append(df)
            print(f"[OK] {arquivo.name}")

        except Exception as e:
            print(f"[ERRO] {arquivo.name} -> {e}")
            
    if not dfs_validos:
        print("Nenhuma tabela válida encontrada.")
        return None

    df_final = pd.concat(dfs_validos, ignore_index=True)

    # salva arquivo final
    df_final.to_excel(ARQUIVO_SAIDA, index=False)

    print(f"\n✅ Consolidado salvo em: {ARQUIVO_SAIDA}")

    return df_final


