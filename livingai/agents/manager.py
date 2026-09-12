"""
LivingAI Agent Manager
=====================

Manages agents and their lifecycle.
"""

import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum


class AgentStatus(Enum):
    IDLE = "idle"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ERROR = "error"


@dataclass
class Agent:
    """Represents an AI agent."""
    id: str
    name: str
    description: str = ""
    status: AgentStatus = AgentStatus.IDLE
    config: Dict[str, Any] = field(default_factory=dict)
    current_task: Optional[str] = None
    tasks_completed: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'status': self.status.value,
            'config': self.config,
            'current_task': self.current_task,
            'tasks_completed': self.tasks_completed
        }


@dataclass
class Task:
    """Represents a task for an agent."""
    id: str
    description: str
    agent_id: Optional[str] = None
    status: str = "pending"
    priority: int = 0
    completed: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'description': self.description,
            'agent_id': self.agent_id,
            'status': self.status,
            'priority': self.priority,
            'completed': self.completed
        }


@dataclass
class Goal:
    """Represents a goal for an agent."""
    id: str
    description: str
    agent_id: Optional[str] = None
    status: str = "pending"
    priority: int = 0
    completed: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'description': self.description,
            'agent_id': self.agent_id,
            'status': self.status,
            'priority': self.priority,
            'completed': self.completed
        }


class AgentManager:
    """
    Manages AI agents and their tasks/goals.
    """
    
    def __init__(self):
        self._agents: Dict[str, Agent] = {}
        self._tasks: Dict[str, Task] = {}
        self._goals: Dict[str, Goal] = {}
        self._active_task: Optional[str] = None
        self._active_goal: Optional[str] = None
        self.logger = logging.getLogger(__name__)
        self._next_id = 1
    
    def create_agent(
        self,
        name: str,
        description: str = "",
        config: Dict[str, Any] = None
    ) -> Agent:
        """Create a new agent."""
        agent_id = f"agent_{self._next_id}"
        self._next_id += 1
        
        agent = Agent(
            id=agent_id,
            name=name,
            description=description,
            config=config or {}
        )
        self._agents[agent_id] = agent
        self.logger.info(f"Created agent: {agent_id}")
        return agent
    
    def get_agent(self, agent_id: str) -> Optional[Agent]:
        """Get an agent by ID."""
        return self._agents.get(agent_id)
    
    def list_agents(self) -> List[str]:
        """List all agent IDs."""
        return list(self._agents.keys())
    
    def update_agent_status(self, agent_id: str, status: AgentStatus) -> bool:
        """Update an agent's status."""
        agent = self._agents.get(agent_id)
        if agent:
            agent.status = status
            self.logger.info(f"Updated agent {agent_id} status to {status.value}")
            return True
        return False
    
    def create_task(
        self,
        description: str,
        agent_id: Optional[str] = None,
        priority: int = 0
    ) -> Task:
        """Create a new task."""
        task_id = f"task_{self._next_id}"
        self._next_id += 1
        
        task = Task(
            id=task_id,
            description=description,
            agent_id=agent_id,
            priority=priority
        )
        self._tasks[task_id] = task
        self.logger.info(f"Created task: {task_id}")
        return task
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """Get a task by ID."""
        return self._tasks.get(task_id)
    
    def list_tasks(self) -> List[str]:
        """List all task IDs."""
        return list(self._tasks.keys())
    
    def get_pending_tasks(self) -> List[Task]:
        """Get all pending tasks."""
        return [task for task in self._tasks.values() if task.status == "pending"]
    
    def get_active_task(self) -> Optional[Task]:
        """Get the currently active task."""
        if self._active_task:
            return self._tasks.get(self._active_task)
        return None
    
    def activate_task(self, task_id: str) -> bool:
        """Activate a task."""
        if task_id in self._tasks:
            self._active_task = task_id
            self._tasks[task_id].status = "active"
            self.logger.info(f"Activated task: {task_id}")
            return True
        return False
    
    def update_task_status(self, task_id: str, status: str) -> bool:
        """Update a task's status."""
        task = self._tasks.get(task_id)
        if task:
            task.status = status
            if status == "completed":
                task.completed = True
            self.logger.info(f"Updated task {task_id} status to {status}")
            return True
        return False
    
    def complete_task(self, task_id: str) -> bool:
        """Mark a task as completed."""
        return self.update_task_status(task_id, "completed")
    
    def create_goal(
        self,
        description: str,
        agent_id: Optional[str] = None,
        priority: int = 0
    ) -> Goal:
        """Create a new goal."""
        goal_id = f"goal_{self._next_id}"
        self._next_id += 1
        
        goal = Goal(
            id=goal_id,
            description=description,
            agent_id=agent_id,
            priority=priority
        )
        self._goals[goal_id] = goal
        self.logger.info(f"Created goal: {goal_id}")
        return goal
    
    def get_goal(self, goal_id: str) -> Optional[Goal]:
        """Get a goal by ID."""
        return self._goals.get(goal_id)
    
    def list_goals(self) -> List[str]:
        """List all goal IDs."""
        return list(self._goals.keys())
    
    def get_pending_goals(self) -> List[Goal]:
        """Get all pending goals."""
        return [goal for goal in self._goals.values() if goal.status == "pending"]
    
    def get_active_goal(self) -> Optional[Goal]:
        """Get the currently active goal."""
        if self._active_goal:
            return self._goals.get(self._active_goal)
        return None
    
    def activate_goal(self, goal_id: str) -> bool:
        """Activate a goal."""
        if goal_id in self._goals:
            self._active_goal = goal_id
            self._goals[goal_id].status = "active"
            self.logger.info(f"Activated goal: {goal_id}")
            return True
        return False
    
    def update_goal_status(self, goal_id: str, status: str) -> bool:
        """Update a goal's status."""
        goal = self._goals.get(goal_id)
        if goal:
            goal.status = status
            if status == "completed":
                goal.completed = True
            self.logger.info(f"Updated goal {goal_id} status to {status}")
            return True
        return False
    
    def complete_goal(self, goal_id: str) -> bool:
        """Mark a goal as completed."""
        return self.update_goal_status(goal_id, "completed")
