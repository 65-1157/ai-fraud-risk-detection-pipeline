# Monitoring Report

## 1. Objective

This report provides a lightweight monitoring view of the fraud risk pipeline. It is designed to demonstrate MLOps thinking for score distribution, review workload, and operational risk monitoring.

## 2. Dataset overview

- Total scored transactions: **25,000**
- Unique customers: **1,000**
- Average transaction amount: **130.80**
- Fraud label rate: **4.95%**
- AML-inspired alert rate: **4.50%**

## 3. Risk level distribution

| Category | Count | Percentage |
|---|---:|---:|
| low | 15,178 | 60.71% |
| medium | 7,861 | 31.44% |
| high | 1,883 | 7.53% |
| very_high | 78 | 0.31% |

## 4. Recommended action distribution

| Category | Count | Percentage |
|---|---:|---:|
| approve | 15,178 | 60.71% |
| monitor | 7,861 | 31.44% |
| manual_review | 1,883 | 7.53% |
| block_or_urgent_review | 78 | 0.31% |

## 5. Final risk score summary

| Statistic | Value |
|---|---:|
| mean | 0.2683 |
| median | 0.1737 |
| std | 0.1614 |
| min | 0.0801 |
| p25 | 0.1311 |
| p75 | 0.4245 |
| p90 | 0.4808 |
| p95 | 0.5411 |
| max | 0.8767 |

## 6. Fraud probability summary

| Statistic | Value |
|---|---:|
| mean | 0.3210 |
| median | 0.1686 |
| std | 0.2252 |
| min | 0.0795 |
| p25 | 0.1303 |
| p75 | 0.5731 |
| p90 | 0.6406 |
| p95 | 0.6707 |
| max | 0.8985 |

## 7. Anomaly score summary

| Statistic | Value |
|---|---:|
| mean | 0.2159 |
| median | 0.1892 |
| std | 0.1356 |
| min | 0.0000 |
| p25 | 0.1169 |
| p75 | 0.2824 |
| p90 | 0.3849 |
| p95 | 0.4641 |
| max | 1.0000 |

## 8. Rule-based score summary

| Statistic | Value |
|---|---:|
| mean | 0.2154 |
| median | 0.1500 |
| std | 0.1386 |
| min | 0.0000 |
| p25 | 0.1500 |
| p75 | 0.3500 |
| p90 | 0.4000 |
| p95 | 0.4000 |
| max | 1.0000 |

## 9. Monitoring flags

- No major monitoring flags detected under the current thresholds.

## 10. Suggested production monitoring extensions

In a production environment, this monitoring layer should be extended to track:

- data drift between training and scoring windows;
- feature distribution drift;
- model performance decay when labels become available;
- alert volume by day, week, channel, and customer segment;
- false positive and false negative feedback from analysts;
- model retraining triggers;
- approval workflow and auditability.

## 11. Interview relevance

This module demonstrates that the project does not stop at model training. It also considers the operational layer required to monitor model outputs and business impact over time.
