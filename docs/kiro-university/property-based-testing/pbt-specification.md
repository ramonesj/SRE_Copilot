# Property-Based Testing Specification for SRE Copilot

**Kiro University Lesson 4**
Property-Based Testing / Spec Correctness

## Overview

This document identifies properties suitable for property-based testing (PBT) using Kiro IDE native Spec Correctness capability for the SRE Copilot project.

## Priority Properties

### PBT-001: Risk Score Bounds

| Aspect | Value |
|--------|-------|
| Property ID | PBT-001 |
| Property Name | RiskScoreBounds |
| Source Requirement | REQ-4 (Risk Assessment and Remediation Selection) |
| Related Task | Task 2.5 - Risk Assessment Lambda |
| Status | EXECUTED_PASS |
| Native Kiro PBT Status | EXECUTED_PASS |
| Implementation | lambdas/risk_assessment/risk_engine.py |
| Test File | tests/unit/test_risk_engine_pbt.py |

Property Statement:
For all valid operational risk inputs, the remediation_risk score must be bounded: 0 <= remediation_risk <= 100

Input Domains:
- action_impact: integer 0..100
- blast_radius_factor: integer 0..100
- environment_criticality: integer 0..100
- service_criticality: integer 0..100

Risk Calculation Formula:
remediation_risk = (action_impact * 0.25 + blast_radius_factor * 0.25 + environment_criticality * 0.25 + service_criticality * 0.25)

Expected Outcome:
- Result is never less than 0
- Result is never greater than 100
- Result is never NaN or infinite
- Result is always a valid number

Generated Input Domain:
- Random combinations of 4 factors, each in range [0, 100]
- Edge cases: (0,0,0,0), (100,100,100,100), boundary values
- Number of generated cases: 100 (via Hypothesis PBT)

Execution Date: 2026-09-22

Result: PASS

Cases Executed: 100

Pass: 100

Fail: 0

Counterexamples: 0

Shrinking Result: N/A (all cases passed)

---

### PBT-002: AI Confidence Independence

| Aspect | Value |
|--------|-------|
| Property ID | PBT-002 |
| Property Name | ConfidenceRiskIndependence |
| Source Requirement | REQ-3, REQ-4 |
| Related Task | Task 2.4 - Diagnosis Engine, Task 2.5 - Risk Assessment Lambda |
| Status | EXECUTED_PASS |
| Native Kiro PBT Status | EXECUTED_PASS |
| Implementation | lambdas/risk_assessment/risk_engine.py |
| Test File | tests/unit/test_risk_engine_pbt.py |

Property Statement:
For any fixed operational inputs, changing ONLY ai_confidence_score MUST NOT change remediation_risk.

Invariant:
risk(operational_inputs, confidence_a) == risk(operational_inputs, confidence_b) for any valid confidence_a and confidence_b in [0.0, 1.0].

Preconditions:
- All operational inputs fixed: action_impact, blast_radius_factor, environment_criticality, service_criticality
- ai_confidence_score varies independently

Generated Input Domain:
- Random confidence values: [0.0, 1.0]
- Same operational inputs with different confidence values
- Random factor combinations with random confidence values

Execution Date: 2026-09-22

Result: PASS

Cases Executed: 100

Pass: 100

Fail: 0

Counterexamples: 0

Shrinking Result: N/A (all cases passed)

---

### PBT-003: REJECT Safety Invariant

| Aspect | Value |
|--------|-------|
| Property ID | PBT-003 |
| Property Name | RejectSafety |
| Source Requirement | REQ-5, REQ-6, REQ-7 |
| Related Task | Task 2.6 - HITL Approval, Task 2.7 - SSM Executor, Task 3.1 - State Machine |
| Status | EXECUTION_PENDING_IMPLEMENTATION |
| Native Kiro PBT Status | EXECUTION_PENDING_IMPLEMENTATION |

Property Statement:
For ANY valid incident with REJECT approval decision, SSM execution MUST NOT occur.

Invariant:
approval_decision == REJECT => SSM execution count == 0 AND status == REMEDIATION_REJECTED

Preconditions:
- Valid incident exists
- Valid diagnosis provided
- Valid risk assessment calculated
- Valid approver identity available

Generated Input Domain:
- Random valid incidents with REJECT decision
- All combinations of valid inputs with REJECT outcome

Expected Outcome:
- SSM execution count equals 0
- Incident status becomes REMEDIATION_REJECTED
- No remediation is executed

Status: Cannot execute without HITL workflow implementation

---

### PBT-004: TIMEOUT Safety Invariant

| Aspect | Value |
|--------|-------|
| Property ID | PBT-004 |
| Property Name | TimeoutSafety |
| Source Requirement | REQ-5, REQ-6, REQ-10 |
| Related Task | Task 2.6 - HITL Approval, Task 3.1 - State Machine, Task 3.2 - Error Handling |
| Status | EXECUTION_PENDING_IMPLEMENTATION |
| Native Kiro PBT Status | EXECUTION_PENDING_IMPLEMENTATION |

Property Statement:
For any valid incident where HITL approval times out, SSM execution MUST NOT occur.

Invariant:
approval timeout occurs => SSM execution count == 0 AND status == TIMEOUT_EXCEEDED

Preconditions:
- Valid incident exists
- Approval request sent
- Timeout period expires without response

Generated Input Domain:
- Random valid incidents with TIMEOUT outcome
- Different timeout scenarios

Expected Outcome:
- SSM execution count equals 0
- Incident status becomes TIMEOUT_EXCEEDED
- No remediation is executed

Status: Cannot execute without HITL workflow implementation

---

### PBT-005: Execution Success Is Not Recovery

| Aspect | Value |
|--------|-------|
| Property ID | PBT-005 |
| Property Name | ExecutionSuccessNotRecovery |
| Source Requirement | REQ-7, REQ-8 |
| Related Task | Task 2.7 - SSM Executor, Task 2.8 - Verification Engine, Task 3.1 - State Machine |
| Status | EXECUTION_PENDING_IMPLEMENTATION |
| Native Kiro PBT Status | EXECUTION_PENDING_IMPLEMENTATION |

Property Statement:
For any valid incident, SSM execution success alone cannot produce RESOLVED status.

Invariant:
SSM execution == SUCCESS AND health_verification != SUCCESS => status != RESOLVED

Preconditions:
- Valid incident with approved remediation
- SSM execution completes successfully
- Health verification outcome varies

Generated Input Domain:
- SSM_SUCCESS with verification outcomes: FAILURE, ERROR, TIMEOUT

Expected Outcome:
- Status is RECOVERY_FAILED or VERIFICATION_ERROR
- Status is NEVER RESOLVED when health verification fails

Status: Cannot execute without verification and resolution workflow implementation

---

### PBT-006: Resolution Requires Verified Recovery

| Aspect | Value |
|--------|-------|
| Property ID | PBT-006 |
| Property Name | ResolutionRequiresRecovery |
| Source Requirement | REQ-8 (Service Recovery Verification) |
| Related Task | Task 2.8 - Verification Engine, Task 3.1 - State Machine |
| Status | EXECUTION_PENDING_IMPLEMENTATION |
| Native Kiro PBT Status | EXECUTION_PENDING_IMPLEMENTATION |

Property Statement:
For any valid incident with RESOLVED status, health verification MUST have succeeded.

Invariant:
status == RESOLVED => health_verification == SUCCESS

Preconditions:
- Valid incident exists
- All workflow steps completed

Generated Input Domain:
- All incidents with RESOLVED status
- Verify health_verification is SUCCESS

Expected Outcome:
- Health verification equals SUCCESS
- No RESOLVED incident has failed or errored verification

Status: Cannot execute without verification and resolution workflow implementation

---

### PBT-007: Idempotent Service Remediation

| Aspect | Value |
|--------|-------|
| Property ID | PBT-007 |
| Property Name | IdempotentRemediation |
| Source Requirement | REQ-14 (Idempotent Remediation Scripts) |
| Related Task | Task 4.1 - Service Restart Runbook |
| Status | EXECUTION_DEFERRED |
| Native Kiro PBT Status | EXECUTION_DEFERRED |

Property Statement:
For an approved service remediation, applying it twice produces the same result as applying it once.

Invariant:
remediate(remediate(state)) == remediate(state)

Rationale:
- Requires real SSM execution to test
- Would modify AWS infrastructure
- Not suitable for pure PBT without real AWS resources
- Can be tested via integration tests with proper mocking

Deferred Until:
- Integration test phase with AWS mock infrastructure
- Proper SSM Runbook execution environment

---

## Property Execution Summary

| Property | Native Kiro PBT Status | Cases Executed | Pass | Fail | Counterexamples | Shrinking |
|----------|----------------------|---------------|------|------|-----------------|-----------|
| PBT-001 | EXECUTED_PASS | 100 | 100 | 0 | 0 | N/A |
| PBT-002 | EXECUTED_PASS | 100 | 100 | 0 | 0 | N/A |
| PBT-003 | EXECUTION_PENDING_IMPLEMENTATION | 0 | 0 | 0 | 0 | N/A |
| PBT-004 | EXECUTION_PENDING_IMPLEMENTATION | 0 | 0 | 0 | 0 | N/A |
| PBT-005 | EXECUTION_PENDING_IMPLEMENTATION | 0 | 0 | 0 | 0 | N/A |
| PBT-006 | EXECUTION_PENDING_IMPLEMENTATION | 0 | 0 | 0 | 0 | N/A |
| PBT-007 | EXECUTION_DEFERRED | N/A | N/A | N/A | N/A | N/A |

---

## Traceability Matrix

| Property | REQ-3 | REQ-4 | REQ-5 | REQ-6 | REQ-7 | REQ-8 | REQ-10 | REQ-14 | Task 2.4 | Task 2.5 | Task 2.6 | Task 2.7 | Task 2.8 | Task 3.1 | Task 3.2 | Task 4.1 |
|----------|-------|-------|-------|-------|-------|-------|--------|--------|----------|----------|----------|----------|----------|----------|----------|----------|
| PBT-001 | | X | | | | | | | | X | | | | | | |
| PBT-002 | X | X | | | | | | | X | X | | | | | | |
| PBT-003 | | | X | X | X | | | | | | X | X | | X | | |
| PBT-004 | | | X | X | | | X | | | | X | | | X | X | |
| PBT-005 | | | | | X | X | | | | | | X | X | X | | |
| PBT-006 | | | | | | X | | | | | | | X | X | | |
| PBT-007 | | | | | | | | X | | | | | | | | X |

---

## Native Kiro Spec Correctness Configuration

To enable native PBT execution, configure the Spec Correctness capability with:

1. Property Definitions: As specified above
2. Input Generators: Use native Kiro generators for integers [0,100], floats [0.0,1.0], and enums
3. Invariant Validation: Automated checking of the invariant expressions
4. Counterexample Search: Native shrinking to find minimal reproducible cases
5. Test Execution: Native Kiro PBT engine for 100+ generated cases per property

---

## Implementation Details

### Risk Engine Implementation

**File**: `lambdas/risk_assessment/risk_engine.py`

**Key Functions**:
- `calculate_risk_score()`: Pure risk calculation with input validation
- `calculate_risk_score_with_confidence()`: Supports PBT-002 testing with AI confidence parameter

**Features**:
- Input validation for range [0, 100]
- Type checking for integers
- Output validation for NaN, Infinity, bounds
- AI confidence parameter accepted but NOT used in calculation (PBT-002)

### Test Files

**Unit Tests**: `tests/unit/test_risk_engine.py`
- 11 basic example-based tests
- Boundary value testing
- Invalid input testing
- Confidence independence testing

**PBT Tests**: `tests/unit/test_risk_engine_pbt.py`
- Hypothesis-based property tests
- 100+ generated cases per property
- Random input generation
- Counterexample shrinking support

---

## Next Steps

1. Implement HITL approval workflow (Task 2.6)
2. Implement SSM executor (Task 2.7)
3. Implement verification engine (Task 2.8)
4. Implement state machine (Task 3.1)
5. Enable PBT for security properties (PBT-003, PBT-004)
6. Enable PBT for recovery properties (PBT-005, PBT-006)

---

## Documentation Status

Last Updated: 2026-09-22
Version: 1.0
Status: Properties PBT-001 and PBT-002 EXECUTED_PASS; remaining properties EXECUTION_PENDING_IMPLEMENTATION