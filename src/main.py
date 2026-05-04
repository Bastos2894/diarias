from src.extractSelenium import baixar_excel
from utils.unificarPlanilhas import unificar_tudo


# def executar_coleta():
#     for ano in  (2026,):
#         for mes in range (1,5):
#             caminho = baixar_excel(mes, ano, 17601, 14, 2)

#             if caminho is None:
#                 print(f"Falha em {ano}-{mes:02}")

# executar_coleta()

# =========================
# EXECUÇÃO
# =========================
if __name__ == "__main__":
    unificar_tudo()