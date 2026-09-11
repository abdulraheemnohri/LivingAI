# LivingAI State Models
# =======================
# This module defines the data models for the state system.

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from enum import Enum
import time


class StateVariable(Enum):
    """Variables that can be tracked in the state system."""
    ENERGY = "energy"           # Current energy level (0.0 to 1.0)
    FOCUS = "focus"             # Current focus level (0.0 to 1.0)
    CONFIDENCE = "confidence"   # Current confidence level (0.0 to 1.0)
    UNCERTAINTY = "uncertainty" # Current uncertainty level (0.0 to 1.0)
    CURIOUSITY = "curiosity"     # Current curiosity level (0.0 to 1.0)
    URGENCY = "urgency"           # Current urgency level (0.0 to 1.0)
    ATTENTION = "attention"       # Current attention level (0.0 to 1.0)
    SATISFACTION = "satisfaction" # Current satisfaction level (0.0 to 1.0)
    ACTIVITY = "activity"         # Current activity state


class ActivityState(Enum):
    """Possible activity states."""
    IDLE = "idle"               # System is idle
    THINKING = "thinking"         # System is thinking
    PLANNING = "planning"         # System is planning
    ACTING = "acting"             # System is acting
    OBSERVING = "observing"       # System is observing
    REFLECTING = "reflecting"     # System is reflecting
    LEARNING = "learning"         # System is learning
    CONSOLIDATING = "consolidating" # System is consolidating
    SLEEPING = "sleeping"         # System is sleeping
    WAITING = "waiting"           # System is waiting


@dataclass
class State:
    """
    Represents the current state of the LivingAI system.
    
    Attributes:
        variables: Dictionary of state variables and their values.
        activity: Current activity state.
        timestamp: When the state was last updated.
        metadata: Additional metadata about the state.
    """
    variables: Dict[StateVariable, float] = field(default_factory=dict)
    activity: ActivityState = ActivityState.IDLE
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Post-initialization processing."""
        # Initialize default values for variables
        if not self.variables:
            self.variables = {
                StateVariable.ENERGY: 1.0,
                StateVariable.FOCUS: 1.0,
                StateVariable.CONFIDENCE: 0.8,
                StateVariable.UNCERTAINTY: 0.2,
                StateVariable.CURIOUSITY: 0.7,
                StateVariable.URGENCY: 0.3,
                StateVariable.ATTENTION: 0.8,
                StateVariable.SATISFACTION: 0.5,
            }
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the state to a dictionary.
        
        Returns:
            Dict[str, Any]: Dictionary representation of the state.
        """
        return {
            "variables": {v.value: val for v, val in self.variables.items()},
            "activity": self.activity.value,
            "timestamp": self.timestamp,
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "State":
        """
        Create a State from a dictionary.
        
        Args:
            data: Dictionary with state data.
            
        Returns:
            State: State instance.
        """
        variables = {}
        for var_name, value in data.get("variables", {}).items():
            try:
                var = StateVariable(var_name)
                variables[var] = value
            except ValueError:
                pass
        
        activity = data.get("activity", ActivityState.IDLE.value)
        try:
            activity = ActivityState(activity)
        except ValueError:
            activity = ActivityState.IDLE
        
        return cls(
            variables=variables,
            activity=activity,
            timestamp=data.get("timestamp", time.time()),
            metadata=data.get("metadata", {}),
        )
    
    def get_variable(self, variable: StateVariable) -> float:
        """
        Get the value of a state variable.
        
        Args:
            variable: The state variable to get.
            
        Returns:
            float: The value of the variable.
        """
        return self.variables.get(variable, 0.0)
    
    def set_variable(self, variable: StateVariable, value: float) -> None:
        """
        Set the value of a state variable.
        
        Args:
            variable: The state variable to set.
            value: The value to set (0.0 to 1.0).
        """
        self.variables[variable] = max(0.0, min(1.0, value))
        self.timestamp = time.time()
    
    def adjust_variable(self, variable: StateVariable, delta: float) -> None:
        """
        Adjust the value of a state variable by a delta.
        
        Args:
            variable: The state variable to adjust.
            delta: The amount to adjust by (can be positive or negative).
        """
        current = self.variables.get(variable, 0.5)
        new_value = max(0.0, min(1.0, current + delta))
        self.variables[variable] = new_value
        self.timestamp = time.time()
    
    def get_activity(self) -> ActivityState:
        """
        Get the current activity state.
        
        Returns:
            ActivityState: The current activity.
        """
        return self.activity
    
    def set_activity(self, activity: ActivityState) -> None:
        """
        Set the current activity state.
        
        Args:
            activity: The new activity state.
        """
        self.activity = activity
        self.timestamp = time.time()
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the current state.
        
        Returns:
            Dict[str, Any]: State summary.
        """
        return {
            "activity": self.activity.value,
            "variables": {v.value: self.variables.get(v, 0.0) for v in StateVariable},
            "timestamp": self.timestamp,
        }


@dataclass
class StateHistory:
    """
    Represents the history of state changes.
    
    Attributes:
        states: List of historical states.
        max_size: Maximum number of states to keep in history.
    """
    states: List[State] = field(default_factory=list)
    max_size: int = 100
    
    def add_state(self, state: State) -> None:
        """
        Add a state to the history.
        
        Args:
            state: The state to add.
        """
        self.states.append(state)
        
        # Trim if necessary
        if len(self.states) > self.max_size:
            self.states = self.states[-self.max_size:]
    
    def get_states(self) -> List[State]:
        """
        Get all states in the history.
        
        Returns:
            List[State]: List of historical states.
        """
        return self.states.copy()
    
    def get_state_at(self, index: int) -> Optional[State]:
        """
        Get a state at a specific index.
        
        Args:
            index: Index of the state to get.
            
        Returns:
            Optional[State]: The state at the index, or None if not found.
        """
        if 0 <= index < len(self.states):
            return self.states[index]
        return None
    
    def get_latest(self) -> Optional[State]:
        """
        Get the latest state.
        
        Returns:
            Optional[State]: The latest state, or None if history is empty.
        """
        return self.states[-1] if self.states else None
    
    def clear(self) -> None:
        """Clear the state history."""
        self.states = []
    
    def get_changes(self) -> List[Dict[str, Any]]:
        """
        Get a list of state changes.
        
        Returns:
            List[Dict[str, Any]]: List of state changes.
        """
        changes = []
        
        for i in range(1, len(self.states)):
            prev = self.states[i-1]
            curr = self.states[i]
            
            change = {
                "timestamp": curr.timestamp,
                "activity_change": prev.activity != curr.activity,
                "variable_changes": {},
            }
            
            # Check for variable changes
            for var in StateVariable:
                prev_val = prev.variables.get(var, 0.0)
                curr_val = curr.variables.get(var, 0.0)
                
                if prev_val != curr_val:
                    change["variable_changes"][var.value] = {
                        "from": prev_val,
                        "to": curr_val,
                        "delta": curr_val - prev_val,
                    }
            
            if change["activity_change"] or change["variable_changes"]:
                changes.append(change)
        
        return changes
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the state history.
        
        Returns:
            Dict[str, Any]: State history statistics.
        """
        if not self.states:
            return {
                "total_states": 0,
                "duration": 0.0,
                "activity_distribution": {},
                "variable_averages": {},
            }
        
        # Calculate duration
        first_timestamp = self.states[0].timestamp
        last_timestamp = self.states[-1].timestamp
        duration = last_timestamp - first_timestamp
        
        # Activity distribution
        activity_distribution = {}
        for state in self.states:
            activity = state.activity.value
            activity_distribution[activity] = activity_distribution.get(activity, 0) + 1
        
        # Variable averages
        variable_averages = {}
        for var in StateVariable:
            values = [s.variables.get(var, 0.0) for s in self.states]
            variable_averages[var.value] = sum(values) / len(values) if values else 0.0
        
        return {
            "total_states": len(self.states),
            "duration": duration,
            "activity_distribution": activity_distribution,
            "variable_averages": variable_averages,
        }
