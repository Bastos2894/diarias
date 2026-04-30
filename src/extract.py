import requests
from pathlib import Path
import time

BASE_URL = "https://consultas.transparencia.mt.gov.br/pessoal/diarias_por_orgao/"
DOWNLOAD_URL = "https://consultas.transparencia.mt.gov.br/download_excel.php"

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Referer": BASE_URL + "resultado_3.php"
}


def baixar_excel(mes, ano, orgao, elemento, sub_elemento):

    params = {
        "mes": mes,
        "ano": ano,
        "orgao": orgao,
        "elemento": elemento,
        "sub_elemento": sub_elemento
    }

    pasta = Path(f"dados/originais/{ano}")
    pasta.mkdir(parents=True, exist_ok=True)

    caminho = pasta / f"diarias_{ano}_{mes:02}.xlsx"
   
    with requests.Session() as s:

        # PASSO 1:cria sessão com filtros
        r1 = s.get(
            BASE_URL + "resultado_3.php",
            params = params,
            headers= HEADERS
        )

        if r1.status_code != 200:
            print(f"[ERRO] Falha ao carregar página {mes}/{ano}")

        time.sleep(2)  # 👈 evita bloqueio
        

        # PASSO 2: download com sessão ativa
        r2 = s.get(
            DOWNLOAD_URL,
            headers=HEADERS
        )

        # validação

        if not r2.content.startswith(b'PK'):
            print(f"[ERRO] {mes}/{ano} Não retornou  Excel válido")
            return None

        with open(caminho, "wb") as f:
            f.write(r2.content)

    print(f"[OK] {caminho}")
    return caminho