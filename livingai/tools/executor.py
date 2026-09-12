"""
LivingAI Tool Executor
=====================

Executes tools with full pipeline: validation, permissions, sandboxing, and observation.
"""

import logging
import time
import json
from typing import Dict, Any, Optional, List, Callable, Union
from dataclasses import dataclass, field
from enum import Enum

from .permissions import ToolPermissionManager, ToolPermission
from .sandbox import ToolSandbox, SandboxResult, SandboxConfig
from livingai.security.policy import RiskLevel
from livingai.security.approval import ApprovalManager, ApprovalRequest


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
    approval_request: Optional[ApprovalRequest] = None
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
            'result': self._serialize_result(self.result),
            'error': self.error,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'execution_time': self.execution_time,
            'sandbox_result': self.sandbox_result.to_dict() if self.sandbox_result else None,
            'approval_request': self.approval_request.to_dict() if self.approval_request else None,
            'observations': self.observations,
            'metrics': self.metrics
        }
    
    def _serialize_result(self, result: Any) -> Any:
        if isinstance(result, dict):
            return {k: self._serialize_result(v) for k, v in result.items()}
        elif isinstance(result, list):
            return [self._serialize_result(item) for item in result]
        elif hasattr(result, 'to_dict'):
            return result.to_dict()
        elif isinstance(result, (str, int, float, bool, type(None))):
            return result
        else:
            return str(result)


@dataclass
class ExecutionHook:
    name: str
    callback: Callable
    priority: int = 0


class ToolExecutor:
    def __init__(
        self,
        sandbox: ToolSandbox = None,
        permission_manager: ToolPermissionManager = None,
        approval_manager: ApprovalManager = None,
        config: Dict[str, Any] = None
    ):
        self.sandbox = sandbox or ToolSandbox()
        self.permission_manager = permission_manager or ToolPermissionManager()
        self.approval_manager = approval_manager
        self.config = config or {}
        
        self._executions: Dict[str, ToolExecution] = {}
        self._execution_counter = 0
        self._hooks: Dict[str, List[ExecutionHook]] = {
            'pre_execute': [],
            'post_execute': [],
            'on_success': [],
            'on_failure': [],
            'on_blocked': [],
            'on_observation': []
        }
        
        self.logger = logging.getLogger(__name__)
    
    def register_hook(
        self,
        event: str,
        callback: Callable,
        name: str = None,
        priority: int = 0
    ) -> None:
        hook = ExecutionHook(
            name=name or f"hook_{len(self._hooks.get(event, []))}",
            callback=callback,
            priority=priority
        )
        self._hooks.setdefault(event, []).append(hook)
        self._hooks[event].sort(key=lambda h: h.priority, reverse=True)
    
    def _trigger_hooks(self, event: str, *args, **kwargs) -> None:
        for hook in self._hooks.get(event, []):
            try:
                hook.callback(*args, **kwargs)
            except Exception as e:
                self.logger.error(f"Hook {hook.name} error: {e}")
    
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
            self._trigger_hooks('pre_execute', execution=execution, context=context)
            execution.status = ExecutionStatus.RUNNING
            
            perm_check = self._check_permissions(execution, context)
            if not perm_check.get('allowed', False):
                execution.status = ExecutionStatus.BLOCKED
                execution.error = perm_check.get('reason', 'Permission denied')
                self._trigger_hooks('on_blocked', execution=execution, reason=execution.error)
                return execution
            
            risk = self._classify_risk(execution, context)
            execution.metrics['risk'] = risk.value
            
            approval = self._check_approval(execution, risk, context)
            if approval is not None:
                execution.approval_request = approval
                execution.status = ExecutionStatus.PENDING
                return execution
            
            sandbox_result = self._execute_in_sandbox(execution)
            execution.sandbox_result = sandbox_result
            
            if sandbox_result.success:
                execution.status = ExecutionStatus.COMPLETED
                execution.result = sandbox_result.output
                execution.error = None
                self._trigger_hooks('on_success', execution=execution, result=sandbox_result)
            else:
                execution.status = ExecutionStatus.FAILED
                execution.result = sandbox_result.output
                execution.error = sandbox_result.error
                self._trigger_hooks('on_failure', execution=execution, error=sandbox_result.error)
        except Exception as e:
            execution.status = ExecutionStatus.FAILED
            execution.error = str(e)
            self._trigger_hooks('on_failure', execution=execution, exception=e)
            self.logger.exception(f"Tool execution failed: {tool_name}.{method}")
        finally:
            execution.end_time = time.time()
            execution.execution_time = execution.end_time - execution.start_time
            execution.metrics['execution_time'] = execution.execution_time
            self._trigger_hooks('post_execute', execution=execution)
        
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
    
    def _classify_risk(
        self,
        execution: ToolExecution,
        context: Dict[str, Any] = None
    ) -> RiskLevel:
        from livingai.security.policy import SecurityPolicyManager
        policy_manager = SecurityPolicyManager()
        risk = policy_manager.classify_risk(
            f"{execution.tool_name}.{execution.method}",
            execution.tool_name
        )
        all_args = {**execution.args, **execution.kwargs}
        for arg_name, arg_value in all_args.items():
            arg_risk = self._classify_arg_risk(arg_name, arg_value)
            if arg_risk.value == RiskLevel.CRITICAL.value:
                return RiskLevel.CRITICAL
            elif arg_risk.value == RiskLevel.HIGH.value and risk.value != RiskLevel.CRITICAL.value:
                risk = RiskLevel.HIGH
        return risk
    
    def _classify_arg_risk(self, arg_name: str, arg_value: Any) -> RiskLevel:
        from livingai.security.policy import RiskLevel
        if isinstance(arg_value, str):
            dangerous_patterns = [
                ('rm -rf', RiskLevel.CRITICAL),
                ('rm -r', RiskLevel.HIGH),
                ('> /', RiskLevel.CRITICAL),
                ('; ', RiskLevel.CRITICAL),
                ('&& ', RiskLevel.CRITICAL),
                ('| ', RiskLevel.HIGH),
                ('`', RiskLevel.HIGH),
                ('$(', RiskLevel.HIGH),
                ('sudo', RiskLevel.CRITICAL),
                ('su ', RiskLevel.CRITICAL),
                ('chmod', RiskLevel.HIGH),
                ('chown', RiskLevel.HIGH)
            ]
            for pattern, risk in dangerous_patterns:
                if pattern in arg_value:
                    return risk
        if arg_name.lower() in ['path', 'file', 'dir', 'directory', 'target']:
            if isinstance(arg_value, str):
                if arg_value.startswith('/'):
                    if arg_value.startswith('/etc') or arg_value.startswith('/usr'):
                        return RiskLevel.CRITICAL
                    elif arg_value.startswith('/'):
                        return RiskLevel.HIGH
        return RiskLevel.LOW
    
    def _check_approval(
        self,
        execution: ToolExecution,
        risk: RiskLevel,
        context: Dict[str, Any] = None
    ) -> Optional[ApprovalRequest]:
        if not self.approval_manager:
            return None
        if self.approval_manager.check_rule(
            f"{execution.tool_name}.{execution.method}",
            execution.tool_name,
            risk
        ):
            return None
        from livingai.security.policy import SecurityPolicyManager, PermissionProfile
        policy_manager = SecurityPolicyManager()
        profile = context.get('profile', PermissionProfile.SAFE.value) if context else PermissionProfile.SAFE.value
        perm_check = policy_manager.check_permission(
            action=f"{execution.tool_name}.{execution.method}",
            tool=execution.tool_name,
            profile=PermissionProfile(profile)
        )
        if perm_check.get('requires_confirmation', False):
            request = self.approval_manager.request_approval(
                action=f"{execution.tool_name}.{execution.method}",
                tool=execution.tool_name,
                args={**execution.args, **execution.kwargs},
                risk=risk,
                agent_id=context.get('agent_id') if context else None,
                task_id=context.get('task_id') if context else None,
                goal_id=context.get('goal_id') if context else None,
                profile=profile
            )
            return request
        return None
    
    def _execute_in_sandbox(self, execution: ToolExecution) -> SandboxResult:
        return self.sandbox.execute(
            execution.tool_name,
            execution.method,
            execution.args,
            execution.kwargs
        )
    
    def execute_command(
        self,
        command: str,
        context: Dict[str, Any] = None
    ) -> ToolExecution:
        self._execution_counter += 1
        execution_id = f"exec_{self._execution_counter}"
        execution = ToolExecution(
            id=execution_id,
            tool_name='terminal',
            method='execute',
            args={'command': command},
            start_time=time.time()
        )
        self._executions[execution_id] = execution
        try:
            perm_check = self._check_permissions(execution, context)
            if not perm_check.get('allowed', False):
                execution.status = ExecutionStatus.BLOCKED
                execution.error = perm_check.get('reason', 'Permission denied')
                return execution
            risk = self._classify_risk(execution, context)
            execution.metrics['risk'] = risk.value
            approval = self._check_approval(execution, risk, context)
            if approval is not None:
                execution.approval_request = approval
                execution.status = ExecutionStatus.PENDING
                return execution
            sandbox_result = self.sandbox.execute_command(command)
            execution.sandbox_result = sandbox_result
            if sandbox_result.success:
                execution.status = ExecutionStatus.COMPLETED
                execution.result = sandbox_result.output
            else:
                execution.status = ExecutionStatus.FAILED
                execution.error = sandbox_result.error
        except Exception as e:
            execution.status = ExecutionStatus.FAILED
            execution.error = str(e)
        finally:
            execution.end_time = time.time()
            execution.execution_time = execution.end_time - execution.start_time
        return execution
    
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
    
    def cancel_execution(self, execution_id: str) -> bool:
        execution = self._executions.get(execution_id)
        if not execution:
            return False
        if execution.status == ExecutionStatus.PENDING:
            execution.status = ExecutionStatus.CANCELLED
            execution.error = "Execution cancelled"
            return True
        return False
    
    def cleanup_executions(self, older_than: float = 3600.0) -> int:
        cutoff = time.time() - older_than
        removed = 0
        for exec_id, execution in list(self._executions.items()):
            if execution.end_time < cutoff:
                del self._executions[exec_id]
                removed += 1
        return removed
    
    def get_stats(self) -> Dict[str, Any]:
        stats = {
            'total': len(self._executions),
            'pending': 0,
            'running': 0,
            'completed': 0,
            'failed': 0,
            'blocked': 0,
            'timeout': 0,
            'cancelled': 0,
            'total_execution_time': 0.0,
            'avg_execution_time': 0.0
        }
        for execution in self._executions.values():
            stats['total'] += 1
            stats[execution.status.value] += 1
            stats['total_execution_time'] += execution.execution_time
        if stats['total'] > 0:
            stats['avg_execution_time'] = stats['total_execution_time'] / stats['total']
        return stats
    
    def add_observation(
        self,
        execution_id: str,
        observation: str,
        data: Dict[str, Any] = None
    ) -> bool:
        execution = self._executions.get(execution_id)
        if not execution:
            return False
        obs = {
            'timestamp': time.time(),
            'content': observation,
            'data': data
        }
        execution.observations.append(obs)
        self._trigger_hooks('on_observation', execution=execution, observation=obs)
        return True
