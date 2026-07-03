WITH source_data AS (
    SELECT * FROM {{ source('saas_bronze', 'logs_utilizacao') }}
)

SELECT
    -- Chaves e IDs
    CAST(event_id AS INT64) AS event_id,
    CAST(customer_id AS INT64) AS customer_id,
    
    -- Dados da Requisição
    TRIM(endpoint) AS api_endpoint,
    CAST(status_code AS INT64) AS http_status_code,
    CAST(response_time_ms AS INT64) AS response_time_ms,
    
    -- Tratamento de Tempo (Convertendo string ISO para TIMESTAMP real do BigQuery)
    CAST(timestamp AS TIMESTAMP) AS event_timestamp,
    
    -- Metadados de Partição do GCS (Hive)
    year,
    month,
    day

FROM source_data