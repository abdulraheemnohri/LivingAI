"""
LivingAI Agent State Machine
===========================

Manages agent state transitions.
"""

import logging
from typing import Dict, Any, Optional
from enum import Enum


class AgentStateEnum(Enum):
    IDLE = "idle"
    THINKING = "thinking"
    PLANNING = "planning"
    EXECUTING = "executing"
    LEARNING = "learning"
    WAITING = "waiting"
    ERROR = "error"


class AgentStateMachine:
    """
    Manages state transitions for agents.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._current_state: Optional[AgentStateEnum] = None
    
    def transition_to(self, new_state: AgentStateEnum) -> bool:
        """
        Transition to a new state.
        
        Args:
            new_state: The state to transition to
            
        Returns:
            True if transition was successful
        """
        old_state = self._current_state
        self._current_state = new_state
        
        self.logger.debug(f"State transition: {old_state} -> {new_state}")
        return True
    
    def get_current_state(self) -> Optional[AgentStateEnum]:
        """Get the current state."""
        return self._current_state
    
    def can_transition(self, from_state: AgentStateEnum, to_state: AgentStateEnum) -> bool:
        """
        Check if a state transition is valid.
        
        Args:
            from_state: The current state
            to_state: The target state
            
        Returns:
            True if the transition is valid
        """
        # Define valid transitions
        valid_transitions = {
            AgentStateEnum.IDLE: [
                AgentStateEnum.THINKING,
                AgentStateEnum.WAITING,
                AgentStateEnum.ERROR
            ],
            AgentStateEnum.THINKING: [
                AgentStateEnum.PLANNING,
                AgentStateEnum.IDLE,
                AgentStateEnum.ERROR
            ],
            AgentStateEnum.PLANNING: [
                AgentStateEnum.EXECUTING,
                AgentStateEnum.THINKING,
                AgentStateEnum.IDLE,
                AgentStateEnum.ERROR
            ],
            AgentStateEnum.EXECUTING: [
                AgentStateEnum.LEARNING,
                AgentStateEnum.PLANNING,
                AgentStateEnum.IDLE,
                AgentStateEnum.ERROR,
                AgentStateEnum.WAITING
            ],
            AgentStateEnum.LEARNING: [
                AgentStateEnum.IDLE,
                AgentStateEnum.THINKING,
                AgentStateEnum.ERROR
            ],
            AgentStateEnum.WAITING: [
                AgentStateEnum.THINKING,
                AgentStateEnum.IDLE,
                AgentStateEnum.ERROR
            ],
            AgentStateEnum.ERROR: [
                AgentStateEnum.IDLE,
                AgentStateEnum.THINKING
            ]
        }
        
        return to_state in valid_transitions.get(from_state, [])
