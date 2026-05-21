# GenAI-Style Risk Explanation Report

## 1. Objective

This module converts model outputs into business-readable explanations without using a paid GenAI provider.

The current implementation uses deterministic templates. It is LLM-ready, but it does not require OpenAI, Azure OpenAI, Gemini, Bedrock, or any external API.

## 2. Why this matters

Fraud and risk models should not only generate scores. They should also help analysts understand why a transaction was prioritized for review.

## 3. Explanation strategy

The explanation engine considers:

- supervised fraud probability;
- unsupervised anomaly score;
- rule-based risk score;
- final risk level;
- recommended action.

## 4. Short reason distribution

| Short reason | Count |
|---|---:|
| low_or_monitored_risk | 22,992 |
| combined_medium_risk | 804 |
| high_supervised_model_risk | 572 |
| high_rule_based_risk | 354 |
| high_anomaly_risk | 155 |
| high_model_and_anomaly_risk | 123 |

## 5. High-priority explanation examples

| transaction_id | risk_level | action | explanation |
|---|---|---|---|
| T0010722 | very_high | block_or_urgent_review | Transaction T0010722 for customer C00625 received a very_high risk level with final score 0.88. The main drivers were: high supervised fraud probability (0.86); high anomaly score (0.82); strong rule-based risk indicators (1.00). The transaction should be prioritized for urgent review before approval. |
| T0002673 | very_high | block_or_urgent_review | Transaction T0002673 for customer C00744 received a very_high risk level with final score 0.83. The main drivers were: high supervised fraud probability (0.81); high anomaly score (0.89); strong rule-based risk indicators (0.80). The transaction should be prioritized for urgent review before approval. |
| T0001624 | very_high | block_or_urgent_review | Transaction T0001624 for customer C00859 received a very_high risk level with final score 0.82. The main drivers were: high supervised fraud probability (0.76); high anomaly score (0.82); strong rule-based risk indicators (1.00). The transaction should be prioritized for urgent review before approval. |
| T0023033 | very_high | block_or_urgent_review | Transaction T0023033 for customer C00317 received a very_high risk level with final score 0.82. The main drivers were: high supervised fraud probability (0.70); high anomaly score (0.90); strong rule-based risk indicators (1.00). The transaction should be prioritized for urgent review before approval. |
| T0015792 | very_high | block_or_urgent_review | Transaction T0015792 for customer C00056 received a very_high risk level with final score 0.82. The main drivers were: high supervised fraud probability (0.83); high anomaly score (0.81); strong rule-based risk indicators (0.80). The transaction should be prioritized for urgent review before approval. |
| T0019353 | very_high | block_or_urgent_review | Transaction T0019353 for customer C00959 received a very_high risk level with final score 0.82. The main drivers were: high supervised fraud probability (0.72); high anomaly score (0.86); strong rule-based risk indicators (1.00). The transaction should be prioritized for urgent review before approval. |
| T0011556 | very_high | block_or_urgent_review | Transaction T0011556 for customer C00854 received a very_high risk level with final score 0.82. The main drivers were: high supervised fraud probability (0.83); high anomaly score (0.74); strong rule-based risk indicators (0.90). The transaction should be prioritized for urgent review before approval. |
| T0011221 | very_high | block_or_urgent_review | Transaction T0011221 for customer C00399 received a very_high risk level with final score 0.82. The main drivers were: high supervised fraud probability (0.84); high anomaly score (0.71); strong rule-based risk indicators (0.90). The transaction should be prioritized for urgent review before approval. |
| T0022202 | very_high | block_or_urgent_review | Transaction T0022202 for customer C00826 received a very_high risk level with final score 0.81. The main drivers were: high supervised fraud probability (0.79); high anomaly score (0.86); strong rule-based risk indicators (0.80). The transaction should be prioritized for urgent review before approval. |
| T0019860 | very_high | block_or_urgent_review | Transaction T0019860 for customer C00275 received a very_high risk level with final score 0.81. The main drivers were: high supervised fraud probability (0.80); high anomaly score (0.85); strong rule-based risk indicators (0.80). The transaction should be prioritized for urgent review before approval. |

## 6. Optional LLM extension

In an enterprise environment, the deterministic template could be replaced or complemented by a private LLM, local LLM, or approved cloud provider. The default project version intentionally avoids paid dependencies.
