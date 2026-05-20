"""
Synthetic data generator for the AI Fraud Risk Detection Pipeline.

This module creates synthetic but realistic financial data for:
- customers
- accounts
- transactions
- fraud / AML-inspired alerts

The generated data is safe for public GitHub use because it does not contain
real customer information.
"""

from pathlib import Path
import numpy as np
import pandas as pd


RANDOM_SEED = 42

N_CUSTOMERS = 1_000
N_TRANSACTIONS = 25_000

RAW_DIR = Path("data/raw")


def ensure_directories() -> None:
    """Create required data directories if they do not exist."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)


def generate_customers(n_customers: int = N_CUSTOMERS) -> pd.DataFrame:
    """Generate synthetic customer-level data."""
    rng = np.random.default_rng(RANDOM_SEED)

    customer_ids = [f"C{str(i).zfill(5)}" for i in range(1, n_customers + 1)]

    age = rng.integers(18, 80, size=n_customers)

    income_range = rng.choice(
        ["low", "medium", "high", "very_high"],
        size=n_customers,
        p=[0.35, 0.40, 0.20, 0.05],
    )

    segment = rng.choice(
        ["retail", "premium", "business"],
        size=n_customers,
        p=[0.75, 0.20, 0.05],
    )

    state = rng.choice(
        ["SP", "RJ", "MG", "PR", "RS", "BA", "PE", "DF", "CE", "SC"],
        size=n_customers,
        p=[0.32, 0.12, 0.11, 0.08, 0.07, 0.07, 0.06, 0.05, 0.06, 0.06],
    )

    risk_profile = rng.choice(
        ["low", "medium", "high"],
        size=n_customers,
        p=[0.70, 0.25, 0.05],
    )

    start_dates = pd.to_datetime("2018-01-01") + pd.to_timedelta(
        rng.integers(0, 2_200, size=n_customers), unit="D"
    )

    customers = pd.DataFrame(
        {
            "customer_id": customer_ids,
            "age": age,
            "income_range": income_range,
            "segment": segment,
            "state": state,
            "account_open_date": start_dates,
            "risk_profile": risk_profile,
        }
    )

    return customers


def generate_accounts(customers: pd.DataFrame) -> pd.DataFrame:
    """Generate synthetic account data linked to customers."""
    rng = np.random.default_rng(RANDOM_SEED + 1)

    accounts = customers[["customer_id"]].copy()
    accounts["account_id"] = [f"A{str(i).zfill(5)}" for i in range(1, len(accounts) + 1)]

    accounts["account_type"] = rng.choice(
        ["checking", "savings", "digital"],
        size=len(accounts),
        p=[0.55, 0.25, 0.20],
    )

    accounts["account_status"] = rng.choice(
        ["active", "inactive", "blocked"],
        size=len(accounts),
        p=[0.92, 0.06, 0.02],
    )

    accounts["credit_limit"] = rng.choice(
        [1000, 2500, 5000, 10000, 20000, 50000],
        size=len(accounts),
        p=[0.25, 0.25, 0.20, 0.15, 0.10, 0.05],
    )

    return accounts


def generate_transactions(
    customers: pd.DataFrame,
    accounts: pd.DataFrame,
    n_transactions: int = N_TRANSACTIONS,
) -> pd.DataFrame:
    """Generate synthetic transaction-level data."""
    rng = np.random.default_rng(RANDOM_SEED + 2)

    customer_sample = rng.choice(customers["customer_id"], size=n_transactions)
    account_lookup = accounts.set_index("customer_id")["account_id"].to_dict()
    account_sample = [account_lookup[c] for c in customer_sample]

    start_date = pd.to_datetime("2024-01-01")
    transaction_dates = start_date + pd.to_timedelta(
        rng.integers(0, 365, size=n_transactions), unit="D"
    )

    transaction_hour = rng.integers(0, 24, size=n_transactions)

    merchant_category = rng.choice(
        [
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
        ],
        size=n_transactions,
        p=[0.24, 0.12, 0.16, 0.08, 0.10, 0.10, 0.10, 0.03, 0.03, 0.04],
    )

    channel = rng.choice(
        ["card_present", "ecommerce", "mobile_app", "atm", "bank_transfer"],
        size=n_transactions,
        p=[0.35, 0.25, 0.20, 0.10, 0.10],
    )

    state = rng.choice(
        ["SP", "RJ", "MG", "PR", "RS", "BA", "PE", "DF", "CE", "SC"],
        size=n_transactions,
        p=[0.32, 0.12, 0.11, 0.08, 0.07, 0.07, 0.06, 0.05, 0.06, 0.06],
    )

    is_international = rng.choice([0, 1], size=n_transactions, p=[0.96, 0.04])

    device_id = [
        f"D{rng.integers(1, 2500):05d}" for _ in range(n_transactions)
    ]

    # Base amount: lognormal distribution creates a realistic long-tail behavior.
    amount = rng.lognormal(mean=4.0, sigma=0.9, size=n_transactions)

    # Merchant-specific amplification.
    high_amount_categories = np.isin(
        merchant_category, ["travel", "electronics", "crypto", "gambling", "luxury"]
    )
    amount = np.where(high_amount_categories, amount * rng.uniform(1.5, 4.0, size=n_transactions), amount)

    # International transactions tend to be larger.
    amount = np.where(is_international == 1, amount * rng.uniform(1.8, 3.5, size=n_transactions), amount)

    amount = np.round(amount, 2)

    transactions = pd.DataFrame(
        {
            "transaction_id": [f"T{str(i).zfill(7)}" for i in range(1, n_transactions + 1)],
            "customer_id": customer_sample,
            "account_id": account_sample,
            "transaction_date": transaction_dates,
            "transaction_hour": transaction_hour,
            "amount": amount,
            "merchant_category": merchant_category,
            "channel": channel,
            "state": state,
            "is_international": is_international,
            "device_id": device_id,
        }
    )

    return transactions


def generate_alerts(transactions: pd.DataFrame, customers: pd.DataFrame) -> pd.DataFrame:
    """
    Generate synthetic fraud and AML-inspired labels.

    The labels are created from simple probabilistic rules so the project has
    realistic signal without using private data.
    """
    rng = np.random.default_rng(RANDOM_SEED + 3)

    customer_risk = customers.set_index("customer_id")["risk_profile"].to_dict()
    tx = transactions.copy()
    tx["customer_risk_profile"] = tx["customer_id"].map(customer_risk)

    high_risk_category = tx["merchant_category"].isin(["crypto", "gambling", "luxury"]).astype(int)
    night_transaction = tx["transaction_hour"].between(0, 5).astype(int)
    high_amount = (tx["amount"] > tx["amount"].quantile(0.97)).astype(int)
    international = tx["is_international"]

    customer_high_risk = (tx["customer_risk_profile"] == "high").astype(int)

    raw_score = (
        0.30 * high_risk_category
        + 0.20 * night_transaction
        + 0.30 * high_amount
        + 0.25 * international
        + 0.25 * customer_high_risk
    )

    fraud_probability = np.clip(0.01 + raw_score * 0.35, 0, 0.95)
    aml_probability = np.clip(0.01 + raw_score * 0.25 + 0.15 * international, 0, 0.95)

    fraud_label = rng.binomial(1, fraud_probability)
    aml_alert_label = rng.binomial(1, aml_probability)

    alerts = pd.DataFrame(
        {
            "transaction_id": tx["transaction_id"],
            "fraud_label": fraud_label,
            "aml_alert_label": aml_alert_label,
        }
    )

    return alerts


def save_dataframes(
    customers: pd.DataFrame,
    accounts: pd.DataFrame,
    transactions: pd.DataFrame,
    alerts: pd.DataFrame,
) -> None:
    """Save generated datasets as CSV files."""
    customers.to_csv(RAW_DIR / "customers.csv", index=False)
    accounts.to_csv(RAW_DIR / "accounts.csv", index=False)
    transactions.to_csv(RAW_DIR / "transactions.csv", index=False)
    alerts.to_csv(RAW_DIR / "alerts.csv", index=False)


def main() -> None:
    """Run the synthetic data generation pipeline."""
    ensure_directories()

    customers = generate_customers()
    accounts = generate_accounts(customers)
    transactions = generate_transactions(customers, accounts)
    alerts = generate_alerts(transactions, customers)

    save_dataframes(customers, accounts, transactions, alerts)

    print("Synthetic data generated successfully.")
    print(f"Customers:     {len(customers):,}")
    print(f"Accounts:      {len(accounts):,}")
    print(f"Transactions:  {len(transactions):,}")
    print(f"Alerts:        {len(alerts):,}")
    print(f"Output folder: {RAW_DIR.resolve()}")


if __name__ == "__main__":
    main()
