# 📊 Projeto ETL - Diárias (Análise de Gastos Públicos)

## 📌 Descrição

Este projeto tem como objetivo realizar o processo de **ETL (Extração, Transformação e Carga)** de dados relacionados a **diárias**, padronizando diferentes fontes e consolidando em uma base única para análise no Power BI.

O fluxo garante que os dados estejam limpos, consistentes e prontos para uso em dashboards e relatórios analíticos.

---

## ⚙️ Tecnologias Utilizadas

* 🐍 Python
* 📦 Pandas / Polars
* 📊 Power BI
* 🗂️ YAML (configurações)
* 📁 Excel (fontes de dados)

---

## 🏗️ Estrutura do Projeto

```
📦 projeto-diarias
├── 📁 config
│   ├── config.yaml
│   └── database.yaml
│
├── 📁 dados
│   ├── brutos/
│   ├── processadas/
│   └── final/
│
├── 📁 utils
│   ├── config_loader.py
│   ├── data_padrao.py
│   └── style_planilhas.py
│
├── 📁 scripts
│   └── padronizarDados.py
│
└── README.md
```

---

## 🔄 Pipeline ETL

### 1. 📥 Extração

* Leitura de múltiplas planilhas Excel
* Fontes com diferentes estruturas e formatos

---

### 2. 🔧 Transformação

* Padronização de nomes de colunas
* Conversão de tipos de dados:

  * Datas → `datetime`
  * Valores → `float`
  * Ano → `int`
* Limpeza de dados inconsistentes
* Tratamento de valores nulos
* Normalização de campos como `modelo`, `orgão`, etc.

---

### 3. 📤 Carga

* Geração de tabela unificada
* Exportação para:

  * Excel (`.xlsx`)
  * Base pronta para Power BI

---

## 📊 Integração com Power BI

A base final é utilizada para criação de dashboards com:

* 💰 Total de gastos com diárias
* 📈 Análise por modelo
* 🏢 Gastos por órgão (`nmorgao`)
* 📅 Análise temporal (ano, mês)

---

## ⚠️ Problemas comuns tratados

* ❌ Datas interpretadas incorretamente (ex: ano 1905)
* ❌ Valores monetários como texto (`R$ 1.234,56`)
* ❌ Diferença de formatação entre arquivos
* ❌ Inconsistência entre tabelas

---

## 🚀 Como executar o projeto

### 1. Clonar o repositório

```bash
git clone https://github.com/seu-usuario/projeto-diarias.git
cd projeto-diarias
```

### 2. Criar ambiente virtual

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows
```

### 3. Instalar dependências

```bash
pip install -r requirements.txt
```

### 4. Executar o ETL

```bash
python -m utils.padronizarDados
```

---

## 🧠 Boas práticas adotadas

* Separação entre configuração e código
* Pipeline modularizado
* Reutilização de funções utilitárias
* Padronização antes da carga no BI
* Evita transformação dentro do Power BI

---

## 📌 Melhorias futuras

* 🔄 Automatização do pipeline (agendamento)
* ☁️ Integração com banco de dados
* 📊 Dashboard mais avançado no Power BI
* 🧪 Testes automatizados
* 📈 Monitoramento de qualidade dos dados

---

## 👨‍💻 Autor

Harison Bastos Pinheiro

---

## 📄 Licença

Este projeto é de uso livre para fins de estudo e aprimoramento.
