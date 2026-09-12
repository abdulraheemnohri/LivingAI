# LivingAI Task Scheduler
# ==========================
# This module implements task scheduling for LivingAI.

import os
import time
import uuid
import logging
import threading
from typing import Dict, Any, Optional, List, Callable, Tuple
from enum import Enum
from dataclasses import dataclass, field

# Local imports
from ..config import ConfigManager
from ..security.audit import AuditLogger


class TaskStatus(Enum):
    """Status of a scheduled task."""
    PENDING = "pending"     # Task is waiting to be executed
    RUNNING = "running"     # Task is currently executing
    COMPLETED = "completed" # Task completed successfully
    FAILED = "failed"       # Task failed
    CANCELLED = "cancelled" # Task was cancelled


@dataclass
class ScheduledTask:
    """
    Represents a scheduled task.
    
    Attributes:
        task_id: Unique identifier for the task.
        task: The callable task to execute.
        name: Name of the task.
        run_at: Timestamp when the task should run.
        interval: Optional interval for repeating tasks.
        status: Current status of the task.
        result: Result of the task execution.
        error: Error message if the task failed.
        created_at: Timestamp when the task was created.
        started_at: Timestamp when the task started executing.
        completed_at: Timestamp when the task completed.
        retries: Number of retries attempted.
        max_retries: Maximum number of retries.
    """
    task_id: str
    task: Callable
    name: str = ""
    run_at: float = 0.0
    interval: Optional[float] = None
    status: TaskStatus = TaskStatus.PENDING
    result: Any = None
    error: Optional[str] = None
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    retries: int = 0
    max_retries: int = 3
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the scheduled task to a dictionary.
        
        Returns:
            Dict[str, Any]: Dictionary representation.
        """
        return {
            "task_id": self.task_id,
            "name": self.name,
            "run_at": self.run_at,
            "interval": self.interval,
            "status": self.status.value,
            "result": self.result,
            "error": self.error,
            "created_at": self.created_at,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "retries": self.retries,
            "max_retries": self.max_retries,
        }


class TaskScheduler:
    """
    Implements task scheduling for LivingAI.
    
    Responsibilities:
    - Schedule tasks for future execution
    - Execute tasks when they're due
    - Handle repeating tasks
    - Manage task lifecycle
    - Track task history
    """
    
    def __init__(
        self,
        config: ConfigManager,
        audit_logger: AuditLogger
    ):
        """
        Initialize the TaskScheduler.
        
        Args:
            config: Configuration manager.
            audit_logger: Audit logger for tracking actions.
        """
        self.config = config
        self.audit_logger = audit_logger
        
        # Task storage
        self._tasks: Dict[str, ScheduledTask] = {}
        self._task_queue: List[ScheduledTask] = []
        self._completed_tasks: List[ScheduledTask] = []
        self._failed_tasks: List[ScheduledTask] = []
        
        # Scheduler state
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._last_run_time: Optional[float] = None
        
        logging.info("TaskScheduler initialized")
    
    def start(self) -> bool:
        """
        Start the task scheduler.
        
        Returns:
            bool: True if scheduler started successfully, False otherwise.
        """
        if self._running:
            logging.warning("Task scheduler is already running")
            return False
        
        self._running = True
        self._stop_event.clear()
        
        # Create and start the scheduler thread
        self._thread = threading.Thread(
            target=self._run,
            daemon=True,
            name="LivingAI-TaskScheduler"
        )
        self._thread.start()
        
        self.audit_logger.log("SCHEDULER_START", "Task scheduler started")
        return True
    
    def stop(self) -> bool:
        """
        Stop the task scheduler.
        
        Returns:
            bool: True if scheduler stopped successfully, False otherwise.
        """
        if not self._running:
            logging.warning("Task scheduler is not running")
            return False
        
        self._running = False
        self._stop_event.set()
        
        # Wait for the thread to stop
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=5.0)
        
        self.audit_logger.log("SCHEDULER_STOP", "Task scheduler stopped")
        return True
    
    def _run(self) -> None:
        """Main scheduler loop."""
        try:
            while not self._stop_event.is_set():
                # Run pending tasks
                self.run_pending_tasks()
                
                # Sleep for a short time
                sleep_time = self.config.get("autonomy.scheduler_interval", 1.0)
                time.sleep(sleep_time)
            
        except Exception as e:
            self.audit_logger.log("SCHEDULER_ERROR", str(e))
            logging.error(f"Task scheduler error: {e}")
    
    def schedule_task(
        self,
        task: Callable,
        delay: float = 0.0,
        interval: Optional[float] = None,
        name: Optional[str] = None
    ) -> str:
        """
        Schedule a task for future execution.
        
        Args:
            task: Task to execute (callable).
            delay: Delay before first execution in seconds.
            interval: Optional interval for repeating tasks in seconds.
            name: Optional name for the task.
            
        Returns:
            str: Task ID.
        """
        # Generate task ID
        task_id = str(uuid.uuid4())
        
        # Calculate run time
        run_at = time.time() + delay
        
        # Create scheduled task
        scheduled_task = ScheduledTask(
            task_id=task_id,
            task=task,
            name=name or f"task_{task_id[:8]}",
            run_at=run_at,
            interval=interval,
        )
        
        # Store the task
        self._tasks[task_id] = scheduled_task
        
        # Add to queue
        self._add_to_queue(scheduled_task)
        
        self.audit_logger.log(
            "SCHEDULER_SCHEDULE",
            f"Scheduled task {task_id} to run at {run_at}"
        )
        
        return task_id
    
    def _add_to_queue(self, task: ScheduledTask) -> None:
        """
        Add a task to the execution queue.
        
        Args:
            task: Task to add to the queue.
        """
        # Insert the task in the correct position based on run_at time
        for i, existing_task in enumerate(self._task_queue):
            if task.run_at < existing_task.run_at:
                self._task_queue.insert(i, task)
                return
        
        # If we get here, add to the end
        self._task_queue.append(task)
    
    def run_pending_tasks(self) -> int:
        """
        Run all pending tasks that are due.
        
        Returns:
            int: Number of tasks executed.
        """
        current_time = time.time()
        executed_count = 0
        
        # Process tasks in order
        for i, task in enumerate(self._task_queue):
            if task.run_at > current_time:
                # No more tasks to run
                break
            
            # Remove from queue
            self._task_queue.pop(i)
            
            # Execute the task
            self._execute_task(task)
            executed_count += 1
            
            # If it's a repeating task, reschedule it
            if task.interval is not None and task.status == TaskStatus.COMPLETED:
                self._reschedule_task(task)
        
        return executed_count
    
    def _execute_task(self, task: ScheduledTask) -> None:
        """
        Execute a scheduled task.
        
        Args:
            task: Task to execute.
        """
        try:
            # Update task status
            task.status = TaskStatus.RUNNING
            task.started_at = time.time()
            task.retries += 1
            
            # Execute the task
            task.result = task.task()
            
            # Update task status
            task.status = TaskStatus.COMPLETED
            task.completed_at = time.time()
            task.error = None
            
            # Add to completed tasks
            self._completed_tasks.append(task)
            
            self.audit_logger.log(
                "SCHEDULER_TASK_COMPLETE",
                f"Task {task.task_id} completed successfully"
            )
            
        except Exception as e:
            # Update task status
            task.status = TaskStatus.FAILED
            task.completed_at = time.time()
            task.error = str(e)
            
            # Check if we should retry
            if task.retries < task.max_retries:
                # Reschedule for retry
                retry_delay = self.config.get("autonomy.retry_delay", 5.0)
                task.run_at = time.time() + retry_delay
                task.status = TaskStatus.PENDING
                self._add_to_queue(task)
                
                self.audit_logger.log(
                    "SCHEDULER_TASK_RETRY",
                    f"Task {task.task_id} failed, retry {task.retries + 1}/{task.max_retries}"
                )
            else:
                # Add to failed tasks
                self._failed_tasks.append(task)
                
                self.audit_logger.log(
                    "SCHEDULER_TASK_FAIL",
                    f"Task {task.task_id} failed permanently: {str(e)}"
                )
    
    def _reschedule_task(self, task: ScheduledTask) -> None:
        """
        Reschedule a repeating task.
        
        Args:
            task: Task to reschedule.
        """
        if task.interval is None:
            return
        
        # Calculate next run time
        task.run_at = time.time() + task.interval
        task.status = TaskStatus.PENDING
        task.started_at = None
        task.completed_at = None
        task.result = None
        task.error = None
        
        # Add back to queue
        self._add_to_queue(task)
        
        self.audit_logger.log(
            "SCHEDULER_TASK_RESCHEDULE",
            f"Task {task.task_id} rescheduled to run at {task.run_at}"
        )
    
    def cancel_task(self, task_id: str) -> bool:
        """
        Cancel a scheduled task.
        
        Args:
            task_id: ID of the task to cancel.
            
        Returns:
            bool: True if task was cancelled, False otherwise.
        """
        # Remove from tasks dict
        if task_id in self._tasks:
            task = self._tasks[task_id]
            
            # Remove from queue if present
            if task in self._task_queue:
                self._task_queue.remove(task)
            
            # Update status
            task.status = TaskStatus.CANCELLED
            task.completed_at = time.time()
            
            # Remove from tasks dict
            del self._tasks[task_id]
            
            self.audit_logger.log(
                "SCHEDULER_TASK_CANCEL",
                f"Task {task_id} cancelled"
            )
            
            return True
        
        return False
    
    def get_task(self, task_id: str) -> Optional[ScheduledTask]:
        """
        Get a scheduled task by ID.
        
        Args:
            task_id: ID of the task to get.
            
        Returns:
            Optional[ScheduledTask]: The task, or None if not found.
        """
        return self._tasks.get(task_id)
    
    def get_scheduled_tasks(self) -> List[Dict[str, Any]]:
        """
        Get all scheduled tasks.
        
        Returns:
            List[Dict[str, Any]]: List of scheduled tasks.
        """
        return [task.to_dict() for task in self._task_queue]
    
    def get_completed_tasks(self) -> List[Dict[str, Any]]:
        """
        Get all completed tasks.
        
        Returns:
            List[Dict[str, Any]]: List of completed tasks.
        """
        return [task.to_dict() for task in self._completed_tasks]
    
    def get_failed_tasks(self) -> List[Dict[str, Any]]:
        """
        Get all failed tasks.
        
        Returns:
            List[Dict[str, Any]]: List of failed tasks.
        """
        return [task.to_dict() for task in self._failed_tasks]
    
    def clear_tasks(self) -> None:
        """Clear all scheduled tasks."""
        self._task_queue = []
        self._tasks = {}
        
        self.audit_logger.log("SCHEDULER_CLEAR", "All scheduled tasks cleared")
    
    def clear_history(self) -> None:
        """Clear task history."""
        self._completed_tasks = []
        self._failed_tasks = []
        
        self.audit_logger.log("SCHEDULER_CLEAR_HISTORY", "Task history cleared")
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get the current status of the scheduler.
        
        Returns:
            Dict[str, Any]: Scheduler status.
        """
        return {
            "running": self._running,
            "pending_tasks": len(self._task_queue),
            "completed_tasks": len(self._completed_tasks),
            "failed_tasks": len(self._failed_tasks),
            "total_tasks": len(self._tasks),
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the scheduler.
        
        Returns:
            Dict[str, Any]: Scheduler statistics.
        """
        total_tasks = len(self._completed_tasks) + len(self._failed_tasks)
        
        return {
            "total_tasks": total_tasks,
            "completed": len(self._completed_tasks),
            "failed": len(self._failed_tasks),
            "success_rate": (
                len(self._completed_tasks) / total_tasks
                if total_tasks > 0
                else 0.0
            ),
        }
    
    def run_now(self, task_id: str) -> bool:
        """
        Run a scheduled task immediately.
        
        Args:
            task_id: ID of the task to run.
            
        Returns:
            bool: True if task was run, False otherwise.
        """
        if task_id not in self._tasks:
            return False
        
        task = self._tasks[task_id]
        
        # Remove from queue if present
        if task in self._task_queue:
            self._task_queue.remove(task)
        
        # Execute immediately
        task.run_at = time.time()
        self._execute_task(task)
        
        # If it's a repeating task, reschedule it
        if task.interval is not None and task.status == TaskStatus.COMPLETED:
            self._reschedule_task(task)
        
        return True
    
    def get_next_task_time(self) -> Optional[float]:
        """
        Get the time when the next task will run.
        
        Returns:
            Optional[float]: Timestamp of next task, or None if no tasks.
        """
        if not self._task_queue:
            return None
        
        return self._task_queue[0].run_at
    
    def get_time_until_next_task(self) -> Optional[float]:
        """
        Get the time until the next task will run.
        
        Returns:
            Optional[float]: Seconds until next task, or None if no tasks.
        """
        next_task_time = self.get_next_task_time()
        
        if next_task_time is None:
            return None
        
        return max(0.0, next_task_time - time.time())
