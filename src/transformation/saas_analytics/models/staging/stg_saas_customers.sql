WITH source_data AS (
    SELECT * FROM {{ source('saas_bronze', 'saas_customers') }}
)

SELECT
    -- Chaves e IDs
    CAST(customer_id AS INT64) AS customer_id,
    CAST(plan_id AS INT64) AS plan_id,
    
    -- Textos descritivos
    TRIM(company_name) AS company_name,
    TRIM(status) AS customer_status,
    
    -- CORREÇÃO: Como o BigQuery já detectou como DATE, fazemos apenas o CAST explícito
    CAST(created_at AS DATE) AS account_created_at,
    
    -- Metadados de Partição do GCS
    year,
    month,
    day

FROM source_data