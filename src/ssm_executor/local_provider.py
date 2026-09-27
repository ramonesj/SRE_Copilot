"""
Mock SSM Execution Provider for Local MVP

This provider simulates SSM Runbook execution without AWS dependencies.
It demonstrates the execution engine concept while maintaining security boundaries.

Key concepts:
- Simulates SSM execution success/failure
- Maintains execution state
- Includes retry logic
- Tracks execution history
- No AWS API calls or credentials
"""

import json
import os
import random
import time
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, Tuple, List
from uuid import uuid4

from shared.models import Incident
from .models import SSMExecution, ExecutionStatus, ExecutionParameters


class MockSSMProvider:
    """
    Mock SSM provider that simulates execution without AWS dependencies.
    
    This provider:
    1. Simulates SSM Runbook execution (success/failure)
    2. Maintains execution state and history
    3. Implements retry logic
    4. Provides execution status tracking
    5. NEVER makes real AWS API calls
    """
    
    def __init__(self, data_dir: str = "data/ssm_executions"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        
        # Simulated runbook outcomes for testing
        self._runbook_outcomes = {
            'SRE-Copilot-ServiceRestart': {
                'success_rate': 0.9,
                'typical_duration': 30,  # seconds
                'error_patterns': ['ServiceNotFound', 'PermissionDenied', 'Timeout']
            },
            'SRE-Copilot-RedisMemoryOptimization': {
                'success_rate': 0.8,
                'typical_duration': 60,
                'error_patterns': ['MemoryThresholdExceeded', 'ConnectionFailed']
            },
            'SRE-Copilot-PostgreSQLRestart': {
                'success_rate': 0.7,
                'typical_duration': 120,
                'error_patterns': ['DatabaseInUse', 'ConnectionLimitExceeded']
            }
        }
    
    def execute_ssm_runbook(
        self,
        incident: Incident,
        runbook_name: str,
        parameters: Dict[str, Any]
    ) -> Tuple[bool, Optional[SSMExecution], Optional[str]]:
        """
        Execute an SSM Runbook (simulated).
        
        Args:
            incident: Incident object
            runbook_name: Name of the SSM Runbook
            parameters: Execution parameters
            
        Returns:
            tuple: (success, SSMExecution, error_message)
            
        Note: This is a simulation. No real SSM execution occurs.
        """
        try:
            # Generate execution ID
            execution_id = f"exec-{uuid4().hex[:12]}"
            
            # Create execution record
            execution = SSMExecution(
                execution_id=execution_id,
                incident_id=incident.incident_id,
                runbook_name=runbook_name,
                parameters=parameters,
                status=ExecutionStatus.PENDING
            )
            
            # Start execution
            execution.started_at = datetime.utcnow()
            execution.status = ExecutionStatus.STARTED
            
            # Save initial state
            self._save_execution(execution)
            
            # Simulate execution based on runbook type
            success, execution = self._simulate_execution(execution)
            
            # Set completion time before accessing isoformat
            execution.completed_at = datetime.utcnow()
            
            if success:
                execution.status = ExecutionStatus.SUCCESS
                execution.output = {
                    'result': 'success',
                    'message': f'Runbook {runbook_name} executed successfully',
                    'execution_summary': self._generate_success_summary(runbook_name),
                    'timestamp': execution.completed_at.isoformat()
                }
            else:
                execution.status = ExecutionStatus.FAILED
                execution.error_message = f'Runbook execution failed: {execution.error_message}'
                execution.output = {
                    'result': 'failure',
                    'error': execution.error_message,
                    'timestamp': execution.completed_at.isoformat()
                }
            
            # Save final state
            self._save_execution(execution)
            
            return success, execution, None
            
        except Exception as e:
            return False, None, f"Error executing runbook: {str(e)}"
    
    def _simulate_execution(self, execution: SSMExecution) -> Tuple[bool, SSMExecution]:
        """
        Simulate SSM execution with random outcomes.
        
        This simulates:
        - Execution duration
        - Success/failure probability
        - Error generation
        - Retry logic
        """
        runbook_name = execution.runbook_name
        
        # Get runbook configuration
        runbook_config = self._runbook_outcomes.get(
            runbook_name,
            {'success_rate': 0.85, 'typical_duration': 45, 'error_patterns': ['GenericError']}
        )
        
        # Determine if execution succeeds based on success rate
        success = random.random() < runbook_config['success_rate']
        
        # Simulate execution duration
        execution_duration = self._calculate_execution_duration(runbook_config['typical_duration'])
        time.sleep(0.1)  # Simulate a small delay for realism
        
        if success:
            return True, execution
        else:
            # Generate realistic error
            error_pattern = random.choice(runbook_config['error_patterns'])
            execution.error_message = f"{error_pattern}: Failed to execute {runbook_name}"
            
            # Check if we should retry
            if execution.retry_count < execution.max_retries:
                execution.retry_count += 1
                
                # Simulate retry delay
                retry_delay = min(2 ** execution.retry_count, 30)  # Exponential backoff, max 30s
                execution.output = {
                    'retry_attempt': execution.retry_count,
                    'retry_delay_seconds': retry_delay,
                    'max_retries': execution.max_retries
                }
                
                return False, execution
            else:
                return False, execution
    
    def _calculate_execution_duration(self, typical_duration: int) -> int:
        """Calculate execution duration with some variability"""
        variation = random.uniform(0.8, 1.2)  # +/- 20%
        return int(typical_duration * variation)
    
    def _generate_success_summary(self, runbook_name: str) -> Dict[str, Any]:
        """Generate realistic success summary based on runbook type"""
        if 'ServiceRestart' in runbook_name:
            return {
                'service_state': 'active',
                'restart_count': 1,
                'uptime_minutes': random.randint(1, 5),
                'check_result': 'SUCCESS'
            }
        elif 'Redis' in runbook_name:
            return {
                'memory_usage_percent': random.randint(40, 60),
                'connection_count': random.randint(50, 150),
                'cache_hit_rate': random.uniform(0.85, 0.99),
                'optimization_result': 'SUCCESS'
            }
        elif 'PostgreSQL' in runbook_name:
            return {
                'connection_count': random.randint(10, 50),
                'active_sessions': random.randint(5, 20),
                'buffer_hit_ratio': random.uniform(0.9, 0.99),
                'restart_result': 'SUCCESS'
            }
        else:
            return {'result': 'success', 'details': 'Runbook executed successfully'}
    
    def get_execution_status(self, execution_id: str) -> Tuple[bool, Optional[SSMExecution], Optional[str]]:
        """
        Get execution status by ID.
        
        Args:
            execution_id: Execution identifier
            
        Returns:
            tuple: (success, SSMExecution, error_message)
        """
        try:
            execution = self._load_execution(execution_id)
            if not execution:
                return False, None, f"Execution not found: {execution_id}"
            
            return True, execution, None
            
        except Exception as e:
            return False, None, f"Error getting execution status: {str(e)}"
    
    def get_executions_by_incident(self, incident_id: str) -> Tuple[bool, List[SSMExecution], Optional[str]]:
        """
        Get all executions for an incident.
        
        Args:
            incident_id: Incident identifier
            
        Returns:
            tuple: (success, list of SSMExecution, error_message)
        """
        try:
            executions = []
            
            for filename in os.listdir(self.data_dir):
                if filename.startswith('execution_') and filename.endswith('.json'):
                    execution_id = filename[10:-5]  # Remove 'execution_' prefix and '.json' suffix
                    execution = self._load_execution(execution_id)
                    if execution and execution.incident_id == incident_id:
                        executions.append(execution)
            
            return True, executions, None
            
        except Exception as e:
            return False, [], f"Error getting executions by incident: {str(e)}"
    
    def retry_execution(self, execution_id: str) -> Tuple[bool, Optional[SSMExecution], Optional[str]]:
        """
        Retry a failed execution.
        
        Args:
            execution_id: Execution identifier
            
        Returns:
            tuple: (success, SSMExecution, error_message)
        """
        try:
            # Load existing execution
            execution = self._load_execution(execution_id)
            if not execution:
                return False, None, f"Execution not found: {execution_id}"
            
            # Check if retry is allowed
            if execution.retry_count >= execution.max_retries:
                return False, None, f"Maximum retries exceeded: {execution.max_retries}"
            
            # Update execution for retry
            execution.retry_count += 1
            execution.started_at = datetime.utcnow()
            execution.status = ExecutionStatus.STARTED
            execution.error_message = None
            
            # Save retry state
            self._save_execution(execution)
            
            # Simulate retry execution
            success, execution = self._simulate_execution(execution)
            
            if success:
                execution.status = ExecutionStatus.SUCCESS
                execution.output = {
                    'result': 'success',
                    'message': f'Runbook {execution.runbook_name} executed successfully on retry',
                    'retry_attempt': execution.retry_count
                }
            else:
                execution.status = ExecutionStatus.FAILED
                execution.error_message = f'Retry failed: {execution.error_message}'
                execution.output = {
                    'result': 'failure',
                    'error': execution.error_message,
                    'retry_attempt': execution.retry_count
                }
            
            execution.completed_at = datetime.utcnow()
            self._save_execution(execution)
            
            return success, execution, None
            
        except Exception as e:
            return False, None, f"Error retrying execution: {str(e)}"
    
    def _save_execution(self, execution: SSMExecution) -> bool:
        """Save execution record to local file"""
        try:
            execution_file = f"{self.data_dir}/execution_{execution.execution_id}.json"
            
            with open(execution_file, 'w') as f:
                json.dump(execution.to_dict(), f, indent=2)
            
            return True
        except Exception:
            return False
    
    def _load_execution(self, execution_id: str) -> Optional[SSMExecution]:
        """Load execution record from local file"""
        execution_file = f"{self.data_dir}/execution_{execution_id}.json"
        
        if not os.path.exists(execution_file):
            return None
        
        try:
            with open(execution_file, 'r') as f:
                data = json.load(f)
            
            return SSMExecution.from_dict(data)
        except Exception:
            return None
    
    def cleanup_old_executions(self, days_old: int = 7) -> Tuple[bool, int, Optional[str]]:
        """
        Clean up execution records older than specified days.
        
        Args:
            days_old: Delete records older than this many days
            
        Returns:
            tuple: (success, deleted_count, error_message)
        """
        try:
            from datetime import timedelta
            
            cutoff_date = datetime.utcnow() - timedelta(days=days_old)
            deleted_count = 0
            
            for filename in os.listdir(self.data_dir):
                if filename.startswith('execution_') and filename.endswith('.json'):
                    execution_id = filename[10:-5]
                    execution = self._load_execution(execution_id)
                    
                    if execution and execution.created_at < cutoff_date:
                        execution_file = f"{self.data_dir}/execution_{execution_id}.json"
                        os.remove(execution_file)
                        deleted_count += 1
            
            return True, deleted_count, None
            
        except Exception as e:
            return False, 0, f"Error cleaning up executions: {str(e)}"