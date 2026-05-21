# Feature Dictionary

## Identification columns

| Feature | Meaning |
|---|---|
| transaction_id | Unique transaction identifier |
| customer_id | Unique customer identifier |
| account_id | Unique account identifier |
| transaction_date | Transaction date |

## Transaction-level features

| Feature | Meaning |
|---|---|
| amount | Transaction amount |
| transaction_hour | Hour of transaction, from 0 to 23 |
| is_international | Flag for international transaction |
| is_night_transaction | Flag for transactions between midnight and 5 AM |
| is_high_risk_category | Flag for categories such as crypto, gambling, and luxury |
| is_customer_state_diff | Flag for transaction state different from customer's home state |

## Customer and account features

| Feature | Meaning |
|---|---|
| age | Customer age |
| income_numeric | Encoded income range |
| customer_risk_numeric | Encoded customer risk profile |
| credit_limit | Account credit limit |
| account_age_days | Days between account opening and transaction date |

## Behavioral features

| Feature | Meaning |
|---|---|
| customer_total_transactions | Total number of transactions by customer |
| customer_avg_amount | Average transaction amount by customer |
| customer_std_amount | Standard deviation of transaction amount by customer |
| customer_max_amount | Maximum transaction amount by customer |
| customer_total_amount | Total amount transacted by customer |
| customer_unique_devices | Number of unique devices used by customer |
| customer_international_ratio | Share of international transactions by customer |
| customer_night_ratio | Share of night transactions by customer |
| customer_diff_state_ratio | Share of transactions outside customer's home state |
| customer_high_risk_category_ratio | Share of transactions in high-risk categories |

## Temporal and deviation features

| Feature | Meaning |
|---|---|
| amount_vs_customer_avg | Transaction amount divided by customer average |
| amount_zscore_by_customer | Amount deviation from customer's historical average |
| days_since_previous_transaction | Days since customer's previous transaction |
| previous_amount | Previous transaction amount by customer |
| amount_change_from_previous | Difference between current and previous transaction amount |

## Rule-based risk features

| Feature | Meaning |
|---|---|
| rule_high_amount | Flag for transaction at least 5 times customer average |
| rule_amount_zscore | Flag for transaction at least 3 standard deviations above customer average |
| rule_new_or_rare_device | Proxy flag for customers with many unique devices |
| rule_based_score | Weighted rule-based risk score |

## Target labels

| Feature | Meaning |
|---|---|
| fraud_label | Synthetic supervised fraud label |
| aml_alert_label | Synthetic AML-inspired alert label |
