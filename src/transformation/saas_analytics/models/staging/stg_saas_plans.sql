WITH source_data AS (
    SELECT * FROM {{ source('saas_bronze', 'saas_plans') }}
)

SELECT
    -- Chaves e IDs (Garantindo que sejam Inteiros)
    CAST(plan_id AS INT64) AS plan_id,
    
    -- Textos (Garantindo que sejam Strings limpas)
    TRIM(plan_name) AS plan_name,
    
    -- Valores Financeiros (Garantindo formato Numérico/Float)
    CAST(monthly_price AS FLOAT64) AS monthly_price,
    
    -- Métricas de Limite
    CAST(api_limit AS INT64) AS api_limit_per_month,
    
    -- Metadados de Partição do GCS
    year,
    month,
    day

FROM source_data