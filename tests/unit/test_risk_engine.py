"""Unit tests for the Risk Engine module.

These tests provide basic validation behavior and example test cases.
They are separate from Kiro native PBT tests.

For PBT execution, use Kiro's native Spec Correctness capability.
"""

import math
import pytest

from lambdas.risk_assessment.risk_engine import calculate_risk_score


class TestRiskScoreCalculation:
    """Test suite for risk score calculation."""

    def test_risk_score_calculates_correctly(self):
        """Test basic risk score calculation."""
        result = calculate_risk_score(100, 100, 100, 100)
        assert result == 100.0

    def test_risk_score_with_all_zeros(self):
        """Test risk score when all factors are zero."""
        result = calculate_risk_score(0, 0, 0, 0)
        assert result == 0.0

    def test_risk_score_boundary_minimum(self):
        """Test risk score at minimum boundary."""
        result = calculate_risk_score(0, 0, 0, 0)
        assert result == 0.0
        assert result >= 0

    def test_risk_score_boundary_maximum(self):
        """Test risk score at maximum boundary."""
        result = calculate_risk_score(100, 100, 100, 100)
        assert result == 100.0
        assert result <= 100

    def test_risk_score_weighted_average(self):
        """Test risk score with mixed factors."""
        # All factors at 50 should give risk = 50
        result = calculate_risk_score(50, 50, 50, 50)
        assert result == 50.0

    def test_risk_score_invalid_input_type_string(self):
        """Test that string input raises TypeError."""
        with pytest.raises(TypeError):
            calculate_risk_score("100", 0, 0, 0)

    def test_risk_score_invalid_input_type_float(self):
        """Test that float input raises TypeError."""
        with pytest.raises(TypeError):
            calculate_risk_score(100.5, 0, 0, 0)

    def test_risk_score_invalid_input_below_zero(self):
        """Test that negative input raises ValueError."""
        with pytest.raises(ValueError):
            calculate_risk_score(-1, 0, 0, 0)

    def test_risk_score_invalid_input_above_hundred(self):
        """Test that input > 100 raises ValueError."""
        with pytest.raises(ValueError):
            calculate_risk_score(101, 0, 0, 0)


class TestRiskScoreIndependence:
    """Test that risk calculation is independent from AI confidence."""

    def test_risk_score_same_operational_inputs_different_confidence(self):
        """Verify that changing AI confidence does not affect risk score."""
        from lambdas.risk_assessment.risk_engine import calculate_risk_score_with_confidence

        operational_inputs = (50, 50, 50, 50)

        risk_a = calculate_risk_score_with_confidence(
            operational_inputs[0], operational_inputs[1],
            operational_inputs[2], operational_inputs[3],
            0.5
        )

        risk_b = calculate_risk_score_with_confidence(
            operational_inputs[0], operational_inputs[1],
            operational_inputs[2], operational_inputs[3],
            0.9
        )

        assert risk_a == risk_b, (
            f"Risk score should be independent of AI confidence. "
            f"Got {risk_a} vs {risk_b}"
        )

    def test_risk_score_all_confidence_values_produce_same_risk(self):
        """Verify risk is identical across all valid confidence values."""
        from lambdas.risk_assessment.risk_engine import calculate_risk_score_with_confidence

        operational_inputs = (25, 75, 50, 100)

        base_risk = calculate_risk_score_with_confidence(
            operational_inputs[0], operational_inputs[1],
            operational_inputs[2], operational_inputs[3],
            0.0
        )

        for confidence in [0.0, 0.25, 0.5, 0.75, 0.9, 1.0]:
            risk = calculate_risk_score_with_confidence(
                operational_inputs[0], operational_inputs[1],
                operational_inputs[2], operational_inputs[3],
                confidence
            )
            assert risk == base_risk, (
                f"Risk should be independent of confidence={confidence}. "
                f"Got {risk} vs {base_risk}"
            )