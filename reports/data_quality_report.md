# Data Quality Report

## 1. Row counts

| Dataset | Raw rows | Clean rows | Removed rows |
|---|---:|---:|---:|
| customers | 1,000 | 1,000 | 0 |
| accounts | 1,000 | 1,000 | 0 |
| transactions | 25,000 | 25,000 | 0 |
| alerts | 25,000 | 25,000 | 0 |

## 2. Missing values after cleaning

### customers

No missing values detected after cleaning.

### accounts

No missing values detected after cleaning.

### transactions

No missing values detected after cleaning.

### alerts

No missing values detected after cleaning.

## 3. Cleaning rules applied

- Removed duplicate primary keys.
- Converted date and numeric fields to proper data types.
- Removed invalid ages, amounts, hours, labels, and categories.
- Kept only transactions linked to valid customers and accounts.
- Kept only alerts linked to valid transactions.
