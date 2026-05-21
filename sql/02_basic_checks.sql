-- ============================================================
-- 02_customer_aggregations.sql
-- Customer-level behavioral aggregations for fraud/risk analysis.
--
-- These queries show how customer behavior features can be
-- constructed using SQL before or alongside PySpark.
-- ============================================================


-- 1. Customer transaction summary
SELECT
    customer_id,
    COUNT(*) AS total_transactions,
    SUM(amount) AS total_amount,
    AVG(amount) AS avg_amount,
    MAX(amount) AS max_amount,
    STDDEV(amount) AS std_amount,
    COUNT(DISTINCT device_id) AS unique_devices
FROM transactions
GROUP BY customer_id;


-- 2. Customer international transaction ratio
SELECT
    customer_id,
    COUNT(*) AS total_transactions,
    SUM(CASE WHEN is_international = 1 THEN 1 ELSE 0 END) AS international_transactions,
    1.0 * SUM(CASE WHEN is_international = 1 THEN 1 ELSE 0 END) / COUNT(*) AS international_ratio
FROM transactions
GROUP BY customer_id;


-- 3. Customer night transaction ratio
SELECT
    customer_id,
    COUNT(*) AS total_transactions,
    SUM(CASE WHEN transaction_hour BETWEEN 0 AND 5 THEN 1 ELSE 0 END) AS night_transactions,
    1.0 * SUM(CASE WHEN transaction_hour BETWEEN 0 AND 5 THEN 1 ELSE 0 END) / COUNT(*) AS night_ratio
FROM transactions
GROUP BY customer_id;


-- 4. Customer high-risk merchant category ratio
SELECT
    customer_id,
    COUNT(*) AS total_transactions,
    SUM(
        CASE
            WHEN merchant_category IN ('crypto', 'gambling', 'luxury') THEN 1
            ELSE 0
        END
    ) AS high_risk_category_transactions,
    1.0 * SUM(
        CASE
            WHEN merchant_category IN ('crypto', 'gambling', 'luxury') THEN 1
            ELSE 0
        END
    ) / COUNT(*) AS high_risk_category_ratio
FROM transactions
GROUP BY customer_id;


-- 5. Customer behavior joined with fraud labels
SELECT
    t.customer_id,
    COUNT(*) AS total_transactions,
    SUM(a.fraud_label) AS fraud_cases,
    AVG(a.fraud_label) AS fraud_rate,
    SUM(a.aml_alert_label) AS aml_alert_cases,
    AVG(a.aml_alert_label) AS aml_alert_rate,
    AVG(t.amount) AS avg_amount,
    MAX(t.amount) AS max_amount
FROM transactions t
INNER JOIN alerts a
    ON t.transaction_id = a.transaction_id
GROUP BY t.customer_id
ORDER BY fraud_rate DESC, total_transactions DESC;


-- 6. Customers with many devices
SELECT
    customer_id,
    COUNT(DISTINCT device_id) AS unique_devices,
    COUNT(*) AS total_transactions
FROM transactions
GROUP BY customer_id
HAVING COUNT(DISTINCT device_id) >= 8
ORDER BY unique_devices DESC;


-- 7. Customers with unusual amount concentration
SELECT
    customer_id,
    COUNT(*) AS total_transactions,
    AVG(amount) AS avg_amount,
    MAX(amount) AS max_amount,
    MAX(amount) / NULLIF(AVG(amount), 0) AS max_to_avg_ratio
FROM transactions
GROUP BY customer_id
HAVING MAX(amount) / NULLIF(AVG(amount), 0) >= 5
ORDER BY max_to_avg_ratio DESC;