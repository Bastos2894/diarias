from src.extractSelenium import baixar_excel
from utils.unificarPlanilhas import unificar_tudo
from utils.db import _LOADget_engine

ENGINE = _LOADget_engine()


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
print(ENGINE)
  