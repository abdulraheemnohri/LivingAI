"""
LivingAI Agentic Loop
=====================

Main agentic AI execution loop for LivingAI V1+V2.
Implements autonomous agent behavior with tool execution, memory, and learning.
"""

import logging
import time
import asyncio
from typing import Dict, Any, Optional, List, Callable, Union
from dataclasses import dataclass, field
from enum import Enum

from livingai.tools.integration import ToolsIntegration
from livingai.agents.manager import AgentManager
from livingai.agents.planner import TaskPlanner
from livingai.agents.state_machine import AgentStateMachine
from livingai.memory import MemoryManager
from livingai.learning import LearningSystem


class AgentStatus(Enum):
    IDLE = "idle"
    THINKING = "thinking"
    PLANNING = "planning"
    EXECUTING = "executing"
    LEARNING = "learning"
    WAITING = "waiting"
    ERROR = "error"


@dataclass
class AgentAction:
    """Represents an action to be taken by the agent."""
    action_type: str
    tool_name: Optional[str] = None
    method: Optional[str] = None
    args: Dict[str, Any] = field(default_factory=dict)
    kwargs: Dict[str, Any] = field(default_factory=dict)
    description: str = ""
    priority: int = 0


@dataclass
class AgentState:
    """Represents the current state of the agent."""
    status: AgentStatus
    current_task: Optional[str] = None
    current_goal: Optional[str] = None
    memory_context: Dict[str, Any] = field(default_factory=dict)
    execution_history: List[Dict[str, Any]] = field(default_factory=list)
    error: Optional[str] = None


class AgenticLoop:
    """
    Main agentic loop for LivingAI.
    
    Implements a continuous loop that:
    1. Perceives the environment and context
    2. Plans actions based on goals and context
    3. Executes actions using available tools
    4. Learns from results and updates memory
    5. Repeats autonomously
    
    Responsibilities:
    - Maintain agent state
    - Execute the agentic loop
    - Manage tool execution
    - Handle errors and recovery
    - Track agent performance
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the AgenticLoop.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.tools = ToolsIntegration(self.config)
        self.agent_manager = AgentManager()
        self.planner = TaskPlanner()
        self.state_machine = AgentStateMachine()
        self.memory = MemoryManager()
        self.learning = LearningSystem()
        
        # Agent state
        self.state = AgentState(
            status=AgentStatus.IDLE,
            memory_context={},
            execution_history=[]
        )
        
        # Loop control
        self._running = False
        self._loop_thread = None
        self._stop_event = asyncio.Event()
        
        self.logger.info("AgenticLoop initialized")
    
    async def start(self) -> None:
        """Start the agentic loop."""
        if self._running:
            self.logger.warning("Agentic loop is already running")
            return
        
        self._running = True
        self._stop_event.clear()
        self.state.status = AgentStatus.IDLE
        
        self.logger.info("Starting agentic loop")
        
        try:
            while not self._stop_event.is_set():
                await self._run_cycle()
        except Exception as e:
            self.logger.error(f"Agentic loop error: {e}")
            self.state.status = AgentStatus.ERROR
            self.state.error = str(e)
        finally:
            self._running = False
            self.logger.info("Agentic loop stopped")
    
    async def stop(self) -> None:
        """Stop the agentic loop."""
        self._stop_event.set()
        if self._loop_thread:
            await self._loop_thread
        self._running = False
    
    async def _run_cycle(self) -> None:
        """
        Run one complete cycle of the agentic loop.
        
        Cycle:
        1. Perceive - Gather information from environment
        2. Think - Process information and determine goals
        3. Plan - Create a plan of actions
        4. Act - Execute the plan
        5. Learn - Update knowledge based on results
        """
        try:
            # Step 1: Perceive
            self.state.status = AgentStatus.THINKING
            await self._perceive()
            
            # Step 2: Think
            await self._think()
            
            # Step 3: Plan
            self.state.status = AgentStatus.PLANNING
            actions = await self._plan()
            
            # Step 4: Act
            self.state.status = AgentStatus.EXECUTING
            await self._act(actions)
            
            # Step 5: Learn
            self.state.status = AgentStatus.LEARNING
            await self._learn()
            
            # Update state
            self.state.status = AgentStatus.IDLE
            
        except Exception as e:
            self.logger.error(f"Cycle error: {e}")
            self.state.status = AgentStatus.ERROR
            self.state.error = str(e)
    
    async def _perceive(self) -> None:
        """
        Gather information from the environment.
        
        This includes:
        - Current task/goal state
        - Available tools
        - Memory context
        - External inputs
        """
        self.logger.debug("Perceiving environment...")
        
        # Get current context
        self.state.memory_context = self.memory.get_context()
        
        # Check for active tasks
        active_task = self.agent_manager.get_active_task()
        if active_task:
            self.state.current_task = active_task.id
        
        # Check for active goals
        active_goal = self.agent_manager.get_active_goal()
        if active_goal:
            self.state.current_goal = active_goal.id
        
        self.logger.debug(f"Perceived: task={self.state.current_task}, goal={self.state.current_goal}")
    
    async def _think(self) -> None:
        """
        Process information and determine goals.
        
        This includes:
        - Analyzing current state
        - Determining what needs to be done
        - Setting or updating goals
        """
        self.logger.debug("Thinking...")
        
        # If we have an active goal, continue with it
        if self.state.current_goal:
            goal = self.agent_manager.get_goal(self.state.current_goal)
            if goal and not goal.completed:
                self.logger.debug(f"Continuing with goal: {goal.description}")
                return
        
        # If we have an active task, continue with it
        if self.state.current_task:
            task = self.agent_manager.get_task(self.state.current_task)
            if task and not task.completed:
                self.logger.debug(f"Continuing with task: {task.description}")
                return
        
        # No active goal or task, check for new ones
        pending_goals = self.agent_manager.get_pending_goals()
        if pending_goals:
            new_goal = pending_goals[0]
            self.agent_manager.activate_goal(new_goal.id)
            self.state.current_goal = new_goal.id
            self.logger.info(f"New goal activated: {new_goal.description}")
    
    async def _plan(self) -> List[AgentAction]:
        """
        Create a plan of actions.
        
        Returns:
            List of actions to execute
        """
        self.logger.debug("Planning actions...")
        
        actions = []
        
        # If we have an active task, plan for it
        if self.state.current_task:
            task = self.agent_manager.get_task(self.state.current_task)
            if task:
                task_actions = self.planner.plan_for_task(task)
                actions.extend(task_actions)
        
        # If we have an active goal, plan for it
        if self.state.current_goal and not actions:
            goal = self.agent_manager.get_goal(self.state.current_goal)
            if goal:
                goal_actions = self.planner.plan_for_goal(goal)
                actions.extend(goal_actions)
        
        # If no specific actions, check for general tasks
        if not actions:
            pending_tasks = self.agent_manager.get_pending_tasks()
            if pending_tasks:
                task = pending_tasks[0]
                self.agent_manager.activate_task(task.id)
                self.state.current_task = task.id
                actions = self.planner.plan_for_task(task)
        
        self.logger.debug(f"Planned {len(actions)} actions")
        return actions
    
    async def _act(self, actions: List[AgentAction]) -> None:
        """
        Execute the planned actions.
        
        Args:
            actions: List of actions to execute
        """
        if not actions:
            self.logger.debug("No actions to execute")
            return
        
        self.logger.info(f"Executing {len(actions)} actions")
        
        for action in actions:
            try:
                # Record action in history
                action_record = {
                    'timestamp': time.time(),
                    'action_type': action.action_type,
                    'tool': action.tool_name,
                    'method': action.method,
                    'description': action.description
                }
                self.state.execution_history.append(action_record)
                
                # Execute tool action
                if action.action_type == 'tool' and action.tool_name:
                    result = self.tools.execute_tool(
                        tool_name=action.tool_name,
                        method=action.method,
                        args=action.args,
                        kwargs=action.kwargs,
                        context={
                            'agent_id': 'main_agent',
                            'task_id': self.state.current_task,
                            'goal_id': self.state.current_goal
                        }
                    )
                    
                    # Store result in memory
                    if result:
                        self.memory.add_experience(
                            action_description=action.description,
                            result=result.to_dict() if hasattr(result, 'to_dict') else str(result),
                            success=result.status.value == 'COMPLETED' if hasattr(result, 'status') else True
                        )
                    
                    # Update task/goal status
                    if self.state.current_task:
                        self.agent_manager.update_task_status(
                            self.state.current_task,
                            'IN_PROGRESS'
                        )
                    if self.state.current_goal:
                        self.agent_manager.update_goal_status(
                            self.state.current_goal,
                            'IN_PROGRESS'
                        )
                
                # Handle other action types
                elif action.action_type == 'wait':
                    await asyncio.sleep(action.kwargs.get('duration', 1))
                
                elif action.action_type == 'learn':
                    await self.learning.learn_from_experience(
                        experience=action.description,
                        context=self.state.memory_context
                    )
                
            except Exception as e:
                self.logger.error(f"Action execution error: {e}")
                action_record = {
                    'timestamp': time.time(),
                    'action_type': action.action_type,
                    'error': str(e)
                }
                self.state.execution_history.append(action_record)
    
    async def _learn(self) -> None:
        """
        Learn from the results of the cycle.
        
        This includes:
        - Updating memory with new information
        - Improving models based on results
        - Updating knowledge base
        """
        self.logger.debug("Learning from cycle...")
        
        # Update memory with recent experiences
        if self.state.execution_history:
            recent_actions = self.state.execution_history[-5:]  # Last 5 actions
            for action in recent_actions:
                if 'error' not in action:
                    self.memory.add_experience(
                        action_description=action.get('description', ''),
                        result=action,
                        success=True
                    )
        
        # Update learning system
        await self.learning.update_models()
        
        # Check if tasks/goals are complete
        if self.state.current_task:
            task = self.agent_manager.get_task(self.state.current_task)
            if task and task.completed:
                self.logger.info(f"Task completed: {task.description}")
                self.agent_manager.complete_task(self.state.current_task)
                self.state.current_task = None
        
        if self.state.current_goal:
            goal = self.agent_manager.get_goal(self.state.current_goal)
            if goal and goal.completed:
                self.logger.info(f"Goal completed: {goal.description}")
                self.agent_manager.complete_goal(self.state.current_goal)
                self.state.current_goal = None
    
    def run_once(self) -> None:
        """
        Run one complete cycle of the agentic loop (synchronous).
        """
        import asyncio
        asyncio.run(self._run_cycle())
    
    def run_continuous(self, interval: float = 1.0) -> None:
        """
        Run the agentic loop continuously at the specified interval.
        
        Args:
            interval: Time between cycles in seconds
        """
        async def continuous_loop():
            while not self._stop_event.is_set():
                await self._run_cycle()
                await asyncio.sleep(interval)
        
        self._loop_thread = asyncio.create_task(continuous_loop())
    
    def get_state(self) -> AgentState:
        """Get the current agent state."""
        return self.state
    
    def get_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get the execution history.
        
        Args:
            limit: Maximum number of history entries to return
            
        Returns:
            List of history entries
        """
        return self.state.execution_history[-limit:]
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get agentic loop statistics.
        
        Returns:
            Statistics dictionary
        """
        return {
            'status': self.state.status.value,
            'running': self._running,
            'current_task': self.state.current_task,
            'current_goal': self.state.current_goal,
            'cycles_completed': len(self.state.execution_history),
            'tools_stats': self.tools.get_stats(),
            'memory_size': len(self.state.memory_context)
        }


# Global instance for convenience
agentic_loop = AgenticLoop()


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'start':
        loop = AgenticLoop()
        loop.run_continuous()
        print("Agentic loop started. Press Ctrl+C to stop.")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            loop.stop()
            print("Agentic loop stopped.")
    elif len(sys.argv) > 1 and sys.argv[1] == 'once':
        loop = AgenticLoop()
        loop.run_once()
        print("Agentic loop completed one cycle.")
    else:
        loop = AgenticLoop()
        stats = loop.get_stats()
        print(f"Agentic Loop Status: {stats}")
