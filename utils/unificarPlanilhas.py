import sys
from pathlib import Path
import pandas as pd
from utils.config_loader import load_config
from utils.stylePlanilhas import style_planilhas

# =========================
# CONFIG 
# =========================
BASE_DIR = Path(__file__).resolve().parents[1]
CONFIG = load_config()

ENTRADA_DIR = BASE_DIR / CONFIG["paths"]["input"]
# START = CONFIG["paths"]["years"]["start"]
# END = CONFIG["paths"]["years"]["end"]
OUTPUT_DIR = BASE_DIR / CONFIG["paths"]["output"]
DADOS = CONFIG["Processamento"]["formatos_aceitos"]

NOME_SAIDA = CONFIG["excel"]["nome_saida"]
ARQUIVO_SAIDA = OUTPUT_DIR / NOME_SAIDA

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# =========================
# MAPA DE MODELO
# =========================
# MAPA_MODELO = {
#     "1": "diarias dentro do estado",
#     "2": "diarias fora do estado"
# }

# ========================
# Nome e ID do orgão
# ========================
# Mapa_orgao = {
#     "idorgao": 17101,
#     "nmorgao":"SEDEC"
# }

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


# def extrair_modelo(nome_arquivo: str):
#     try:
#         codigo = nome_arquivo.split("_")[-1].split(".")[0]
#         return MAPA_MODELO.get(codigo, "desconhecido")
#     except:
#         return "desconhecido"


# def extrair_mes(nome_arquivo: str):
#     try:
#         return nome_arquivo.split("_")[2]
#     except:
#         return None


# def extrair_ano(path: Path):
#     for parte in path.parts:
#         if parte.isdigit() and len(parte) == 4:
#             return int(parte)
#     return None


# =========================
# FUNÇÃO PRINCIPAL
# =========================
def unificar_tudo():
    arquivos = list(ENTRADA_DIR.rglob("*.xls*"))

    if not arquivos:
        print("Nenhum arquivo encontrado.")
        return None

    dfs_validos = []

    # ano_inicio = CONFIG["paths"]["Year_start"]
    # ano_fim = CONFIG["paths"]["Year_end"]

    # for ano in range(ano_inicio, ano_fim + 1):
    #     pasta_ano = ENTRADA_DIR / str(ano)

    #     if not pasta_ano.exists():
    #         print(f"[AVISO] Pasta não encontrada: {pasta_ano}")
    #         continue

    #     arquivos = list(pasta_ano.glob("*xls*"))

    #     print(f"\n📂 Processando ano: {ano} ({len(arquivos)} arquivos)")

    for arquivo in arquivos:
        try:
            tabelas = pd.read_excel(arquivo, sheet_name=None)

            if not tabelas:
                print(f"[IGNORADO] {arquivo.name}")
                continue

            df = None

            for nome, tabela in tabelas.items():
                if not tabela.empty and tabela_valida(tabela):
                    df = tabela
                    break

            if df is None:
                print(f"[VAZIO] {arquivo.name}")
                continue
            
            # remove linhas duplicadas de cabeçalho
            # if "Nome do Servidor" in df.columns:
            #     df = df[df["Nome do Servidor"] != "Nome do Servidor"]

            # adiciona colunas
            # df["modelo"] = extrair_modelo(arquivo.name)
            # df["ano"] = arquivo.parent.name
            # df["mes"] = extrair_mes(arquivo.name)

            dfs_validos.append(df)
                # print(f"[OK] {arquivo.name}")

        except Exception as e:
            print(f"[ERRO] {arquivo.name} -> {e}")
            
    # if not dfs_validos:
    #     print("Nenhuma tabela válida encontrada.")
    #     return None

    df_final = pd.concat(dfs_validos, ignore_index=True)

    df_final.to_excel(ARQUIVO_SAIDA, index=False)
    # Aplica estilo após salvar o arquivo
    style_planilhas(ARQUIVO_SAIDA)  

    print(f"\n✅ Consolidado salvo em: {ARQUIVO_SAIDA}")

    return df_final