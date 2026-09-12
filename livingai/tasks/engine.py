"""
LivingAI Task Engine
==================

Orchestrates task execution with dependency management and scheduling.
"""

import logging
import time
from typing import Dict, Any, Optional, List
from queue import PriorityQueue
from threading import Lock, Thread, Event
from concurrent.futures import ThreadPoolExecutor, as_completed
import heapq

from .manager import TaskManager, Task, TaskStatus, TaskPriority


class TaskQueue:
    """
    Priority queue for managing task execution order.
    
    Uses a priority queue to ensure tasks are executed in the correct order
    based on priority and dependencies.
    """
    
    def __init__(self):
        self._queue = []
        self._index = 0
        self._lock = Lock()
    
    def push(self, task: Task, priority: int = 0):
        """
        Add a task to the queue.
        
        Args:
            task: Task to add
            priority: Priority value (lower = higher priority)
        """
        with self._lock:
            # Use task priority and creation time for ordering
            task_priority = {
                TaskPriority.CRITICAL: 0,
                TaskPriority.HIGH: 1,
                TaskPriority.NORMAL: 2,
                TaskPriority.LOW: 3,
                TaskPriority.BACKGROUND: 4
            }.get(task.priority, 2)
            
            heapq.heappush(self._queue, (task_priority, task.created_at, self._index, task))
            self._index += 1
    
    def pop(self) -> Optional[Task]:
        """
        Get the next task from the queue.
        
        Returns:
            Next Task or None if queue is empty
        """
        with self._lock:
            if self._queue:
                return heapq.heappop(self._queue)[3]
            return None
    
    def peek(self) -> Optional[Task]:
        """
        Peek at the next task without removing it.
        
        Returns:
            Next Task or None if queue is empty
        """
        with self._lock:
            if self._queue:
                return self._queue[0][3]
            return None
    
    def remove(self, task: Task) -> bool:
        """
        Remove a task from the queue.
        
        Args:
            task: Task to remove
            
        Returns:
            True if removed, False if not found
        """
        with self._lock:
            for i, (priority, created, index, t) in enumerate(self._queue):
                if t.id == task.id:
                    self._queue[i] = self._queue[-1]
                    self._queue.pop()
                    heapq.heapify(self._queue)
                    return True
            return False
    
    def is_empty(self) -> bool:
        """Check if queue is empty."""
        with self._lock:
            return len(self._queue) == 0
    
    def size(self) -> int:
        """Get queue size."""
        with self._lock:
            return len(self._queue)


class TaskExecutor:
    """
    Executes individual tasks with tool support.
    
    Handles the actual execution of a task including:
    - Tool selection
    - Tool execution
    - Result capture
    - Observation
    - Verification
    """
    
    def __init__(self, tool_registry: Any = None):
        """
        Initialize the TaskExecutor.
        
        Args:
            tool_registry: Tool registry for executing tools
        """
        self.tool_registry = tool_registry
        self.logger = logging.getLogger(__name__)
    
    def execute(self, task: Task, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Execute a task.
        
        Args:
            task: Task to execute
            context: Additional context for execution
            
        Returns:
            Dictionary with execution results
        """
        context = context or {}
        result = {
            'task_id': task.id,
            'started_at': time.time(),
            'status': 'started',
            'observations': [],
            'tool_calls': [],
            'errors': []
        }
        
        try:
            self.logger.info(f"Executing task: {task.id} - {task.title}")
            
            # Mark as running
            result['status'] = 'running'
            
            # Execute task based on its requirements
            if task.tool_requirements:
                for tool_name in task.tool_requirements:
                    tool_result = self._execute_tool(tool_name, task, context)
                    result['tool_calls'].append(tool_result)
                    
                    if tool_result.get('status') == 'error':
                        result['errors'].append(tool_result)
                        break
            else:
                # Task without specific tools - use default execution
                observation = self._execute_default(task, context)
                result['observations'].append(observation)
            
            # Verify task completion
            verification = self._verify_completion(task, result)
            result['verification'] = verification
            
            if verification.get('completed', False):
                result['status'] = 'completed'
            else:
                result['status'] = 'failed'
                result['error'] = verification.get('reason', 'Verification failed')
            
        except Exception as e:
            result['status'] = 'failed'
            result['error'] = str(e)
            self.logger.error(f"Task {task.id} failed: {e}")
        
        result['completed_at'] = time.time()
        return result
    
    def _execute_tool(self, tool_name: str, task: Task, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a specific tool.
        
        Args:
            tool_name: Name of tool to execute
            task: Current task
            context: Execution context
            
        Returns:
            Tool execution result
        """
        if not self.tool_registry:
            return {
                'tool': tool_name,
                'status': 'error',
                'error': 'Tool registry not available'
            }
        
        try:
            tool = self.tool_registry.get_tool(tool_name)
            if not tool:
                return {
                    'tool': tool_name,
                    'status': 'error',
                    'error': f'Tool {tool_name} not found'
                }
            
            # Prepare arguments
            args = context.get('tool_args', {})
            
            # Execute tool
            execution_result = tool.execute(**args)
            
            return {
                'tool': tool_name,
                'status': 'success',
                'args': args,
                'result': execution_result,
                'timestamp': time.time()
            }
            
        except Exception as e:
            return {
                'tool': tool_name,
                'status': 'error',
                'error': str(e),
                'timestamp': time.time()
            }
    
    def _execute_default(self, task: Task, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Default task execution without specific tools.
        
        Args:
            task: Task to execute
            context: Execution context
            
        Returns:
            Observation from execution
        """
        # This would be overridden by subclasses or use model inference
        return {
            'task_id': task.id,
            'description': f'Executed: {task.title}',
            'timestamp': time.time(),
            'status': 'completed'
        }
    
    def _verify_completion(self, task: Task, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verify task completion based on success criteria.
        
        Args:
            task: Task being verified
            result: Execution result
            
        Returns:
            Verification result
        """
        verification = {
            'completed': True,
            'reason': 'Success criteria met'
        }
        
        # Check if there were errors
        if result.get('errors'):
            verification['completed'] = False
            verification['reason'] = f"Errors occurred: {result['errors']}"
            return verification
        
        # Check success criteria if defined
        if task.success_criteria:
            for criterion, expected in task.success_criteria.items():
                actual = result.get(criterion)
                if actual != expected:
                    verification['completed'] = False
                    verification['reason'] = f"Criteria '{criterion}' not met: expected {expected}, got {actual}"
                    return verification
        
        return verification


class TaskEngine:
    """
    Main task engine that orchestrates task execution.
    
    Manages:
    - Task queue
    - Dependency resolution
    - Parallel execution
    - Task lifecycle
    - Error handling
    """
    
    def __init__(
        self,
        task_manager: TaskManager,
        max_workers: int = 1,
        tool_registry: Any = None
    ):
        """
        Initialize the TaskEngine.
        
        Args:
            task_manager: Task manager instance
            max_workers: Maximum number of parallel workers
            tool_registry: Tool registry for task execution
        """
        self.task_manager = task_manager
        self.max_workers = max_workers
        self.tool_registry = tool_registry
        
        self._queue = TaskQueue()
        self._executor = TaskExecutor(tool_registry)
        self._lock = Lock()
        self._stop_event = Event()
        self._running = False
        
        self.logger = logging.getLogger(__name__)
    
    def start(self):
        """Start the task engine."""
        if self._running:
            return
        
        self._running = True
        self._stop_event.clear()
        
        # Start worker threads
        for i in range(self.max_workers):
            worker = Thread(target=self._worker_loop, name=f"TaskWorker-{i}")
            worker.daemon = True
            worker.start()
        
        self.logger.info(f"Task engine started with {self.max_workers} workers")
    
    def stop(self):
        """Stop the task engine."""
        self._running = False
        self._stop_event.set()
        self.logger.info("Task engine stopped")
    
    def _worker_loop(self):
        """Worker thread main loop."""
        while not self._stop_event.is_set():
            try:
                # Get next ready task
                with self._lock:
                    ready_tasks = self.task_manager.get_ready_tasks()
                    
                    # Filter out tasks already in queue
                    for task in ready_tasks:
                        if not any(t.id == task.id for _, _, _, t in self._queue._queue):
                            # Check dependencies
                            unresolved = self.task_manager.resolve_dependencies(task)
                            if not unresolved:
                                self._queue.push(task)
                            else:
                                self.task_manager.mark_blocked(task.id, f"Waiting for: {unresolved}")
                
                # Execute next task from queue
                task = self._queue.pop()
                if task:
                    self._execute_task(task)
                else:
                    # No tasks, wait a bit
                    self._stop_event.wait(timeout=1.0)
                    
            except Exception as e:
                self.logger.error(f"Worker error: {e}")
                self._stop_event.wait(timeout=1.0)
    
    def _execute_task(self, task: Task):
        """
        Execute a single task.
        
        Args:
            task: Task to execute
        """
        # Mark as running
        self.task_manager.mark_running(task.id)
        
        try:
            # Execute task
            result = self._executor.execute(task)
            
            if result.get('status') == 'completed':
                # Task completed successfully
                self.task_manager.mark_completed(task.id, result)
                self.logger.info(f"Task {task.id} completed successfully")
                
                # Update dependent tasks
                self._update_dependent_tasks(task)
                
            elif result.get('status') == 'failed':
                # Task failed
                error = result.get('error', 'Unknown error')
                self.task_manager.mark_failed(task.id, error)
                self.logger.warning(f"Task {task.id} failed: {error}")
                
                # Check if we should retry
                if task.can_retry():
                    self.logger.info(f"Task {task.id} will be retried")
                    # Don't auto-retry immediately, let the system re-queue it
                
            else:
                # Unknown status
                self.task_manager.mark_failed(task.id, f"Unknown status: {result.get('status')}")
                
        except Exception as e:
            self.task_manager.mark_failed(task.id, str(e))
            self.logger.error(f"Task {task.id} execution error: {e}")
    
    def _update_dependent_tasks(self, completed_task: Task):
        """
        Update tasks that depend on the completed task.
        
        Args:
            completed_task: Task that just completed
        """
        # Find all tasks that depend on this one
        all_tasks = self.task_manager.list_tasks()
        for task in all_tasks:
            if completed_task.id in task.dependencies:
                # Check if all dependencies are now complete
                unresolved = self.task_manager.resolve_dependencies(task)
                if not unresolved:
                    # All dependencies met, mark as ready
                    self.task_manager.mark_ready(task.id)
    
    def submit_task(self, task: Task) -> str:
        """
        Submit a task for execution.
        
        Args:
            task: Task to submit
            
        Returns:
            Task ID
        """
        # Add to task manager
        if task.id not in self.task_manager._tasks:
            self.task_manager._tasks[task.id] = task
        
        # Check dependencies
        unresolved = self.task_manager.resolve_dependencies(task)
        if unresolved:
            self.task_manager.mark_blocked(task.id, f"Waiting for: {unresolved}")
        else:
            self.task_manager.mark_ready(task.id)
        
        self.logger.info(f"Task {task.id} submitted: {task.title}")
        return task.id
    
    def submit_tasks(self, tasks: List[Task]) -> List[str]:
        """
        Submit multiple tasks.
        
        Args:
            tasks: List of tasks to submit
            
        Returns:
            List of task IDs
        """
        return [self.submit_task(task) for task in tasks]
    
    def get_queue_size(self) -> int:
        """Get current queue size."""
        return self._queue.size()
    
    def get_active_count(self) -> int:
        """Get number of actively running tasks."""
        return len([t for t in self.task_manager._tasks.values() if t.status == TaskStatus.RUNNING])
    
    def is_running(self) -> bool:
        """Check if engine is running."""
        return self._running
