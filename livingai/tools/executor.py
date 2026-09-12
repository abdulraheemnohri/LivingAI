"""
LivingAI Tool Executor
=====================

Executes tools with full pipeline: validation, permissions, sandboxing, and observation.
"""

import logging
import time
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
from enum import Enum

from .permissions import ToolPermissionManager
from .sandbox import ToolSandbox, SandboxResult, SandboxConfig


class ExecutionStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"


@dataclass
class ToolExecution:
    id: str
    tool_name: str
    method: str
    args: Dict[str, Any] = field(default_factory=dict)
    kwargs: Dict[str, Any] = field(default_factory=dict)
    status: ExecutionStatus = ExecutionStatus.PENDING
    result: Any = None
    error: Optional[str] = None
    start_time: float = 0.0
    end_time: float = 0.0
    execution_time: float = 0.0
    sandbox_result: Optional[SandboxResult] = None
    observations: List[Dict[str, Any]] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'tool_name': self.tool_name,
            'method': self.method,
            'args': self.args,
            'kwargs': self.kwargs,
            'status': self.status.value,
            'result': str(self.result) if self.result else None,
            'error': self.error,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'execution_time': self.execution_time,
            'sandbox_result': self.sandbox_result.to_dict() if self.sandbox_result else None,
            'observations': self.observations,
            'metrics': self.metrics
        }


class ToolExecutor:
    def __init__(
        self,
        sandbox: ToolSandbox = None,
        permission_manager: ToolPermissionManager = None,
        config: Dict[str, Any] = None
    ):
        self.sandbox = sandbox or ToolSandbox()
        self.permission_manager = permission_manager or ToolPermissionManager()
        self.config = config or {}
        
        self._executions: Dict[str, ToolExecution] = {}
        self._execution_counter = 0
        self.logger = logging.getLogger(__name__)
    
    def execute(
        self,
        tool_name: str,
        method: str = None,
        args: Dict[str, Any] = None,
        kwargs: Dict[str, Any] = None,
        context: Dict[str, Any] = None
    ) -> ToolExecution:
        self._execution_counter += 1
        execution_id = f"exec_{self._execution_counter}"
        
        execution = ToolExecution(
            id=execution_id,
            tool_name=tool_name,
            method=method or 'execute',
            args=args or {},
            kwargs=kwargs or {},
            start_time=time.time()
        )
        
        self._executions[execution_id] = execution
        
        try:
            execution.status = ExecutionStatus.RUNNING
            
            perm_check = self._check_permissions(execution, context)
            if not perm_check.get('allowed', False):
                execution.status = ExecutionStatus.BLOCKED
                execution.error = perm_check.get('reason', 'Permission denied')
                return execution
            
            sandbox_result = self._execute_in_sandbox(execution)
            execution.sandbox_result = sandbox_result
            
            if sandbox_result.success:
                execution.status = ExecutionStatus.COMPLETED
                execution.result = sandbox_result.output
            else:
                execution.status = ExecutionStatus.FAILED
                execution.result = sandbox_result.output
                execution.error = sandbox_result.error
        except Exception as e:
            execution.status = ExecutionStatus.FAILED
            execution.error = str(e)
            self.logger.exception(f"Tool execution failed: {tool_name}.{method}")
        finally:
            execution.end_time = time.time()
            execution.execution_time = execution.end_time - execution.start_time
        
        return execution
    
    def _check_permissions(
        self,
        execution: ToolExecution,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        profile = context.get('profile') if context else None
        return self.permission_manager.check_tool_access(
            execution.tool_name,
            execution.method,
            {**execution.args, **execution.kwargs},
            profile
        )
    
    def _execute_in_sandbox(self, execution: ToolExecution) -> SandboxResult:
        return self.sandbox.execute(
            execution.tool_name,
            execution.method,
            execution.args,
            execution.kwargs
        )
    
    def get_execution(self, execution_id: str) -> Optional[ToolExecution]:
        return self._executions.get(execution_id)
    
    def list_executions(
        self,
        status: ExecutionStatus = None,
        tool_name: str = None,
        limit: int = 100
    ) -> List[ToolExecution]:
        executions = list(self._executions.values())
        if status:
            executions = [e for e in executions if e.status == status]
        if tool_name:
            executions = [e for e in executions if e.tool_name == tool_name]
        executions.sort(key=lambda e: e.start_time, reverse=True)
        return executions[:limit]
    
    def get_stats(self) -> Dict[str, Any]:
        stats = {
            'total': len(self._executions),
            'pending': 0,
            'running': 0,
            'completed': 0,
            'failed': 0,
            'blocked': 0
        }
        for execution in self._executions.values():
            stats['total'] += 1
            stats[execution.status.value] += 1
        return stats
