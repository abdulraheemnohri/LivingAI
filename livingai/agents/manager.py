"""
Agent Manager
=============

Manages the lifecycle of autonomous agents in LivingAI.
"""

import uuid
import time
import threading
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum

from .state_machine import AgentState, AgentStateMachine
from .planner import AgentPlanner
from .task import TaskGraph
from .tool_registry import ToolRegistry
from .verification import VerificationEngine
from .database import AgentDatabase


class AgentMode(Enum):
    """Agent operation modes."""
    ASK = "ask"              # Answer only
    ASSIST = "assist"        # Create plans and request confirmation
    PLAN = "plan"            # Create a plan without executing
    EXECUTE = "execute"      # Execute approved plan
    AUTONOMOUS = "autonomous" # Execute allowed tasks according to policies
    BACKGROUND = "background"  # Work on approved background goals during idle


class AgentPriority(Enum):
    """Agent priority levels."""
    CRITICAL = "critical"
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"
    BACKGROUND = "background"


@dataclass
class AgentBudget:
    """Resource budget for an agent."""
    max_steps: int = 50
    max_retries: int = 3
    max_runtime_minutes: int = 30
    max_tool_calls: int = 100
    max_filesystem_ops: int = 50
    max_generated_output: int = 10000
    max_background_runtime: int = 60


@dataclass
class AgentConfig:
    """Configuration for an agent."""
    id: str = field(default_factory=lambda: f"AGT-{uuid.uuid4().hex[:8].upper()}")
    name: str = ""
    description: str = ""
    goal: str = ""
    mode: AgentMode = AgentMode.ASSIST
    priority: AgentPriority = AgentPriority.NORMAL
    budget: AgentBudget = field(default_factory=AgentBudget)
    require_confirmation: bool = True
    verify_actions: bool = True
    learn_from_runs: bool = True
    permission_profile: str = "SAFE"
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)


@dataclass
class AgentRun:
    """Represents an agent execution run."""
    run_id: str = field(default_factory=lambda: f"RUN-{uuid.uuid4().hex[:8].upper()}")
    agent_id: str = ""
    goal: str = ""
    state: AgentState = AgentState.CREATED
    plan: Optional[Dict] = None
    tasks: List[Dict] = field(default_factory=list)
    completed_tasks: int = 0
    total_tasks: int = 0
    steps_taken: int = 0
    retries_used: int = 0
    tool_calls: int = 0
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None
    result: Optional[Dict] = None
    error: Optional[str] = None
    checkpoint: Optional[Dict] = None


class AgentManager:
    """
    Manages the creation, execution, and lifecycle of autonomous agents.
    
    Responsibilities:
    - Create and manage agents
    - Start, pause, resume, stop agent runs
    - Track agent state and progress
    - Manage agent goals and plans
    - Manage tool permissions and budgets
    - Store agent history and checkpoints
    """
    
    def __init__(self, db_path: Optional[str] = None):
        """Initialize the Agent Manager."""
        self.database = AgentDatabase(db_path)
        self.state_machine = AgentStateMachine()
        self.planner = AgentPlanner()
        self.tool_registry = ToolRegistry()
        self.verification_engine = VerificationEngine()
        
        self._agents: Dict[str, AgentConfig] = {}
        self._runs: Dict[str, AgentRun] = {}
        self._active_runs: Dict[str, AgentRun] = {}
        self._lock = threading.RLock()
        
        # Load existing agents from database
        self._load_agents()
    
    def _load_agents(self):
        """Load agents from database."""
        agents = self.database.get_all_agents()
        for agent_data in agents:
            config = AgentConfig(**agent_data)
            self._agents[config.id] = config
    
    def create_agent(
        self,
        goal: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        mode: AgentMode = AgentMode.ASSIST,
        priority: AgentPriority = AgentPriority.NORMAL,
        permission_profile: str = "SAFE",
        **kwargs
    ) -> AgentConfig:
        """
        Create a new agent configuration.
        """
        config = AgentConfig(
            name=name or f"Agent-{goal[:20]}",
            description=description or goal,
            goal=goal,
            mode=mode,
            priority=priority,
            permission_profile=permission_profile,
            **kwargs
        )
        
        self.database.create_agent(config)
        self._agents[config.id] = config
        
        return config
    
    def start_agent(
        self,
        agent_id: str,
        goal: Optional[str] = None,
        mode: Optional[AgentMode] = None
    ) -> AgentRun:
        """Start an agent run with a goal."""
        with self._lock:
            if agent_id not in self._agents:
                if goal:
                    config = self.create_agent(goal, mode=mode or AgentMode.ASSIST)
                else:
                    raise ValueError(f"Agent {agent_id} not found")
            else:
                config = self._agents[agent_id]
                if goal:
                    config = AgentConfig(**{**config.__dict__, "goal": goal})
            
            run = AgentRun(
                agent_id=config.id,
                goal=config.goal,
                state=AgentState.CREATED
            )
            
            plan = self.planner.create_plan(config.goal, config=config)
            run.plan = plan
            run.total_tasks = len(plan.get('tasks', []))
            
            self.database.create_agent_run(run)
            self._runs[run.run_id] = run
            self._active_runs[run.run_id] = run
            
            thread = threading.Thread(
                target=self._run_agent,
                args=(run, config),
                daemon=True
            )
            thread.start()
            
            return run
    
    def _run_agent(self, run: AgentRun, config: AgentConfig):
        """Internal method to run an agent."""
        try:
            with self._lock:
                self.state_machine.transition(run, AgentState.INITIALIZING)
            
            self._initialize_agent(run, config)
            
            with self._lock:
                self.state_machine.transition(run, AgentState.UNDERSTANDING)
            
            self._understand_goal(run, config)
            
            with self._lock:
                self.state_machine.transition(run, AgentState.PLANNING)
            
            if not run.plan:
                run.plan = self.planner.create_plan(config.goal, config=config)
                run.total_tasks = len(run.plan.get('tasks', []))
            
            with self._lock:
                self.state_machine.transition(run, AgentState.READY)
            
            with self._lock:
                self.state_machine.transition(run, AgentState.EXECUTING)
            
            self._execute_tasks(run, config)
            
            with self._lock:
                self.state_machine.transition(run, AgentState.VERIFYING)
            
            self._verify_results(run, config)
            
            with self._lock:
                self.state_machine.transition(run, AgentState.COMPLETED)
                run.end_time = time.time()
            
            self._save_checkpoint(run)
            
            if config.learn_from_runs:
                self._learn_from_run(run)
            
        except Exception as e:
            with self._lock:
                run.error = str(e)
                self.state_machine.transition(run, AgentState.FAILED)
            self.database.update_agent_run(run)
    
    def _initialize_agent(self, run: AgentRun, config: AgentConfig):
        """Initialize agent context."""
        pass
    
    def _understand_goal(self, run: AgentRun, config: AgentConfig):
        """Understand the agent's goal."""
        pass
    
    def _execute_tasks(self, run: AgentRun, config: AgentConfig):
        """Execute agent tasks."""
        tasks = run.plan.get('tasks', [])
        
        for task in tasks:
            if run.steps_taken >= config.budget.max_steps:
                run.error = "Maximum steps exceeded"
                self.state_machine.transition(run, AgentState.FAILED)
                break
            
            success = self._execute_task(run, config, task)
            
            if success:
                run.completed_tasks += 1
                run.steps_taken += 1
            else:
                if run.retries_used < config.budget.max_retries:
                    run.retries_used += 1
                else:
                    run.error = f"Task failed after {config.budget.max_retries} retries"
                    self.state_machine.transition(run, AgentState.FAILED)
                    break
            
            self.database.update_agent_run(run)
    
    def _execute_task(self, run: AgentRun, config: AgentConfig, task: Dict) -> bool:
        """Execute a single task."""
        tool_name = task.get('tool')
        if tool_name:
            result = self.tool_registry.execute(tool_name, task.get('arguments', {}))
            task['result'] = result
            run.tool_calls += 1
            return result.get('success', False)
        return True
    
    def _verify_results(self, run: AgentRun, config: AgentConfig):
        """Verify agent results."""
        if config.verify_actions:
            verification = self.verification_engine.verify(run)
            run.result = {
                'verification': verification,
                'completed_tasks': run.completed_tasks,
                'total_tasks': run.total_tasks
            }
        else:
            run.result = {
                'completed_tasks': run.completed_tasks,
                'total_tasks': run.total_tasks
            }
    
    def _save_checkpoint(self, run: AgentRun):
        """Save agent checkpoint."""
        checkpoint = {
            'run_id': run.run_id,
            'agent_id': run.agent_id,
            'state': run.state.value,
            'plan': run.plan,
            'completed_tasks': run.completed_tasks,
            'total_tasks': run.total_tasks,
            'context': {}
        }
        run.checkpoint = checkpoint
        self.database.save_checkpoint(checkpoint)
    
    def _learn_from_run(self, run: AgentRun):
        """Learn from agent run."""
        lessons = []
        if run.error:
            lessons.append({
                'type': 'failure',
                'description': f"Agent failed: {run.error}",
                'recommendation': 'Review agent configuration and permissions'
            })
        if run.completed_tasks < run.total_tasks:
            lessons.append({
                'type': 'partial_success',
                'description': f"Only {run.completed_tasks}/{run.total_tasks} tasks completed",
                'recommendation': 'Check task dependencies and requirements'
            })
        for lesson in lessons:
            self.database.save_lesson(lesson)
    
    def pause_agent(self, run_id: str):
        """Pause an agent run."""
        with self._lock:
            if run_id in self._active_runs:
                run = self._active_runs[run_id]
                self.state_machine.transition(run, AgentState.PAUSED)
                self._save_checkpoint(run)
                self.database.update_agent_run(run)
    
    def resume_agent(self, run_id: str) -> bool:
        """Resume a paused agent run."""
        with self._lock:
            if run_id in self._runs:
                run = self._runs[run_id]
                if run.state == AgentState.PAUSED:
                    self.state_machine.transition(run, AgentState.READY)
                    self._active_runs[run_id] = run
                    config = self._agents.get(run.agent_id)
                    if config:
                        thread = threading.Thread(
                            target=self._run_agent,
                            args=(run, config),
                            daemon=True
                        )
                        thread.start()
                        return True
        return False
    
    def stop_agent(self, run_id: str):
        """Stop an agent run."""
        with self._lock:
            if run_id in self._active_runs:
                run = self._active_runs[run_id]
                self.state_machine.transition(run, AgentState.CANCELLED)
                run.end_time = time.time()
                self._active_runs.pop(run_id, None)
                self.database.update_agent_run(run)
    
    def inspect_agent(self, run_id: str) -> Optional[AgentRun]:
        """Get agent run details."""
        return self._runs.get(run_id)
    
    def list_agents(self) -> List[AgentConfig]:
        """List all agent configurations."""
        return list(self._agents.values())
    
    def list_runs(self, agent_id: Optional[str] = None) -> List[AgentRun]:
        """List agent runs."""
        if agent_id:
            return [r for r in self._runs.values() if r.agent_id == agent_id]
        return list(self._runs.values())
    
    def get_status(self, run_id: str) -> Optional[Dict]:
        """Get agent status."""
        run = self._runs.get(run_id)
        if run:
            return {
                'run_id': run.run_id,
                'agent_id': run.agent_id,
                'goal': run.goal,
                'state': run.state.value,
                'progress': f"{run.completed_tasks}/{run.total_tasks} tasks",
                'steps': f"{run.steps_taken}/{run.budget.max_steps}",
                'tools': run.tool_calls,
                'retries': f"{run.retries_used}/{run.budget.max_retries}",
                'runtime': self._format_runtime(run),
                'risk': run.plan.get('risk', 'UNKNOWN') if run.plan else 'UNKNOWN'
            }
        return None
    
    def _format_runtime(self, run: AgentRun) -> str:
        """Format runtime as HH:MM."""
        elapsed = time.time() - run.start_time
        if run.end_time:
            elapsed = run.end_time - run.start_time
        minutes = int(elapsed // 60)
        seconds = int(elapsed % 60)
        return f"{minutes:02d}:{seconds:02d}"
    
    def get_logs(self, run_id: str) -> List[Dict]:
        """Get agent logs."""
        return self.database.get_agent_logs(run_id)
    
    def delete_agent(self, agent_id: str):
        """Delete an agent."""
        with self._lock:
            if agent_id in self._agents:
                del self._agents[agent_id]
                self.database.delete_agent(agent_id)
    
    def cleanup(self):
        """Clean up completed runs."""
        with self._lock:
            completed_runs = [
                run_id for run_id, run in self._runs.items()
                if run.state in [AgentState.COMPLETED, AgentState.FAILED, AgentState.CANCELLED]
            ]
            for run_id in completed_runs:
                self._runs.pop(run_id, None)
                self._active_runs.pop(run_id, None)
