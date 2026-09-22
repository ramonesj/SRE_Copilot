"""Property-Based Tests for the Risk Engine module.

These tests use Hypothesis to generate random test cases for PBT-001 and PBT-002.

For Kiro native Spec Correctness, these tests demonstrate the property definitions.
"""

import pytest
from hypothesis import given, strategies as st

from lambdas.risk_assessment.risk_engine import (
    calculate_risk_score,
    calculate_risk_score_with_confidence,
)


# Strategy for valid risk factor inputs
valid_risk_factors = st.integers(min_value=0, max_value=100)


@given(
    action_impact=valid_risk_factors,
    blast_radius_factor=valid_risk_factors,
    environment_criticality=valid_risk_factors,
    service_criticality=valid_risk_factors,
)
def test_pbt_001_risk_score_bounds(
    action_impact,
    blast_radius_factor,
    environment_criticality,
    service_criticality,
):
    """PBT-001: Risk Score Bounds

    For all valid operational risk inputs, the remediation_risk score must be bounded:
    0 <= remediation_risk <= 100
    """
    result = calculate_risk_score(
        action_impact, blast_radius_factor,
        environment_criticality, service_criticality
    )

    assert 0 <= result <= 100, (
        f"Risk score {result} is out of bounds [0, 100] for inputs: "
        f"action_impact={action_impact}, blast_radius_factor={blast_radius_factor}, "
        f"environment_criticality={environment_criticality}, "
        f"service_criticality={service_criticality}"
    )

    # Additional assertions to verify calculation correctness
    expected = (
        action_impact * 0.25 +
        blast_radius_factor * 0.25 +
        environment_criticality * 0.25 +
        service_criticality * 0.25
    )
    assert result == expected, (
        f"Risk calculation incorrect. Expected {expected}, got {result}"
    )


@given(
    action_impact=valid_risk_factors,
    blast_radius_factor=valid_risk_factors,
    environment_criticality=valid_risk_factors,
    service_criticality=valid_risk_factors,
    confidence_a=st.floats(min_value=0.0, max_value=1.0),
    confidence_b=st.floats(min_value=0.0, max_value=1.0),
)
def test_pbt_002_ai_confidence_independence(
    action_impact,
    blast_radius_factor,
    environment_criticality,
    service_criticality,
    confidence_a,
    confidence_b,
):
    """PBT-002: AI Confidence Independence

    For identical operational risk inputs, changing ONLY ai_confidence_score
    MUST NOT change remediation_risk.

    AI Confidence and Remediation Risk are INDEPENDENT concepts.
    """
    risk_a = calculate_risk_score_with_confidence(
        action_impact, blast_radius_factor,
        environment_criticality, service_criticality,
        confidence_a
    )

    risk_b = calculate_risk_score_with_confidence(
        action_impact, blast_radius_factor,
        environment_criticality, service_criticality,
        confidence_b
    )

    assert risk_a == risk_b, (
        f"AI confidence should not affect risk. "
        f"With confidence_a={confidence_a}, risk={risk_a}; "
        f"With confidence_b={confidence_b}, risk={risk_b}"
    )