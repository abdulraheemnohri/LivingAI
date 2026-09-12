"""
LivingAI Task Planner
====================

Plans tasks and actions for agents.
"""

import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field

from .manager import Task, Goal, AgentManager


@dataclass
class PlannedAction:
    """Represents a planned action."""
    action_type: str  # 'tool', 'wait', 'learn'
    tool_name: Optional[str] = None
    method: Optional[str] = None
    args: Dict[str, Any] = field(default_factory=dict)
    kwargs: Dict[str, Any] = field(default_factory=dict)
    description: str = ""
    priority: int = 0


class TaskPlanner:
    """
    Plans actions for tasks and goals.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def plan_for_task(self, task: Task) -> List[PlannedAction]:
        """
        Create a plan for a task.
        
        Args:
            task: The task to plan for
            
        Returns:
            List of planned actions
        """
        actions = []
        
        # Parse the task description to determine actions
        description = task.description.lower()
        
        if 'search' in description or 'find' in description:
            actions.append(PlannedAction(
                action_type='tool',
                tool_name='file_inspector',
                method='inspect',
                description=f"Search for files related to: {task.description}",
                priority=10
            ))
        elif 'list' in description or 'show' in description:
            actions.append(PlannedAction(
                action_type='tool',
                tool_name='filesystem',
                method='list',
                description=f"List items: {task.description}",
                priority=10
            ))
        elif 'calculate' in description or 'math' in description:
            actions.append(PlannedAction(
                action_type='tool',
                tool_name='calculator',
                method='calculate',
                description=f"Calculate: {task.description}",
                priority=10
            ))
        elif 'memory' in description or 'remember' in description:
            actions.append(PlannedAction(
                action_type='tool',
                tool_name='memory',
                method='add',
                description=f"Remember: {task.description}",
                priority=10
            ))
        else:
            # Default: try to use text_processor
            actions.append(PlannedAction(
                action_type='tool',
                tool_name='text_processor',
                method='extract',
                description=f"Process: {task.description}",
                priority=5
            ))
        
        self.logger.info(f"Planned {len(actions)} actions for task: {task.id}")
        return actions
    
    def plan_for_goal(self, goal: Goal) -> List[PlannedAction]:
        """
        Create a plan for a goal.
        
        Args:
            goal: The goal to plan for
            
        Returns:
            List of planned actions
        """
        actions = []
        
        # Break down the goal into subtasks
        description = goal.description.lower()
        
        if 'build' in description or 'create' in description:
            actions.append(PlannedAction(
                action_type='tool',
                tool_name='filesystem',
                method='write',
                description=f"Build: {goal.description}",
                priority=10
            ))
        elif 'analyze' in description or 'check' in description:
            actions.append(PlannedAction(
                action_type='tool',
                tool_name='file_inspector',
                method='inspect',
                description=f"Analyze: {goal.description}",
                priority=10
            ))
        elif 'learn' in description or 'study' in description:
            actions.append(PlannedAction(
                action_type='learn',
                description=f"Learn: {goal.description}",
                priority=10
            ))
        else:
            # Default: use text_processor
            actions.append(PlannedAction(
                action_type='tool',
                tool_name='text_processor',
                method='extract',
                description=f"Process goal: {goal.description}",
                priority=5
            ))
        
        self.logger.info(f"Planned {len(actions)} actions for goal: {goal.id}")
        return actions
