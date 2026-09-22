# Lesson 3: Kiro Hooks for SRE Copilot

This document records the hooks implementation for the SRE Copilot project during Kiro University Challenge Lesson 3.

## Overview

Three production-relevant Kiro Hooks were created to reinforce the SRE Copilot's architectural invariant.

## Hook 1: Python Quality Gate

| Property | Value |
|----------|-------|
| **Name** | Python Quality Gate |
| **Trigger** | PostFileSave |
| **Matcher** | \.py$ |
| **Action Type** | agent |

**Real Behavior**: Performs Python quality validation on saved files

**Implementation**: Uses agent action to perform syntax and linting checks without automatic dependency installation.

**Validation Result**:
- Schema v1: Correct
- Trigger PostFileSave: Supported
- Matcher targets Python files
- No dependency installation
- Actual validation performed
- Fails safely

---

## Hook 2: SRE Copilot Security Boundary Guard

| Property | Value |
|----------|-------|
| **Name** | SRE Copilot Security Boundary Guard |
| **Trigger** | PreToolUse |
| **Matcher** | fs_write\|str_replace\|fs_append\|fs_read |
| **Action Type** | agent |

**Real Behavior**: Validates file operations against security boundaries

**Implementation**: Uses agent action to check for violations of architectural safety invariant.

**Validation Result**:
- Schema v1: Correct
- Trigger PreToolUse: Supported
- Matcher targets tool names (not file paths)
- Meaningful validation performed
- Safe read-only operations allowed

**Architectural Rules Enforced**:
- AI Diagnosis Engine MUST NOT execute SSM
- Policy/Risk Engine MUST NOT execute remediation
- HITL approval MUST be maintained
- Task Tokens MUST NOT be exposed
- Secrets MUST NOT be hardcoded

---

## Hook 3: Post Task Spec Validation

| Property | Value |
|----------|-------|
| **Name** | Post Task Spec Validation |
| **Trigger** | PostTaskExecution |
| **Action Type** | agent |

**Real Behavior**: Validates completed Spec tasks against requirements and safety invariant

**Implementation**: Uses agent action to verify compliance with acceptance criteria, requirements.md, design.md, and architectural safety invariant.

**Validation Result**:
- Schema v1: Correct
- Trigger PostTaskExecution: Supported (corrected from PostTaskExec)
- Meaningful comprehensive validation
- Architectural invariant checks
- Comprehensive coverage

**Architectural Rules Enforced**:
- AI Diagnosis has NOT gained SSM permissions
- Policy/Risk has NOT gained execution permissions
- HITL remains mandatory
- Task Tokens are NOT exposed
- No secrets introduced

---

## Files Modified

| File | Action |
|------|--------|
| .kiro/hooks/python-quality-gate.json | Fixed |
| .kiro/hooks/security-boundary-guard.json | Fixed |
| .kiro/hooks/post-task-validation.json | Fixed |

---

## Conclusion

All three Kiro University Lesson 3 Hooks have been corrected and validated. The hooks reinforce the SRE Copilot's architectural safety invariant while maintaining safe operation during development.

Status: Complete


## Demonstration Evidence

### Python Quality Gate Demonstration

| Property | Value |
|----------|-------|
| **Date** | 2026-09-22 |
| **Hook** | Python Quality Gate |
| **Trigger** | PostFileSave |
| **Demonstration File** | tests/hook_demo.py |

**Whether Hook Actually Fired**: YES

**Validation Checks Performed**:
1. Python syntax validity - CHECKED (via py_compile)
2. Linting availability - CHECKED (no linters found)
3. Tools availability - REPORTED

**Result**: PASS

**Python Version**: 3.14.4

**Tools Available**: Python interpreter with py_compile module

**Tools Missing** (not installed, not attempted):
- pylint - Not found (not installed)
- flake8 - Not found (not installed)
- pyflakes - Not found (not installed)

**Syntax Check Result**: PASS - No syntax errors found

**Limitations**:
- Optional linters (pylint, flake8) not available in environment
- Hook correctly reports availability rather than failing
- No automatic dependency installation performed
- Hook fails safely when optional tools are unavailable

**Demonstration Confirmation**:
- File created by Kiro agent (tests/hook_demo.py)
- PostFileSave hook triggered automatically
- Python Quality Gate executed with agent action
- Syntax validation performed successfully
- Validation result reported (PASS)
- No dependencies installed automatically
- No AWS resources deployed
- Temporary file removed after demonstration
