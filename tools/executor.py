"""
Tool Executor Module

Handles the execution of AI tools with queue management, 
parallel execution, and result handling.

Author: Abdulraheem Nohari
"""

import asyncio
import logging
import time
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
from enum import Enum
from queue import Queue, Empty
from threading import Lock, Event

from .sandbox import ToolSandbox, ExecutionResult, ExecutionStatus
from .permissions import ToolPermissions

logger = logging.getLogger(__name__)


class ExecutionPriority(Enum):
    """Priority levels for tool execution"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


class QueueStatus(Enum):
    """Status of the execution queue"""
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"


@dataclass
class ExecutionTask:
    """Represents a task to be executed"""
    task_id: str
    tool_name: str
    args: Tuple = ()
    kwargs: Dict = field(default_factory=dict)
    priority: ExecutionPriority = ExecutionPriority.NORMAL
    created_at: float = field(default_factory=time.time)
    timeout: Optional[float] = None
    retry_count: int = 0
    max_retries: int = 3
    callback: Optional[Callable] = None
    
    @property
    def age(self) -> float:
        """Get the age of the task in seconds"""
        return time.time() - self.created_at


@dataclass
class QueueStats:
    """Statistics for the execution queue"""
    total_tasks: int = 0
    pending_tasks: int = 0
    running_tasks: int = 0
    completed_tasks: int = 0
    failed_tasks: int = 0
    average_execution_time: float = 0.0
    max_queue_size: int = 0
    current_queue_size: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'total_tasks': self.total_tasks,
            'pending_tasks': self.pending_tasks,
            'running_tasks': self.running_tasks,
            'completed_tasks': self.completed_tasks,
            'failed_tasks': self.failed_tasks,
            'average_execution_time': self.average_execution_time,
            'max_queue_size': self.max_queue_size,
            'current_queue_size': self.current_queue_size,
        }


class ToolExecutor:
    """
    Executes AI tools with queue management and parallel processing.
    
    This class provides a robust execution system with support for:
    - Priority-based task queue
    - Parallel execution with configurable workers
    - Retry logic for failed tasks
    - Timeout handling
    - Result callbacks
    - Queue statistics and monitoring
    """
    
    def __init__(self, 
                 max_workers: int = 5,
                 max_queue_size: int = 100,
                 max_retries: int = 3,
                 default_timeout: float = 30.0):
        """
        Initialize the executor.
        
        Args:
            max_workers: Maximum number of parallel workers
            max_queue_size: Maximum size of the task queue
            max_retries: Default maximum number of retries
            default_timeout: Default timeout for tasks in seconds
        """
        self.max_workers = max_workers
        self.max_queue_size = max_queue_size
        self.max_retries = max_retries
        self.default_timeout = default_timeout
        
        # Task queue
        self._task_queue: Queue = Queue()
        self._priority_queues: Dict[ExecutionPriority, Queue] = {
            ExecutionPriority.LOW: Queue(),
            ExecutionPriority.NORMAL: Queue(),
            ExecutionPriority.HIGH: Queue(),
            ExecutionPriority.CRITICAL: Queue(),
        }
        
        # State management
        self._running: bool = False
        self._paused: bool = False
        self._stop_event: Event = Event()
        self._lock: Lock = Lock()
        
        # Tracking
        self._active_tasks: Dict[str, ExecutionTask] = {}
        self._task_results: Dict[str, ExecutionResult] = {}
        self._stats: QueueStats = QueueStats()
        self._executor: Optional[ThreadPoolExecutor] = None
        
        # Sandbox integration
        self._sandbox: ToolSandbox = ToolSandbox()
        self._permissions: ToolPermissions = ToolPermissions()
        
        logger.info(f"ToolExecutor initialized with {max_workers} workers")
    
    def start(self):
        """Start the executor"""
        if self._running:
            return
        
        self._running = True
        self._stop_event.clear()
        self._executor = ThreadPoolExecutor(max_workers=self.max_workers)
        
        # Start worker threads
        for _ in range(self.max_workers):
            self._executor.submit(self._worker)
        
        logger.info("ToolExecutor started")
    
    def stop(self, wait_for_completion: bool = True):
        """
        Stop the executor.
        
        Args:
            wait_for_completion: Whether to wait for running tasks to complete
        """
        if not self._running:
            return
        
        self._stop_event.set()
        
        if wait_for_completion:
            # Wait for active tasks to complete
            while self._active_tasks:
                time.sleep(0.1)
        
        if self._executor:
            self._executor.shutdown(wait=False)
        
        self._running = False
        logger.info("ToolExecutor stopped")
    
    def pause(self):
        """Pause the executor"""
        self._paused = True
        logger.info("ToolExecutor paused")
    
    def resume(self):
        """Resume the executor"""
        self._paused = False
        logger.info("ToolExecutor resumed")
    
    @property
    def is_running(self) -> bool:
        """Check if executor is running"""
        return self._running and not self._stop_event.is_set()
    
    @property
    def is_paused(self) -> bool:
        """Check if executor is paused"""
        return self._paused
    
    @property
    def status(self) -> QueueStatus:
        """Get current queue status"""
        if not self._running:
            return QueueStatus.STOPPED
        if self._paused:
            return QueueStatus.PAUSED
        if self._active_tasks:
            return QueueStatus.RUNNING
        return QueueStatus.IDLE
    
    @property
    def stats(self) -> QueueStats:
        """Get current queue statistics"""
        with self._lock:
            # Update stats
            self._stats.current_queue_size = self.queue_size
            self._stats.pending_tasks = self.pending_tasks
            self._stats.running_tasks = len(self._active_tasks)
        return self._stats
    
    @property
    def queue_size(self) -> int:
        """Get total queue size"""
        total = 0
        for queue in self._priority_queues.values():
            total += queue.qsize()
        return total
    
    @property
    def pending_tasks(self) -> int:
        """Get number of pending tasks"""
        return self.queue_size
    
    def submit(self, 
              tool_name: str,
              *args,
              priority: ExecutionPriority = ExecutionPriority.NORMAL,
              timeout: Optional[float] = None,
              retry_count: int = 0,
              max_retries: Optional[int] = None,
              callback: Optional[Callable[[ExecutionResult], None]] = None,
              **kwargs) -> str:
        """
        Submit a task for execution.
        
        Args:
            tool_name: Name of the tool to execute
            *args: Positional arguments for the tool
            priority: Execution priority
            timeout: Timeout in seconds
            retry_count: Current retry count
            max_retries: Maximum number of retries
            callback: Callback function for result
            **kwargs: Keyword arguments for the tool
            
        Returns:
            Task ID
            
        Raises:
            RuntimeError: If queue is full
        """
        if not self._running:
            self.start()
        
        # Check queue size
        if self.queue_size >= self.max_queue_size:
            raise RuntimeError(f"Queue is full. Max size: {self.max_queue_size}")
        
        # Create task
        task = ExecutionTask(
            task_id=str(uuid.uuid4()),
            tool_name=tool_name,
            args=args,
            kwargs=kwargs,
            priority=priority,
            timeout=timeout or self.default_timeout,
            retry_count=retry_count,
            max_retries=max_retries or self.max_retries,
            callback=callback,
        )
        
        # Add to priority queue
        self._priority_queues[priority].put(task)
        
        with self._lock:
            self._stats.total_tasks += 1
            if self.queue_size > self._stats.max_queue_size:
                self._stats.max_queue_size = self.queue_size
        
        logger.debug(f"Task submitted: {task.task_id} (tool: {tool_name}, priority: {priority.name})")
        
        return task.task_id
    
    def submit_sync(self, 
                   tool_name: str,
                   *args,
                   timeout: Optional[float] = None,
                   **kwargs) -> ExecutionResult:
        """
        Submit a task and wait for completion (synchronous).
        
        Args:
            tool_name: Name of the tool to execute
            *args: Positional arguments for the tool
            timeout: Timeout in seconds
            **kwargs: Keyword arguments for the tool
            
        Returns:
            ExecutionResult
        """
        # For synchronous execution, use the sandbox directly
        return self._sandbox.execute(tool_name, *args, timeout=timeout, **kwargs)
    
    async def submit_async(self, 
                          tool_name: str,
                          *args,
                          timeout: Optional[float] = None,
                          **kwargs) -> ExecutionResult:
        """
        Submit a task and wait for completion (asynchronous).
        
        Args:
            tool_name: Name of the tool to execute
            *args: Positional arguments for the tool
            timeout: Timeout in seconds
            **kwargs: Keyword arguments for the tool
            
        Returns:
            ExecutionResult
        """
        # For async execution, use the sandbox directly
        return await self._sandbox.execute_async(tool_name, *args, timeout=timeout, **kwargs)
    
    def _worker(self):
        """Worker thread that processes tasks"""
        while not self._stop_event.is_set():
            try:
                # Check if paused
                if self._paused:
                    time.sleep(0.1)
                    continue
                
                # Get next task from highest priority queue
                task = self._get_next_task()
                
                if task is None:
                    time.sleep(0.1)
                    continue
                
                # Execute the task
                self._execute_task(task)
                
            except Empty:
                time.sleep(0.1)
            except Exception as e:
                logger.error(f"Worker error: {e}")
                time.sleep(1)
    
    def _get_next_task(self) -> Optional[ExecutionTask]:
        """
        Get the next task from the highest priority queue.
        
        Returns:
            ExecutionTask or None if no tasks
        """
        # Try queues in priority order
        for priority in [
            ExecutionPriority.CRITICAL,
            ExecutionPriority.HIGH,
            ExecutionPriority.NORMAL,
            ExecutionPriority.LOW,
        ]:
            try:
                return self._priority_queues[priority].get_nowait()
            except Empty:
                continue
        return None
    
    def _execute_task(self, task: ExecutionTask):
        """Execute a task"""
        with self._lock:
            self._active_tasks[task.task_id] = task
        
        try:
            # Execute using sandbox
            result = self._sandbox.execute(
                task.tool_name,
                *task.args,
                timeout=task.timeout,
                **task.kwargs
            )
            
            # Store result
            with self._lock:
                self._task_results[task.task_id] = result
                if result.status == ExecutionStatus.COMPLETED:
                    self._stats.completed_tasks += 1
                else:
                    self._stats.failed_tasks += 1
            
            # Call callback if provided
            if task.callback:
                try:
                    task.callback(result)
                except Exception as e:
                    logger.error(f"Callback error for task {task.task_id}: {e}")
            
        except Exception as e:
            logger.error(f"Task execution failed: {task.task_id} - {e}")
            
            # Create error result
            result = ExecutionResult(
                status=ExecutionStatus.FAILED,
                tool_name=task.tool_name,
                input_args=task.kwargs,
                error=str(e),
            )
            
            with self._lock:
                self._task_results[task.task_id] = result
                self._stats.failed_tasks += 1
            
            # Retry if applicable
            if task.retry_count < task.max_retries:
                new_task = ExecutionTask(
                    task_id=str(uuid.uuid4()),
                    tool_name=task.tool_name,
                    args=task.args,
                    kwargs=task.kwargs,
                    priority=task.priority,
                    timeout=task.timeout,
                    retry_count=task.retry_count + 1,
                    max_retries=task.max_retries,
                    callback=task.callback,
                )
                self._priority_queues[task.priority].put(new_task)
                logger.info(f"Task {task.task_id} failed, retrying ({new_task.retry_count}/{task.max_retries})")
            elif task.callback:
                try:
                    task.callback(result)
                except Exception as e:
                    logger.error(f"Callback error for task {task.task_id}: {e}")
        
        finally:
            with self._lock:
                self._active_tasks.pop(task.task_id, None)
    
    def get_result(self, task_id: str) -> Optional[ExecutionResult]:
        """
        Get the result of a task.
        
        Args:
            task_id: Task ID
            
        Returns:
            ExecutionResult or None if not found
        """
        with self._lock:
            return self._task_results.get(task_id)
    
    def get_task(self, task_id: str) -> Optional[ExecutionTask]:
        """
        Get a task by ID.
        
        Args:
            task_id: Task ID
            
        Returns:
            ExecutionTask or None if not found
        """
        with self._lock:
            return self._active_tasks.get(task_id)
    
    def cancel_task(self, task_id: str) -> bool:
        """
        Cancel a task.
        
        Args:
            task_id: Task ID to cancel
            
        Returns:
            True if task was cancelled
        """
        with self._lock:
            if task_id in self._active_tasks:
                # For active tasks, we can only mark them for cancellation
                # Actual cancellation depends on the tool implementation
                self._sandbox.cancel_execution(task_id)
                return True
            return False
    
    def cancel_all_tasks(self) -> int:
        """
        Cancel all pending and running tasks.
        
        Returns:
            Number of tasks cancelled
        """
        count = 0
        
        # Cancel active tasks
        with self._lock:
            for task_id in list(self._active_tasks.keys()):
                if self.cancel_task(task_id):
                    count += 1
        
        # Clear queues
        for queue in self._priority_queues.values():
            while not queue.empty():
                try:
                    queue.get_nowait()
                    count += 1
                except Empty:
                    break
        
        logger.info(f"Cancelled {count} tasks")
        return count
    
    def clear_results(self):
        """Clear all stored results"""
        with self._lock:
            self._task_results.clear()
        logger.info("Cleared all task results")
    
    def clear_queue(self):
        """Clear all pending tasks from the queue"""
        for queue in self._priority_queues.values():
            while not queue.empty():
                try:
                    queue.get_nowait()
                except Empty:
                    break
        logger.info("Cleared task queue")
    
    def reset_stats(self):
        """Reset queue statistics"""
        with self._lock:
            self._stats = QueueStats()
        logger.info("Reset queue statistics")


# Global executor instance
executor = ToolExecutor()


def get_executor() -> ToolExecutor:
    """Get the global tool executor instance"""
    return executor
