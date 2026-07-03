import os
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
from google.cloud import storage
from sqlalchemy import create_engine

# 1. Carrega as variáveis de ambiente do .env
load_dotenv()

def get_gcs_client():
    """Inicializa e retorna o cliente do Google Cloud Storage usando o .env"""
    # DICA: O google-cloud-storage lê a variável GOOGLE_APPLICATION_CREDENTIALS 
    # automaticamente se ela estiver definida no ambiente!
    return storage.Client()

def upload_to_gcs(bucket_name, source_file_path, destination_blob_name):
    """Envia um arquivo local para o GCS"""
    # O storage.Client() busca a variável GOOGLE_APPLICATION_CREDENTIALS do .env automaticamente
    client = storage.Client() 
    
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    
    # Executa o upload do arquivo local
    blob.upload_from_filename(source_file_path)
    print(f"🚀 Arquivo {source_file_path} enviado com sucesso para {destination_blob_name}!")
    
from urllib.parse import quote_plus  # <-- ADICIONE NO TOPO DO ARQUIVO    
def extract_postgres_table(table_name):
    db_user = os.getenv("DB_USER")
    db_pass = os.getenv("DB_PASS")
    db_host = os.getenv("DB_HOST")
    db_port = os.getenv("DB_PORT")
    db_name = os.getenv("DB_NAME")
    
    # PROTEÇÃO SÊNIOR: Trata caracteres especiais da senha
    senha_segura = quote_plus(db_pass)
    
    connection_string = f"postgresql://{db_user}:{senha_segura}@{db_host}:{db_port}/{db_name}"
    engine = create_engine(connection_string)
    
    query = f"SELECT * FROM {table_name}"
    df = pd.read_sql(query, engine)
    
    return df

# Lógica Principal (Orquestração local provisória)
if __name__ == "__main__":
    # Verifica se as variáveis do banco existem antes de continuar
    if not os.getenv("DB_HOST") or os.getenv("DB_PORT") is None:
        print("❌ ERRO: Variáveis de conexão do Postgres (DB_HOST, DB_PORT, etc.) não configuradas no .env!")
        exit(1) # Para a execução do script com código de erro
    
    # CONFIGURAÇÃO: Altere para o nome exato do bucket que você criou no GCS
    # Boa prática: Você também pode colocar isso no seu .env como BUCKET_NAME="..."
    BUCKET_NAME = os.getenv("BUCKET_NAME", "saas-data-lake-portfolio-pedro-zogbi") 
    
    # Garantir que a pasta temporária local existe
    os.makedirs("tmp", exist_ok=True)
    
    # 1. Definir o caminho particionado por data (Garantindo a Idempotência)
    data_hoje = datetime.now()
    ano = data_hoje.strftime("%Y")
    mes = data_hoje.strftime("%m")
    dia = data_hoje.strftime("%d")
    particao_data = f"year={ano}/month={mes}/day={dia}"
    
    # =========================================================================
    # PARTE 1: Extração e Ingestão das Tabelas do Postgres (Dados Estruturados)
    # =========================================================================
    tabelas_para_extrair = ["saas_plans", "saas_customers"]
    
    for tabela in tabelas_para_extrair:
        print(f"\n🔄 Iniciando ingestão da tabela relacional: {tabela}")
        
        # Passo 1: Extrair os dados do Cloud SQL para a memória (DataFrame)
        df_tabela = extract_postgres_table(tabela)
        
        # Passo 2: Salvar temporariamente no seu computador em formato CSV
        caminho_local_csv = f"tmp/{tabela}.csv"
        df_tabela.to_csv(caminho_local_csv, index=False)
        
        # Passo 3: Criar o caminho de destino no Data Lake (Estrutura Medalhão/Bronze)
        caminho_nuvem_gcs = f"bronze/{tabela}/{particao_data}/{tabela}.csv"
        
        # Passo 4: Fazer o upload para o GCS trancado e privado
        upload_to_gcs(BUCKET_NAME, caminho_local_csv, caminho_nuvem_gcs)

    # =========================================================================
    # PARTE 2: Ingestão dos Logs de Utilização do App (Dados Semi-estruturados)
    # =========================================================================
    print("\n📝 Iniciando ingestão dos Logs de Utilização do App...")
    caminho_local_logs = "tmp/logs_utilizacao.json"
    
    # Verifica se você já rodou o script 'generate_mock_data.py' antes
    if os.path.exists(caminho_local_logs):
        # Caminho estruturado no GCS para a pasta de logs
        caminho_nuvem_logs = f"bronze/logs_utilizacao/{particao_data}/logs_utilizacao.json"
        
        # Faz o upload do arquivo JSON direto para o GCS
        upload_to_gcs(BUCKET_NAME, caminho_local_logs, caminho_nuvem_logs)
    else:
        print("⚠️ Arquivo de logs não encontrado. Certifique-se de rodar o gerador de dados primeiro!")
        
    print("\n🎉 Pipeline de Ingestão executado com sucesso!")