"""
Verification Engine
==================

Verifies the results of agent actions and tasks.
"""

import os
import hashlib
from dataclasses import dataclass
from typing import Dict, List, Optional, Any


@dataclass
class VerificationResult:
    """Result of a verification check."""
    success: bool
    checks: List[Dict[str, Any]]
    warnings: List[str]
    errors: List[str]
    overall_status: str = "PASS"


class VerificationEngine:
    """
    Verifies agent actions and results.
    
    Responsibilities:
    - Verify file operations
    - Verify tool execution results
    - Verify task completion
    - Verify agent run success
    """
    
    def __init__(self):
        """Initialize the verification engine."""
        self.verification_log: List[Dict] = []
    
    def verify(self, obj: Any, context: Optional[Dict] = None) -> VerificationResult:
        """
        Verify an object (task, tool result, or agent run).
        
        Args:
            obj: The object to verify
            context: Optional context for verification
            
        Returns:
            VerificationResult: The verification result
        """
        checks = []
        warnings = []
        errors = []
        
        # Determine what we're verifying
        if hasattr(obj, 'run_id'):
            # Agent run
            result = self._verify_agent_run(obj)
            checks.extend(result.checks)
            warnings.extend(result.warnings)
            errors.extend(result.errors)
        elif hasattr(obj, 'task_id') or (isinstance(obj, dict) and 'id' in obj and 'tool' in obj):
            # Task
            result = self._verify_task(obj)
            checks.extend(result.checks)
            warnings.extend(result.warnings)
            errors.extend(result.errors)
        elif isinstance(obj, dict) and 'tool' in obj:
            # Tool result
            result = self._verify_tool_result(obj)
            checks.extend(result.checks)
            warnings.extend(result.warnings)
            errors.extend(result.errors)
        else:
            # Generic verification
            checks.append({'check': 'basic_validation', 'passed': True, 'message': 'Object exists'})
        
        overall_status = "PASS" if not errors else "FAIL"
        if errors and warnings:
            overall_status = "FAIL_WITH_WARNINGS"
        elif warnings and not errors:
            overall_status = "PASS_WITH_WARNINGS"
        
        result = VerificationResult(
            success=len(errors) == 0,
            checks=checks,
            warnings=warnings,
            errors=errors,
            overall_status=overall_status
        )
        
        # Log verification
        self._log_verification(obj, result)
        
        return result
    
    def _verify_agent_run(self, run: Any) -> VerificationResult:
        """Verify an agent run."""
        checks = []
        warnings = []
        errors = []
        
        # Check if run completed
        if run.state.value == 'COMPLETED':
            checks.append({'check': 'run_completed', 'passed': True, 'message': 'Run completed successfully'})
        else:
            checks.append({'check': 'run_completed', 'passed': False, 'message': f'Run state: {run.state.value}'})
            errors.append(f'Run did not complete: {run.state.value}')
        
        # Check task completion
        if run.total_tasks > 0:
            completion_rate = run.completed_tasks / run.total_tasks
            checks.append({
                'check': 'task_completion',
                'passed': completion_rate >= 0.9,
                'message': f'Completed {run.completed_tasks}/{run.total_tasks} tasks ({completion_rate:.1%})'
            })
            
            if completion_rate < 1.0:
                warnings.append(f'Not all tasks completed: {run.completed_tasks}/{run.total_tasks}')
            
            if completion_rate < 0.5:
                errors.append(f'Less than 50% tasks completed: {run.completed_tasks}/{run.total_tasks}')
        
        # Check for errors
        if run.error:
            errors.append(f'Run error: {run.error}')
        
        # Check budget limits
        if run.steps_taken >= run.budget.max_steps:
            errors.append(f'Maximum steps exceeded: {run.steps_taken}/{run.budget.max_steps}')
        
        if run.retries_used >= run.budget.max_retries:
            warnings.append(f'Maximum retries used: {run.retries_used}/{run.budget.max_retries}')
        
        if run.tool_calls >= run.budget.max_tool_calls:
            warnings.append(f'Maximum tool calls used: {run.tool_calls}/{run.budget.max_tool_calls}')
        
        return VerificationResult(
            success=len(errors) == 0,
            checks=checks,
            warnings=warnings,
            errors=errors
        )
    
    def _verify_task(self, task: Any) -> VerificationResult:
        """Verify a task."""
        checks = []
        warnings = []
        errors = []
        
        # Check task status
        status = task.get('status', 'PENDING') if isinstance(task, dict) else task.status.value
        
        if status == 'COMPLETED':
            checks.append({'check': 'task_completed', 'passed': True, 'message': 'Task completed'})
        elif status == 'FAILED':
            checks.append({'check': 'task_completed', 'passed': False, 'message': 'Task failed'})
            errors.append('Task failed')
        else:
            checks.append({'check': 'task_completed', 'passed': False, 'message': f'Task status: {status}'})
            warnings.append(f'Task not completed: {status}')
        
        # Check for result
        result = task.get('result') if isinstance(task, dict) else task.result
        if result:
            if isinstance(result, dict) and 'success' in result:
                if result['success']:
                    checks.append({'check': 'tool_success', 'passed': True, 'message': 'Tool executed successfully'})
                else:
                    checks.append({'check': 'tool_success', 'passed': False, 'message': 'Tool execution failed'})
                    errors.append(f'Tool error: {result.get("error", "Unknown error")}')
        
        return VerificationResult(
            success=len(errors) == 0,
            checks=checks,
            warnings=warnings,
            errors=errors
        )
    
    def _verify_tool_result(self, result: Dict) -> VerificationResult:
        """Verify a tool execution result."""
        checks = []
        warnings = []
        errors = []
        
        # Check success flag
        if result.get('success', False):
            checks.append({'check': 'success_flag', 'passed': True, 'message': 'Tool reported success'})
        else:
            checks.append({'check': 'success_flag', 'passed': False, 'message': 'Tool reported failure'})
            errors.append(f'Tool failed: {result.get("error", "Unknown error")}')
        
        # Check for specific tool verifications
        tool_name = result.get('tool')
        
        if tool_name and tool_name.startswith('filesystem.'):
            # Verify filesystem operations
            self._verify_filesystem(result, checks, warnings, errors)
        elif tool_name == 'terminal.execute':
            # Verify terminal execution
            if result.get('returncode') != 0:
                errors.append(f'Command failed with return code {result.get("returncode")}')
            if result.get('stderr'):
                warnings.append(f'Command stderr: {result.get("stderr")[:200]}')
        elif tool_name == 'sqlite.query':
            # Verify SQLite query
            if result.get('rows_affected') == 0 and not result.get('results'):
                warnings.append('Query returned no results and affected no rows')
        
        return VerificationResult(
            success=len(errors) == 0,
            checks=checks,
            warnings=warnings,
            errors=errors
        )
    
    def _verify_filesystem(self, result: Dict, checks: List, warnings: List, errors: List):
        """Verify filesystem operations."""
        tool = result.get('tool', '')
        
        if 'filesystem.list' in tool:
            files = result.get('files', [])
            checks.append({'check': 'list_result', 'passed': isinstance(files, list), 'message': f'Listed {len(files) if files else 0} files'})
        
        elif 'filesystem.read' in tool:
            content = result.get('content')
            checks.append({'check': 'read_result', 'passed': content is not None, 'message': f'Read {len(content) if content else 0} bytes'})
        
        elif 'filesystem.write' in tool:
            path = result.get('path')
            bytes_written = result.get('bytes_written', 0)
            checks.append({'check': 'write_result', 'passed': bytes_written > 0, 'message': f'Wrote {bytes_written} bytes to {path}'})
            
            # Verify file exists
            if path and os.path.exists(path):
                checks.append({'check': 'file_exists', 'passed': True, 'message': f'File {path} exists'})
            else:
                checks.append({'check': 'file_exists', 'passed': False, 'message': f'File {path} does not exist'})
                errors.append(f'File not created: {path}')
        
        elif 'filesystem.copy' in tool or 'filesystem.move' in tool:
            source = result.get('source')
            destination = result.get('destination')
            
            # Check destination exists
            if destination and os.path.exists(destination):
                checks.append({'check': 'destination_exists', 'passed': True, 'message': f'Destination {destination} exists'})
            else:
                checks.append({'check': 'destination_exists', 'passed': False, 'message': f'Destination {destination} does not exist'})
                errors.append(f'Operation failed: destination does not exist')
            
            # For move, check source doesn't exist
            if 'filesystem.move' in tool and source and not os.path.exists(source):
                checks.append({'check': 'source_removed', 'passed': True, 'message': f'Source {source} removed'})
            elif 'filesystem.move' in tool and source and os.path.exists(source):
                warnings.append(f'Source {source} still exists after move')
        
        elif 'filesystem.delete' in tool:
            path = result.get('path')
            if path and not os.path.exists(path):
                checks.append({'check': 'file_deleted', 'passed': True, 'message': f'File {path} deleted'})
            else:
                checks.append({'check': 'file_deleted', 'passed': False, 'message': f'File {path} still exists'})
                errors.append(f'File not deleted: {path}')
        
        elif 'filesystem.mkdir' in tool:
            path = result.get('path')
            if path and os.path.isdir(path):
                checks.append({'check': 'directory_created', 'passed': True, 'message': f'Directory {path} created'})
            else:
                checks.append({'check': 'directory_created', 'passed': False, 'message': f'Directory {path} does not exist'})
                errors.append(f'Directory not created: {path}')
    
    def _log_verification(self, obj: Any, result: VerificationResult):
        """Log verification result."""
        obj_id = getattr(obj, 'run_id', getattr(obj, 'id', 'unknown'))
        self.verification_log.append({
            'object_id': obj_id,
            'success': result.success,
            'overall_status': result.overall_status,
            'checks': len(result.checks),
            'warnings': len(result.warnings),
            'errors': len(result.errors),
            'timestamp': __import__('time').time()
        })
        # Limit log size
        if len(self.verification_log) > 1000:
            self.verification_log = self.verification_log[-500:]
    
    def verify_file_integrity(self, path: str, expected_checksum: Optional[str] = None) -> VerificationResult:
        """Verify file integrity using checksum."""
        checks = []
        warnings = []
        errors = []
        
        # Check file exists
        if not os.path.exists(path):
            errors.append(f'File does not exist: {path}')
            return VerificationResult(success=False, checks=checks, warnings=warnings, errors=errors)
        
        checks.append({'check': 'file_exists', 'passed': True, 'message': f'File {path} exists'})
        
        # Calculate checksum
        try:
            with open(path, 'rb') as f:
                content = f.read()
            checksum = hashlib.sha256(content).hexdigest()
            checks.append({'check': 'checksum_calculated', 'passed': True, 'message': f'SHA256: {checksum}'})
            
            # Verify against expected
            if expected_checksum and checksum != expected_checksum:
                errors.append(f'Checksum mismatch: expected {expected_checksum}, got {checksum}')
                checks.append({'check': 'checksum_match', 'passed': False, 'message': 'Checksum does not match'})
            elif expected_checksum:
                checks.append({'check': 'checksum_match', 'passed': True, 'message': 'Checksum matches'})
        except Exception as e:
            errors.append(f'Failed to calculate checksum: {e}')
        
        return VerificationResult(
            success=len(errors) == 0,
            checks=checks,
            warnings=warnings,
            errors=errors
        )
    
    def verify_directory_structure(self, path: str, expected_structure: Optional[Dict] = None) -> VerificationResult:
        """Verify directory structure matches expected."""
        checks = []
        warnings = []
        errors = []
        
        if not os.path.isdir(path):
            errors.append(f'Path is not a directory: {path}')
            return VerificationResult(success=False, checks=checks, warnings=warnings, errors=errors)
        
        # List actual structure
        actual_files = []
        actual_dirs = []
        for item in os.listdir(path):
            item_path = os.path.join(path, item)
            if os.path.isfile(item_path):
                actual_files.append(item)
            elif os.path.isdir(item_path):
                actual_dirs.append(item)
        
        checks.append({'check': 'directory_exists', 'passed': True, 'message': f'Directory {path} exists'})
        checks.append({'check': 'file_count', 'passed': True, 'message': f'Found {len(actual_files)} files, {len(actual_dirs)} directories'})
        
        # If expected structure provided, verify against it
        if expected_structure:
            expected_files = expected_structure.get('files', [])
            expected_dirs = expected_structure.get('directories', [])
            
            for f in expected_files:
                if f not in actual_files:
                    errors.append(f'Expected file not found: {f}')
            
            for d in expected_dirs:
                if d not in actual_dirs:
                    errors.append(f'Expected directory not found: {d}')
            
            for f in actual_files:
                if f not in expected_files:
                    warnings.append(f'Unexpected file: {f}')
            
            for d in actual_dirs:
                if d not in expected_dirs:
                    warnings.append(f'Unexpected directory: {d}')
        
        return VerificationResult(
            success=len(errors) == 0,
            checks=checks,
            warnings=warnings,
            errors=errors
        )
