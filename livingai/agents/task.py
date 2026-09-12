"""
Task Management
===============

Task and TaskGraph implementations for agent planning.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum


class TaskState(Enum):
    """States for tasks."""
    PENDING = "PENDING"
    READY = "READY"
    RUNNING = "RUNNING"
    WAITING = "WAITING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    RETRYING = "RETRYING"
    BLOCKED = "BLOCKED"
    CANCELLED = "CANCELLED"
    SKIPPED = "SKIPPED"


@dataclass
class Task:
    """Represents a single task in a plan."""
    id: str
    title: str
    description: str
    status: str = "PENDING"
    priority: int = 5
    dependencies: List[str] = field(default_factory=list)
    tool: Optional[str] = None
    arguments: Dict[str, Any] = field(default_factory=dict)
    risk: str = "LOW"
    timeout: int = 300
    retry_limit: int = 3
    verification_required: bool = True
    result: Optional[Dict] = None
    
    def to_dict(self) -> Dict:
        """Convert task to dictionary."""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'status': self.status,
            'priority': self.priority,
            'dependencies': self.dependencies,
            'tool': self.tool,
            'arguments': self.arguments,
            'risk': self.risk,
            'timeout': self.timeout,
            'retry_limit': self.retry_limit,
            'verification_required': self.verification_required,
            'result': self.result
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Task':
        """Create task from dictionary."""
        return cls(**data)


class TaskGraph:
    """
    Manages a graph of tasks with dependencies.
    
    Supports:
    - Adding tasks with dependencies
    - Topological sorting for execution order
    - Finding ready tasks (all dependencies satisfied)
    - Cycle detection
    """
    
    def __init__(self):
        self.tasks: Dict[str, Task] = {}
        self.dependency_graph: Dict[str, List[str]] = {}
    
    def add_task(self, task: Task):
        """Add a task to the graph."""
        self.tasks[task.id] = task
        self.dependency_graph[task.id] = task.dependencies
        
        for dep_id in task.dependencies:
            if dep_id not in self.tasks:
                self.tasks[dep_id] = Task(
                    id=dep_id,
                    title=f"Dependency: {dep_id}",
                    description="Placeholder for dependency"
                )
                self.dependency_graph[dep_id] = []
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """Get a task by ID."""
        return self.tasks.get(task_id)
    
    def get_dependencies(self, task_id: str) -> List[str]:
        """Get dependencies for a task."""
        return self.dependency_graph.get(task_id, [])
    
    def get_dependents(self, task_id: str) -> List[str]:
        """Get tasks that depend on this task."""
        dependents = []
        for tid, deps in self.dependency_graph.items():
            if task_id in deps:
                dependents.append(tid)
        return dependents
    
    def topological_sort(self) -> List[str]:
        """
        Return tasks in topological order (dependencies first).
        Uses Kahn's algorithm.
        """
        in_degree: Dict[str, int] = {tid: 0 for tid in self.tasks}
        
        for tid, deps in self.dependency_graph.items():
            for dep in deps:
                if dep in in_degree:
                    in_degree[tid] += 1
        
        queue = [tid for tid, degree in in_degree.items() if degree == 0]
        result: List[str] = []
        
        while queue:
            queue.sort(key=lambda tid: self.tasks[tid].priority, reverse=True)
            task_id = queue.pop(0)
            result.append(task_id)
            
            for dependent in self.get_dependents(task_id):
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    queue.append(dependent)
        
        if len(result) != len(self.tasks):
            missing = set(self.tasks.keys()) - set(result)
            result.extend(missing)
        
        return result
    
    def get_ready_tasks(self) -> List[Task]:
        """Get tasks that have all dependencies satisfied."""
        ready = []
        for task in self.tasks.values():
            if task.status in [TaskState.PENDING.value, TaskState.READY.value]:
                deps_satisfied = all(
                    self.tasks[dep].status == TaskState.COMPLETED.value
                    for dep in task.dependencies
                )
                if deps_satisfied or not task.dependencies:
                    ready.append(task)
        return ready
    
    def has_cycle(self) -> bool:
        """Check if the graph has cycles."""
        sorted_tasks = self.topological_sort()
        return len(sorted_tasks) != len(self.tasks)
    
    def to_dict(self) -> Dict:
        """Convert graph to dictionary."""
        return {
            'tasks': {tid: task.to_dict() for tid, task in self.tasks.items()},
            'dependencies': self.dependency_graph
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'TaskGraph':
        """Create graph from dictionary."""
        graph = cls()
        for tid, task_data in data.get('tasks', {}).items():
            task = Task.from_dict(task_data)
            graph.add_task(task)
        return graph
    
    def __len__(self) -> int:
        return len(self.tasks)
    
    def __contains__(self, task_id: str) -> bool:
        return task_id in self.tasks
