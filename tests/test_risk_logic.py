"""
Unit tests for risk scoring business logic.

These tests validate the score-to-action and score-to-risk-level rules
used by src/risk_scoring.py.
"""

from src.risk_scoring import assign_action, assign_risk_level


def test_assign_risk_level_low():
    assert assign_risk_level(0.10) == "low"
    assert assign_risk_level(0.2999) == "low"


def test_assign_risk_level_medium():
    assert assign_risk_level(0.30) == "medium"
    assert assign_risk_level(0.4999) == "medium"


def test_assign_risk_level_high():
    assert assign_risk_level(0.50) == "high"
    assert assign_risk_level(0.7499) == "high"


def test_assign_risk_level_very_high():
    assert assign_risk_level(0.75) == "very_high"
    assert assign_risk_level(0.95) == "very_high"


def test_assign_action_approve():
    assert assign_action(0.10) == "approve"
    assert assign_action(0.2999) == "approve"


def test_assign_action_monitor():
    assert assign_action(0.30) == "monitor"
    assert assign_action(0.4999) == "monitor"


def test_assign_action_manual_review():
    assert assign_action(0.50) == "manual_review"
    assert assign_action(0.7499) == "manual_review"


def test_assign_action_urgent_review():
    assert assign_action(0.75) == "block_or_urgent_review"
    assert assign_action(0.95) == "block_or_urgent_review"