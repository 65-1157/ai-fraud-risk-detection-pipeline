"""
Monitoring module for the AI Fraud Risk Detection Pipeline.

This script creates a lightweight monitoring report for the final
risk-scored transactions.

Input:
- data/processed/risk_scored_transactions.csv

Output:
- reports/monitoring_report.md

The goal is to demonstrate basic MLOps thinking:
- score distribution monitoring;
- alert volume monitoring;
- risk level monitoring;
- possible drift indicators;
- operational review workload.
"""

from pathlib import Path

import pandas as pd


PROCESSED_DIR = Path("data/processed")
REPORTS_DIR = Path("reports")

INPUT_PATH = PROCESSED_DIR / "risk_scored_transactions.csv"
REPORT_PATH = REPORTS_DIR / "monitoring_report.md"


def load_scored_data() -> pd.DataFrame:
    """Load final risk-scored transactions."""
    if not INPUT_PATH.exists():
        raise FileNotFoundError("Run src/risk_scoring.py first.")

    df = pd.read_csv(INPUT_PATH)

    required_columns = [
        "transaction_id",
        "customer_id",
        "amount",
        "fraud_probability",
        "anomaly_score",
        "rule_based_score",
        "final_risk_score",
        "risk_level",
        "recommended_action",
        "fraud_label",
        "aml_alert_label",
    ]

    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    return df


def numeric_summary(df: pd.DataFrame, column: str) -> dict:
    """Create summary statistics for a numeric column."""
    return {
        "mean": df[column].mean(),
        "median": df[column].median(),
        "std": df[column].std(),
        "min": df[column].min(),
        "p25": df[column].quantile(0.25),
        "p75": df[column].quantile(0.75),
        "p90": df[column].quantile(0.90),
        "p95": df[column].quantile(0.95),
        "max": df[column].max(),
    }


def get_monitoring_flags(df: pd.DataFrame) -> list[str]:
    """Create simple operational monitoring flags."""
    flags = []

    high_risk_rate = (df["final_risk_score"] >= 0.50).mean()
    very_high_risk_rate = (df["final_risk_score"] >= 0.75).mean()
    manual_review_rate = df["recommended_action"].isin(
        ["manual_review", "block_or_urgent_review"]
    ).mean()
    fraud_rate = df["fraud_label"].mean()
    aml_rate = df["aml_alert_label"].mean()

    if high_risk_rate > 0.25:
        flags.append(
            f"High risk volume is elevated: {high_risk_rate:.2%} of transactions scored >= 0.50."
        )

    if very_high_risk_rate > 0.05:
        flags.append(
            f"Very high risk volume is elevated: {very_high_risk_rate:.2%} of transactions scored >= 0.75."
        )

    if manual_review_rate > 0.20:
        flags.append(
            f"Manual review workload may be high: {manual_review_rate:.2%} of transactions require review."
        )

    if fraud_rate > 0.10:
        flags.append(
            f"Fraud label rate is high in the synthetic dataset: {fraud_rate:.2%}."
        )

    if aml_rate > 0.15:
        flags.append(
            f"AML-inspired alert rate is high in the synthetic dataset: {aml_rate:.2%}."
        )

    if not flags:
        flags.append("No major monitoring flags detected under the current thresholds.")

    return flags


def write_distribution_table(lines: list[str], title: str, counts: pd.Series) -> None:
    """Append a distribution table to the markdown report."""
    lines.append(f"## {title}")
    lines.append("")
    lines.append("| Category | Count | Percentage |")
    lines.append("|---|---:|---:|")

    total = counts.sum()
    for category, count in counts.items():
        pct = count / total if total else 0
        lines.append(f"| {category} | {count:,} | {pct:.2%} |")

    lines.append("")


def write_numeric_summary_table(lines: list[str], title: str, summary: dict) -> None:
    """Append numeric summary table to markdown report."""
    lines.append(f"## {title}")
    lines.append("")
    lines.append("| Statistic | Value |")
    lines.append("|---|---:|")

    for key, value in summary.items():
        lines.append(f"| {key} | {value:.4f} |")

    lines.append("")


def write_report(df: pd.DataFrame) -> None:
    """Write the monitoring report."""
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    risk_counts = df["risk_level"].value_counts()
    action_counts = df["recommended_action"].value_counts()

    final_score_summary = numeric_summary(df, "final_risk_score")
    fraud_probability_summary = numeric_summary(df, "fraud_probability")
    anomaly_score_summary = numeric_summary(df, "anomaly_score")
    rule_score_summary = numeric_summary(df, "rule_based_score")

    flags = get_monitoring_flags(df)

    lines = []

    lines.append("# Monitoring Report")
    lines.append("")
    lines.append("## 1. Objective")
    lines.append("")
    lines.append(
        "This report provides a lightweight monitoring view of the fraud risk pipeline. "
        "It is designed to demonstrate MLOps thinking for score distribution, review workload, "
        "and operational risk monitoring."
    )
    lines.append("")

    lines.append("## 2. Dataset overview")
    lines.append("")
    lines.append(f"- Total scored transactions: **{len(df):,}**")
    lines.append(f"- Unique customers: **{df['customer_id'].nunique():,}**")
    lines.append(f"- Average transaction amount: **{df['amount'].mean():.2f}**")
    lines.append(f"- Fraud label rate: **{df['fraud_label'].mean():.2%}**")
    lines.append(f"- AML-inspired alert rate: **{df['aml_alert_label'].mean():.2%}**")
    lines.append("")

    write_distribution_table(lines, "3. Risk level distribution", risk_counts)
    write_distribution_table(lines, "4. Recommended action distribution", action_counts)

    write_numeric_summary_table(lines, "5. Final risk score summary", final_score_summary)
    write_numeric_summary_table(lines, "6. Fraud probability summary", fraud_probability_summary)
    write_numeric_summary_table(lines, "7. Anomaly score summary", anomaly_score_summary)
    write_numeric_summary_table(lines, "8. Rule-based score summary", rule_score_summary)

    lines.append("## 9. Monitoring flags")
    lines.append("")
    for flag in flags:
        lines.append(f"- {flag}")
    lines.append("")

    lines.append("## 10. Suggested production monitoring extensions")
    lines.append("")
    lines.append("In a production environment, this monitoring layer should be extended to track:")
    lines.append("")
    lines.append("- data drift between training and scoring windows;")
    lines.append("- feature distribution drift;")
    lines.append("- model performance decay when labels become available;")
    lines.append("- alert volume by day, week, channel, and customer segment;")
    lines.append("- false positive and false negative feedback from analysts;")
    lines.append("- model retraining triggers;")
    lines.append("- approval workflow and auditability.")
    lines.append("")

    lines.append("## 11. Interview relevance")
    lines.append("")
    lines.append(
        "This module demonstrates that the project does not stop at model training. "
        "It also considers the operational layer required to monitor model outputs and "
        "business impact over time."
    )
    lines.append("")

    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    """Run monitoring report generation."""
    df = load_scored_data()
    write_report(df)

    print("Monitoring report generated successfully.")
    print(f"Rows monitored: {len(df):,}")
    print(f"Report: {REPORT_PATH.resolve()}")


if __name__ == "__main__":
    main()