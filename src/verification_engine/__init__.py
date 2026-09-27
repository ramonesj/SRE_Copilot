"""
Health Verification Engine Module

This module provides health verification capabilities for the SRE Copilot.
The local provider simulates health checks after SSM execution to verify service recovery.

Components:
- LocalVerificationProvider: Local health verification provider
- verify_service_recovery: Convenience function for service recovery verification
- VerificationResult: Health verification result model
- HealthStatus: Health status enum
"""

from .models import VerificationResult, HealthStatus
from .local_provider import LocalVerificationProvider, verify_service_recovery

__all__ = ['LocalVerificationProvider', 'verify_service_recovery', 'VerificationResult', 'HealthStatus']