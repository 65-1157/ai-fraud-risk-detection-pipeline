# AI Fraud Risk Detection Pipeline

## 1. Brief Executive Summary

This project demonstrates an end-to-end fraud risk detection pipeline using synthetic financial transaction data.

It covers data generation, data cleaning, PySpark feature engineering, supervised fraud classification, unsupervised anomaly detection, final risk scoring, local GenAI-style explanations, monitoring, SQL validation, Databricks migration notes, and unit tests.

The project is local-first, reproducible, Databricks-ready, and does not require paid cloud services, private banking data, or paid GenAI providers.

## 2. Pipeline Overview

```text
Synthetic data generation
        ↓
Data cleaning
        ↓
PySpark feature engineering
        ↓
Supervised fraud classification
        ↓
Unsupervised anomaly detection
        ↓
Final risk scoring
        ↓
Local GenAI-style explanations
        ↓
Monitoring report

3. Business Goal

Financial institutions need to identify suspicious transactions, fraud patterns, and abnormal customer behavior.

This project simulates that challenge with synthetic customers, accounts, transactions, and alert labels. The final output is a transaction-level risk table with risk scores, recommended actions, and business-readable explanations.

4. Main subjects covered
Python data pipeline development
pandas and NumPy data handling
PySpark feature engineering
SQL validation and analytical queries
Supervised machine learning with Random Forest
Unsupervised anomaly detection with Isolation Forest
Fraud and AML-inspired risk monitoring
Final risk scoring logic
Local GenAI-style explanation generation
Monitoring and MLOps-oriented reporting
Git/GitHub project organization
Databricks-ready architecture

5. Project Structure
ai-fraud-risk-detection-pipeline/
│
├── README.md
├── requirements.txt
├── .gitignore
│
├── src/
│   ├── data_generator.py
│   ├── cleaning.py
│   ├── features_pyspark.py
│   ├── train_supervised.py
│   ├── train_anomaly.py
│   ├── risk_scoring.py
│   ├── llm_explainer.py
│   └── monitoring.py
│
├── sql/
│   ├── 01_basic_checks.sql
│   ├── 02_customer_aggregations.sql
│   └── 03_risk_queries.sql
│
├── reports/
│   ├── executive_summary.md
│   ├── data_quality_report.md
│   ├── feature_dictionary.md
│   ├── model_results.md
│   ├── anomaly_results.md
│   ├── risk_scoring_report.md
│   ├── genai_explanation_report.md
│   └── monitoring_report.md
│
├── databricks/
│   └── databricks_migration_notes.md
│
└── tests/
    └── test_risk_logic.py

6. How to Run

Create and activate a virtual environment:
py -3.11 -m venv .venv
source .venv/Scripts/activate
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
python src/data_generator.py
python src/cleaning.py
python src/features_pyspark.py
python src/train_supervised.py
python src/train_anomaly.py
python src/risk_scoring.py
python src/llm_explainer.py
python src/monitoring.py
pytest

7. Final Risk Score

The final risk score combines three components:
final_risk_score =
    0.50 * fraud_probability
  + 0.30 * anomaly_score
  + 0.20 * rule_based_score

8. GenAI-Style Explanations

This project does not depend on paid GenAI providers.

The explanation module uses deterministic templates to convert risk scores and model outputs into natural-language explanations. This keeps the project local, reproducible, auditable, and free from API-key dependencies.

The module is LLM-ready and could later be connected to a private or approved enterprise LLM if needed.

9. Databricks Readiness

The project runs locally with open-source PySpark, but the architecture can be migrated to Databricks using:

Delta Lake tables;
Databricks Workflows;
MLflow tracking;
Unity Catalog;
Lakehouse architecture;
Databricks SQL dashboards.

Databricks is optional and not required to run this repository.

10. Main Outputs
| Output                         | Description                           |
| ------------------------------ | ------------------------------------- |
| `features_model_ready.parquet` | Final engineered feature table        |
| `model_results.md`             | Supervised fraud model report         |
| `anomaly_results.md`           | Unsupervised anomaly detection report |
| `risk_scoring_report.md`       | Final risk scoring report             |
| `genai_explanation_report.md`  | Local explanation report              |
| `monitoring_report.md`         | Monitoring and MLOps-style report     |


