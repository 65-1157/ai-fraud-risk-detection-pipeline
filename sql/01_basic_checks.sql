-- ============================================================
-- 01_basic_checks.sql
-- Basic data quality checks for the fraud risk pipeline.
--
-- These queries assume the existence of analytical tables:
-- customers
-- accounts
-- transactions
-- alerts
--
-- They can be adapted to Databricks SQL, PostgreSQL, Athena,
-- BigQuery, Snowflake, or other SQL engines.
-- ============================================================


-- 1. Row counts by table
SELECT 'customers' AS table_name, COUNT(*) AS row_count FROM customers
UNION ALL
SELECT 'accounts' AS table_name, COUNT(*) AS row_count FROM accounts
UNION ALL
SELECT 'transactions' AS table_name, COUNT(*) AS row_count FROM transactions
UNION ALL
SELECT 'alerts' AS table_name, COUNT(*) AS row_count FROM alerts;


-- 2. Check duplicate customer IDs
SELECT
    customer_id,
    COUNT(*) AS duplicate_count
FROM customers
GROUP BY customer_id
HAVING COUNT(*) > 1;


-- 3. Check duplicate transaction IDs
SELECT
    transaction_id,
    COUNT(*) AS duplicate_count
FROM transactions
GROUP BY transaction_id
HAVING COUNT(*) > 1;


-- 4. Check transactions without valid customer
SELECT
    t.transaction_id,
    t.customer_id
FROM transactions t
LEFT JOIN customers c
    ON t.customer_id = c.customer_id
WHERE c.customer_id IS NULL;


-- 5. Check transactions without valid account
SELECT
    t.transaction_id,
    t.account_id
FROM transactions t
LEFT JOIN accounts a
    ON t.account_id = a.account_id
WHERE a.account_id IS NULL;


-- 6. Check alerts without valid transaction
SELECT
    a.transaction_id
FROM alerts a
LEFT JOIN transactions t
    ON a.transaction_id = t.transaction_id
WHERE t.transaction_id IS NULL;


-- 7. Check invalid transaction amounts
SELECT
    transaction_id,
    amount
FROM transactions
WHERE amount <= 0
   OR amount IS NULL;


-- 8. Check invalid transaction hours
SELECT
    transaction_id,
    transaction_hour
FROM transactions
WHERE transaction_hour < 0
   OR transaction_hour > 23
   OR transaction_hour IS NULL;


-- 9. Check label distribution
SELECT
    fraud_label,
    COUNT(*) AS total_transactions
FROM alerts
GROUP BY fraud_label
ORDER BY fraud_label;


-- 10. Check AML alert distribution
SELECT
    aml_alert_label,
    COUNT(*) AS total_transactions
FROM alerts
GROUP BY aml_alert_label
ORDER BY aml_alert_label;