from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import os
from pathlib import Path

def esperar_download(pasta, arquivos_antes, timeout=60):
    tempo_inicial = time.time()

    while True:
        arquivos_agora = set(pasta.glob("*.xls*"))
        novos = arquivos_agora - arquivos_antes

        temporarios = list(pasta.glob("*.crdownload"))

        if novos and not temporarios:
            return max(novos, key=os.path.getctime)

        if time.time() - tempo_inicial > timeout:
            return None

        time.sleep(1)



def baixar_excel(mes, ano, orgao, elemento, sub_elemento):

    pasta = Path(f"dados/originais/{ano}")
    pasta.mkdir(parents=True, exist_ok=True)
   
        
    options = webdriver.ChromeOptions()

    prefs = {
        "download.default_directory": str(pasta.resolve()),
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
    }

    options.add_experimental_option("prefs", prefs)

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

    url = f"https://consultas.transparencia.mt.gov.br/pessoal/diarias_por_orgao/resultado_3.php?mes={mes}&ano={ano}&orgao={orgao}&elemento={elemento}&sub_elemento={sub_elemento}"

    driver.get(url)

    time.sleep(3)

    # clica no botão
    wait = WebDriverWait(driver, 30)
    botao_dropdown = wait.until(
        EC.element_to_be_clickable((
            By.XPATH, "//button[contains(@class, 'dropdown-toggle')]"
        ))
    ) 

    botao_dropdown.click()

        # captura estado antes
    arquivos_antes = set(pasta.glob("*"))

    # encontra botão
    botao_excel = wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//a[contains(@href, 'download_excel')]")
        )
    )

    # 🔥 clica primeiro
    driver.execute_script("arguments[0].click();", botao_excel)

    # 🔥 depois espera o novo arquivo
    arquivo = esperar_download(pasta, arquivos_antes)
    driver.quit()

    if arquivo is not None:

        novo_nome = pasta / f"diarias_{ano}_{mes:02}_{sub_elemento}.xls"

        if novo_nome.exists():
            novo_nome.unlink()

        arquivo.rename(novo_nome)

        print(f"[OK] {novo_nome}")
        return novo_nome

    else:
        print("[ERRO] Download não encontrado")
        print("Conteúdo da pasta:", list(pasta.glob("*")))
        return None