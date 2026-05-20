"""
Data cleaning module for the AI Fraud Risk Detection Pipeline.

This script reads the synthetic raw CSV files, applies basic cleaning rules,
validates key columns, and saves clean datasets as Parquet files.

Input:
- data/raw/customers.csv
- data/raw/accounts.csv
- data/raw/transactions.csv
- data/raw/alerts.csv

Output:
- data/processed/customers_clean.parquet
- data/processed/accounts_clean.parquet
- data/processed/transactions_clean.parquet
- data/processed/alerts_clean.parquet
- reports/data_quality_report.md
"""

from pathlib import Path
import pandas as pd


RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")
REPORTS_DIR = Path("reports")


def ensure_directories() -> None:
    """Create output directories if they do not exist."""
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)


def read_raw_data() -> dict[str, pd.DataFrame]:
    """Read raw CSV files into pandas DataFrames."""
    files = {
        "customers": RAW_DIR / "customers.csv",
        "accounts": RAW_DIR / "accounts.csv",
        "transactions": RAW_DIR / "transactions.csv",
        "alerts": RAW_DIR / "alerts.csv",
    }

    missing_files = [str(path) for path in files.values() if not path.exists()]
    if missing_files:
        raise FileNotFoundError(
            "Missing raw data files. Run src/data_generator.py first. "
            f"Missing: {missing_files}"
        )

    return {
        name: pd.read_csv(path)
        for name, path in files.items()
    }


def clean_customers(df: pd.DataFrame) -> pd.DataFrame:
    """Clean customer data."""
    df = df.copy()

    df["customer_id"] = df["customer_id"].astype(str)
    df["age"] = pd.to_numeric(df["age"], errors="coerce")
    df["account_open_date"] = pd.to_datetime(df["account_open_date"], errors="coerce")

    df = df.drop_duplicates(subset=["customer_id"])
    df = df[df["age"].between(18, 100)]
    df = df.dropna(subset=["customer_id", "age", "account_open_date"])

    valid_income = {"low", "medium", "high", "very_high"}
    valid_segment = {"retail", "premium", "business"}
    valid_risk = {"low", "medium", "high"}

    df = df[df["income_range"].isin(valid_income)]
    df = df[df["segment"].isin(valid_segment)]
    df = df[df["risk_profile"].isin(valid_risk)]

    return df.reset_index(drop=True)


def clean_accounts(df: pd.DataFrame, customers: pd.DataFrame) -> pd.DataFrame:
    """Clean account data and keep only valid customers."""
    df = df.copy()

    df["customer_id"] = df["customer_id"].astype(str)
    df["account_id"] = df["account_id"].astype(str)
    df["credit_limit"] = pd.to_numeric(df["credit_limit"], errors="coerce")

    df = df.drop_duplicates(subset=["account_id"])
    df = df.dropna(subset=["customer_id", "account_id", "credit_limit"])

    valid_customers = set(customers["customer_id"])
    df = df[df["customer_id"].isin(valid_customers)]

    valid_account_type = {"checking", "savings", "digital"}
    valid_status = {"active", "inactive", "blocked"}

    df = df[df["account_type"].isin(valid_account_type)]
    df = df[df["account_status"].isin(valid_status)]
    df = df[df["credit_limit"] > 0]

    return df.reset_index(drop=True)


def clean_transactions(
    df: pd.DataFrame,
    customers: pd.DataFrame,
    accounts: pd.DataFrame,
) -> pd.DataFrame:
    """Clean transaction data and keep only valid customer/account relationships."""
    df = df.copy()

    df["transaction_id"] = df["transaction_id"].astype(str)
    df["customer_id"] = df["customer_id"].astype(str)
    df["account_id"] = df["account_id"].astype(str)
    df["transaction_date"] = pd.to_datetime(df["transaction_date"], errors="coerce")
    df["transaction_hour"] = pd.to_numeric(df["transaction_hour"], errors="coerce")
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
    df["is_international"] = pd.to_numeric(df["is_international"], errors="coerce")

    df = df.drop_duplicates(subset=["transaction_id"])
    df = df.dropna(
        subset=[
            "transaction_id",
            "customer_id",
            "account_id",
            "transaction_date",
            "transaction_hour",
            "amount",
        ]
    )

    valid_customers = set(customers["customer_id"])
    valid_accounts = set(accounts["account_id"])

    df = df[df["customer_id"].isin(valid_customers)]
    df = df[df["account_id"].isin(valid_accounts)]

    df = df[df["transaction_hour"].between(0, 23)]
    df = df[df["amount"] > 0]
    df = df[df["is_international"].isin([0, 1])]

    valid_channels = {
        "card_present",
        "ecommerce",
        "mobile_app",
        "atm",
        "bank_transfer",
    }

    valid_categories = {
        "grocery",
        "fuel",
        "restaurant",
        "travel",
        "electronics",
        "cash_withdrawal",
        "online_services",
        "crypto",
        "gambling",
        "luxury",
    }

    df = df[df["channel"].isin(valid_channels)]
    df = df[df["merchant_category"].isin(valid_categories)]

    return df.reset_index(drop=True)


def clean_alerts(df: pd.DataFrame, transactions: pd.DataFrame) -> pd.DataFrame:
    """Clean fraud and AML-inspired alert labels."""
    df = df.copy()

    df["transaction_id"] = df["transaction_id"].astype(str)
    df["fraud_label"] = pd.to_numeric(df["fraud_label"], errors="coerce")
    df["aml_alert_label"] = pd.to_numeric(df["aml_alert_label"], errors="coerce")

    df = df.drop_duplicates(subset=["transaction_id"])
    df = df.dropna(subset=["transaction_id", "fraud_label", "aml_alert_label"])

    valid_transactions = set(transactions["transaction_id"])
    df = df[df["transaction_id"].isin(valid_transactions)]

    df = df[df["fraud_label"].isin([0, 1])]
    df = df[df["aml_alert_label"].isin([0, 1])]

    df["fraud_label"] = df["fraud_label"].astype(int)
    df["aml_alert_label"] = df["aml_alert_label"].astype(int)

    return df.reset_index(drop=True)


def create_quality_report(
    raw_data: dict[str, pd.DataFrame],
    clean_data: dict[str, pd.DataFrame],
) -> str:
    """Create a simple markdown data quality report."""
    lines = []

    lines.append("# Data Quality Report")
    lines.append("")
    lines.append("## 1. Row counts")
    lines.append("")
    lines.append("| Dataset | Raw rows | Clean rows | Removed rows |")
    lines.append("|---|---:|---:|---:|")

    for name in raw_data:
        raw_rows = len(raw_data[name])
        clean_rows = len(clean_data[name])
        removed = raw_rows - clean_rows
        lines.append(f"| {name} | {raw_rows:,} | {clean_rows:,} | {removed:,} |")

    lines.append("")
    lines.append("## 2. Missing values after cleaning")
    lines.append("")

    for name, df in clean_data.items():
        lines.append(f"### {name}")
        lines.append("")
        missing = df.isna().sum()
        missing = missing[missing > 0]

        if missing.empty:
            lines.append("No missing values detected after cleaning.")
        else:
            lines.append("| Column | Missing values |")
            lines.append("|---|---:|")
            for col, value in missing.items():
                lines.append(f"| {col} | {value:,} |")

        lines.append("")

    lines.append("## 3. Cleaning rules applied")
    lines.append("")
    lines.append("- Removed duplicate primary keys.")
    lines.append("- Converted date and numeric fields to proper data types.")
    lines.append("- Removed invalid ages, amounts, hours, labels, and categories.")
    lines.append("- Kept only transactions linked to valid customers and accounts.")
    lines.append("- Kept only alerts linked to valid transactions.")
    lines.append("")

    return "\n".join(lines)


def save_clean_data(clean_data: dict[str, pd.DataFrame]) -> None:
    """Save clean datasets as Parquet files."""
    for name, df in clean_data.items():
        output_path = PROCESSED_DIR / f"{name}_clean.parquet"
        df.to_parquet(output_path, index=False)


def main() -> None:
    """Run full cleaning pipeline."""
    ensure_directories()

    raw_data = read_raw_data()

    customers = clean_customers(raw_data["customers"])
    accounts = clean_accounts(raw_data["accounts"], customers)
    transactions = clean_transactions(raw_data["transactions"], customers, accounts)
    alerts = clean_alerts(raw_data["alerts"], transactions)

    clean_data = {
        "customers": customers,
        "accounts": accounts,
        "transactions": transactions,
        "alerts": alerts,
    }

    save_clean_data(clean_data)

    report = create_quality_report(raw_data, clean_data)
    report_path = REPORTS_DIR / "data_quality_report.md"
    report_path.write_text(report, encoding="utf-8")

    print("Data cleaning completed successfully.")
    for name, df in clean_data.items():
        print(f"{name}: {len(df):,} clean rows")
    print(f"Quality report: {report_path.resolve()}")


if __name__ == "__main__":
    main()
