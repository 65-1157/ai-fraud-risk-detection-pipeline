-- ============================================================
-- 03_risk_queries.sql
-- Risk analytics queries for final scored transactions.
--
-- These queries assume the final table:
-- risk_scored_transactions
--
-- Example columns:
-- transaction_id
-- customer_id
-- amount
-- fraud_probability
-- anomaly_score
-- rule_based_score
-- final_risk_score
-- risk_level
-- recommended_action
-- fraud_label
-- aml_alert_label
-- ============================================================


-- 1. Distribution of recommended actions
SELECT
    recommended_action,
    COUNT(*) AS total_transactions
FROM risk_scored_transactions
GROUP BY recommended_action
ORDER BY total_transactions DESC;


-- 2. Distribution of risk levels
SELECT
    risk_level,
    COUNT(*) AS total_transactions
FROM risk_scored_transactions
GROUP BY risk_level
ORDER BY total_transactions DESC;


-- 3. Top 50 highest-risk transactions
SELECT
    transaction_id,
    customer_id,
    amount,
    fraud_probability,
    anomaly_score,
    rule_based_score,
    final_risk_score,
    risk_level,
    recommended_action
FROM risk_scored_transactions
ORDER BY final_risk_score DESC
LIMIT 50;


-- 4. Average risk score by recommended action
SELECT
    recommended_action,
    COUNT(*) AS total_transactions,
    AVG(final_risk_score) AS avg_final_risk_score,
    MIN(final_risk_score) AS min_final_risk_score,
    MAX(final_risk_score) AS max_final_risk_score
FROM risk_scored_transactions
GROUP BY recommended_action
ORDER BY avg_final_risk_score DESC;


-- 5. Fraud and AML labels by risk level
SELECT
    risk_level,
    COUNT(*) AS total_transactions,
    SUM(fraud_label) AS fraud_cases,
    AVG(fraud_label) AS fraud_rate,
    SUM(aml_alert_label) AS aml_alert_cases,
    AVG(aml_alert_label) AS aml_alert_rate
FROM risk_scored_transactions
GROUP BY risk_level
ORDER BY fraud_rate DESC;


-- 6. High-value transactions selected for manual review
SELECT
    transaction_id,
    customer_id,
    amount,
    final_risk_score,
    fraud_probability,
    anomaly_score,
    recommended_action
FROM risk_scored_transactions
WHERE amount >= 1000
  AND recommended_action IN ('manual_review', 'block_or_urgent_review')
ORDER BY final_risk_score DESC;


-- 7. Customers with repeated high-risk transactions
SELECT
    customer_id,
    COUNT(*) AS high_risk_transactions,
    AVG(final_risk_score) AS avg_final_risk_score,
    MAX(final_risk_score) AS max_final_risk_score,
    SUM(fraud_label) AS fraud_cases
FROM risk_scored_transactions
WHERE final_risk_score >= 0.50
GROUP BY customer_id
HAVING COUNT(*) >= 3
ORDER BY high_risk_transactions DESC, avg_final_risk_score DESC;


-- 8. Cases where anomaly score is high but fraud probability is low
SELECT
    transaction_id,
    customer_id,
    amount,
    fraud_probability,
    anomaly_score,
    rule_based_score,
    final_risk_score,
    recommended_action
FROM risk_scored_transactions
WHERE anomaly_score >= 0.70
  AND fraud_probability < 0.40
ORDER BY anomaly_score DESC;


-- 9. Cases where supervised model is high but anomaly score is low
SELECT
    transaction_id,
    customer_id,
    amount,
    fraud_probability,
    anomaly_score,
    rule_based_score,
    final_risk_score,
    recommended_action
FROM risk_scored_transactions
WHERE fraud_probability >= 0.70
  AND anomaly_score < 0.40
ORDER BY fraud_probability DESC;


-- 10. Potential review workload by action
SELECT
    recommended_action,
    COUNT(*) AS case_count,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS case_percentage
FROM risk_scored_transactions
GROUP BY recommended_action
ORDER BY case_count DESC;