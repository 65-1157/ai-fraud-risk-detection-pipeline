# Final Risk Scoring Report

## 1. Objective

This module combines supervised fraud probability, unsupervised anomaly score, and rule-based risk score into a final transaction risk score.

## 2. Final score formula

```text
final_risk_score =
    0.50 * fraud_probability
  + 0.30 * anomaly_score
  + 0.20 * rule_based_score
```

## 3. Recommended action distribution

| Recommended action | Count |
|---|---:|
| approve | 15,178 |
| monitor | 7,861 |
| manual_review | 1,883 |
| block_or_urgent_review | 78 |

## 4. Risk level distribution

| Risk level | Count |
|---|---:|
| low | 15,178 |
| medium | 7,861 |
| high | 1,883 |
| very_high | 78 |

## 5. Top 10 highest-risk transactions

| transaction_id | customer_id | amount | fraud_probability | anomaly_score | final_risk_score | action |
|---|---|---:|---:|---:|---:|---|
| T0010722 | C00625 | 876.60 | 0.8623 | 0.8184 | 0.8767 | block_or_urgent_review |
| T0002673 | C00744 | 1159.54 | 0.8109 | 0.8880 | 0.8319 | block_or_urgent_review |
| T0001624 | C00859 | 986.91 | 0.7554 | 0.8217 | 0.8242 | block_or_urgent_review |
| T0023033 | C00317 | 1858.66 | 0.7016 | 0.9003 | 0.8209 | block_or_urgent_review |
| T0015792 | C00056 | 745.36 | 0.8321 | 0.8092 | 0.8188 | block_or_urgent_review |
| T0019353 | C00959 | 1109.28 | 0.7212 | 0.8582 | 0.8180 | block_or_urgent_review |
| T0011556 | C00854 | 705.86 | 0.8324 | 0.7363 | 0.8171 | block_or_urgent_review |
| T0011221 | C00399 | 825.99 | 0.8448 | 0.7132 | 0.8164 | block_or_urgent_review |
| T0022202 | C00826 | 1651.85 | 0.7944 | 0.8583 | 0.8147 | block_or_urgent_review |
| T0019860 | C00275 | 1243.21 | 0.7954 | 0.8550 | 0.8142 | block_or_urgent_review |

## 6. Interpretation

The final score is designed for decision support. High-risk cases should not be treated as automatically fraudulent; they should be prioritized for review according to the institution's governance, compliance, and risk policies.
