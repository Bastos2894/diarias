from src.extractSelenium import baixar_excel
# from src.transform import tratar_arquivo
# from src.load import salvar

# def executar_coleta():
#     for ano in range(2025, 2026):
#         for mes in range(1,3):
#             caminho = baixar_excel(mes, ano, 17101, 14, 1)

#     if caminho:
#         df = tratar_arquivo(caminho)

if __name__ == "__main__":
  baixar_excel(1, 2025, 17101, 14, 1)
  baixar_excel(2, 2025, 17101, 14, 1)
  

