"""
PySpark feature engineering module for the AI Fraud Risk Detection Pipeline.

This script reads the clean Parquet datasets and creates a model-ready feature table.

Input:
- data/processed/customers_clean.parquet
- data/processed/accounts_clean.parquet
- data/processed/transactions_clean.parquet
- data/processed/alerts_clean.parquet

Output:
- data/processed/features_model_ready.parquet
- reports/feature_dictionary.md
"""

from pathlib import Path
import shutil

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.window import Window


PROCESSED_DIR = Path("data/processed")
REPORTS_DIR = Path("reports")


def create_spark_session() -> SparkSession:
    """
    Create a local Spark session.

    The configuration below keeps the local Windows execution cleaner by
    reducing unnecessary Spark console output.
    """
    spark = (
        SparkSession.builder
        .appName("AI Fraud Risk Feature Engineering")
        .master("local[*]")
        .config("spark.sql.shuffle.partitions", "8")
        .config("spark.ui.showConsoleProgress", "false")
        .config("spark.sql.debug.maxToStringFields", "200")
        .getOrCreate()
    )

    spark.sparkContext.setLogLevel("ERROR")
    return spark


def read_clean_data(spark: SparkSession) -> dict:
    """Read clean Parquet datasets."""
    paths = {
        "customers": PROCESSED_DIR / "customers_clean.parquet",
        "accounts": PROCESSED_DIR / "accounts_clean.parquet",
        "transactions": PROCESSED_DIR / "transactions_clean.parquet",
        "alerts": PROCESSED_DIR / "alerts_clean.parquet",
    }

    missing = [str(path) for path in paths.values() if not path.exists()]
    if missing:
        raise FileNotFoundError(
            "Missing clean Parquet files. Run src/cleaning.py first. "
            f"Missing: {missing}"
        )

    return {
        name: spark.read.parquet(str(path))
        for name, path in paths.items()
    }


def build_base_table(data: dict):
    """Join transactions with customers, accounts, and alert labels."""
    transactions = data["transactions"]
    customers = data["customers"]
    accounts = data["accounts"]
    alerts = data["alerts"]

    customers_selected = customers.select(
        "customer_id",
        "age",
        "income_range",
        "segment",
        "state",
        "account_open_date",
        "risk_profile",
    ).withColumnRenamed("state", "customer_state")

    accounts_selected = accounts.select(
        "customer_id",
        "account_id",
        "account_type",
        "account_status",
        "credit_limit",
    )

    alerts_selected = alerts.select(
        "transaction_id",
        "fraud_label",
        "aml_alert_label",
    )

    df = (
        transactions
        .join(customers_selected, on="customer_id", how="left")
        .join(accounts_selected, on=["customer_id", "account_id"], how="left")
        .join(alerts_selected, on="transaction_id", how="left")
    )

    return df


def add_transaction_level_features(df):
    """Create transaction-level fraud-risk features."""
    df = df.withColumn(
        "is_night_transaction",
        F.when(F.col("transaction_hour").between(0, 5), 1).otherwise(0),
    )

    df = df.withColumn(
        "is_high_risk_category",
        F.when(F.col("merchant_category").isin("crypto", "gambling", "luxury"), 1).otherwise(0),
    )

    df = df.withColumn(
        "is_customer_state_diff",
        F.when(F.col("state") != F.col("customer_state"), 1).otherwise(0),
    )

    df = df.withColumn(
        "account_age_days",
        F.datediff(F.col("transaction_date"), F.col("account_open_date")),
    )

    df = df.withColumn(
        "customer_risk_numeric",
        F.when(F.col("risk_profile") == "low", 0)
        .when(F.col("risk_profile") == "medium", 1)
        .when(F.col("risk_profile") == "high", 2)
        .otherwise(0),
    )

    df = df.withColumn(
        "income_numeric",
        F.when(F.col("income_range") == "low", 0)
        .when(F.col("income_range") == "medium", 1)
        .when(F.col("income_range") == "high", 2)
        .when(F.col("income_range") == "very_high", 3)
        .otherwise(0),
    )

    return df


def add_customer_behavior_features(df):
    """Create customer-level behavior features using Spark aggregations."""
    customer_agg = (
        df.groupBy("customer_id")
        .agg(
            F.count("transaction_id").alias("customer_total_transactions"),
            F.avg("amount").alias("customer_avg_amount"),
            F.stddev("amount").alias("customer_std_amount"),
            F.max("amount").alias("customer_max_amount"),
            F.sum("amount").alias("customer_total_amount"),
            F.countDistinct("device_id").alias("customer_unique_devices"),
            F.avg("is_international").alias("customer_international_ratio"),
            F.avg("is_night_transaction").alias("customer_night_ratio"),
            F.avg("is_customer_state_diff").alias("customer_diff_state_ratio"),
            F.avg("is_high_risk_category").alias("customer_high_risk_category_ratio"),
        )
    )

    df = df.join(customer_agg, on="customer_id", how="left")

    df = df.withColumn(
        "amount_vs_customer_avg",
        F.col("amount") / F.when(F.col("customer_avg_amount") > 0, F.col("customer_avg_amount")).otherwise(F.lit(1)),
    )

    df = df.withColumn(
        "amount_zscore_by_customer",
        (F.col("amount") - F.col("customer_avg_amount"))
        / F.when(F.col("customer_std_amount") > 0, F.col("customer_std_amount")).otherwise(F.lit(1)),
    )

    return df


def add_window_features(df):
    """Create simple temporal features with Spark window functions."""
    customer_time_window = Window.partitionBy("customer_id").orderBy("transaction_date", "transaction_id")

    df = df.withColumn(
        "previous_transaction_date",
        F.lag("transaction_date").over(customer_time_window),
    )

    df = df.withColumn(
        "days_since_previous_transaction",
        F.datediff(F.col("transaction_date"), F.col("previous_transaction_date")),
    )

    df = df.withColumn(
        "previous_amount",
        F.lag("amount").over(customer_time_window),
    )

    df = df.withColumn(
        "amount_change_from_previous",
        F.col("amount") - F.col("previous_amount"),
    )

    df = df.fillna(
        {
            "days_since_previous_transaction": 999,
            "previous_amount": 0.0,
            "amount_change_from_previous": 0.0,
        }
    )

    return df


def add_rule_based_score(df):
    """Create a simple rule-based risk score."""
    df = df.withColumn(
        "rule_high_amount",
        F.when(F.col("amount_vs_customer_avg") >= 5, 1).otherwise(0),
    )

    df = df.withColumn(
        "rule_amount_zscore",
        F.when(F.col("amount_zscore_by_customer") >= 3, 1).otherwise(0),
    )

    df = df.withColumn(
        "rule_new_or_rare_device",
        F.when(F.col("customer_unique_devices") >= 8, 1).otherwise(0),
    )

    df = df.withColumn(
        "rule_based_score",
        (
            0.25 * F.col("is_high_risk_category")
            + 0.20 * F.col("is_night_transaction")
            + 0.20 * F.col("is_international")
            + 0.15 * F.col("is_customer_state_diff")
            + 0.10 * F.col("rule_high_amount")
            + 0.10 * F.col("rule_amount_zscore")
        ),
    )

    return df


def select_model_ready_columns(df):
    """Select final model-ready features."""
    selected_columns = [
        "transaction_id",
        "customer_id",
        "account_id",
        "transaction_date",

        "amount",
        "transaction_hour",
        "is_international",
        "is_night_transaction",
        "is_high_risk_category",
        "is_customer_state_diff",

        "age",
        "income_numeric",
        "customer_risk_numeric",
        "credit_limit",
        "account_age_days",

        "customer_total_transactions",
        "customer_avg_amount",
        "customer_std_amount",
        "customer_max_amount",
        "customer_total_amount",
        "customer_unique_devices",
        "customer_international_ratio",
        "customer_night_ratio",
        "customer_diff_state_ratio",
        "customer_high_risk_category_ratio",

        "amount_vs_customer_avg",
        "amount_zscore_by_customer",
        "days_since_previous_transaction",
        "previous_amount",
        "amount_change_from_previous",

        "rule_high_amount",
        "rule_amount_zscore",
        "rule_new_or_rare_device",
        "rule_based_score",

        "fraud_label",
        "aml_alert_label",
    ]

    return df.select(*selected_columns)


def write_feature_dictionary() -> None:
    """Write a markdown feature dictionary."""
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    content = """# Feature Dictionary

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
"""

    (REPORTS_DIR / "feature_dictionary.md").write_text(content, encoding="utf-8")


def main() -> None:
    """Run PySpark feature engineering pipeline."""
    spark = create_spark_session()

    try:
        data = read_clean_data(spark)

        df = build_base_table(data)
        df = add_transaction_level_features(df)
        df = add_customer_behavior_features(df)
        df = add_window_features(df)
        df = add_rule_based_score(df)

        features = select_model_ready_columns(df)

        output_path = PROCESSED_DIR / "features_model_ready.parquet"

        # Local Windows-safe output strategy:
        # Spark performs the feature engineering, but pandas/pyarrow writes the
        # final compact feature table to avoid Hadoop/winutils write issues.
        if output_path.exists():
            if output_path.is_dir():
                shutil.rmtree(output_path)
            else:
                output_path.unlink()

        row_count = features.count()
        column_count = len(features.columns)

        features_pd = features.toPandas()
        features_pd.to_parquet(
            output_path,
            index=False,
            engine="pyarrow",
            coerce_timestamps="ms",
            allow_truncated_timestamps=True,
        )

        write_feature_dictionary()

        print("PySpark feature engineering completed successfully.")
        print(f"Rows: {row_count:,}")
        print(f"Columns: {column_count:,}")
        print(f"Output: {output_path.resolve()}")
        print(f"Feature dictionary: {(REPORTS_DIR / 'feature_dictionary.md').resolve()}")

    finally:
        spark.stop()


if __name__ == "__main__":
    main()
