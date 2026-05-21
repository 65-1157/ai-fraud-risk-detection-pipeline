# Supervised Fraud Model Results

## 1. Objective

This module trains a supervised Random Forest classifier to predict the synthetic fraud label using transaction, customer, behavioral, temporal, and rule-based risk features.

## 2. Dataset summary

- Rows used: **25,000**
- Fraud rate: **4.95%**

## 3. Metrics

| Metric | Value |
|---|---:|
| Accuracy | 0.6882 |
| Precision | 0.1110 |
| Recall | 0.7573 |
| F1-score | 0.1936 |
| ROC-AUC | 0.7593 |

## 4. Confusion matrix

|  | Predicted 0 | Predicted 1 |
|---|---:|---:|
| Actual 0 | 4,067 | 1,874 |
| Actual 1 | 75 | 234 |

## 5. Interpretation

In fraud detection, accuracy alone is not enough because fraud is often a minority class. Recall is important because it measures how many fraud cases were captured. Precision is also important because false positives increase the manual review workload.

## 6. Top feature importances

| Rank | Feature | Importance |
|---:|---|---:|
| 1 | rule_based_score | 0.2720 |
| 2 | is_high_risk_category | 0.0961 |
| 3 | is_night_transaction | 0.0913 |
| 4 | transaction_hour | 0.0756 |
| 5 | customer_risk_numeric | 0.0675 |
| 6 | amount | 0.0407 |
| 7 | amount_change_from_previous | 0.0376 |
| 8 | amount_vs_customer_avg | 0.0342 |
| 9 | amount_zscore_by_customer | 0.0277 |
| 10 | customer_total_amount | 0.0212 |
| 11 | account_age_days | 0.0208 |
| 12 | customer_max_amount | 0.0207 |
| 13 | is_international | 0.0193 |
| 14 | customer_avg_amount | 0.0191 |
| 15 | customer_std_amount | 0.0176 |

## 7. Classification report

```text
              precision    recall  f1-score   support

           0       0.98      0.68      0.81      5941
           1       0.11      0.76      0.19       309

    accuracy                           0.69      6250
   macro avg       0.55      0.72      0.50      6250
weighted avg       0.94      0.69      0.78      6250

```
