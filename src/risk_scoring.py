"""
Final risk scoring module.

This script combines:
- supervised fraud probability;
- unsupervised anomaly score;
- rule-based score;

to create a final transaction risk score and recommended action.

Input:
- data/processed/features_model_ready.parquet
- data/processed/anomaly_scored_transactions.csv

Output:
- data/processed/risk_scored_transactions.csv
- reports/risk_scoring_report.md
"""

from pathlib import Path

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split


PROCESSED_DIR = Path("data/processed")
REPORTS_DIR = Path("reports")

FEATURE_PATH = PROCESSED_DIR / "features_model_ready.parquet"
ANOMALY_PATH = PROCESSED_DIR / "anomaly_scored_transactions.csv"
OUTPUT_PATH = PROCESSED_DIR / "risk_scored_transactions.csv"
REPORT_PATH = REPORTS_DIR / "risk_scoring_report.md"

TARGET_COLUMN = "fraud_label"

FEATURE_COLUMNS = [
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
]


def load_feature_data() -> pd.DataFrame:
    """Load model-ready features."""
    if not FEATURE_PATH.exists():
        raise FileNotFoundError("Run src/features_pyspark.py first.")

    df = pd.read_parquet(FEATURE_PATH)

    required_columns = [
        "transaction_id",
        "customer_id",
        "transaction_date",
        "amount",
        "rule_based_score",
        TARGET_COLUMN,
        "aml_alert_label",
    ] + FEATURE_COLUMNS

    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    return df


def load_anomaly_scores() -> pd.DataFrame:
    """Load anomaly scores."""
    if not ANOMALY_PATH.exists():
        raise FileNotFoundError("Run src/train_anomaly.py first.")

    anomaly = pd.read_csv(ANOMALY_PATH)

    required_columns = ["transaction_id", "anomaly_score", "anomaly_flag"]
    missing = [col for col in required_columns if col not in anomaly.columns]
    if missing:
        raise ValueError(f"Missing anomaly columns: {missing}")

    return anomaly[required_columns]


def prepare_model_data(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    """Prepare features and target."""
    model_df = df[FEATURE_COLUMNS + [TARGET_COLUMN]].copy()
    model_df = model_df.replace([float("inf"), float("-inf")], pd.NA)

    for col in FEATURE_COLUMNS:
        model_df[col] = pd.to_numeric(model_df[col], errors="coerce")
        model_df[col] = model_df[col].fillna(model_df[col].median())

    model_df[TARGET_COLUMN] = model_df[TARGET_COLUMN].astype(int)

    X = model_df[FEATURE_COLUMNS]
    y = model_df[TARGET_COLUMN]

    return X, y


def train_probability_model(X: pd.DataFrame, y: pd.Series) -> RandomForestClassifier:
    """Train a supervised model to estimate fraud probability."""
    X_train, _, y_train, _ = train_test_split(
        X,
        y,
        test_size=0.25,
        random_state=42,
        stratify=y,
    )

    model = RandomForestClassifier(
        n_estimators=150,
        max_depth=8,
        min_samples_leaf=20,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1,
    )

    model.fit(X_train, y_train)
    return model


def assign_action(score: float) -> str:
    """Assign business action based on final risk score."""
    if score >= 0.75:
        return "block_or_urgent_review"
    if score >= 0.50:
        return "manual_review"
    if score >= 0.30:
        return "monitor"
    return "approve"


def assign_risk_level(score: float) -> str:
    """Assign risk level based on final risk score."""
    if score >= 0.75:
        return "very_high"
    if score >= 0.50:
        return "high"
    if score >= 0.30:
        return "medium"
    return "low"


def create_risk_scores(df: pd.DataFrame, anomaly: pd.DataFrame) -> pd.DataFrame:
    """Create final risk scoring table."""
    X, y = prepare_model_data(df)
    model = train_probability_model(X, y)

    fraud_probability = model.predict_proba(X)[:, 1]

    scored = df[
        [
            "transaction_id",
            "customer_id",
            "transaction_date",
            "amount",
            "rule_based_score",
            "fraud_label",
            "aml_alert_label",
        ]
    ].copy()

    scored["fraud_probability"] = fraud_probability

    scored = scored.merge(
        anomaly,
        on="transaction_id",
        how="left",
    )

    scored["anomaly_score"] = scored["anomaly_score"].fillna(0.0)
    scored["anomaly_flag"] = scored["anomaly_flag"].fillna(0).astype(int)

    scored["final_risk_score"] = (
        0.50 * scored["fraud_probability"]
        + 0.30 * scored["anomaly_score"]
        + 0.20 * scored["rule_based_score"]
    )

    scored["risk_level"] = scored["final_risk_score"].apply(assign_risk_level)
    scored["recommended_action"] = scored["final_risk_score"].apply(assign_action)

    scored = scored.sort_values("final_risk_score", ascending=False)

    return scored


def write_report(scored: pd.DataFrame) -> None:
    """Write risk scoring report."""
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    action_counts = scored["recommended_action"].value_counts()
    risk_counts = scored["risk_level"].value_counts()

    lines = []

    lines.append("# Final Risk Scoring Report")
    lines.append("")
    lines.append("## 1. Objective")
    lines.append("")
    lines.append(
        "This module combines supervised fraud probability, unsupervised anomaly score, "
        "and rule-based risk score into a final transaction risk score."
    )
    lines.append("")

    lines.append("## 2. Final score formula")
    lines.append("")
    lines.append("```text")
    lines.append("final_risk_score =")
    lines.append("    0.50 * fraud_probability")
    lines.append("  + 0.30 * anomaly_score")
    lines.append("  + 0.20 * rule_based_score")
    lines.append("```")
    lines.append("")

    lines.append("## 3. Recommended action distribution")
    lines.append("")
    lines.append("| Recommended action | Count |")
    lines.append("|---|---:|")
    for action, count in action_counts.items():
        lines.append(f"| {action} | {count:,} |")
    lines.append("")

    lines.append("## 4. Risk level distribution")
    lines.append("")
    lines.append("| Risk level | Count |")
    lines.append("|---|---:|")
    for risk_level, count in risk_counts.items():
        lines.append(f"| {risk_level} | {count:,} |")
    lines.append("")

    lines.append("## 5. Top 10 highest-risk transactions")
    lines.append("")
    lines.append(
        "| transaction_id | customer_id | amount | fraud_probability | anomaly_score | final_risk_score | action |"
    )
    lines.append("|---|---|---:|---:|---:|---:|---|")

    for row in scored.head(10).itertuples(index=False):
        lines.append(
            f"| {row.transaction_id} | {row.customer_id} | "
            f"{row.amount:.2f} | {row.fraud_probability:.4f} | "
            f"{row.anomaly_score:.4f} | {row.final_risk_score:.4f} | "
            f"{row.recommended_action} |"
        )

    lines.append("")
    lines.append("## 6. Interpretation")
    lines.append("")
    lines.append(
        "The final score is designed for decision support. High-risk cases should not "
        "be treated as automatically fraudulent; they should be prioritized for review "
        "according to the institution's governance, compliance, and risk policies."
    )
    lines.append("")

    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    """Run final risk scoring pipeline."""
    df = load_feature_data()
    anomaly = load_anomaly_scores()

    scored = create_risk_scores(df, anomaly)

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    scored.to_csv(OUTPUT_PATH, index=False)

    write_report(scored)

    print("Final risk scoring completed successfully.")
    print(f"Rows scored: {len(scored):,}")
    print(f"Average final risk score: {scored['final_risk_score'].mean():.4f}")
    print(f"High or very high risk cases: {(scored['final_risk_score'] >= 0.50).sum():,}")
    print(f"Output: {OUTPUT_PATH.resolve()}")
    print(f"Report: {REPORT_PATH.resolve()}")


if __name__ == "__main__":
    main()