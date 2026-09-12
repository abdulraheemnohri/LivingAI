"""
Agent State Machine
===================

Manages agent state transitions and lifecycle.
"""

from enum import Enum, auto
from typing import Dict, List, Optional, Any


class AgentState(Enum):
    """
    Agent lifecycle states.
    
    The agent moves through these states during execution:
    
    CREATED -> INITIALIZING -> UNDERSTANDING -> PLANNING -> READY ->
    EXECUTING -> OBSERVING -> EVALUATING -> VERIFYING -> COMPLETED
    
    Failure path:
    EXECUTING -> FAILED -> DIAGNOSING -> RETRYING -> EXECUTING
    
    Blocked path:
    EXECUTING -> BLOCKED -> USER_INPUT_REQUIRED
    
    Pause/Resume:
    Any state -> PAUSED -> READY
    
    Stop:
    Any state -> CANCELLED
    """
    CREATED = auto()
    INITIALIZING = auto()
    UNDERSTANDING = auto()
    PLANNING = auto()
    WAITING_APPROVAL = auto()
    READY = auto()
    EXECUTING = auto()
    OBSERVING = auto()
    EVALUATING = auto()
    VERIFYING = auto()
    RETRYING = auto()
    DIAGNOSING = auto()
    BLOCKED = auto()
    PAUSED = auto()
    COMPLETED = auto()
    FAILED = auto()
    CANCELLED = auto()


# Valid state transitions
VALID_TRANSITIONS: Dict[AgentState, List[AgentState]] = {
    AgentState.CREATED: [AgentState.INITIALIZING, AgentState.CANCELLED],
    AgentState.INITIALIZING: [AgentState.UNDERSTANDING, AgentState.CANCELLED, AgentState.PAUSED],
    AgentState.UNDERSTANDING: [AgentState.PLANNING, AgentState.CANCELLED, AgentState.PAUSED],
    AgentState.PLANNING: [AgentState.READY, AgentState.WAITING_APPROVAL, AgentState.CANCELLED, AgentState.PAUSED],
    AgentState.WAITING_APPROVAL: [AgentState.READY, AgentState.CANCELLED],
    AgentState.READY: [AgentState.EXECUTING, AgentState.CANCELLED, AgentState.PAUSED],
    AgentState.EXECUTING: [
        AgentState.OBSERVING, 
        AgentState.FAILED, 
        AgentState.BLOCKED,
        AgentState.CANCELLED,
        AgentState.PAUSED
    ],
    AgentState.OBSERVING: [AgentState.EVALUATING, AgentState.CANCELLED, AgentState.PAUSED],
    AgentState.EVALUATING: [
        AgentState.VERIFYING,
        AgentState.RETRYING,
        AgentState.BLOCKED,
        AgentState.CANCELLED,
        AgentState.PAUSED
    ],
    AgentState.VERIFYING: [
        AgentState.COMPLETED,
        AgentState.FAILED,
        AgentState.CANCELLED,
        AgentState.PAUSED
    ],
    AgentState.RETRYING: [AgentState.EXECUTING, AgentState.FAILED, AgentState.CANCELLED],
    AgentState.DIAGNOSING: [AgentState.RETRYING, AgentState.BLOCKED, AgentState.CANCELLED],
    AgentState.BLOCKED: [AgentState.EXECUTING, AgentState.CANCELLED],
    AgentState.PAUSED: [AgentState.READY, AgentState.CANCELLED],
    AgentState.COMPLETED: [],
    AgentState.FAILED: [AgentState.DIAGNOSING, AgentState.CANCELLED],
    AgentState.CANCELLED: []
}


class AgentStateMachine:
    """
    Manages state transitions for agents.
    
    Ensures only valid state transitions are allowed.
    """
    
    def __init__(self):
        """Initialize the state machine."""
        self.transition_log: List[Dict[str, Any]] = []
    
    def transition(self, obj: Any, new_state: AgentState) -> bool:
        """
        Attempt to transition an object to a new state.
        
        Args:
            obj: Object with current state (must have .state attribute)
            new_state: The new state to transition to
            
        Returns:
            bool: True if transition was successful, False otherwise
        """
        current_state = obj.state
        
        # Check if transition is valid
        if not self._is_valid_transition(current_state, new_state):
            return False
        
        # Perform transition
        obj.state = new_state
        
        # Log transition
        self.transition_log.append({
            'object_id': getattr(obj, 'run_id', getattr(obj, 'id', 'unknown')),
            'from_state': current_state.name,
            'to_state': new_state.name,
            'timestamp': __import__('time').time()
        })
        
        return True
    
    def _is_valid_transition(self, current: AgentState, next_state: AgentState) -> bool:
        """Check if a transition is valid."""
        # Any state can transition to CANCELLED
        if next_state == AgentState.CANCELLED:
            return True
        
        # PAUSED can be entered from most states
        if next_state == AgentState.PAUSED:
            return current not in [AgentState.COMPLETED, AgentState.CANCELLED]
        
        # Check valid transitions
        valid_next = VALID_TRANSITIONS.get(current, [])
        return next_state in valid_next
    
    def can_transition(self, current: AgentState, next_state: AgentState) -> bool:
        """Check if a transition is possible."""
        return self._is_valid_transition(current, next_state)
    
    def get_valid_transitions(self, current: AgentState) -> List[AgentState]:
        """Get list of valid transitions from a state."""
        return VALID_TRANSITIONS.get(current, [])
    
    def is_terminal_state(self, state: AgentState) -> bool:
        """Check if a state is terminal (no outgoing transitions)."""
        return len(VALID_TRANSITIONS.get(state, [])) == 0
    
    def get_state_name(self, state: AgentState) -> str:
        """Get the name of a state."""
        return state.name
    
    def get_all_states(self) -> List[AgentState]:
        """Get all possible states."""
        return list(AgentState)
    
    def reset(self):
        """Reset the state machine (clear logs)."""
        self.transition_log = []
