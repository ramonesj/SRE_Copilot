"""
SSM Execution Engine Module

This module provides SSM (Systems Manager) execution capabilities for the SRE Copilot.
The local provider simulates SSM runbook execution without AWS dependencies.

Components:
- MockSSMProvider: Local SSM execution provider
- SSMExecution: Execution record model
"""

from .models import SSMExecution, ExecutionStatus
from .local_provider import MockSSMProvider

__all__ = ['MockSSMProvider', 'SSMExecution', 'ExecutionStatus']