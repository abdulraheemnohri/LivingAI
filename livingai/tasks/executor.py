"""
LivingAI Task Executor
=====================

Advanced task executor with tool integration, observation, and verification.
"""

import logging
import time
import json
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass

from .manager import Task, TaskStatus


@dataclass
class ToolCall:
    """Represents a tool call made during task execution."""
    tool_name: str
    arguments: Dict[str, Any]
    timestamp: float
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    execution_time: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'tool_name': self.tool_name,
            'arguments': self.arguments,
            'timestamp': self.timestamp,
            'result': self.result,
            'error': self.error,
            'execution_time': self.execution_time
        }


@dataclass
class Observation:
    """Represents an observation made during task execution."""
    content: str
    timestamp: float
    data: Optional[Dict[str, Any]] = None
    source: str = "executor"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'content': self.content,
            'timestamp': self.timestamp,
            'data': self.data,
            'source': self.source
        }


class TaskExecutor:
    """
    Executes tasks with full pipeline support:
    - Tool execution
    - Observation capture
    - Result verification
    - Error handling
    - Retry logic
    """
    
    def __init__(self, tool_registry: Any = None):
        """
        Initialize the TaskExecutor.
        
        Args:
            tool_registry: Tool registry for executing tools
        """
        self.tool_registry = tool_registry
        self.logger = logging.getLogger(__name__)
        self._hooks: Dict[str, List[Callable]] = {
            'pre_execute': [],
            'post_execute': [],
            'on_success': [],
            'on_failure': [],
            'on_observe': []
        }
    
    def register_hook(self, event: str, callback: Callable) -> None:
        """
        Register a hook for task execution events.
        
        Args:
            event: Event name (pre_execute, post_execute, on_success, on_failure, on_observe)
            callback: Function to call
        """
        if event in self._hooks:
            self._hooks[event].append(callback)
    
    def _trigger_hooks(self, event: str, *args, **kwargs) -> None:
        """Trigger all hooks for an event."""
        for callback in self._hooks.get(event, []):
            try:
                callback(*args, **kwargs)
            except Exception as e:
                self.logger.error(f"Hook {event} error: {e}")
    
    def execute(
        self,
        task: Task,
        context: Dict[str, Any] = None,
        tool_args: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Execute a task with full pipeline.
        
        Pipeline:
        1. Pre-execute hooks
        2. Execute tools/operations
        3. Capture observations
        4. Verify results
        5. Post-execute hooks
        6. Handle success/failure
        
        Args:
            task: Task to execute
            context: Execution context
            tool_args: Arguments for tool execution
            
        Returns:
            Execution result dictionary
        """
        context = context or {}
        tool_args = tool_args or {}
        
        start_time = time.time()
        result: Dict[str, Any] = {
            'task_id': task.id,
            'started_at': start_time,
            'status': 'pending',
            'tool_calls': [],
            'observations': [],
            'errors': [],
            'warnings': [],
            'metrics': {
                'execution_time': 0.0,
                'tool_calls_count': 0,
                'successful_tools': 0,
                'failed_tools': 0
            }
        }
        
        try:
            # Step 1: Pre-execute hooks
            self._trigger_hooks('pre_execute', task=task, context=context)
            result['status'] = 'running'
            
            # Step 2: Execute task
            execution_result = self._execute_task(task, context, tool_args, result)
            result.update(execution_result)
            
            # Step 3: Verify results
            verification = self._verify_results(task, result)
            result['verification'] = verification
            
            # Step 4: Determine final status
            if verification.get('completed', False):
                result['status'] = 'completed'
                self._trigger_hooks('on_success', task=task, result=result)
            else:
                result['status'] = 'failed'
                result['error'] = verification.get('reason', 'Verification failed')
                self._trigger_hooks('on_failure', task=task, result=result)
            
        except Exception as e:
            result['status'] = 'failed'
            result['error'] = str(e)
            result['errors'].append({'message': str(e), 'type': type(e).__name__})
            self._trigger_hooks('on_failure', task=task, result=result, exception=e)
            self.logger.exception(f"Task {task.id} execution failed")
        
        # Step 5: Post-execute hooks
        result['metrics']['execution_time'] = time.time() - start_time
        self._trigger_hooks('post_execute', task=task, result=result)
        
        result['completed_at'] = time.time()
        return result
    
    def _execute_task(
        self,
        task: Task,
        context: Dict[str, Any],
        tool_args: Dict[str, Any],
        result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute the actual task operations.
        
        Args:
            task: Task to execute
            context: Execution context
            tool_args: Tool arguments
            result: Result dictionary to update
            
        Returns:
            Updated result dictionary
        """
        # If task has specific tool requirements, execute them
        if task.tool_requirements:
            for tool_name in task.tool_requirements:
                tool_result = self._execute_tool(tool_name, context, tool_args, result)
                result['tool_calls'].append(tool_result.to_dict())
                result['metrics']['tool_calls_count'] += 1
                
                if tool_result.error:
                    result['errors'].append({
                        'tool': tool_name,
                        'error': tool_result.error
                    })
                    result['metrics']['failed_tools'] += 1
                    # Stop on first error by default
                    break
                else:
                    result['metrics']['successful_tools'] += 1
                    
                    # Add observation for successful tool execution
                    observation = Observation(
                        content=f"Tool {tool_name} executed successfully",
                        timestamp=time.time(),
                        data={'tool': tool_name, 'result': tool_result.result}
                    )
                    result['observations'].append(observation.to_dict())
                    self._trigger_hooks('on_observe', observation=observation, task=task)
        else:
            # Task without specific tools - execute default behavior
            observation = self._execute_default(task, context)
            result['observations'].append(observation.to_dict())
            self._trigger_hooks('on_observe', observation=observation, task=task)
        
        return result
    
    def _execute_tool(
        self,
        tool_name: str,
        context: Dict[str, Any],
        tool_args: Dict[str, Any],
        result: Dict[str, Any]
    ) -> ToolCall:
        """
        Execute a specific tool.
        
        Args:
            tool_name: Name of tool to execute
            context: Execution context
            tool_args: Arguments for tool
            result: Current result dictionary
            
        Returns:
            ToolCall object with execution details
        """
        start_time = time.time()
        
        # Get tool arguments for this specific tool
        args = tool_args.get(tool_name, {})
        
        try:
            if self.tool_registry:
                tool = self.tool_registry.get_tool(tool_name)
                if tool:
                    # Execute tool with validation
                    tool_result = tool.execute(**args)
                    execution_time = time.time() - start_time
                    
                    return ToolCall(
                        tool_name=tool_name,
                        arguments=args,
                        timestamp=start_time,
                        result=tool_result,
                        execution_time=execution_time
                    )
                else:
                    return ToolCall(
                        tool_name=tool_name,
                        arguments=args,
                        timestamp=start_time,
                        error=f"Tool '{tool_name}' not found in registry",
                        execution_time=time.time() - start_time
                    )
            else:
                return ToolCall(
                    tool_name=tool_name,
                    arguments=args,
                    timestamp=start_time,
                    error="Tool registry not available",
                    execution_time=time.time() - start_time
                )
                
        except Exception as e:
            return ToolCall(
                tool_name=tool_name,
                arguments=args,
                timestamp=start_time,
                error=str(e),
                execution_time=time.time() - start_time
            )
    
    def _execute_default(self, task: Task, context: Dict[str, Any]) -> Observation:
        """
        Default execution for tasks without specific tool requirements.
        
        This can be overridden to use model inference for task execution.
        
        Args:
            task: Task to execute
            context: Execution context
            
        Returns:
            Observation from execution
        """
        return Observation(
            content=f"Executed task: {task.title}",
            timestamp=time.time(),
            data={
                'task_id': task.id,
                'description': task.description,
                'status': 'executed'
            }
        )
    
    def _verify_results(self, task: Task, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verify task results against success criteria.
        
        Args:
            task: Task being verified
            result: Execution result
            
        Returns:
            Verification result with completion status and reason
        """
        verification: Dict[str, Any] = {
            'completed': True,
            'reason': 'All success criteria met',
            'checked_criteria': [],
            'failed_criteria': []
        }
        
        # Check for execution errors
        if result.get('errors'):
            verification['completed'] = False
            verification['reason'] = f"Execution errors: {len(result['errors'])} error(s)"
            verification['failed_criteria'].append('no_errors')
            return verification
        
        # Check task-specific success criteria
        if task.success_criteria:
            for criterion, expected_value in task.success_criteria.items():
                criterion_result = {
                    'criterion': criterion,
                    'expected': expected_value
                }
                
                # Try to find the actual value in results
                actual_value = self._find_value(criterion, result)
                criterion_result['actual'] = actual_value
                
                # Check if criterion is met
                if self._check_criterion(criterion, expected_value, actual_value):
                    criterion_result['status'] = 'met'
                    verification['checked_criteria'].append(criterion_result)
                else:
                    criterion_result['status'] = 'failed'
                    verification['failed_criteria'].append(criterion_result)
                    verification['completed'] = False
                
                verification['checked_criteria'].append(criterion_result)
        
        # If there are failed criteria, update reason
        if verification['failed_criteria']:
            failed_names = [c['criterion'] for c in verification['failed_criteria']]
            verification['reason'] = f"Criteria not met: {', '.join(failed_names)}"
        
        return verification
    
    def _find_value(self, key: str, data: Dict[str, Any]) -> Any:
        """
        Recursively find a value in nested dictionary.
        
        Args:
            key: Key to find
            data: Dictionary to search
            
        Returns:
            Value if found, None otherwise
        """
        # Try direct access
        if key in data:
            return data[key]
        
        # Try nested access with dot notation
        if '.' in key:
            parts = key.split('.')
            current = data
            for part in parts:
                if isinstance(current, dict) and part in current:
                    current = current[part]
                else:
                    return None
            return current
        
        # Search recursively
        for k, v in data.items():
            if isinstance(v, dict):
                found = self._find_value(key, v)
                if found is not None:
                    return found
            elif isinstance(v, list):
                for item in v:
                    if isinstance(item, dict):
                        found = self._find_value(key, item)
                        if found is not None:
                            return found
        
        return None
    
    def _check_criterion(self, criterion: str, expected: Any, actual: Any) -> bool:
        """
        Check if a criterion is met.
        
        Args:
            criterion: Criterion name
            expected: Expected value
            actual: Actual value
            
        Returns:
            True if criterion is met, False otherwise
        """
        # Handle None cases
        if expected is None and actual is None:
            return True
        if expected is None or actual is None:
            return False
        
        # Direct equality
        if expected == actual:
            return True
        
        # Type-specific checks
        if isinstance(expected, (list, tuple)) and isinstance(actual, (list, tuple)):
            return set(expected) == set(actual)
        
        if isinstance(expected, dict) and isinstance(actual, dict):
            return expected == actual
        
        # String comparison (case-insensitive for some cases)
        if isinstance(expected, str) and isinstance(actual, str):
            return expected.lower() == actual.lower()
        
        # Numeric comparison with tolerance
        if isinstance(expected, (int, float)) and isinstance(actual, (int, float)):
            return abs(expected - actual) < 0.0001
        
        return False
    
    def add_observation(self, task: Task, content: str, data: Dict[str, Any] = None) -> Observation:
        """
        Add an observation to a task.
        
        Args:
            task: Task to add observation to
            content: Observation content
            data: Optional data
            
        Returns:
            Created Observation
        """
        observation = Observation(
            content=content,
            timestamp=time.time(),
            data=data
        )
        
        task.observations.append(observation.to_dict())
        self._trigger_hooks('on_observe', observation=observation, task=task)
        
        return observation
