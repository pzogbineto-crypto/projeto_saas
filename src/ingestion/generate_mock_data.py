import os
import random
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv
from sqlalchemy import create_engine
from urllib.parse import quote_plus

load_dotenv()
hoje = datetime.now()

def gerar_clientes_e_planos(num_clientes=50):
    """Gera dinamicamente a estrutura de planos e clientes assinantes"""
    # 1. Configuração estática dos planos (Padrão de mercado SaaS)
    planos = [
        {"plan_id": 1, "plan_name": "Bronze", "monthly_price": 49.90, "api_limit": 1000},
        {"plan_id": 2, "plan_name": "Silver", "monthly_price": 199.90, "api_limit": 10000},
        {"plan_id": 3, "plan_name": "Gold", "monthly_price": 499.90, "api_limit": 50000}
    ]
    
    # Pools de nomes para gerar empresas aleatórias legais
    prefixos = ["Cyber", "Apex", "Nexus", "Nova", "Stellar", "Quantum", "Alpha", "Omega", "Vortex", "Horizon"]
    sufixos = ["Tech", "Systems", "Labs", "Digital", "Data", "Solutions", "AI", "Networks", "Infra", "SaaS"]
    
    clientes = []
    for i in range(num_clientes):
        customer_id = 100 + i  # IDs começam em 100, 101, 102...
        nome_empresa = f"{random.choice(prefixos)} {random.choice(sufixos)} {customer_id}"
        
        # Distribuindo status com pesos realistas (Mais ativos, alguns inadimplentes e cancelados)
        status = random.choices(
            population=["active", "past_due", "churned"],
            weights=[0.70, 0.15, 0.15],
            k=1
        )[0]
        
        # Data de criação da conta aleatória nos últimos 12 meses
        data_criacao = hoje - timedelta(days=random.randint(30, 365))
        
        clientes.append({
            "customer_id": customer_id,
            "company_name": nome_empresa,
            "plan_id": random.choice([1, 2, 3]), # Escolha aleatória de plano
            "status": status,
            "created_at": data_criacao.strftime("%Y-%m-%d")
        })
        
    return pd.DataFrame(planos), pd.DataFrame(clientes)


def gerar_logs_uso(clientes_ids, num_linhas=15000):
    """Gera dados de uso baseados nos IDs de clientes gerados dinamicamente"""
    endpoints = ["/api/v1/auth", "/api/v1/data", "/api/v1/analytics", "/api/v1/export"]
    
    dados = []
    for _ in range(num_linhas):
        # Data aleatória dentro dos últimos 30 dias
        data_evento = hoje - timedelta(days=random.randint(0, 30), hours=random.randint(0, 23))
        
        dados.append({
            "event_id": random.randint(100000, 999999),
            "customer_id": random.choice(clientes_ids), # Consome a lista dinâmica de IDs reais
            "endpoint": random.choice(endpoints),
            "status_code": random.choices([200, 400, 500], weights=[0.85, 0.10, 0.05], k=1)[0],
            "response_time_ms": random.randint(10, 1500),
            "timestamp": data_evento.isoformat()
        })
        
    df_logs = pd.DataFrame(dados)
    os.makedirs("tmp", exist_ok=True)
    
    caminho_json = "tmp/logs_utilizacao.json"
    df_logs.to_json(caminho_json, orient="records", lines=True)
    print(f"✅ {num_linhas} linhas de logs de uso geradas em '{caminho_json}'")


def popular_banco_postgres(df_planos, df_clientes):
    """Insere as tabelas estruturadas dentro do Cloud SQL Postgres"""
    db_user = os.getenv("DB_USER")
    db_pass = os.getenv("DB_PASS")
    db_host = os.getenv("DB_HOST")
    db_port = os.getenv("DB_PORT")
    db_name = os.getenv("DB_NAME")
    
    if all([db_user, db_pass, db_host, db_port, db_name]):
        senha_segura = quote_plus(db_pass)
        connection_string = f"postgresql://{db_user}:{senha_segura}@{db_host}:{db_port}/{db_name}"
        engine = create_engine(connection_string)
        
        df_planos.to_sql("saas_plans", engine, if_exists="replace", index=False)
        df_clientes.to_sql("saas_customers", engine, if_exists="replace", index=False)
        print(f"✅ Tabelas 'saas_plans' e 'saas_customers' ({len(df_clientes)} clientes) populadas no Cloud SQL!")
    else:
        print("⚠️ Variáveis de conexão do banco não encontradas no .env. Carga abortada.")


if __name__ == "__main__":
    print("🚀 Iniciando pipeline de geração de massa de dados sintética...")
    
    # 1. Gera os dataframes na memória
    df_planos, df_clientes = gerar_clientes_e_planos(num_clientes=50)
    
    # 2. Extrai a lista de IDs reais gerados para alimentar os logs
    lista_ids_reais = df_clientes["customer_id"].tolist()
    
    # 3. Gera 15.000 linhas de logs distribuídas entre esses clientes reais
    gerar_logs_uso(clientes_ids=lista_ids_reais, num_linhas=15000)
    
    # 4. Envia os dados cadastrais para o banco na nuvem
    popular_banco_postgres(df_planos, df_clientes)