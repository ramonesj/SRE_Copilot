"""Risk Engine - Pure deterministic risk calculation module.

This module provides the core risk calculation logic for the SRE Copilot
Policy/Risk Engine. It is designed to be pure, deterministic, and testable
without any AWS dependencies.

The risk calculation is:

    remediation_risk = (
        action_impact * 0.25 +
        blast_radius_factor * 0.25 +
        environment_criticality * 0.25 +
        service_criticality * 0.25
    )

All inputs must be in the valid range [0, 100].
The output will be in the range [0, 100].

AI Confidence and Remediation Risk are INDEPENDENT concepts.
AI Confidence (ai_confidence_score) is NEVER part of the risk calculation.
"""

import math


def calculate_risk_score(
    action_impact: int,
    blast_radius_factor: int,
    environment_criticality: int,
    service_criticality: int,
) -> float:
    """Calculate remediation risk score using the weighted formula.

    This is a PURE function with NO side effects and NO AWS dependencies.

    Args:
        action_impact: Impact score of the remediation action (0-100)
        blast_radius_factor: Factor representing affected services and nodes (0-100)
        environment_criticality: Environment criticality score (0-100)
        service_criticality: Service criticality score (0-100)

    Returns:
        Remediation risk score in range [0, 100]

    Raises:
        ValueError: If any input is outside the valid range [0, 100]
        TypeError: If any input is not an integer
    """
    # Input validation - must be integers
    for name, value in [
        ("action_impact", action_impact),
        ("blast_radius_factor", blast_radius_factor),
        ("environment_criticality", environment_criticality),
        ("service_criticality", service_criticality),
    ]:
        if not isinstance(value, int):
            raise TypeError(f"{name} must be an integer, got {type(value).__name__}")
        if value < 0 or value > 100:
            raise ValueError(f"{name} must be in range [0, 100], got {value}")

    # Calculate weighted risk score
    risk_score = (
        action_impact * 0.25 +
        blast_radius_factor * 0.25 +
        environment_criticality * 0.25 +
        service_criticality * 0.25
    )

    # Verify output bounds
    if math.isnan(risk_score):
        raise ValueError("Risk calculation produced NaN")
    if math.isinf(risk_score):
        raise ValueError("Risk calculation produced Infinity")
    if risk_score < 0:
        raise ValueError(f"Risk calculation produced negative value: {risk_score}")
    if risk_score > 100:
        raise ValueError(f"Risk calculation produced value > 100: {risk_score}")

    return risk_score


def calculate_risk_score_with_confidence(
    action_impact: int,
    blast_radius_factor: int,
    environment_criticality: int,
    service_criticality: int,
    ai_confidence_score: float,
) -> float:
    """Calculate remediation risk score while accepting AI confidence as a parameter.

    This function exists to support PBT-002 (AI Confidence Independence) testing.

    IMPORTANT: AI Confidence (ai_confidence_score) is accepted as a parameter
    but is NOT USED in the risk calculation. This verifies that AI Confidence
    and Remediation Risk remain independent concepts.

    Args:
        action_impact: Impact score of the remediation action (0-100)
        blast_radius_factor: Factor representing affected services and nodes (0-100)
        environment_criticality: Environment criticality score (0-100)
        service_criticality: Service criticality score (0-100)
        ai_confidence_score: AI confidence score (0.0-1.0) - NOT USED in calculation

    Returns:
        Remediation risk score in range [0, 100]

    Raises:
        ValueError: If operational inputs are invalid OR ai_confidence_score is out of range
        TypeError: If any input has wrong type
    """
    # Validate operational inputs (same as base function)
    for name, value in [
        ("action_impact", action_impact),
        ("blast_radius_factor", blast_radius_factor),
        ("environment_criticality", environment_criticality),
        ("service_criticality", service_criticality),
    ]:
        if not isinstance(value, int):
            raise TypeError(f"{name} must be an integer, got {type(value).__name__}")
        if value < 0 or value > 100:
            raise ValueError(f"{name} must be in range [0, 100], got {value}")

    # Validate ai_confidence_score separately (for testing)
    if not isinstance(ai_confidence_score, (int, float)):
        raise TypeError(f"ai_confidence_score must be a number, got {type(ai_confidence_score).__name__}")
    if ai_confidence_score < 0.0 or ai_confidence_score > 1.0:
        raise ValueError(f"ai_confidence_score must be in range [0.0, 1.0], got {ai_confidence_score}")

    # Calculate risk score using ONLY operational factors
    risk_score = (
        action_impact * 0.25 +
        blast_radius_factor * 0.25 +
        environment_criticality * 0.25 +
        service_criticality * 0.25
    )

    # Verify output bounds
    if math.isnan(risk_score):
        raise ValueError("Risk calculation produced NaN")
    if math.isinf(risk_score):
        raise ValueError("Risk calculation produced Infinity")
    if risk_score < 0:
        raise ValueError(f"Risk calculation produced negative value: {risk_score}")
    if risk_score > 100:
        raise ValueError(f"Risk calculation produced value > 100: {risk_score}")

    return risk_score