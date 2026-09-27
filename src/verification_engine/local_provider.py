"""
Local Verification Provider

This provider simulates health verification for the SRE Copilot MVP.
It simulates health checks for service recovery verification.

Key Features:
1. No AWS dependencies - local simulation only
2. No secrets or credentials
3. No infrastructure modification permissions
4. Critical invariant enforcement: SSM success ≠ recovery verified

The provider simulates increasing success probability over retries
to demonstrate verification workflow with retry logic.

Security Note: This provider has NO execution permissions and cannot
bypass HITL approval or modify any infrastructure.
"""

import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from .models import (
    VerificationResult, 
    HealthCheck, 
    HealthStatus,
    VerificationMethod,
    VerificationCriteria
)


class LocalVerificationProvider:
    """
    Local health verification provider that simulates health checks.
    
    This provider demonstrates the critical safety invariant:
    Execution Success ≠ Recovery Verified
    
    SSM execution success alone does NOT mark incidents as RESOLVED.
    Only successful health verification leads to RESOLVED status.
    """
    
    def __init__(self, success_probability: float = 0.7, 
                 max_simulation_delay: float = 2.0):
        """
        Initialize local verification provider.
        
        Args:
            success_probability: Base probability of verification success (0.0-1.0)
            max_simulation_delay: Maximum simulated delay for health checks (seconds)
        """
        self.success_probability = max(0.0, min(1.0, success_probability))
        self.max_simulation_delay = max(0.1, max_simulation_delay)
        
    def verify_health(self, 
                      incident_id: str,
                      execution_id: str,
                      service_name: str,
                      node_id: str,
                      criteria: Optional[VerificationCriteria] = None) -> VerificationResult:
        """
        Perform health verification for a service after remediation.
        
        Args:
            incident_id: Incident being verified
            execution_id: SSM execution ID that was completed
            service_name: Service name (e.g., "nginx", "httpd")
            node_id: Node/instance ID
            criteria: Verification criteria (uses defaults if None)
            
        Returns:
            VerificationResult with health verification outcome
            
        Critical Safety Note:
        - This method only verifies health, never modifies infrastructure
        - Execution success alone does NOT guarantee verification success
        - Only successful verification leads to RESOLVED incident status
        """
        # Use default criteria if not provided
        if criteria is None:
            criteria = VerificationCriteria(
                required_checks=[
                    VerificationMethod.SERVICE_STATUS,
                    VerificationMethod.ENDPOINT_CHECK
                ],
                minimum_confidence=0.8,
                timeout_seconds=60,
                max_retries=3,
                retry_delay_seconds=10
            )
        
        verification_id = f"ver-{uuid.uuid4().hex[:8]}"
        
        # Simulate health checks with increasing success probability
        checks = []
        overall_healthy = True
        confidence_score = 0.0
        
        # Simulate service status check
        service_check = self._simulate_service_status_check(service_name, node_id)
        checks.append(service_check)
        if service_check.status != HealthStatus.HEALTHY:
            overall_healthy = False
        
        # Simulate endpoint check (if applicable)
        if VerificationMethod.ENDPOINT_CHECK in criteria.required_checks:
            endpoint_check = self._simulate_endpoint_check(service_name, node_id)
            checks.append(endpoint_check)
            if endpoint_check.status != HealthStatus.HEALTHY:
                overall_healthy = False
        
        # Calculate confidence score based on checks
        successful_checks = sum(1 for check in checks if check.status == HealthStatus.HEALTHY)
        total_checks = len(checks)
        
        if total_checks > 0:
            # Base confidence from checks
            confidence_score = successful_checks / total_checks
            
            # Adjust confidence with random factor for simulation
            import random
            confidence_score += (random.random() - 0.5) * 0.2
            confidence_score = max(0.0, min(1.0, confidence_score))
        
        # Determine if verification succeeded
        success = overall_healthy and confidence_score >= criteria.minimum_confidence
        
        # Determine overall status
        if overall_healthy:
            overall_status = HealthStatus.HEALTHY if success else HealthStatus.DEGRADED
        else:
            overall_status = HealthStatus.UNHEALTHY
        
        # Calculate total duration
        verification_duration = sum(check.duration_seconds for check in checks)
        
        return VerificationResult(
            verification_id=verification_id,
            incident_id=incident_id,
            execution_id=execution_id,
            overall_status=overall_status,
            success=success,
            checks=checks,
            verified_at=datetime.utcnow(),
            verification_duration_seconds=verification_duration,
            confidence_score=confidence_score,
            failure_reason=None if success else f"Service {service_name} failed health verification",
            retry_count=0
        )
    
    def verify_health_with_retry(self,
                                incident_id: str,
                                execution_id: str,
                                service_name: str,
                                node_id: str,
                                criteria: Optional[VerificationCriteria] = None,
                                max_attempts: int = 3) -> VerificationResult:
        """
        Perform health verification with retry logic.
        
        This demonstrates the verification retry pattern where failed
        verification can be retried (with increasing success probability)
        before marking incident as RECOVERY_FAILED.
        
        Args:
            incident_id: Incident being verified
            execution_id: SSM execution ID that was completed
            service_name: Service name
            node_id: Node/instance ID
            criteria: Verification criteria
            max_attempts: Maximum verification attempts
            
        Returns:
            VerificationResult from the final verification attempt
        """
        attempts = 0
        last_result = None
        
        while attempts < max_attempts:
            attempts += 1
            
            # Simulate retry delay (except first attempt)
            if attempts > 1:
                time.sleep(2.0)  # Simulate delay between retries
            
            # Perform verification with adjusted success probability
            # Increase success probability with each retry attempt
            adjusted_probability = min(1.0, self.success_probability + (attempts * 0.2))
            provider = LocalVerificationProvider(
                success_probability=adjusted_probability,
                max_simulation_delay=self.max_simulation_delay
            )
            
            last_result = provider.verify_health(
                incident_id=incident_id,
                execution_id=execution_id,
                service_name=service_name,
                node_id=node_id,
                criteria=criteria
            )
            
            # Set retry count
            last_result.retry_count = attempts - 1  # First attempt is 0 retries
            
            # If verification succeeded, return success
            if last_result.success:
                return last_result
        
        # All attempts failed
        if last_result:
            last_result.retry_count = max_attempts - 1
            last_result.failure_reason = f"Service {service_name} failed health verification after {max_attempts} attempts"
        
        return last_result or self._create_failed_verification(
            incident_id, execution_id, service_name, node_id
        )
    
    def _simulate_service_status_check(self, service_name: str, node_id: str) -> HealthCheck:
        """Simulate checking service status (systemctl status)"""
        import random
        import time
        
        check_id = f"check-{uuid.uuid4().hex[:6]}"
        start_time = time.time()
        
        # Simulate check execution time
        execution_delay = random.uniform(0.1, self.max_simulation_delay)
        time.sleep(execution_delay)
        
        # Determine check result with random success
        is_healthy = random.random() < self.success_probability
        
        duration = time.time() - start_time
        
        return HealthCheck(
            check_id=check_id,
            method=VerificationMethod.SERVICE_STATUS,
            status=HealthStatus.HEALTHY if is_healthy else HealthStatus.UNHEALTHY,
            executed_at=datetime.utcnow(),
            duration_seconds=duration,
            details={
                'service_name': service_name,
                'node_id': node_id,
                'simulated_check': True,
                'check_type': 'service_status',
                'execution_delay': execution_delay
            },
            error_message=None if is_healthy else f"Service {service_name} not responding"
        )
    
    def _simulate_endpoint_check(self, service_name: str, node_id: str) -> HealthCheck:
        """Simulate checking service endpoint/port"""
        import random
        import time
        
        check_id = f"check-{uuid.uuid4().hex[:6]}"
        start_time = time.time()
        
        # Simulate check execution time
        execution_delay = random.uniform(0.1, self.max_simulation_delay)
        time.sleep(execution_delay)
        
        # Determine check result with random success (slightly lower probability)
        is_healthy = random.random() < (self.success_probability * 0.9)
        
        duration = time.time() - start_time
        
        return HealthCheck(
            check_id=check_id,
            method=VerificationMethod.ENDPOINT_CHECK,
            status=HealthStatus.HEALTHY if is_healthy else HealthStatus.UNHEALTHY,
            executed_at=datetime.utcnow(),
            duration_seconds=duration,
            details={
                'service_name': service_name,
                'node_id': node_id,
                'simulated_check': True,
                'check_type': 'endpoint_health',
                'endpoint_simulated': f"http://{node_id}:80/health",
                'execution_delay': execution_delay
            },
            error_message=None if is_healthy else f"Endpoint for {service_name} not reachable"
        )
    
    def _create_failed_verification(self, incident_id: str, execution_id: str, 
                                   service_name: str, node_id: str) -> VerificationResult:
        """Create a failed verification result for error cases"""
        return VerificationResult(
            verification_id=f"ver-{uuid.uuid4().hex[:8]}",
            incident_id=incident_id,
            execution_id=execution_id,
            overall_status=HealthStatus.UNHEALTHY,
            success=False,
            checks=[],
            verified_at=datetime.utcnow(),
            verification_duration_seconds=0.0,
            confidence_score=0.0,
            failure_reason=f"Health verification failed for service {service_name}",
            retry_count=0
        )


def create_default_verification_provider() -> LocalVerificationProvider:
    """
    Create a default local verification provider.
    
    This is the primary entry point for verification engine.
    It creates a provider with reasonable defaults for MVP.
    """
    return LocalVerificationProvider(
        success_probability=0.7,
        max_simulation_delay=1.5
    )


def verify_service_recovery(incident_id: str,
                           execution_id: str,
                           service_name: str,
                           node_id: str,
                           use_retry: bool = True) -> VerificationResult:
    """
    Convenience function to verify service recovery.
    
    This is the main public API for the verification engine.
    It handles both single verification and retry logic.
    
    Args:
        incident_id: Incident ID
        execution_id: SSM execution ID
        service_name: Service name
        node_id: Node/instance ID
        use_retry: Whether to use retry logic for failed verification
        
    Returns:
        VerificationResult indicating whether recovery was verified
    """
    provider = create_default_verification_provider()
    
    if use_retry:
        return provider.verify_health_with_retry(
            incident_id=incident_id,
            execution_id=execution_id,
            service_name=service_name,
            node_id=node_id
        )
    else:
        return provider.verify_health(
            incident_id=incident_id,
            execution_id=execution_id,
            service_name=service_name,
            node_id=node_id
        )


# Example usage for testing
if __name__ == "__main__":
    print("Testing LocalVerificationProvider...")
    
    # Create a provider
    provider = create_default_verification_provider()
    
    # Test single verification
    result = provider.verify_health(
        incident_id="inc-123",
        execution_id="exec-456",
        service_name="nginx",
        node_id="i-0123456789abcdef"
    )
    
    print(f"Verification Result:")
    print(f"  Incident ID: {result.incident_id}")
    print(f"  Execution ID: {result.execution_id}")
    print(f"  Success: {result.success}")
    print(f"  Overall Status: {result.overall_status}")
    print(f"  Confidence: {result.confidence_score:.2f}")
    print(f"  Checks Performed: {len(result.checks)}")
    
    # Test retry verification
    print("\nTesting retry verification...")
    retry_result = verify_service_recovery(
        incident_id="inc-123",
        execution_id="exec-456",
        service_name="nginx",
        node_id="i-0123456789abcdef",
        use_retry=True
    )
    
    print(f"Retry Verification:")
    print(f"  Success: {retry_result.success}")
    print(f"  Retry Count: {retry_result.retry_count}")
    print(f"  Final Status: {retry_result.overall_status}")
    
    # Demonstrate critical safety invariant
    print("\n" + "="*60)
    print("CRITICAL SAFETY INVARIANT DEMONSTRATION:")
    print("="*60)
    print("Execution Success ≠ Recovery Verified")
    print("Even if SSM execution succeeds, health verification may fail.")
    print("Only VerificationResult.success = True leads to RESOLVED status.")
    print("="*60)