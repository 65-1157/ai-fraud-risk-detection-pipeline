"""
Supervised fraud classification module.

This script trains a baseline supervised model to predict fraud_label
using the feature table created by src/features_pyspark.py.

Input:
- data/processed/features_model_ready.parquet

Output:
- reports/model_results.md
"""

from pathlib import Path

import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    classification_report,
)
from sklearn.model_selection import train_test_split


PROCESSED_DIR = Path("data/processed")
REPORTS_DIR = Path("reports")

FEATURE_PATH = PROCESSED_DIR / "features_model_ready.parquet"
REPORT_PATH = REPORTS_DIR / "model_results.md"

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


def load_data() -> pd.DataFrame:
    """Load the model-ready feature table."""
    if not FEATURE_PATH.exists():
        raise FileNotFoundError(
            "Feature table not found. Run src/features_pyspark.py first."
        )

    df = pd.read_parquet(FEATURE_PATH)

    required_columns = FEATURE_COLUMNS + [TARGET_COLUMN]
    missing_columns = [col for col in required_columns if col not in df.columns]

    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")

    return df


def prepare_data(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    """Prepare feature matrix X and target y."""
    model_df = df[FEATURE_COLUMNS + [TARGET_COLUMN]].copy()

    model_df = model_df.replace([float("inf"), float("-inf")], pd.NA)

    for col in FEATURE_COLUMNS:
        model_df[col] = pd.to_numeric(model_df[col], errors="coerce")
        model_df[col] = model_df[col].fillna(model_df[col].median())

    model_df[TARGET_COLUMN] = model_df[TARGET_COLUMN].astype(int)

    X = model_df[FEATURE_COLUMNS]
    y = model_df[TARGET_COLUMN]

    return X, y


def train_model(X_train: pd.DataFrame, y_train: pd.Series) -> RandomForestClassifier:
    """Train a baseline Random Forest classifier."""
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


def evaluate_model(
    model: RandomForestClassifier,
    X_test: pd.DataFrame,
    y_test: pd.Series,
) -> dict:
    """Evaluate model performance."""
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]

    tn, fp, fn, tp = confusion_matrix(y_test, y_pred).ravel()

    metrics = {
        "accuracy": accuracy_score(y_test, y_pred),
        "precision": precision_score(y_test, y_pred, zero_division=0),
        "recall": recall_score(y_test, y_pred, zero_division=0),
        "f1_score": f1_score(y_test, y_pred, zero_division=0),
        "roc_auc": roc_auc_score(y_test, y_proba),
        "tn": int(tn),
        "fp": int(fp),
        "fn": int(fn),
        "tp": int(tp),
        "classification_report": classification_report(
            y_test,
            y_pred,
            zero_division=0,
        ),
    }

    return metrics


def get_feature_importance(model: RandomForestClassifier) -> pd.DataFrame:
    """Create feature importance table."""
    importance = pd.DataFrame(
        {
            "feature": FEATURE_COLUMNS,
            "importance": model.feature_importances_,
        }
    )

    return importance.sort_values("importance", ascending=False)


def write_report(
    metrics: dict,
    feature_importance: pd.DataFrame,
    n_rows: int,
    fraud_rate: float,
) -> None:
    """Write supervised model report."""
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    lines = []

    lines.append("# Supervised Fraud Model Results")
    lines.append("")
    lines.append("## 1. Objective")
    lines.append("")
    lines.append(
        "This module trains a supervised Random Forest classifier to predict "
        "the synthetic fraud label using transaction, customer, behavioral, "
        "temporal, and rule-based risk features."
    )
    lines.append("")

    lines.append("## 2. Dataset summary")
    lines.append("")
    lines.append(f"- Rows used: **{n_rows:,}**")
    lines.append(f"- Fraud rate: **{fraud_rate:.2%}**")
    lines.append("")

    lines.append("## 3. Metrics")
    lines.append("")
    lines.append("| Metric | Value |")
    lines.append("|---|---:|")
    lines.append(f"| Accuracy | {metrics['accuracy']:.4f} |")
    lines.append(f"| Precision | {metrics['precision']:.4f} |")
    lines.append(f"| Recall | {metrics['recall']:.4f} |")
    lines.append(f"| F1-score | {metrics['f1_score']:.4f} |")
    lines.append(f"| ROC-AUC | {metrics['roc_auc']:.4f} |")
    lines.append("")

    lines.append("## 4. Confusion matrix")
    lines.append("")
    lines.append("|  | Predicted 0 | Predicted 1 |")
    lines.append("|---|---:|---:|")
    lines.append(f"| Actual 0 | {metrics['tn']:,} | {metrics['fp']:,} |")
    lines.append(f"| Actual 1 | {metrics['fn']:,} | {metrics['tp']:,} |")
    lines.append("")

    lines.append("## 5. Interpretation")
    lines.append("")
    lines.append(
        "In fraud detection, accuracy alone is not enough because fraud is often "
        "a minority class. Recall is important because it measures how many fraud "
        "cases were captured. Precision is also important because false positives "
        "increase the manual review workload."
    )
    lines.append("")

    lines.append("## 6. Top feature importances")
    lines.append("")
    lines.append("| Rank | Feature | Importance |")
    lines.append("|---:|---|---:|")

    for rank, row in enumerate(feature_importance.head(15).itertuples(index=False), start=1):
        lines.append(f"| {rank} | {row.feature} | {row.importance:.4f} |")

    lines.append("")
    lines.append("## 7. Classification report")
    lines.append("")
    lines.append("```text")
    lines.append(metrics["classification_report"])
    lines.append("```")
    lines.append("")

    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    """Run supervised fraud model pipeline."""
    df = load_data()
    X, y = prepare_data(df)

    if y.nunique() < 2:
        raise ValueError("Target has only one class. Cannot train classifier.")

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.25,
        random_state=42,
        stratify=y,
    )

    model = train_model(X_train, y_train)
    metrics = evaluate_model(model, X_test, y_test)
    feature_importance = get_feature_importance(model)

    write_report(
        metrics=metrics,
        feature_importance=feature_importance,
        n_rows=len(X),
        fraud_rate=y.mean(),
    )

    print("Supervised fraud model trained successfully.")
    print(f"Rows used: {len(X):,}")
    print(f"Fraud rate: {y.mean():.2%}")
    print(f"ROC-AUC: {metrics['roc_auc']:.4f}")
    print(f"Recall: {metrics['recall']:.4f}")
    print(f"Precision: {metrics['precision']:.4f}")
    print(f"Report: {REPORT_PATH.resolve()}")


if __name__ == "__main__":
    main()