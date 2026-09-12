"""
LivingAI Agents Package
=======================

Agentic AI layer for LivingAI - Goal-driven autonomous agents powered by SmolLM3-3B.

This package provides:
- AgentManager: Create, manage, and control agents
- AgentPlanner: Goal understanding, task decomposition, and planning
- TaskGraph: Dependency-aware task management
- ToolRegistry: Tool selection and execution
- VerificationEngine: Result verification and validation
- StateMachine: Agent lifecycle management
"""

from .manager import AgentManager
from .planner import AgentPlanner
from .task import Task, TaskGraph, TaskState
from .tool_registry import ToolRegistry, ToolSelector, ToolExecutor, ToolPermissionManager
from .verification import VerificationEngine
from .state_machine import AgentState, AgentStateMachine
from .database import AgentDatabase

__all__ = [
    'AgentManager',
    'AgentPlanner', 
    'Task',
    'TaskGraph',
    'TaskState',
    'ToolRegistry',
    'ToolSelector',
    'ToolExecutor',
    'ToolPermissionManager',
    'VerificationEngine',
    'AgentState',
    'AgentStateMachine',
    'AgentDatabase',
]
