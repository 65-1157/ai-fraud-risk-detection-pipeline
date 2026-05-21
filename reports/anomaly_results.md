# Unsupervised Anomaly Detection Results

## 1. Objective

This module uses Isolation Forest to identify unusual transactions without using the fraud label during training.

The fraud label is used only afterward as a reference comparison, not as a training target.

## 2. Model

- Algorithm: Isolation Forest
- Contamination: 8%
- Input: engineered transaction and customer behavior features

## 3. Reference comparison metrics

| Metric | Value |
|---|---:|
| Fraud rate | 4.95% |
| Anomaly rate | 8.00% |
| Precision vs fraud label | 0.1525 |
| Recall vs fraud label | 0.2464 |
| F1-score vs fraud label | 0.1884 |

## 4. Confusion matrix against fraud reference

|  | Predicted normal | Predicted anomaly |
|---|---:|---:|
| Actual non-fraud | 22,067 | 1,695 |
| Actual fraud | 933 | 305 |

## 5. Interpretation

Anomaly detection is useful when fraud labels are incomplete, delayed, or unavailable. It helps identify unusual patterns that may deserve manual review, even if they do not perfectly overlap with known fraud labels.

## 6. Top anomaly examples

| transaction_id | customer_id | amount | anomaly_score | fraud_label |
|---|---|---:|---:|---:|
| T0005174 | C00831 | 2194.75 | 1.0000 | 0 |
| T0015379 | C00721 | 2762.79 | 0.9836 | 0 |
| T0005860 | C00546 | 3694.89 | 0.9808 | 0 |
| T0023432 | C00920 | 2953.39 | 0.9714 | 1 |
| T0006341 | C00559 | 2907.76 | 0.9712 | 0 |
| T0000891 | C00274 | 2299.51 | 0.9475 | 0 |
| T0020388 | C00610 | 1793.40 | 0.9373 | 0 |
| T0014230 | C00400 | 4341.50 | 0.9348 | 1 |
| T0020823 | C00385 | 2102.32 | 0.9320 | 0 |
| T0004218 | C00048 | 1863.51 | 0.9173 | 0 |
