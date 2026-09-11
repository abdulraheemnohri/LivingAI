# LivingAI State Engine
# =====================
# This module manages the internal state of the LivingAI system.

import logging
import time
from typing import Dict, Any, Optional, List

# Local imports
from .models import State, StateVariable, ActivityState, StateHistory
from ..config import ConfigManager
from ..security.audit import AuditLogger


class StateEngine:
    """
    Manages the internal state of the LivingAI system.
    
    Responsibilities:
    - Track state variables (energy, focus, confidence, etc.)
    - Manage activity states (idle, thinking, acting, etc.)
    - Update state based on system events
    - Provide state history and statistics
    - Handle state transitions
    """
    
    # Default state variable values
    DEFAULT_STATE = {
        StateVariable.ENERGY: 1.0,
        StateVariable.FOCUS: 1.0,
        StateVariable.CONFIDENCE: 0.8,
        StateVariable.UNCERTAINTY: 0.2,
        StateVariable.CURIOUSITY: 0.7,
        StateVariable.URGENCY: 0.3,
        StateVariable.ATTENTION: 0.8,
        StateVariable.SATISFACTION: 0.5,
    }
    
    # Activity state transitions
    ACTIVITY_TRANSITIONS = {
        ActivityState.IDLE: [
            ActivityState.THINKING,
            ActivityState.PLANNING,
            ActivityState.ACTING,
            ActivityState.SLEEPING,
        ],
        ActivityState.THINKING: [
            ActivityState.IDLE,
            ActivityState.PLANNING,
            ActivityState.ACTING,
        ],
        ActivityState.PLANNING: [
            ActivityState.IDLE,
            ActivityState.THINKING,
            ActivityState.ACTING,
        ],
        ActivityState.ACTING: [
            ActivityState.IDLE,
            ActivityState.THINKING,
            ActivityState.OBSERVING,
        ],
        ActivityState.OBSERVING: [
            ActivityState.IDLE,
            ActivityState.THINKING,
            ActivityState.REFLECTING,
        ],
        ActivityState.REFLECTING: [
            ActivityState.IDLE,
            ActivityState.LEARNING,
        ],
        ActivityState.LEARNING: [
            ActivityState.IDLE,
            ActivityState.CONSOLIDATING,
        ],
        ActivityState.CONSOLIDATING: [
            ActivityState.IDLE,
            ActivityState.SLEEPING,
        ],
        ActivityState.SLEEPING: [
            ActivityState.IDLE,
        ],
        ActivityState.WAITING: [
            ActivityState.IDLE,
            ActivityState.THINKING,
        ],
    }
    
    def __init__(
        self,
        config: ConfigManager,
        audit_logger: AuditLogger
    ):
        """
        Initialize the StateEngine.
        
        Args:
            config: Configuration manager.
            audit_logger: Audit logger for tracking actions.
        """
        self.config = config
        self.audit_logger = audit_logger
        
        # Initialize state
        self._current_state = State()
        
        # Initialize state history
        self._state_history = StateHistory()
        
        # State configuration
        self._decay_rates = self._load_decay_rates()
        self._recovery_rates = self._load_recovery_rates()
        
        # Add initial state to history
        self._state_history.add_state(self._current_state)
        
        logging.info("StateEngine initialized")
    
    def _load_decay_rates(self) -> Dict[StateVariable, float]:
        """
        Load decay rates for state variables.
        
        Returns:
            Dict[StateVariable, float]: Decay rates (0.0 to 1.0).
        """
        # Default decay rates (per minute)
        return {
            StateVariable.ENERGY: 0.01,      # Energy decays slowly
            StateVariable.FOCUS: 0.05,      # Focus decays faster
            StateVariable.CONFIDENCE: 0.02,  # Confidence decays slowly
            StateVariable.UNCERTAINTY: 0.01,  # Uncertainty decays slowly
            StateVariable.CURIOUSITY: 0.03,  # Curiosity decays moderately
            StateVariable.URGENCY: 0.05,      # Urgency decays faster
            StateVariable.ATTENTION: 0.04,   # Attention decays moderately
            StateVariable.SATISFACTION: 0.02, # Satisfaction decays slowly
        }
    
    def _load_recovery_rates(self) -> Dict[StateVariable, float]:
        """
        Load recovery rates for state variables.
        
        Returns:
            Dict[StateVariable, float]: Recovery rates (0.0 to 1.0).
        """
        # Default recovery rates (per minute)
        return {
            StateVariable.ENERGY: 0.05,      # Energy recovers moderately
            StateVariable.FOCUS: 0.1,       # Focus recovers faster
            StateVariable.CONFIDENCE: 0.05,  # Confidence recovers moderately
            StateVariable.UNCERTAINTY: -0.05, # Uncertainty decreases (negative recovery)
            StateVariable.CURIOUSITY: 0.05,   # Curiosity recovers moderately
            StateVariable.URGENCY: -0.1,      # Urgency decreases (negative recovery)
            StateVariable.ATTENTION: 0.08,    # Attention recovers faster
            StateVariable.SATISFACTION: 0.03, # Satisfaction recovers slowly
        }
    
    def get_state(self) -> State:
        """
        Get the current state.
        
        Returns:
            State: The current state.
        """
        return self._current_state
    
    def get_variable(self, variable: StateVariable) -> float:
        """
        Get the value of a state variable.
        
        Args:
            variable: The state variable to get.
            
        Returns:
            float: The value of the variable.
        """
        return self._current_state.get_variable(variable)
    
    def set_variable(self, variable: StateVariable, value: float) -> None:
        """
        Set the value of a state variable.
        
        Args:
            variable: The state variable to set.
            value: The value to set (0.0 to 1.0).
        """
        old_value = self._current_state.get_variable(variable)
        self._current_state.set_variable(variable, value)
        
        # Log the change
        self.audit_logger.log(
            "STATE_VARIABLE_SET",
            f"Set {variable.value} from {old_value:.2f} to {value:.2f}"
        )
        
        # Add to history
        self._state_history.add_state(self._current_state)
    
    def adjust_variable(self, variable: StateVariable, delta: float) -> None:
        """
        Adjust the value of a state variable by a delta.
        
        Args:
            variable: The state variable to adjust.
            delta: The amount to adjust by (can be positive or negative).
        """
        old_value = self._current_state.get_variable(variable)
        self._current_state.adjust_variable(variable, delta)
        new_value = self._current_state.get_variable(variable)
        
        # Log the change
        self.audit_logger.log(
            "STATE_VARIABLE_ADJUST",
            f"Adjusted {variable.value} from {old_value:.2f} to {new_value:.2f} (delta: {delta:.2f})"
        )
        
        # Add to history
        self._state_history.add_state(self._current_state)
    
    def get_activity(self) -> ActivityState:
        """
        Get the current activity state.
        
        Returns:
            ActivityState: The current activity.
        """
        return self._current_state.get_activity()
    
    def set_activity(self, activity: ActivityState) -> bool:
        """
        Set the current activity state.
        
        Args:
            activity: The new activity state.
            
        Returns:
            bool: True if transition succeeded, False otherwise.
        """
        current_activity = self._current_state.get_activity()
        
        # Check if transition is allowed
        if activity not in self.ACTIVITY_TRANSITIONS.get(current_activity, []):
            logging.warning(f"Invalid activity transition: {current_activity.value} -> {activity.value}")
            return False
        
        old_activity = self._current_state.get_activity()
        self._current_state.set_activity(activity)
        
        # Log the change
        self.audit_logger.log(
            "STATE_ACTIVITY_SET",
            f"Changed activity from {old_activity.value} to {activity.value}"
        )
        
        # Add to history
        self._state_history.add_state(self._current_state)
        
        return True
    
    def update(self, delta_time: float = None) -> None:
        """
        Update the state based on time passed.
        
        Args:
            delta_time: Time passed in seconds. If None, uses time since last update.
        """
        if delta_time is None:
            # Calculate time since last update
            last_timestamp = self._current_state.timestamp
            delta_time = time.time() - last_timestamp
        
        # Convert to minutes
        delta_minutes = delta_time / 60.0
        
        # Apply decay and recovery
        for variable, decay_rate in self._decay_rates.items():
            # Get current value
            current_value = self._current_state.get_variable(variable)
            
            # Apply decay
            decay_amount = decay_rate * delta_minutes
            new_value = max(0.0, current_value - decay_amount)
            
            # Apply recovery
            recovery_rate = self._recovery_rates.get(variable, 0.0)
            recovery_amount = recovery_rate * delta_minutes
            new_value = min(1.0, new_value + recovery_amount)
            
            # Update the variable
            self._current_state.set_variable(variable, new_value)
        
        # Add to history
        self._state_history.add_state(self._current_state)
        
        # Log the update
        self.audit_logger.log(
            "STATE_UPDATE",
            f"Updated state after {delta_time:.2f} seconds"
        )
    
    def reset(self) -> None:
        """Reset the state to default values."""
        old_state = self._current_state
        
        # Create new state with default values
        self._current_state = State()
        
        # Add to history
        self._state_history.add_state(self._current_state)
        
        # Log the reset
        self.audit_logger.log("STATE_RESET", "State reset to defaults")
    
    def get_history(self) -> StateHistory:
        """
        Get the state history.
        
        Returns:
            StateHistory: The state history.
        """
        return self._state_history
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the current state.
        
        Returns:
            Dict[str, Any]: State summary.
        """
        return self._current_state.get_summary()
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the state.
        
        Returns:
            Dict[str, Any]: State statistics.
        """
        return {
            "current_state": self._current_state.get_summary(),
            "history_stats": self._state_history.get_stats(),
        }
    
    def display_state(self) -> None:
        """Display the current state in a user-friendly format."""
        state = self._current_state
        
        print("\n" + "=" * 50)
        print("INTERNAL STATE")
        print("=" * 50)
        
        # Display activity
        print(f"\nActivity: {state.get_activity().value.upper()}")
        
        # Display variables
        print("\nVariables:")
        for variable in StateVariable:
            value = state.get_variable(variable)
            bar_length = int(value * 20)
            bar = "█" * bar_length + "░" * (20 - bar_length)
            print(f"{variable.value:12} {bar} {value:.0%}")
        
        print("=" * 50 + "\n")
    
    def get_state_as_dict(self) -> Dict[str, Any]:
        """
        Get the current state as a dictionary.
        
        Returns:
            Dict[str, Any]: State as a dictionary.
        """
        return self._current_state.to_dict()
    
    def set_state_from_dict(self, state_dict: Dict[str, Any]) -> None:
        """
        Set the current state from a dictionary.
        
        Args:
            state_dict: Dictionary with state data.
        """
        old_state = self._current_state
        self._current_state = State.from_dict(state_dict)
        
        # Add to history
        self._state_history.add_state(self._current_state)
        
        # Log the change
        self.audit_logger.log("STATE_SET", "State set from dictionary")
    
    def get_changes(self) -> List[Dict[str, Any]]:
        """
        Get a list of recent state changes.
        
        Returns:
            List[Dict[str, Any]]: List of state changes.
        """
        return self._state_history.get_changes()
    
    def clear_history(self) -> None:
        """Clear the state history."""
        self._state_history.clear()
    
    def get_variable_history(
        self,
        variable: StateVariable,
        limit: int = 10
    ) -> List[Tuple[float, float]]:
        """
        Get the history of a specific variable.
        
        Args:
            variable: The state variable to get history for.
            limit: Maximum number of entries to return.
            
        Returns:
            List[Tuple[float, float]]: List of (timestamp, value) tuples.
        """
        history = []
        
        for state in self._state_history.get_states()[-limit:]:
            history.append((state.timestamp, state.get_variable(variable)))
        
        return history
    
    def get_activity_history(self, limit: int = 10) -> List[Tuple[float, str]]:
        """
        Get the history of activity states.
        
        Args:
            limit: Maximum number of entries to return.
            
        Returns:
            List[Tuple[float, str]]: List of (timestamp, activity) tuples.
        """
        history = []
        
        for state in self._state_history.get_states()[-limit:]:
            history.append((state.timestamp, state.get_activity().value))
        
        return history
