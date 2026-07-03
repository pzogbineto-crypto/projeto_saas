{{ config(
    materialized='view',
    schema='saas_gold'
) }}

-- Agora sim! O comentário SQL fica aqui fora, onde o BigQuery entende.
-- Esta View na Gold apenas aponta para a tabela física da Silver.
SELECT * FROM {{ ref('fct_finops_api_health') }}