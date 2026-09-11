# LivingAI Goal Planner
# ======================
# This module handles planning for goals in the LivingAI system.

import logging
import time
from typing import Dict, Any, Optional, List

# Local imports
from .manager import GoalManager, GoalStatus, GoalPriority
from ..config import ConfigManager
from ..memory.manager import MemoryManager
from ..security.audit import AuditLogger


class GoalPlanner:
    """
    Handles planning for goals in the LivingAI system.
    
    Responsibilities:
    - Create plans for goals
    - Break down goals into tasks
    - Manage task dependencies
    - Estimate task durations
    - Optimize plans
    """
    
    def __init__(
        self,
        goal_manager: GoalManager,
        config: Optional[ConfigManager] = None,
        audit_logger: Optional[AuditLogger] = None
    ):
        """
        Initialize the GoalPlanner.
        
        Args:
            goal_manager: Goal manager for managing goals.
            config: Configuration manager.
            audit_logger: Audit logger for tracking actions.
        """
        self.goal_manager = goal_manager
        self.config = config
        self.audit_logger = audit_logger
        
        # Planning state
        self._planning_history: List[Dict[str, Any]] = []
        
        logging.info("GoalPlanner initialized")
    
    def create_plan(
        self,
        goal_id: int,
        strategy: str = "default"
    ) -> Dict[str, Any]:
        """
        Create a plan for a goal.
        
        Args:
            goal_id: ID of the goal to plan for.
            strategy: Planning strategy to use.
            
        Returns:
            Dict[str, Any]: The created plan.
        """
        self.audit_logger.log(
            "GOAL_PLAN_START",
            f"Creating plan for goal {goal_id} with strategy {strategy}"
        )
        start_time = time.time()
        
        try:
            # Get the goal
            goal = self.goal_manager.get(goal_id)
            if not goal:
                return {"error": f"Goal {goal_id} not found"}
            
            # Select planning strategy
            if strategy == "simple":
                plan = self._create_simple_plan(goal)
            elif strategy == "detailed":
                plan = self._create_detailed_plan(goal)
            elif strategy == "recursive":
                plan = self._create_recursive_plan(goal)
            else:
                plan = self._create_default_plan(goal)
            
            # Add tasks to the goal
            for task in plan.get("tasks", []):
                self.goal_manager.add_task(goal_id, task)
            
            # Update goal progress
            self.goal_manager.update(goal_id, {
                "progress": 0.0,
                "status": GoalStatus.PLANNED.value,
            })
            
            # Record the plan
            plan["goal_id"] = goal_id
            plan["created_at"] = time.time()
            plan["duration"] = time.time() - start_time
            
            self._planning_history.append(plan)
            
            self.audit_logger.log(
                "GOAL_PLAN_SUCCESS",
                f"Created plan for goal {goal_id} with {len(plan.get('tasks', []))} tasks"
            )
            
            return plan
            
        except Exception as e:
            self.audit_logger.log("GOAL_PLAN_FAIL", str(e))
            logging.error(f"Failed to create plan for goal {goal_id}: {e}")
            return {"error": str(e)}
    
    def _create_simple_plan(self, goal: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a simple plan for a goal.
        
        Args:
            goal: The goal to plan for.
            
        Returns:
            Dict[str, Any]: The simple plan.
        """
        title = goal.get("title", "").lower()
        description = goal.get("description", "").lower()
        
        # Create a basic task based on the goal
        task = {
            "id": 1,
            "description": f"Complete: {goal.get('title', 'Untitled')}",
            "status": "pending",
            "priority": goal.get("priority", "medium"),
            "estimated_duration": self._estimate_duration(goal),
            "dependencies": [],
        }
        
        return {
            "strategy": "simple",
            "tasks": [task],
            "total_estimated_duration": task["estimated_duration"],
        }
    
    def _create_detailed_plan(self, goal: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a detailed plan for a goal.
        
        Args:
            goal: The goal to plan for.
            
        Returns:
            Dict[str, Any]: The detailed plan.
        """
        title = goal.get("title", "").lower()
        description = goal.get("description", "").lower()
        
        tasks = []
        total_duration = 0.0
        
        # Analyze the goal and create appropriate tasks
        if any(word in title or word in description for word in ["report", "document", "write"]):
            tasks = self._create_writing_plan(goal)
        elif any(word in title or word in description for word in ["learn", "study", "understand"]):
            tasks = self._create_learning_plan(goal)
        elif any(word in title or word in description for word in ["organize", "clean", "sort"]):
            tasks = self._create_organization_plan(goal)
        elif any(word in title or word in description for word in ["analyze", "review", "evaluate"]):
            tasks = self._create_analysis_plan(goal)
        else:
            tasks = self._create_generic_plan(goal)
        
        # Calculate total duration
        total_duration = sum(t.get("estimated_duration", 0) for t in tasks)
        
        return {
            "strategy": "detailed",
            "tasks": tasks,
            "total_estimated_duration": total_duration,
        }
    
    def _create_recursive_plan(self, goal: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a recursive plan that breaks down tasks into subtasks.
        
        Args:
            goal: The goal to plan for.
            
        Returns:
            Dict[str, Any]: The recursive plan.
        """
        # First create a detailed plan
        detailed_plan = self._create_detailed_plan(goal)
        
        # Then break down each task into subtasks
        refined_tasks = []
        total_duration = 0.0
        
        for task in detailed_plan.get("tasks", []):
            # Break down the task
            subtasks = self._break_down_task(task)
            
            # Add the main task with subtasks
            main_task = {
                **task,
                "subtasks": subtasks,
            }
            refined_tasks.append(main_task)
            
            # Add subtask durations to total
            task_duration = task.get("estimated_duration", 0)
            subtask_duration = sum(st.get("estimated_duration", 0) for st in subtasks)
            total_duration += max(task_duration, subtask_duration)
        
        return {
            "strategy": "recursive",
            "tasks": refined_tasks,
            "total_estimated_duration": total_duration,
        }
    
    def _create_default_plan(self, goal: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a default plan for a goal.
        
        Args:
            goal: The goal to plan for.
            
        Returns:
            Dict[str, Any]: The default plan.
        """
        # Use the simple plan as default
        return self._create_simple_plan(goal)
    
    def _create_writing_plan(self, goal: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Create a plan for a writing goal.
        
        Args:
            goal: The goal to plan for.
            
        Returns:
            List[Dict[str, Any]]: List of tasks for the plan.
        """
        return [
            {
                "id": 1,
                "description": "Outline the content",
                "status": "pending",
                "priority": "high",
                "estimated_duration": 0.5,  # 30 minutes
                "dependencies": [],
            },
            {
                "id": 2,
                "description": "Write the first draft",
                "status": "pending",
                "priority": "high",
                "estimated_duration": 1.0,  # 1 hour
                "dependencies": [1],
            },
            {
                "id": 3,
                "description": "Review and revise",
                "status": "pending",
                "priority": "medium",
                "estimated_duration": 0.5,
                "dependencies": [2],
            },
            {
                "id": 4,
                "description": "Finalize and format",
                "status": "pending",
                "priority": "medium",
                "estimated_duration": 0.25,
                "dependencies": [3],
            },
        ]
    
    def _create_learning_plan(self, goal: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Create a plan for a learning goal.
        
        Args:
            goal: The goal to plan for.
            
        Returns:
            List[Dict[str, Any]]: List of tasks for the plan.
        """
        return [
            {
                "id": 1,
                "description": "Identify learning resources",
                "status": "pending",
                "priority": "high",
                "estimated_duration": 0.25,
                "dependencies": [],
            },
            {
                "id": 2,
                "description": "Study the material",
                "status": "pending",
                "priority": "high",
                "estimated_duration": 1.0,
                "dependencies": [1],
            },
            {
                "id": 3,
                "description": "Take notes on key concepts",
                "status": "pending",
                "priority": "medium",
                "estimated_duration": 0.5,
                "dependencies": [2],
            },
            {
                "id": 4,
                "description": "Practice with exercises",
                "status": "pending",
                "priority": "medium",
                "estimated_duration": 0.5,
                "dependencies": [2],
            },
            {
                "id": 5,
                "description": "Review and test understanding",
                "status": "pending",
                "priority": "medium",
                "estimated_duration": 0.25,
                "dependencies": [3, 4],
            },
        ]
    
    def _create_organization_plan(self, goal: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Create a plan for an organization goal.
        
        Args:
            goal: The goal to plan for.
            
        Returns:
            List[Dict[str, Any]]: List of tasks for the plan.
        """
        return [
            {
                "id": 1,
                "description": "Assess current organization",
                "status": "pending",
                "priority": "high",
                "estimated_duration": 0.25,
                "dependencies": [],
            },
            {
                "id": 2,
                "description": "Identify items to organize",
                "status": "pending",
                "priority": "high",
                "estimated_duration": 0.5,
                "dependencies": [1],
            },
            {
                "id": 3,
                "description": "Categorize items",
                "status": "pending",
                "priority": "medium",
                "estimated_duration": 0.5,
                "dependencies": [2],
            },
            {
                "id": 4,
                "description": "Create organization system",
                "status": "pending",
                "priority": "medium",
                "estimated_duration": 0.5,
                "dependencies": [3],
            },
            {
                "id": 5,
                "description": "Implement organization",
                "status": "pending",
                "priority": "medium",
                "estimated_duration": 0.5,
                "dependencies": [4],
            },
        ]
    
    def _create_analysis_plan(self, goal: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Create a plan for an analysis goal.
        
        Args:
            goal: The goal to plan for.
            
        Returns:
            List[Dict[str, Any]]: List of tasks for the plan.
        """
        return [
            {
                "id": 1,
                "description": "Gather data and information",
                "status": "pending",
                "priority": "high",
                "estimated_duration": 0.5,
                "dependencies": [],
            },
            {
                "id": 2,
                "description": "Analyze the data",
                "status": "pending",
                "priority": "high",
                "estimated_duration": 1.0,
                "dependencies": [1],
            },
            {
                "id": 3,
                "description": "Identify patterns and insights",
                "status": "pending",
                "priority": "medium",
                "estimated_duration": 0.5,
                "dependencies": [2],
            },
            {
                "id": 4,
                "description": "Document findings",
                "status": "pending",
                "priority": "medium",
                "estimated_duration": 0.25,
                "dependencies": [3],
            },
        ]
    
    def _create_generic_plan(self, goal: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Create a generic plan for a goal.
        
        Args:
            goal: The goal to plan for.
            
        Returns:
            List[Dict[str, Any]]: List of tasks for the plan.
        """
        return [
            {
                "id": 1,
                "description": "Understand the goal requirements",
                "status": "pending",
                "priority": "high",
                "estimated_duration": 0.25,
                "dependencies": [],
            },
            {
                "id": 2,
                "description": "Identify required actions",
                "status": "pending",
                "priority": "high",
                "estimated_duration": 0.5,
                "dependencies": [1],
            },
            {
                "id": 3,
                "description": "Execute actions",
                "status": "pending",
                "priority": "medium",
                "estimated_duration": 1.0,
                "dependencies": [2],
            },
            {
                "id": 4,
                "description": "Verify completion",
                "status": "pending",
                "priority": "medium",
                "estimated_duration": 0.25,
                "dependencies": [3],
            },
        ]
    
    def _break_down_task(self, task: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Break down a task into subtasks.
        
        Args:
            task: The task to break down.
            
        Returns:
            List[Dict[str, Any]]: List of subtasks.
        """
        description = task.get("description", "").lower()
        
        # Create subtasks based on the task description
        if any(word in description for word in ["write", "create", "develop"]):
            return [
                {
                    "id": 1,
                    "description": "Outline the content",
                    "status": "pending",
                    "priority": "high",
                    "estimated_duration": task.get("estimated_duration", 0.5) * 0.3,
                    "dependencies": [],
                },
                {
                    "id": 2,
                    "description": "Create initial version",
                    "status": "pending",
                    "priority": "high",
                    "estimated_duration": task.get("estimated_duration", 0.5) * 0.5,
                    "dependencies": [1],
                },
                {
                    "id": 3,
                    "description": "Review and refine",
                    "status": "pending",
                    "priority": "medium",
                    "estimated_duration": task.get("estimated_duration", 0.5) * 0.2,
                    "dependencies": [2],
                },
            ]
        elif any(word in description for word in ["analyze", "review", "evaluate"]):
            return [
                {
                    "id": 1,
                    "description": "Gather information",
                    "status": "pending",
                    "priority": "high",
                    "estimated_duration": task.get("estimated_duration", 0.5) * 0.4,
                    "dependencies": [],
                },
                {
                    "id": 2,
                    "description": "Perform analysis",
                    "status": "pending",
                    "priority": "high",
                    "estimated_duration": task.get("estimated_duration", 0.5) * 0.4,
                    "dependencies": [1],
                },
                {
                    "id": 3,
                    "description": "Document findings",
                    "status": "pending",
                    "priority": "medium",
                    "estimated_duration": task.get("estimated_duration", 0.5) * 0.2,
                    "dependencies": [2],
                },
            ]
        else:
            # Default: split into two subtasks
            return [
                {
                    "id": 1,
                    "description": f"Start {task.get('description', 'task')}",
                    "status": "pending",
                    "priority": task.get("priority", "medium"),
                    "estimated_duration": task.get("estimated_duration", 0.5) * 0.6,
                    "dependencies": [],
                },
                {
                    "id": 2,
                    "description": f"Complete {task.get('description', 'task')}",
                    "status": "pending",
                    "priority": task.get("priority", "medium"),
                    "estimated_duration": task.get("estimated_duration", 0.5) * 0.4,
                    "dependencies": [1],
                },
            ]
    
    def _estimate_duration(self, goal: Dict[str, Any]) -> float:
        """
        Estimate the duration for a goal.
        
        Args:
            goal: The goal to estimate duration for.
            
        Returns:
            float: Estimated duration in hours.
        """
        # Base estimation based on priority
        priority = goal.get("priority", "medium")
        
        if priority == "critical":
            return 2.0  # 2 hours
        elif priority == "high":
            return 1.0  # 1 hour
        elif priority == "medium":
            return 0.5  # 30 minutes
        else:
            return 0.25  # 15 minutes
    
    def optimize_plan(self, goal_id: int) -> Dict[str, Any]:
        """
        Optimize the plan for a goal.
        
        Args:
            goal_id: ID of the goal to optimize.
            
        Returns:
            Dict[str, Any]: Optimization results.
        """
        # Get the goal
        goal = self.goal_manager.get(goal_id)
        if not goal:
            return {"error": f"Goal {goal_id} not found"}
        
        # Get current tasks
        tasks = goal.get("tasks", [])
        
        # Simple optimization: reorder tasks by priority and dependencies
        optimized_tasks = self._optimize_tasks(tasks)
        
        # Update the goal with optimized tasks
        # Clear existing tasks
        goal["tasks"] = []
        
        # Add optimized tasks
        for task in optimized_tasks:
            self.goal_manager.add_task(goal_id, task)
        
        return {
            "goal_id": goal_id,
            "original_tasks": len(tasks),
            "optimized_tasks": len(optimized_tasks),
            "optimizations_applied": ["priority_ordering", "dependency_resolution"],
        }
    
    def _optimize_tasks(self, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Optimize a list of tasks.
        
        Args:
            tasks: List of tasks to optimize.
            
        Returns:
            List[Dict[str, Any]]: Optimized list of tasks.
        """
        # Priority order
        priority_order = {
            "critical": 4,
            "high": 3,
            "medium": 2,
            "low": 1,
        }
        
        # Sort by priority (highest first) and then by dependencies
        optimized = sorted(
            tasks,
            key=lambda x: (
                -priority_order.get(x.get("priority", "medium"), 0),
                len(x.get("dependencies", [])),
            )
        )
        
        # Resolve dependencies (topological sort)
        return self._topological_sort(optimized)
    
    def _topological_sort(self, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Perform a topological sort on tasks based on dependencies.
        
        Args:
            tasks: List of tasks with dependencies.
            
        Returns:
            List[Dict[str, Any]]: Topologically sorted tasks.
        """
        # Create a mapping from task ID to task
        task_map = {t["id"]: t for t in tasks}
        
        # Create adjacency list
        graph = {t["id"]: [] for t in tasks}
        in_degree = {t["id"]: 0 for t in tasks}
        
        for task in tasks:
            for dep_id in task.get("dependencies", []):
                if dep_id in graph:
                    graph[dep_id].append(task["id"])
                    in_degree[task["id"]] += 1
        
        # Kahn's algorithm for topological sort
        queue = []
        for task_id, degree in in_degree.items():
            if degree == 0:
                queue.append(task_id)
        
        sorted_tasks = []
        
        while queue:
            task_id = queue.pop(0)
            sorted_tasks.append(task_map[task_id])
            
            for neighbor_id in graph[task_id]:
                in_degree[neighbor_id] -= 1
                if in_degree[neighbor_id] == 0:
                    queue.append(neighbor_id)
        
        # Check for cycles
        if len(sorted_tasks) != len(tasks):
            logging.warning("Cycle detected in task dependencies")
            # Fall back to original order
            return tasks
        
        return sorted_tasks
    
    def get_planning_history(self) -> List[Dict[str, Any]]:
        """
        Get the history of planning operations.
        
        Returns:
            List[Dict[str, Any]]: Planning history.
        """
        return self._planning_history.copy()
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get planning statistics.
        
        Returns:
            Dict[str, Any]: Planning statistics.
        """
        if not self._planning_history:
            return {
                "total_plans": 0,
                "total_tasks": 0,
                "avg_tasks_per_plan": 0.0,
            }
        
        total_plans = len(self._planning_history)
        total_tasks = sum(len(p.get("tasks", [])) for p in self._planning_history)
        avg_tasks = total_tasks / total_plans if total_plans > 0 else 0.0
        
        return {
            "total_plans": total_plans,
            "total_tasks": total_tasks,
            "avg_tasks_per_plan": avg_tasks,
        }
    
    def clear_history(self) -> None:
        """Clear the planning history."""
        self._planning_history = []
