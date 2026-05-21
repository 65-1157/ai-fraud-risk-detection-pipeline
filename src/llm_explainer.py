"""
GenAI-style risk explanation module.

This script creates human-readable explanations for high-risk transactions
without depending on any paid GenAI provider.

The module uses deterministic templates to simulate the business value of
LLM-generated explanations:

- explain why a transaction received a high risk score;
- summarize the main risk drivers;
- recommend a business action;
- create text suitable for reports or manual review queues.

Input:
- data/processed/risk_scored_transactions.csv

Output:
- data/processed/risk_explained_transactions.csv
- reports/genai_explanation_report.md
"""

from pathlib import Path

import pandas as pd


PROCESSED_DIR = Path("data/processed")
REPORTS_DIR = Path("reports")

INPUT_PATH = PROCESSED_DIR / "risk_scored_transactions.csv"
OUTPUT_PATH = PROCESSED_DIR / "risk_explained_transactions.csv"
REPORT_PATH = REPORTS_DIR / "genai_explanation_report.md"


def load_risk_scores() -> pd.DataFrame:
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


def classify_driver(value: float, medium: float, high: float) -> str:
    """Classify a numeric driver as low, moderate, or high."""
    if value >= high:
        return "high"
    if value >= medium:
        return "moderate"
    return "low"


def build_risk_drivers(row: pd.Series) -> list[str]:
    """Build a list of textual risk drivers for one transaction."""
    drivers = []

    fraud_level = classify_driver(row["fraud_probability"], medium=0.40, high=0.70)
    anomaly_level = classify_driver(row["anomaly_score"], medium=0.40, high=0.70)
    rule_level = classify_driver(row["rule_based_score"], medium=0.30, high=0.60)

    if fraud_level == "high":
        drivers.append(
            f"high supervised fraud probability ({row['fraud_probability']:.2f})"
        )
    elif fraud_level == "moderate":
        drivers.append(
            f"moderate supervised fraud probability ({row['fraud_probability']:.2f})"
        )

    if anomaly_level == "high":
        drivers.append(
            f"high anomaly score ({row['anomaly_score']:.2f})"
        )
    elif anomaly_level == "moderate":
        drivers.append(
            f"moderate anomaly score ({row['anomaly_score']:.2f})"
        )

    if rule_level == "high":
        drivers.append(
            f"strong rule-based risk indicators ({row['rule_based_score']:.2f})"
        )
    elif rule_level == "moderate":
        drivers.append(
            f"some rule-based risk indicators ({row['rule_based_score']:.2f})"
        )

    if not drivers:
        drivers.append("no strong isolated risk driver, but cumulative score was evaluated")

    return drivers


def create_explanation(row: pd.Series) -> str:
    """Create deterministic GenAI-style explanation for a transaction."""
    drivers = build_risk_drivers(row)
    drivers_text = "; ".join(drivers)

    if row["recommended_action"] == "block_or_urgent_review":
        action_text = (
            "The transaction should be prioritized for urgent review before approval."
        )
    elif row["recommended_action"] == "manual_review":
        action_text = (
            "The transaction should be sent to manual review before a final decision."
        )
    elif row["recommended_action"] == "monitor":
        action_text = (
            "The transaction may be approved, but the customer should remain under monitoring."
        )
    else:
        action_text = (
            "The transaction is compatible with approval under the current scoring policy."
        )

    explanation = (
        f"Transaction {row['transaction_id']} for customer {row['customer_id']} "
        f"received a {row['risk_level']} risk level with final score "
        f"{row['final_risk_score']:.2f}. The main drivers were: {drivers_text}. "
        f"{action_text}"
    )

    return explanation


def create_short_reason(row: pd.Series) -> str:
    """Create a short reason label for easier dashboard/report use."""
    if row["fraud_probability"] >= 0.70 and row["anomaly_score"] >= 0.70:
        return "high_model_and_anomaly_risk"
    if row["fraud_probability"] >= 0.70:
        return "high_supervised_model_risk"
    if row["anomaly_score"] >= 0.70:
        return "high_anomaly_risk"
    if row["rule_based_score"] >= 0.60:
        return "high_rule_based_risk"
    if row["final_risk_score"] >= 0.50:
        return "combined_medium_risk"
    return "low_or_monitored_risk"


def create_explanations(df: pd.DataFrame) -> pd.DataFrame:
    """Create explanations and short reason labels."""
    explained = df.copy()

    explained["short_reason"] = explained.apply(create_short_reason, axis=1)
    explained["risk_explanation"] = explained.apply(create_explanation, axis=1)

    return explained


def write_report(explained: pd.DataFrame) -> None:
    """Write explanation report."""
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    high_priority = explained[
        explained["recommended_action"].isin(
            ["block_or_urgent_review", "manual_review"]
        )
    ]

    reason_counts = explained["short_reason"].value_counts()

    lines = []

    lines.append("# GenAI-Style Risk Explanation Report")
    lines.append("")
    lines.append("## 1. Objective")
    lines.append("")
    lines.append(
        "This module converts model outputs into business-readable explanations "
        "without using a paid GenAI provider."
    )
    lines.append("")
    lines.append(
        "The current implementation uses deterministic templates. It is LLM-ready, "
        "but it does not require OpenAI, Azure OpenAI, Gemini, Bedrock, or any external API."
    )
    lines.append("")

    lines.append("## 2. Why this matters")
    lines.append("")
    lines.append(
        "Fraud and risk models should not only generate scores. They should also "
        "help analysts understand why a transaction was prioritized for review."
    )
    lines.append("")

    lines.append("## 3. Explanation strategy")
    lines.append("")
    lines.append("The explanation engine considers:")
    lines.append("")
    lines.append("- supervised fraud probability;")
    lines.append("- unsupervised anomaly score;")
    lines.append("- rule-based risk score;")
    lines.append("- final risk level;")
    lines.append("- recommended action.")
    lines.append("")

    lines.append("## 4. Short reason distribution")
    lines.append("")
    lines.append("| Short reason | Count |")
    lines.append("|---|---:|")
    for reason, count in reason_counts.items():
        lines.append(f"| {reason} | {count:,} |")
    lines.append("")

    lines.append("## 5. High-priority explanation examples")
    lines.append("")
    lines.append("| transaction_id | risk_level | action | explanation |")
    lines.append("|---|---|---|---|")

    for row in high_priority.head(10).itertuples(index=False):
        explanation = row.risk_explanation.replace("|", "-")
        lines.append(
            f"| {row.transaction_id} | {row.risk_level} | "
            f"{row.recommended_action} | {explanation} |"
        )

    lines.append("")
    lines.append("## 6. Optional LLM extension")
    lines.append("")
    lines.append(
        "In an enterprise environment, the deterministic template could be replaced "
        "or complemented by a private LLM, local LLM, or approved cloud provider. "
        "The default project version intentionally avoids paid dependencies."
    )
    lines.append("")

    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    """Run GenAI-style explanation pipeline."""
    df = load_risk_scores()

    explained = create_explanations(df)

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    explained.to_csv(OUTPUT_PATH, index=False)

    write_report(explained)

    high_priority_count = explained[
        explained["recommended_action"].isin(
            ["block_or_urgent_review", "manual_review"]
        )
    ].shape[0]

    print("GenAI-style explanation module completed successfully.")
    print("No paid GenAI provider was used.")
    print(f"Rows explained: {len(explained):,}")
    print(f"High-priority explanations: {high_priority_count:,}")
    print(f"Output: {OUTPUT_PATH.resolve()}")
    print(f"Report: {REPORT_PATH.resolve()}")


if __name__ == "__main__":
    main()