{{ config(materialized='table', schema='saas_gold') }}

WITH api_health AS (
    SELECT * FROM {{ ref('fct_finops_api_health') }}
)

SELECT
    COUNT(DISTINCT customer_id) AS total_customers,
    COUNT(DISTINCT CASE WHEN customer_status = 'active' THEN customer_id END) AS active_customers,
    COUNT(DISTINCT CASE WHEN customer_status = 'churned' THEN customer_id END) AS churned_customers,
    
    -- NOVA MÉTRICA: Percentual de clientes em débito sobre o total de clientes na base
    ROUND(
        (COUNT(DISTINCT CASE WHEN customer_status = 'past_due' THEN customer_id END) / COUNT(DISTINCT customer_id)) * 100, 
        2
    ) AS past_due_percentage,

    ROUND(
        (COUNT(DISTINCT CASE WHEN customer_status = 'churned' THEN customer_id END) / COUNT(DISTINCT customer_id)) * 100, 
        2
    ) AS churn_rate_percentage,

    SUM(CASE WHEN customer_status = 'active' THEN base_mrr ELSE 0 END) AS total_active_mrr,
    SUM(CASE WHEN customer_status = 'past_due' THEN base_mrr ELSE 0 END) AS mrr_at_risk,
    COUNT(DISTINCT CASE WHEN has_exceeded_limit = TRUE THEN customer_id END) AS customers_over_limit,
    SUM(CASE WHEN has_exceeded_limit = TRUE THEN base_mrr * 0.20 ELSE 0 END) AS potential_overage_revenue

FROM api_health