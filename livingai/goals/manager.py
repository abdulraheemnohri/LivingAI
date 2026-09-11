# LivingAI Goal Manager
# =====================
# This module manages goals for the LivingAI system.

import logging
import time
from typing import Dict, Any, Optional, List
from enum import Enum

# Local imports
from ..config import ConfigManager
from ..memory.manager import MemoryManager
from ..security.audit import AuditLogger


class GoalStatus(Enum):
    """Status of a goal."""
    PLANNED = "planned"       # Goal has been created but not started
    ACTIVE = "active"         # Goal is currently being worked on
    PAUSED = "paused"         # Goal is temporarily paused
    BLOCKED = "blocked"       # Goal cannot be completed due to dependencies
    COMPLETED = "completed"   # Goal has been completed
    CANCELLED = "cancelled"   # Goal has been cancelled


class GoalPriority(Enum):
    """Priority levels for goals."""
    CRITICAL = "critical"     # Must be completed as soon as possible
    HIGH = "high"             # Important, should be completed soon
    MEDIUM = "medium"         # Normal priority
    LOW = "low"               # Can be completed when convenient


class GoalManager:
    """
    Manages goals for the LivingAI system.
    
    Responsibilities:
    - CRUD operations for goals
    - Goal status management
    - Goal prioritization
    - Goal progress tracking
    - Goal statistics
    """
    
    def __init__(
        self,
        memory_manager: Optional[MemoryManager] = None,
        config: Optional[ConfigManager] = None,
        audit_logger: Optional[AuditLogger] = None
    ):
        """
        Initialize the GoalManager.
        
        Args:
            memory_manager: Memory manager for storing goals.
            config: Configuration manager.
            audit_logger: Audit logger for tracking actions.
        """
        self.memory_manager = memory_manager
        self.config = config
        self.audit_logger = audit_logger
        
        # Goal storage
        self._goals: Dict[int, Dict[str, Any]] = {}
        self._next_id = 1
        
        # Goal state
        self._active_goals: List[int] = []
        self._completed_goals: List[int] = []
        
        logging.info("GoalManager initialized")
    
    def set_memory_manager(self, memory_manager: MemoryManager) -> None:
        """
        Set the memory manager (for lazy initialization).
        
        Args:
            memory_manager: Memory manager instance.
        """
        self.memory_manager = memory_manager
    
    def add(
        self,
        title: str,
        description: str = "",
        priority: str = "medium",
        due_date: Optional[float] = None,
        tags: Optional[List[str]] = None
    ) -> int:
        """
        Add a new goal.
        
        Args:
            title: Title of the goal.
            description: Description of the goal.
            priority: Priority level ("critical", "high", "medium", "low").
            due_date: Optional due date (timestamp).
            tags: Optional list of tags.
            
        Returns:
            int: ID of the created goal.
        """
        # Validate inputs
        if not title:
            raise ValueError("Goal title cannot be empty")
        
        # Convert priority to enum
        try:
            priority_enum = GoalPriority(priority.lower())
        except ValueError:
            priority_enum = GoalPriority.MEDIUM
        
        # Create goal
        goal = {
            "id": self._next_id,
            "title": title,
            "description": description,
            "status": GoalStatus.PLANNED.value,
            "priority": priority_enum.value,
            "due_date": due_date,
            "tags": tags or [],
            "created_at": time.time(),
            "updated_at": time.time(),
            "started_at": None,
            "completed_at": None,
            "progress": 0.0,
            "tasks": [],
        }
        
        # Store the goal
        self._goals[self._next_id] = goal
        self._next_id += 1
        
        # Store in memory if available
        if self.memory_manager:
            memory_data = {
                "content": f"Goal: {title}\nDescription: {description}",
                "type": "goal",
                "importance": self._priority_to_importance(priority_enum),
                "relevance": 0.8,
                "recency": 1.0,
                "confidence": 0.8,
                "metadata": {
                    "goal_id": goal["id"],
                    "status": goal["status"],
                    "priority": goal["priority"],
                },
            }
            self.memory_manager.add(memory_data)
        
        self.audit_logger.log(
            "GOAL_ADD",
            f"Added goal {goal['id']}: {title}"
        )
        
        return goal["id"]
    
    def _priority_to_importance(self, priority: GoalPriority) -> str:
        """
        Convert goal priority to memory importance.
        
        Args:
            priority: Goal priority.
            
        Returns:
            str: Memory importance level.
        """
        priority_map = {
            GoalPriority.CRITICAL: "critical",
            GoalPriority.HIGH: "high",
            GoalPriority.MEDIUM: "medium",
            GoalPriority.LOW: "low",
        }
        return priority_map.get(priority, "medium")
    
    def get(self, goal_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a goal by ID.
        
        Args:
            goal_id: ID of the goal to retrieve.
            
        Returns:
            Optional[Dict[str, Any]]: The goal, or None if not found.
        """
        return self._goals.get(goal_id)
    
    def update(
        self,
        goal_id: int,
        updates: Dict[str, Any]
    ) -> bool:
        """
        Update a goal.
        
        Args:
            goal_id: ID of the goal to update.
            updates: Dictionary of updates to apply.
            
        Returns:
            bool: True if update succeeded, False otherwise.
        """
        if goal_id not in self._goals:
            return False
        
        goal = self._goals[goal_id]
        
        # Apply updates
        for key, value in updates.items():
            if key in goal:
                goal[key] = value
        
        # Update timestamp
        goal["updated_at"] = time.time()
        
        # Update memory if available
        if self.memory_manager and "status" in updates:
            memory_data = {
                "content": f"Goal Update: {goal['title']}\nStatus: {goal['status']}",
                "type": "goal_update",
                "importance": self._priority_to_importance(GoalPriority(goal["priority"])),
                "relevance": 0.8,
                "recency": 1.0,
                "confidence": 0.8,
                "metadata": {
                    "goal_id": goal_id,
                    "status": goal["status"],
                },
            }
            self.memory_manager.add(memory_data)
        
        self.audit_logger.log(
            "GOAL_UPDATE",
            f"Updated goal {goal_id}"
        )
        
        return True
    
    def delete(self, goal_id: int) -> bool:
        """
        Delete a goal.
        
        Args:
            goal_id: ID of the goal to delete.
            
        Returns:
            bool: True if deletion succeeded, False otherwise.
        """
        if goal_id not in self._goals:
            return False
        
        # Remove from active/completed lists
        if goal_id in self._active_goals:
            self._active_goals.remove(goal_id)
        if goal_id in self._completed_goals:
            self._completed_goals.remove(goal_id)
        
        # Delete the goal
        del self._goals[goal_id]
        
        self.audit_logger.log(
            "GOAL_DELETE",
            f"Deleted goal {goal_id}"
        )
        
        return True
    
    def list(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List all goals, optionally filtered by status.
        
        Args:
            status: Optional status filter.
            
        Returns:
            List[Dict[str, Any]]: List of goals.
        """
        goals = list(self._goals.values())
        
        # Filter by status if specified
        if status:
            goals = [g for g in goals if g.get("status") == status]
        
        # Sort by priority (highest first) and then by created_at (newest first)
        priority_order = {
            "critical": 4,
            "high": 3,
            "medium": 2,
            "low": 1,
        }
        
        goals.sort(
            key=lambda x: (
                -priority_order.get(x.get("priority", "medium"), 0),
                -x.get("created_at", 0)
            )
        )
        
        return goals
    
    def start(self, goal_id: int) -> bool:
        """
        Start working on a goal.
        
        Args:
            goal_id: ID of the goal to start.
            
        Returns:
            bool: True if start succeeded, False otherwise.
        """
        if goal_id not in self._goals:
            return False
        
        goal = self._goals[goal_id]
        
        # Check if goal can be started
        if goal["status"] not in [GoalStatus.PLANNED.value, GoalStatus.PAUSED.value]:
            return False
        
        # Update goal
        goal["status"] = GoalStatus.ACTIVE.value
        goal["started_at"] = time.time()
        goal["updated_at"] = time.time()
        
        # Add to active goals
        if goal_id not in self._active_goals:
            self._active_goals.append(goal_id)
        
        self.audit_logger.log(
            "GOAL_START",
            f"Started goal {goal_id}"
        )
        
        return True
    
    def pause(self, goal_id: int) -> bool:
        """
        Pause a goal.
        
        Args:
            goal_id: ID of the goal to pause.
            
        Returns:
            bool: True if pause succeeded, False otherwise.
        """
        if goal_id not in self._goals:
            return False
        
        goal = self._goals[goal_id]
        
        # Check if goal can be paused
        if goal["status"] != GoalStatus.ACTIVE.value:
            return False
        
        # Update goal
        goal["status"] = GoalStatus.PAUSED.value
        goal["updated_at"] = time.time()
        
        # Remove from active goals
        if goal_id in self._active_goals:
            self._active_goals.remove(goal_id)
        
        self.audit_logger.log(
            "GOAL_PAUSE",
            f"Paused goal {goal_id}"
        )
        
        return True
    
    def complete(self, goal_id: int) -> bool:
        """
        Mark a goal as completed.
        
        Args:
            goal_id: ID of the goal to complete.
            
        Returns:
            bool: True if completion succeeded, False otherwise.
        """
        if goal_id not in self._goals:
            return False
        
        goal = self._goals[goal_id]
        
        # Check if goal can be completed
        if goal["status"] not in [GoalStatus.ACTIVE.value, GoalStatus.PAUSED.value]:
            return False
        
        # Update goal
        goal["status"] = GoalStatus.COMPLETED.value
        goal["completed_at"] = time.time()
        goal["updated_at"] = time.time()
        goal["progress"] = 1.0
        
        # Remove from active goals
        if goal_id in self._active_goals:
            self._active_goals.remove(goal_id)
        
        # Add to completed goals
        if goal_id not in self._completed_goals:
            self._completed_goals.append(goal_id)
        
        # Store in memory if available
        if self.memory_manager:
            memory_data = {
                "content": f"Goal Completed: {goal['title']}\nProgress: 100%",
                "type": "goal_completion",
                "importance": self._priority_to_importance(GoalPriority(goal["priority"])),
                "relevance": 0.9,
                "recency": 1.0,
                "confidence": 0.9,
                "metadata": {
                    "goal_id": goal_id,
                    "status": goal["status"],
                },
            }
            self.memory_manager.add(memory_data)
        
        self.audit_logger.log(
            "GOAL_COMPLETE",
            f"Completed goal {goal_id}"
        )
        
        return True
    
    def cancel(self, goal_id: int) -> bool:
        """
        Cancel a goal.
        
        Args:
            goal_id: ID of the goal to cancel.
            
        Returns:
            bool: True if cancellation succeeded, False otherwise.
        """
        if goal_id not in self._goals:
            return False
        
        goal = self._goals[goal_id]
        
        # Check if goal can be cancelled
        if goal["status"] in [GoalStatus.COMPLETED.value, GoalStatus.CANCELLED.value]:
            return False
        
        # Update goal
        goal["status"] = GoalStatus.CANCELLED.value
        goal["updated_at"] = time.time()
        
        # Remove from active goals
        if goal_id in self._active_goals:
            self._active_goals.remove(goal_id)
        
        self.audit_logger.log(
            "GOAL_CANCEL",
            f"Cancelled goal {goal_id}"
        )
        
        return True
    
    def get_active_goals(self) -> List[Dict[str, Any]]:
        """
        Get all active goals.
        
        Returns:
            List[Dict[str, Any]]: List of active goals.
        """
        return [self._goals[gid] for gid in self._active_goals]
    
    def get_completed_goals(self) -> List[Dict[str, Any]]:
        """
        Get all completed goals.
        
        Returns:
            List[Dict[str, Any]]: List of completed goals.
        """
        return [self._goals[gid] for gid in self._completed_goals]
    
    def get_goal_count(self) -> Dict[str, int]:
        """
        Get the count of goals by status.
        
        Returns:
            Dict[str, int]: Count of goals by status.
        """
        counts = {
            "total": len(self._goals),
            "planned": 0,
            "active": len(self._active_goals),
            "paused": 0,
            "blocked": 0,
            "completed": len(self._completed_goals),
            "cancelled": 0,
        }
        
        for goal in self._goals.values():
            status = goal.get("status", "planned")
            if status in counts:
                counts[status] += 1
        
        return counts
    
    def update_progress(self, goal_id: int, progress: float) -> bool:
        """
        Update the progress of a goal.
        
        Args:
            goal_id: ID of the goal to update.
            progress: Progress value (0.0 to 1.0).
            
        Returns:
            bool: True if update succeeded, False otherwise.
        """
        if goal_id not in self._goals:
            return False
        
        goal = self._goals[goal_id]
        
        # Clamp progress between 0 and 1
        progress = max(0.0, min(1.0, progress))
        
        # Update goal
        goal["progress"] = progress
        goal["updated_at"] = time.time()
        
        # If progress is 100%, mark as completed
        if progress >= 1.0 and goal["status"] == GoalStatus.ACTIVE.value:
            self.complete(goal_id)
        
        self.audit_logger.log(
            "GOAL_PROGRESS",
            f"Updated progress for goal {goal_id} to {progress:.1%}"
        )
        
        return True
    
    def add_task(
        self,
        goal_id: int,
        task: Dict[str, Any]
    ) -> bool:
        """
        Add a task to a goal.
        
        Args:
            goal_id: ID of the goal to add the task to.
            task: Task to add.
            
        Returns:
            bool: True if task was added, False otherwise.
        """
        if goal_id not in self._goals:
            return False
        
        goal = self._goals[goal_id]
        
        # Add task ID if not present
        if "id" not in task:
            task["id"] = len(goal["tasks"]) + 1
        
        # Add default values
        task.setdefault("status", "pending")
        task.setdefault("created_at", time.time())
        
        # Add to goal
        goal["tasks"].append(task)
        goal["updated_at"] = time.time()
        
        self.audit_logger.log(
            "GOAL_TASK_ADD",
            f"Added task to goal {goal_id}"
        )
        
        return True
    
    def update_task(
        self,
        goal_id: int,
        task_id: int,
        updates: Dict[str, Any]
    ) -> bool:
        """
        Update a task in a goal.
        
        Args:
            goal_id: ID of the goal containing the task.
            task_id: ID of the task to update.
            updates: Dictionary of updates to apply.
            
        Returns:
            bool: True if update succeeded, False otherwise.
        """
        if goal_id not in self._goals:
            return False
        
        goal = self._goals[goal_id]
        
        # Find the task
        task = None
        for t in goal["tasks"]:
            if t.get("id") == task_id:
                task = t
                break
        
        if not task:
            return False
        
        # Apply updates
        for key, value in updates.items():
            if key in task:
                task[key] = value
        
        task["updated_at"] = time.time()
        goal["updated_at"] = time.time()
        
        self.audit_logger.log(
            "GOAL_TASK_UPDATE",
            f"Updated task {task_id} in goal {goal_id}"
        )
        
        return True
    
    def get_tasks(self, goal_id: int) -> List[Dict[str, Any]]:
        """
        Get all tasks for a goal.
        
        Args:
            goal_id: ID of the goal.
            
        Returns:
            List[Dict[str, Any]]: List of tasks.
        """
        if goal_id not in self._goals:
            return []
        
        return self._goals[goal_id].get("tasks", [])
    
    def get_next_task(self, goal_id: int) -> Optional[Dict[str, Any]]:
        """
        Get the next pending task for a goal.
        
        Args:
            goal_id: ID of the goal.
            
        Returns:
            Optional[Dict[str, Any]]: Next pending task, or None if none.
        """
        tasks = self.get_tasks(goal_id)
        
        for task in tasks:
            if task.get("status") == "pending":
                return task
        
        return None
    
    def get_goal_stats(self, goal_id: int) -> Dict[str, Any]:
        """
        Get statistics for a goal.
        
        Args:
            goal_id: ID of the goal.
            
        Returns:
            Dict[str, Any]: Goal statistics.
        """
        if goal_id not in self._goals:
            return {}
        
        goal = self._goals[goal_id]
        tasks = goal.get("tasks", [])
        
        total_tasks = len(tasks)
        completed_tasks = sum(1 for t in tasks if t.get("status") == "completed")
        pending_tasks = sum(1 for t in tasks if t.get("status") == "pending")
        
        return {
            "id": goal_id,
            "title": goal.get("title", ""),
            "status": goal.get("status", ""),
            "priority": goal.get("priority", ""),
            "progress": goal.get("progress", 0.0),
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "pending_tasks": pending_tasks,
            "created_at": goal.get("created_at", 0),
            "started_at": goal.get("started_at"),
            "completed_at": goal.get("completed_at"),
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get overall goal statistics.
        
        Returns:
            Dict[str, Any]: Goal statistics.
        """
        counts = self.get_goal_count()
        
        # Calculate average progress for active goals
        active_goals = self.get_active_goals()
        avg_progress = sum(g.get("progress", 0.0) for g in active_goals) / len(active_goals) if active_goals else 0.0
        
        return {
            **counts,
            "avg_progress": avg_progress,
            "active_goal_ids": self._active_goals,
            "completed_goal_ids": self._completed_goals,
        }
    
    def show(self, goal_id: int) -> None:
        """
        Display a goal and its details.
        
        Args:
            goal_id: ID of the goal to display.
        """
        goal = self.get(goal_id)
        
        if not goal:
            print(f"Goal {goal_id} not found")
            return
        
        print("\n" + "=" * 50)
        print(f"GOAL: {goal['title']}")
        print("=" * 50)
        print(f"ID: {goal['id']}")
        print(f"Status: {goal['status']}")
        print(f"Priority: {goal['priority']}")
        print(f"Progress: {goal['progress']:.1%}")
        print(f"Created: {time.ctime(goal['created_at'])}")
        
        if goal.get("started_at"):
            print(f"Started: {time.ctime(goal['started_at'])}")
        if goal.get("completed_at"):
            print(f"Completed: {time.ctime(goal['completed_at'])}")
        
        if goal.get("description"):
            print(f"\nDescription: {goal['description']}")
        
        if goal.get("tags"):
            print(f"\nTags: {', '.join(goal['tags'])}")
        
        # Show tasks
        tasks = goal.get("tasks", [])
        if tasks:
            print(f"\nTasks ({len(tasks)}):")
            for task in tasks:
                status = task.get("status", "pending")
                print(f"  - [{status.upper()}] {task.get('description', 'Untitled')}")
        
        print("=" * 50 + "\n")
