# LivingAI State Engine
# =====================
# This module manages the internal state of the LivingAI system.

import logging
import time
from typing import Dict, Any, Optional, List

# Local imports
from .models import State, StateVariable, StateActivity, StateHistory, StateVariableType
from ..config import ConfigManager
from ..security.audit import AuditLogger


class StateEngine:
    """
    Manages the internal state of the LivingAI system.
    
    Responsibilities:
    - Track state variables (energy, focus, confidence, etc.)
    - Manage activity state
    - Update state based on system events
    - Maintain state history
    - Provide state information
    """
    
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
        self._state = State()
        self._history = StateHistory()
        
        # Initialize default state variables
        self._initialize_default_variables()
        
        # Save initial state
        self._history.add_state(self._state.copy())
        
        logging.info("StateEngine initialized")
    
    def _initialize_default_variables(self) -> None:
        """Initialize default state variables."""
        default_variables = [
            {
                "name": "energy",
                "var_type": StateVariableType.ENERGY,
                "value": 1.0,
                "description": "Current energy level",
            },
            {
                "name": "focus",
                "var_type": StateVariableType.FOCUS,
                "value": 1.0,
                "description": "Current focus level",
            },
            {
                "name": "confidence",
                "var_type": StateVariableType.CONFIDENCE,
                "value": 0.8,
                "description": "Current confidence level",
            },
            {
                "name": "uncertainty",
                "var_type": StateVariableType.UNCERTAINTY,
                "value": 0.2,
                "description": "Current uncertainty level",
            },
            {
                "name": "curiosity",
                "var_type": StateVariableType.CURIOUSITY,
                "value": 0.7,
                "description": "Current curiosity level",
            },
            {
                "name": "urgency",
                "var_type": StateVariableType.URGENCY,
                "value": 0.3,
                "description": "Current urgency level",
            },
            {
                "name": "attention",
                "var_type": StateVariableType.ATTENTION,
                "value": 0.8,
                "description": "Current attention level",
            },
            {
                "name": "satisfaction",
                "var_type": StateVariableType.SATISFACTION,
                "value": 0.5,
                "description": "Current satisfaction level",
            },
        ]
        
        for var_data in default_variables:
            self._state.variables[var_data["name"]] = StateVariable(
                name=var_data["name"],
                var_type=var_data["var_type"],
                value=var_data["value"],
                description=var_data["description"],
            )
    
    def get_state(self) -> State:
        """
        Get the current state.
        
        Returns:
            State: Current state.
        """
        return self._state
    
    def get_variable(self, name: str) -> Optional[StateVariable]:
        """
        Get a state variable by name.
        
        Args:
            name: Name of the variable.
            
        Returns:
            Optional[StateVariable]: The variable, or None if not found.
        """
        return self._state.get_variable(name)
    
    def set_variable(self, name: str, value: float) -> bool:
        """
        Set a state variable.
        
        Args:
            name: Name of the variable.
            value: Value to set (0.0 to 1.0).
            
        Returns:
            bool: True if variable was set, False otherwise.
        """
        # Clamp value between 0 and 1
        value = max(0.0, min(1.0, value))
        
        # Get or create the variable
        if name not in self._state.variables:
            self._state.variables[name] = StateVariable(
                name=name,
                var_type=StateVariableType.ENERGY,  # Default type
                value=value,
            )
        else:
            self._state.variables[name].value = value
            self._state.variables[name].last_updated = time.time()
        
        self._state.last_updated = time.time()
        
        # Save to history
        self._history.add_state(self._state.copy())
        
        self.audit_logger.log(
            "STATE_VARIABLE_SET",
            f"Set {name} to {value}"
        )
        
        return True
    
    def adjust_variable(self, name: str, delta: float) -> bool:
        """
        Adjust a state variable by a delta.
        
        Args:
            name: Name of the variable.
            delta: Amount to adjust by (can be positive or negative).
            
        Returns:
            bool: True if variable was adjusted, False otherwise.
        """
        if name not in self._state.variables:
            return False
        
        current_value = self._state.variables[name].value
        new_value = max(0.0, min(1.0, current_value + delta))
        
        self._state.variables[name].value = new_value
        self._state.variables[name].last_updated = time.time()
        self._state.last_updated = time.time()
        
        # Save to history
        self._history.add_state(self._state.copy())
        
        self.audit_logger.log(
            "STATE_VARIABLE_ADJUST",
            f"Adjusted {name} by {delta} to {new_value}"
        )
        
        return True
    
    def get_activity(self) -> StateActivity:
        """
        Get the current activity.
        
        Returns:
            StateActivity: Current activity.
        """
        return self._state.activity
    
    def set_activity(self, activity: StateActivity) -> bool:
        """
        Set the current activity.
        
        Args:
            activity: New activity.
            
        Returns:
            bool: True if activity was set, False otherwise.
        """
        if isinstance(activity, str):
            try:
                activity = StateActivity(activity)
            except ValueError:
                return False
        
        self._state.activity = activity
        self._state.last_updated = time.time()
        
        # Save to history
        self._history.add_state(self._state.copy())
        
        self.audit_logger.log(
            "STATE_ACTIVITY_SET",
            f"Set activity to {activity.value}"
        )
        
        return True
    
    def update_from_event(self, event: str, data: Optional[Dict[str, Any]] = None) -> None:
        """
        Update state based on a system event.
        
        Args:
            event: Event type.
            data: Optional event data.
        """
        event_handlers = {
            "action_start": self._handle_action_start,
            "action_complete": self._handle_action_complete,
            "action_fail": self._handle_action_fail,
            "learning_success": self._handle_learning_success,
            "learning_fail": self._handle_learning_fail,
            "goal_complete": self._handle_goal_complete,
            "goal_fail": self._handle_goal_fail,
            "idle_start": self._handle_idle_start,
            "idle_end": self._handle_idle_end,
            "sleep_start": self._handle_sleep_start,
            "sleep_end": self._handle_sleep_end,
        }
        
        handler = event_handlers.get(event)
        if handler:
            handler(data)
        else:
            logging.warning(f"No state handler for event: {event}")
    
    def _handle_action_start(self, data: Optional[Dict[str, Any]]) -> None:
        """Handle the start of an action."""
        # Increase urgency and attention
        self.adjust_variable("urgency", 0.1)
        self.adjust_variable("attention", 0.1)
        
        # Set activity
        self.set_activity(StateActivity.ACTING)
    
    def _handle_action_complete(self, data: Optional[Dict[str, Any]]) -> None:
        """Handle the completion of an action."""
        # Decrease urgency
        self.adjust_variable("urgency", -0.1)
        
        # Increase confidence and satisfaction
        self.adjust_variable("confidence", 0.05)
        self.adjust_variable("satisfaction", 0.1)
        
        # Set activity based on what was done
        if data and data.get("action_type") == "learning":
            self.set_activity(StateActivity.LEARNING)
        else:
            self.set_activity(StateActivity.IDLE)
    
    def _handle_action_fail(self, data: Optional[Dict[str, Any]]) -> None:
        """Handle the failure of an action."""
        # Decrease confidence
        self.adjust_variable("confidence", -0.1)
        
        # Increase uncertainty
        self.adjust_variable("uncertainty", 0.2)
        
        # Decrease satisfaction
        self.adjust_variable("satisfaction", -0.1)
        
        # Set activity
        self.set_activity(StateActivity.IDLE)
    
    def _handle_learning_success(self, data: Optional[Dict[str, Any]]) -> None:
        """Handle successful learning."""
        # Increase confidence and satisfaction
        self.adjust_variable("confidence", 0.1)
        self.adjust_variable("satisfaction", 0.1)
        
        # Decrease uncertainty
        self.adjust_variable("uncertainty", -0.1)
        
        # Set activity
        self.set_activity(StateActivity.LEARNING)
    
    def _handle_learning_fail(self, data: Optional[Dict[str, Any]]) -> None:
        """Handle failed learning."""
        # Decrease confidence
        self.adjust_variable("confidence", -0.05)
        
        # Increase uncertainty
        self.adjust_variable("uncertainty", 0.1)
        
        # Set activity
        self.set_activity(StateActivity.IDLE)
    
    def _handle_goal_complete(self, data: Optional[Dict[str, Any]]) -> None:
        """Handle the completion of a goal."""
        # Increase satisfaction and confidence
        self.adjust_variable("satisfaction", 0.2)
        self.adjust_variable("confidence", 0.1)
        
        # Decrease urgency
        self.adjust_variable("urgency", -0.2)
        
        # Set activity
        self.set_activity(StateActivity.IDLE)
    
    def _handle_goal_fail(self, data: Optional[Dict[str, Any]]) -> None:
        """Handle the failure of a goal."""
        # Decrease confidence and satisfaction
        self.adjust_variable("confidence", -0.1)
        self.adjust_variable("satisfaction", -0.2)
        
        # Increase uncertainty
        self.adjust_variable("uncertainty", 0.2)
        
        # Set activity
        self.set_activity(StateActivity.IDLE)
    
    def _handle_idle_start(self, data: Optional[Dict[str, Any]]) -> None:
        """Handle the start of idle mode."""
        # Decrease urgency and attention
        self.adjust_variable("urgency", -0.3)
        self.adjust_variable("attention", -0.2)
        
        # Set activity
        self.set_activity(StateActivity.IDLE)
    
    def _handle_idle_end(self, data: Optional[Dict[str, Any]]) -> None:
        """Handle the end of idle mode."""
        # Increase attention
        self.adjust_variable("attention", 0.2)
        
        # Set activity based on what we're doing
        if data and data.get("next_activity"):
            self.set_activity(StateActivity(data["next_activity"]))
        else:
            self.set_activity(StateActivity.THINKING)
    
    def _handle_sleep_start(self, data: Optional[Dict[str, Any]]) -> None:
        """Handle the start of sleep mode."""
        # Decrease all variables
        for name in self._state.variables:
            self.adjust_variable(name, -0.5)
        
        # Set activity
        self.set_activity(StateActivity.SLEEPING)
    
    def _handle_sleep_end(self, data: Optional[Dict[str, Any]]) -> None:
        """Handle the end of sleep mode."""
        # Reset variables to reasonable values
        self.set_variable("energy", 1.0)
        self.set_variable("focus", 0.8)
        self.set_variable("confidence", 0.8)
        
        # Set activity
        self.set_activity(StateActivity.IDLE)
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the current state.
        
        Returns:
            Dict[str, Any]: State summary.
        """
        return self._state.get_summary()
    
    def get_history(self) -> StateHistory:
        """
        Get the state history.
        
        Returns:
            StateHistory: State history.
        """
        return self._history
    
    def get_state_at(self, timestamp: float) -> Optional[State]:
        """
        Get the state at or before a specific timestamp.
        
        Args:
            timestamp: Timestamp to search for.
            
        Returns:
            Optional[State]: State at or before the timestamp, or None if not found.
        """
        return self._history.get_state_at(timestamp)
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the state.
        
        Returns:
            Dict[str, Any]: State statistics.
        """
        return {
            "current_state": self._state.get_summary(),
            "history": self._history.get_stats(),
        }
    
    def reset(self) -> None:
        """Reset the state to default values."""
        self._state = State()
        self._initialize_default_variables()
        self._history.clear()
        self._history.add_state(self._state.copy())
        
        self.audit_logger.log("STATE_RESET", "State reset to defaults")
    
    def decay_state(self) -> None:
        """
        Decay state variables over time (for idle mode).
        
        This simulates the natural decay of certain state variables
        when the system is not actively being used.
        """
        # Decay energy and focus
        self.adjust_variable("energy", -0.01)
        self.adjust_variable("focus", -0.01)
        
        # Increase uncertainty slightly
        self.adjust_variable("uncertainty", 0.005)
        
        self.audit_logger.log("STATE_DECAY", "State variables decayed")
    
    def boost_state(self, event: str) -> None:
        """
        Boost state variables based on an event.
        
        Args:
            event: Event that triggered the boost.
        """
        boosts = {
            "positive_feedback": {
                "confidence": 0.1,
                "satisfaction": 0.1,
            },
            "successful_action": {
                "confidence": 0.05,
                "satisfaction": 0.1,
                "energy": 0.02,
            },
            "learning_success": {
                "confidence": 0.1,
                "curiosity": 0.05,
            },
            "goal_complete": {
                "satisfaction": 0.2,
                "confidence": 0.1,
            },
        }
        
        event_boosts = boosts.get(event, {})
        for var_name, delta in event_boosts.items():
            self.adjust_variable(var_name, delta)
        
        self.audit_logger.log("STATE_BOOST", f"State boosted by event: {event}")
    
    def get_variable_history(
        self,
        name: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get the history of a specific state variable.
        
        Args:
            name: Name of the variable.
            limit: Maximum number of entries to return.
            
        Returns:
            List[Dict[str, Any]]: History of the variable.
        """
        history = []
        
        for state in self._history.get_states():
            if name in state.variables:
                history.append({
                    "timestamp": state.last_updated,
                    "value": state.variables[name].value,
                })
        
        # Return most recent entries
        return history[-limit:] if limit else history
