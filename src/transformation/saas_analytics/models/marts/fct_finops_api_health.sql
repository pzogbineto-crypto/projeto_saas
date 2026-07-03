{{ config(materialized='table') }} -- Aqui forçamos o dbt a criar uma tabela física no BigQuery para máxima performance

WITH customers AS (
    SELECT * FROM {{ ref('stg_saas_customers') }}
),

plans AS (
    SELECT * FROM {{ ref('stg_saas_plans') }}
),

usage_logs AS (
    -- Agrupamos o volume de requisições por cliente para simplificar a junção
    SELECT
        customer_id,
        COUNT(event_id) AS total_requests_made,
        COUNT(CASE WHEN http_status_code >= 400 THEN 1 END) AS total_errors_encountered,
        ROUND(AVG(response_time_ms), 2) AS avg_response_time_ms
    FROM {{ ref('stg_saas_usage_logs') }}
    GROUP BY customer_id
)

SELECT
    c.customer_id,
    c.company_name,
    c.customer_status,
    p.plan_name,
    p.monthly_price AS base_mrr,
    p.api_limit_per_month,
    
    -- Consumo Real (Tratando clientes que podem não ter logs com COALESCE)
    COALESCE(u.total_requests_made, 0) AS total_requests_made,
    COALESCE(u.total_errors_encountered, 0) AS total_errors_encountered,
    COALESCE(u.avg_response_time_ms, 0) AS avg_response_time_ms,
    
    -- Métrica FinOps Fundamental: Percentual de uso do limite contratado
    ROUND(
        (COALESCE(u.total_requests_made, 0) / p.api_limit_per_month) * 100, 
        2
    ) AS limit_usage_percentage,
    
    -- Regra de Negócio: O cliente estourou o limite do plano dele?
    CASE 
        WHEN COALESCE(u.total_requests_made, 0) > p.api_limit_per_month THEN TRUE
        ELSE FALSE
    END AS has_exceeded_limit

FROM customers c
LEFT JOIN plans p ON c.plan_id = p.plan_id
LEFT JOIN usage_logs u ON c.customer_id = u.customer_id