# 📈 SaaS FinOps Data Pipeline: Da Ingestão ao Business Intelligence

## 📖 Sobre o Projeto
Este projeto implementa um pipeline de dados *end-to-end* baseado nos princípios modernos de **FinOps (Financial Operations)** para uma plataforma SaaS de alta escala. 

O grande desafio de negócio resolvido aqui é o cruzamento de **dados relacionais contratuais** (armazenados em um banco transacional Postgres) com **logs semiestruturados volumosos** de utilização de API (armazenados em JSON no Cloud Storage). Através desse ecossistema, a empresa consegue monitorar a saúde financeira em tempo real, mapeando inadimplência, calculando a taxa de cancelamento (*Churn*) e projetando receitas adicionais através de taxas de *overage* (clientes que abusaram do teto operacional dos seus planos).

---

## 🏗️ Arquitetura e Tech Stack

A arquitetura foi desenhada seguindo as melhores práticas da **Modern Data Stack (MDS)** e os conceitos da **Arquitetura Medalhão**:

* **Banco Transacional (Origem):** PostgreSQL hospedado no Google Cloud SQL.
* **Ingestão & Orquestração:** Script Python (idempotente) aplicando particionamento em estilo *Hive* por Ano/Mês/Dia.
* **Data Lake (Bronze):** Google Cloud Storage (GCS) atuando como repositório de arquivos brutos (CSV e JSON).
* **Data Warehouse:** Google BigQuery processando queries em alta performance.
* **Analytics Engineering (Silver/Gold):** **dbt-core (Data Build Tool)** gerenciando dependências, linhagem e transformações.
* **Data Quality (Testes):** dbt Data Tests nativos garantindo integridade referencial e chaves únicas.
* **Visualização (BI):** Google Looker Studio para o Sumário Executivo e painel operacional.

---

## 🗂️ Estrutura do Repositório

```text
saas_finops_pipeline/
├── credentials/                 # [IGNORADO NO GIT] Chaves privadas de acesso GCP
├── src/
│   ├── ingestion/
│   │   ├── generate_mock_data.py # Geração dinâmica de 50 clientes e 15k logs (Python)
│   │   └── extract_to_gcs.py     # Carga automatizada e particionada para o Storage
│   └── transformation/
│       └── saas_analytics/       # Projeto dbt Core
│           ├── macros/           # Regras globais de sobreposição de esquemas (GCP Gold)
│           ├── models/
│           │   ├── staging/      # Camada Silver: Limpeza, casting e fontes do BigQuery
│           │   └── marts/        # Camada Gold: Tabelas de Fato e Resumos de Negócio
│           └── dbt_project.yml   # Coração da configuração do dbt
└── .gitignore                    # Blindagem de segurança do projeto


🛢️ Fluxo de Modelagem (dbt Lineage DAG)
O dbt orquestrou a transformação dividindo os dados estritamente em camadas de governança:

Staging (saas_silver): stg_saas_customers, stg_saas_plans e stg_saas_usage_logs. Limpeza de strings, tratamento de timestamps ISO e padronização de tipos de dados.

Core / Fatos (saas_silver): fct_finops_api_health. Consolidação atômica cruzando o consumo real de requisições de cada empresa contra as amarras do plano contratado.

Marts / BI (saas_gold): * mart_finops_executive_summary (Tabela estática para C-Level contendo MRR, Churn e Receita Potencial).

mart_finops_api_health_detail (View protegida para ferramentas de BI detalharem o consumo por cliente).

📊 Regras de Negócio Implementadas
Cálculo de Churn Rate: Percentual de clientes com status churned sobre a base histórica de clientes.

MRR em Risco (Past Due): Soma da receita recorrente mensal de clientes que estão ativos operacionalmente, mas com atraso financeiro identificado.

Taxa de Overage FinOps: Identificação de quebra de teto da API (has_exceeded_limit = TRUE). O pipeline calcula e projeta uma receita incremental aplicando uma multa de 20% sobre o preço base do plano do cliente infrator.

🚀 Como Executar o Pipeline Localmente
1. Pré-requisitos e Ambiente
Instale as dependências contidas no ambiente virtual:

python -m venv venv
./venv/Scripts/activate # Windows
pip install -r requirements.txt

2. Geração e Extração de Dados
Certifique-se de configurar o arquivo .env com as credenciais do seu banco e execute a esteira de dados sintéticos:

python src/ingestion/generate_mock_data.py
python src/ingestion/extract_to_gcs.py

3. Execução e Validação com o dbt
Navegue até a pasta do dbt, verifique a conexão com a nuvem e execute o build completo:

cd src/transformation/saas_analytics
dbt debug
dbt run
dbt test

📐 Camada de Visualização (Looker Studio)
O resultado final das tabelas materializadas na camada Gold (saas_gold) foi conectado ao Looker Studio para consumo executivo.

![alt text](image.png)

💡 Principais insights do Dashboard: O painel exibe de forma clara a distribuição de clientes e comprova a eficácia das regras do dbt, permitindo ao CFO visualizar instantaneamente o ganho financeiro potencial com a cobrança de multas por uso excessivo da API.