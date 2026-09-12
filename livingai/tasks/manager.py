"""
LivingAI Task Manager
===================

Manages tasks for the LivingAI system with full lifecycle support.
"""

import logging
import time
from typing import Dict, Any, Optional, List
from enum import Enum
from dataclasses import dataclass, field, asdict
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..memory.manager import MemoryManager
    from ..config import ConfigManager
    from ..security.audit import AuditLogger


class TaskStatus(Enum):
    """Status of a task."""
    PENDING = "pending"       # Task has been created but not ready
    READY = "ready"           # Task is ready to execute
    RUNNING = "running"       # Task is currently executing
    WAITING = "waiting"       # Task is waiting for dependencies
    COMPLETED = "completed"   # Task has been completed successfully
    FAILED = "failed"         # Task has failed
    BLOCKED = "blocked"       # Task cannot be completed due to issues
    CANCELLED = "cancelled"   # Task has been cancelled


class TaskPriority(Enum):
    """Priority levels for tasks."""
    CRITICAL = "critical"     # Must be completed immediately
    HIGH = "high"             # High priority
    NORMAL = "normal"         # Normal priority
    LOW = "low"               # Low priority
    BACKGROUND = "background" # Background task


@dataclass
class Task:
    """
    Represents a single task in the LivingAI system.
    
    Attributes:
        id: Unique identifier for the task
        goal_id: ID of the goal this task belongs to
        agent_id: ID of the agent executing this task
        parent_task_id: ID of parent task if this is a subtask
        title: Human-readable title/description
        description: Detailed description of the task
        priority: Task priority level
        status: Current status of the task
        dependencies: List of task IDs that must complete before this task
        tool_requirements: Tools required for this task
        success_criteria: Criteria for task completion
        retry_count: Number of retry attempts
        max_retries: Maximum number of retries allowed
        created_at: Timestamp when task was created
        started_at: Timestamp when task started executing
        completed_at: Timestamp when task completed
        failed_at: Timestamp when task failed
        result: Result of task execution
        error: Error message if task failed
        observations: Observations from task execution
        verification: Verification results
        metadata: Additional metadata
    """
    id: str
    goal_id: Optional[str] = None
    agent_id: Optional[str] = None
    parent_task_id: Optional[str] = None
    title: str = ""
    description: str = ""
    priority: TaskPriority = TaskPriority.NORMAL
    status: TaskStatus = TaskStatus.PENDING
    dependencies: List[str] = field(default_factory=list)
    tool_requirements: List[str] = field(default_factory=list)
    success_criteria: Dict[str, Any] = field(default_factory=dict)
    retry_count: int = 0
    max_retries: int = 3
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    failed_at: Optional[float] = None
    result: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    observations: List[Dict[str, Any]] = field(default_factory=list)
    verification: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Task':
        """Create task from dictionary."""
        # Convert string status/priority to enum
        if isinstance(data.get('status'), str):
            data['status'] = TaskStatus(data['status'])
        if isinstance(data.get('priority'), str):
            data['priority'] = TaskPriority(data['priority'])
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})
    
    def is_ready(self) -> bool:
        """Check if task is ready to execute (all dependencies completed)."""
        return self.status == TaskStatus.READY
    
    def is_completed(self) -> bool:
        """Check if task is completed."""
        return self.status == TaskStatus.COMPLETED
    
    def is_failed(self) -> bool:
        """Check if task has failed."""
        return self.status == TaskStatus.FAILED
    
    def can_retry(self) -> bool:
        """Check if task can be retried."""
        return self.is_failed() and self.retry_count < self.max_retries


class TaskManager:
    """
    Manages tasks for the LivingAI system.
    
    Responsibilities:
    - CRUD operations for tasks
    - Task status management
    - Task prioritization
    - Task dependency resolution
    - Task progress tracking
    - Task statistics
    """
    
    def __init__(
        self,
        memory_manager: Optional['MemoryManager'] = None,
        config: Optional['ConfigManager'] = None,
        audit_logger: Optional['AuditLogger'] = None
    ):
        """
        Initialize the TaskManager.
        
        Args:
            memory_manager: Memory manager for storing tasks
            config: Configuration manager
            audit_logger: Audit logger for tracking actions
        """
        self.memory_manager = memory_manager
        self.config = config
        self.audit_logger = audit_logger
        
        # Task storage
        self._tasks: Dict[str, Task] = {}
        self._task_index: int = 0
        
        # Logger
        self.logger = logging.getLogger(__name__)
    
    def create_task(
        self,
        title: str,
        description: str = "",
        goal_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        parent_task_id: Optional[str] = None,
        priority: TaskPriority = TaskPriority.NORMAL,
        dependencies: List[str] = None,
        tool_requirements: List[str] = None,
        success_criteria: Dict[str, Any] = None,
        metadata: Dict[str, Any] = None
    ) -> Task:
        """
        Create a new task.
        
        Args:
            title: Task title
            description: Task description
            goal_id: ID of the goal this task belongs to
            agent_id: ID of the agent that will execute this task
            parent_task_id: ID of parent task
            priority: Task priority
            dependencies: List of task IDs this task depends on
            tool_requirements: Tools required for this task
            success_criteria: Criteria for task completion
            metadata: Additional metadata
            
        Returns:
            The created Task object
        """
        self._task_index += 1
        task_id = f"task_{self._task_index}"
        
        task = Task(
            id=task_id,
            title=title,
            description=description,
            goal_id=goal_id,
            agent_id=agent_id,
            parent_task_id=parent_task_id,
            priority=priority,
            dependencies=dependencies or [],
            tool_requirements=tool_requirements or [],
            success_criteria=success_criteria or {},
            metadata=metadata or {}
        )
        
        self._tasks[task_id] = task
        
        # Log creation
        if self.audit_logger:
            self.audit_logger.log("TASK_CREATED", f"Task {task_id} created: {title}")
        
        self.logger.info(f"Task {task_id} created: {title}")
        
        return task
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """
        Get a task by ID.
        
        Args:
            task_id: Task ID
            
        Returns:
            Task object or None if not found
        """
        return self._tasks.get(task_id)
    
    def update_task(self, task_id: str, **kwargs) -> Optional[Task]:
        """
        Update a task.
        
        Args:
            task_id: Task ID
            **kwargs: Task attributes to update
            
        Returns:
            Updated Task object or None if not found
        """
        task = self._tasks.get(task_id)
        if not task:
            self.logger.warning(f"Task {task_id} not found")
            return None
        
        for key, value in kwargs.items():
            if hasattr(task, key):
                setattr(task, key, value)
        
        # Log update
        if self.audit_logger:
            self.audit_logger.log("TASK_UPDATED", f"Task {task_id} updated")
        
        return task
    
    def delete_task(self, task_id: str) -> bool:
        """
        Delete a task.
        
        Args:
            task_id: Task ID
            
        Returns:
            True if deleted, False if not found
        """
        if task_id in self._tasks:
            del self._tasks[task_id]
            
            if self.audit_logger:
                self.audit_logger.log("TASK_DELETED", f"Task {task_id} deleted")
            
            self.logger.info(f"Task {task_id} deleted")
            return True
        
        return False
    
    def list_tasks(
        self,
        goal_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        status: Optional[TaskStatus] = None,
        priority: Optional[TaskPriority] = None
    ) -> List[Task]:
        """
        List tasks with optional filters.
        
        Args:
            goal_id: Filter by goal ID
            agent_id: Filter by agent ID
            status: Filter by status
            priority: Filter by priority
            
        Returns:
            List of matching Task objects
        """
        tasks = list(self._tasks.values())
        
        if goal_id:
            tasks = [t for t in tasks if t.goal_id == goal_id]
        if agent_id:
            tasks = [t for t in tasks if t.agent_id == agent_id]
        if status:
            tasks = [t for t in tasks if t.status == status]
        if priority:
            tasks = [t for t in tasks if t.priority == priority]
        
        return tasks
    
    def get_active_tasks(self) -> List[Task]:
        """Get all active (non-completed, non-failed) tasks."""
        return [t for t in self._tasks.values() 
                if t.status not in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]]
    
    def get_ready_tasks(self) -> List[Task]:
        """Get all tasks that are ready to execute."""
        return [t for t in self._tasks.values() if t.is_ready()]
    
    def get_blocked_tasks(self) -> List[Task]:
        """Get all blocked tasks."""
        return [t for t in self._tasks.values() if t.status == TaskStatus.BLOCKED]
    
    def get_failed_tasks(self) -> List[Task]:
        """Get all failed tasks."""
        return [t for t in self._tasks.values() if t.is_failed()]
    
    def resolve_dependencies(self, task: Task) -> List[str]:
        """
        Resolve task dependencies.
        
        Args:
            task: Task to check
            
        Returns:
            List of unresolved dependency IDs
        """
        unresolved = []
        for dep_id in task.dependencies:
            dep_task = self.get_task(dep_id)
            if not dep_task or not dep_task.is_completed():
                unresolved.append(dep_id)
        return unresolved
    
    def update_task_status(
        self,
        task_id: str,
        new_status: TaskStatus,
        result: Dict[str, Any] = None,
        error: str = None
    ) -> Optional[Task]:
        """
        Update task status with optional result/error.
        
        Args:
            task_id: Task ID
            new_status: New status
            result: Result data (for completed tasks)
            error: Error message (for failed tasks)
            
        Returns:
            Updated Task or None
        """
        task = self._tasks.get(task_id)
        if not task:
            return None
        
        old_status = task.status
        task.status = new_status
        
        if new_status == TaskStatus.RUNNING:
            task.started_at = time.time()
            task.retry_count = 0
        elif new_status == TaskStatus.COMPLETED:
            task.completed_at = time.time()
            task.result = result or {}
        elif new_status == TaskStatus.FAILED:
            task.failed_at = time.time()
            task.error = error
            task.retry_count += 1
        elif new_status == TaskStatus.CANCELLED:
            task.completed_at = time.time()
        
        # Log status change
        if self.audit_logger:
            self.audit_logger.log("TASK_STATUS", 
                f"Task {task_id}: {old_status.value} -> {new_status.value}")
        
        self.logger.info(f"Task {task_id} status: {old_status.value} -> {new_status.value}")
        
        return task
    
    def mark_ready(self, task_id: str) -> Optional[Task]:
        """Mark a task as ready to execute."""
        return self.update_task_status(task_id, TaskStatus.READY)
    
    def mark_running(self, task_id: str) -> Optional[Task]:
        """Mark a task as running."""
        return self.update_task_status(task_id, TaskStatus.RUNNING)
    
    def mark_completed(self, task_id: str, result: Dict[str, Any] = None) -> Optional[Task]:
        """Mark a task as completed."""
        return self.update_task_status(task_id, TaskStatus.COMPLETED, result=result)
    
    def mark_failed(self, task_id: str, error: str = "Unknown error") -> Optional[Task]:
        """Mark a task as failed."""
        return self.update_task_status(task_id, TaskStatus.FAILED, error=error)
    
    def mark_blocked(self, task_id: str, reason: str = "Dependencies not met") -> Optional[Task]:
        """Mark a task as blocked."""
        task = self.update_task_status(task_id, TaskStatus.BLOCKED)
        if task:
            task.error = reason
        return task
    
    def mark_cancelled(self, task_id: str) -> Optional[Task]:
        """Mark a task as cancelled."""
        return self.update_task_status(task_id, TaskStatus.CANCELLED)
    
    def retry_task(self, task_id: str) -> Optional[Task]:
        """
        Retry a failed task.
        
        Args:
            task_id: Task ID
            
        Returns:
            Task if retried, None otherwise
        """
        task = self._tasks.get(task_id)
        if not task or not task.can_retry():
            return None
        
        # Reset task for retry
        task.status = TaskStatus.READY
        task.started_at = None
        task.failed_at = None
        task.error = None
        task.observations = []
        task.verification = {}
        
        if self.audit_logger:
            self.audit_logger.log("TASK_RETRY", f"Task {task_id} retry #{task.retry_count + 1}")
        
        self.logger.info(f"Task {task_id} queued for retry")
        
        return task
    
    def get_task_count(self) -> int:
        """Get total number of tasks."""
        return len(self._tasks)
    
    def get_stats(self) -> Dict[str, int]:
        """Get task statistics."""
        stats = {
            'total': 0,
            'pending': 0,
            'ready': 0,
            'running': 0,
            'waiting': 0,
            'completed': 0,
            'failed': 0,
            'blocked': 0,
            'cancelled': 0
        }
        
        for task in self._tasks.values():
            stats['total'] += 1
            stats[task.status.value] += 1
        
        return stats
    
    def cleanup_completed(self, older_than_seconds: float = 86400) -> int:
        """
        Clean up completed tasks older than specified time.
        
        Args:
            older_than_seconds: Remove tasks completed longer than this
            
        Returns:
            Number of tasks removed
        """
        cutoff = time.time() - older_than_seconds
        removed = 0
        
        for task_id, task in list(self._tasks.items()):
            if task.is_completed() and task.completed_at and task.completed_at < cutoff:
                del self._tasks[task_id]
                removed += 1
        
        if removed > 0 and self.audit_logger:
            self.audit_logger.log("TASK_CLEANUP", f"Removed {removed} old completed tasks")
        
        self.logger.info(f"Cleaned up {removed} completed tasks")
        return removed
