"""
Unsupervised anomaly detection module.

This script trains an Isolation Forest model to detect unusual transactions
using the model-ready feature table created by src/features_pyspark.py.

Input:
- data/processed/features_model_ready.parquet

Output:
- data/processed/anomaly_scored_transactions.csv
- reports/anomaly_results.md
"""

from pathlib import Path

import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.metrics import precision_score, recall_score, f1_score, confusion_matrix
from sklearn.preprocessing import StandardScaler


PROCESSED_DIR = Path("data/processed")
REPORTS_DIR = Path("reports")

FEATURE_PATH = PROCESSED_DIR / "features_model_ready.parquet"
OUTPUT_PATH = PROCESSED_DIR / "anomaly_scored_transactions.csv"
REPORT_PATH = REPORTS_DIR / "anomaly_results.md"

REFERENCE_LABEL = "fraud_label"

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
    "customer_avg_amount",
    "customer_std_amount",
    "customer_max_amount",
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


def load_data() -> pd.DataFrame:
    """Load model-ready features."""
    if not FEATURE_PATH.exists():
        raise FileNotFoundError(
            "Feature table not found. Run src/features_pyspark.py first."
        )

    df = pd.read_parquet(FEATURE_PATH)

    required_columns = FEATURE_COLUMNS + [
        "transaction_id",
        "customer_id",
        REFERENCE_LABEL,
    ]

    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")

    return df


def prepare_features(df: pd.DataFrame) -> pd.DataFrame:
    """Prepare numeric feature matrix for anomaly detection."""
    X = df[FEATURE_COLUMNS].copy()
    X = X.replace([float("inf"), float("-inf")], pd.NA)

    for col in FEATURE_COLUMNS:
        X[col] = pd.to_numeric(X[col], errors="coerce")
        X[col] = X[col].fillna(X[col].median())

    return X


def train_anomaly_model(X: pd.DataFrame) -> tuple[IsolationForest, pd.Series, pd.Series]:
    """Train Isolation Forest and return labels and anomaly scores."""
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    model = IsolationForest(
        n_estimators=200,
        contamination=0.08,
        random_state=42,
        n_jobs=-1,
    )

    raw_prediction = model.fit_predict(X_scaled)

    # Isolation Forest returns -1 for anomaly and 1 for normal.
    anomaly_flag = pd.Series((raw_prediction == -1).astype(int), index=X.index)

    # Lower decision_function means more anomalous.
    raw_score = model.decision_function(X_scaled)
    anomaly_score = pd.Series(-raw_score, index=X.index)

    # Normalize score to 0-1 for easier interpretation.
    anomaly_score = (anomaly_score - anomaly_score.min()) / (
        anomaly_score.max() - anomaly_score.min()
    )

    return model, anomaly_flag, anomaly_score


def evaluate_against_reference(
    df: pd.DataFrame,
    anomaly_flag: pd.Series,
) -> dict:
    """
    Evaluate anomaly flags against the synthetic fraud label.

    This is not a true supervised evaluation of the anomaly model.
    It is only a reference comparison to understand how much overlap exists
    between unsupervised anomalies and synthetic fraud labels.
    """
    y_true = df[REFERENCE_LABEL].astype(int)
    y_pred = anomaly_flag.astype(int)

    tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()

    metrics = {
        "precision": precision_score(y_true, y_pred, zero_division=0),
        "recall": recall_score(y_true, y_pred, zero_division=0),
        "f1_score": f1_score(y_true, y_pred, zero_division=0),
        "tn": int(tn),
        "fp": int(fp),
        "fn": int(fn),
        "tp": int(tp),
        "anomaly_rate": float(y_pred.mean()),
        "fraud_rate": float(y_true.mean()),
    }

    return metrics


def save_scored_transactions(
    df: pd.DataFrame,
    anomaly_flag: pd.Series,
    anomaly_score: pd.Series,
) -> None:
    """Save anomaly-scored transactions."""
    output = df[
        [
            "transaction_id",
            "customer_id",
            "transaction_date",
            "amount",
            "merchant_category" if "merchant_category" in df.columns else "transaction_id",
            "fraud_label",
            "aml_alert_label",
            "rule_based_score",
        ]
    ].copy()

    if "merchant_category" not in output.columns:
        output = df[
            [
                "transaction_id",
                "customer_id",
                "transaction_date",
                "amount",
                "fraud_label",
                "aml_alert_label",
                "rule_based_score",
            ]
        ].copy()

    output["anomaly_flag"] = anomaly_flag.values
    output["anomaly_score"] = anomaly_score.values

    output = output.sort_values("anomaly_score", ascending=False)

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    output.to_csv(OUTPUT_PATH, index=False)


def write_report(metrics: dict, top_anomalies: pd.DataFrame) -> None:
    """Write anomaly detection report."""
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    lines = []

    lines.append("# Unsupervised Anomaly Detection Results")
    lines.append("")
    lines.append("## 1. Objective")
    lines.append("")
    lines.append(
        "This module uses Isolation Forest to identify unusual transactions "
        "without using the fraud label during training."
    )
    lines.append("")
    lines.append(
        "The fraud label is used only afterward as a reference comparison, "
        "not as a training target."
    )
    lines.append("")

    lines.append("## 2. Model")
    lines.append("")
    lines.append("- Algorithm: Isolation Forest")
    lines.append("- Contamination: 8%")
    lines.append("- Input: engineered transaction and customer behavior features")
    lines.append("")

    lines.append("## 3. Reference comparison metrics")
    lines.append("")
    lines.append("| Metric | Value |")
    lines.append("|---|---:|")
    lines.append(f"| Fraud rate | {metrics['fraud_rate']:.2%} |")
    lines.append(f"| Anomaly rate | {metrics['anomaly_rate']:.2%} |")
    lines.append(f"| Precision vs fraud label | {metrics['precision']:.4f} |")
    lines.append(f"| Recall vs fraud label | {metrics['recall']:.4f} |")
    lines.append(f"| F1-score vs fraud label | {metrics['f1_score']:.4f} |")
    lines.append("")

    lines.append("## 4. Confusion matrix against fraud reference")
    lines.append("")
    lines.append("|  | Predicted normal | Predicted anomaly |")
    lines.append("|---|---:|---:|")
    lines.append(f"| Actual non-fraud | {metrics['tn']:,} | {metrics['fp']:,} |")
    lines.append(f"| Actual fraud | {metrics['fn']:,} | {metrics['tp']:,} |")
    lines.append("")

    lines.append("## 5. Interpretation")
    lines.append("")
    lines.append(
        "Anomaly detection is useful when fraud labels are incomplete, delayed, "
        "or unavailable. It helps identify unusual patterns that may deserve "
        "manual review, even if they do not perfectly overlap with known fraud labels."
    )
    lines.append("")

    lines.append("## 6. Top anomaly examples")
    lines.append("")
    lines.append("| transaction_id | customer_id | amount | anomaly_score | fraud_label |")
    lines.append("|---|---|---:|---:|---:|")

    for row in top_anomalies.head(10).itertuples(index=False):
        lines.append(
            f"| {row.transaction_id} | {row.customer_id} | "
            f"{row.amount:.2f} | {row.anomaly_score:.4f} | {row.fraud_label} |"
        )

    lines.append("")

    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    """Run anomaly detection pipeline."""
    df = load_data()
    X = prepare_features(df)

    _, anomaly_flag, anomaly_score = train_anomaly_model(X)

    metrics = evaluate_against_reference(df, anomaly_flag)

    result_df = df.copy()
    result_df["anomaly_flag"] = anomaly_flag.values
    result_df["anomaly_score"] = anomaly_score.values

    save_scored_transactions(df, anomaly_flag, anomaly_score)

    top_anomalies = result_df.sort_values("anomaly_score", ascending=False)
    write_report(metrics, top_anomalies)

    print("Anomaly detection model trained successfully.")
    print(f"Rows used: {len(df):,}")
    print(f"Fraud rate: {metrics['fraud_rate']:.2%}")
    print(f"Anomaly rate: {metrics['anomaly_rate']:.2%}")
    print(f"Precision vs fraud label: {metrics['precision']:.4f}")
    print(f"Recall vs fraud label: {metrics['recall']:.4f}")
    print(f"Output: {OUTPUT_PATH.resolve()}")
    print(f"Report: {REPORT_PATH.resolve()}")


if __name__ == "__main__":
    main()