# LivingAI State Models
# ======================
# This module defines the data models for the state system.

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from enum import Enum
import time


class StateVariableType(Enum):
    """Types of state variables."""
    ENERGY = "energy"           # Energy level (0.0 to 1.0)
    FOCUS = "focus"             # Focus level (0.0 to 1.0)
    CONFIDENCE = "confidence"   # Confidence level (0.0 to 1.0)
    UNCERTAINTY = "uncertainty" # Uncertainty level (0.0 to 1.0)
    CURIOUSITY = "curiosity"     # Curiosity level (0.0 to 1.0)
    URGENCY = "urgency"           # Urgency level (0.0 to 1.0)
    ATTENTION = "attention"       # Attention level (0.0 to 1.0)
    SATISFACTION = "satisfaction" # Satisfaction level (0.0 to 1.0)
    ACTIVITY = "activity"         # Current activity


class StateActivity(Enum):
    """Possible activity states."""
    IDLE = "idle"               # No active processing
    THINKING = "thinking"         # Processing information
    PLANNING = "planning"         # Creating a plan
    ACTING = "acting"             # Executing an action
    LEARNING = "learning"         # Learning from experience
    REFLECTING = "reflecting"     # Reflecting on interactions
    CONSOLIDATING = "consolidating" # Consolidating memories
    SLEEPING = "sleeping"         # In sleep mode
    WAITING = "waiting"           # Waiting for input or resources


@dataclass
class StateVariable:
    """
    Represents a single state variable.
    
    Attributes:
        name: Name of the variable.
        var_type: Type of the variable.
        value: Current value (0.0 to 1.0 for most types).
        min_value: Minimum possible value.
        max_value: Maximum possible value.
        description: Description of the variable.
        last_updated: Timestamp of last update.
    """
    name: str
    var_type: StateVariableType
    value: float = 0.0
    min_value: float = 0.0
    max_value: float = 1.0
    description: str = ""
    last_updated: float = field(default_factory=time.time)
    
    def __post_init__(self):
        """Post-initialization processing."""
        if isinstance(self.var_type, str):
            self.var_type = StateVariableType(self.var_type)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the state variable to a dictionary.
        
        Returns:
            Dict[str, Any]: Dictionary representation.
        """
        return {
            "name": self.name,
            "type": self.var_type.value,
            "value": self.value,
            "min_value": self.min_value,
            "max_value": self.max_value,
            "description": self.description,
            "last_updated": self.last_updated,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StateVariable":
        """
        Create a StateVariable from a dictionary.
        
        Args:
            data: Dictionary with state variable data.
            
        Returns:
            StateVariable: State variable instance.
        """
        return cls(
            name=data.get("name", ""),
            var_type=data.get("type", StateVariableType.ENERGY.value),
            value=data.get("value", 0.0),
            min_value=data.get("min_value", 0.0),
            max_value=data.get("max_value", 1.0),
            description=data.get("description", ""),
            last_updated=data.get("last_updated", time.time()),
        )
    
    def get_percent(self) -> int:
        """
        Get the value as a percentage.
        
        Returns:
            int: Value as a percentage (0-100).
        """
        if self.max_value == self.min_value:
            return 0
        
        normalized = (self.value - self.min_value) / (self.max_value - self.min_value)
        return int(normalized * 100)
    
    def get_bar(self, width: int = 20) -> str:
        """
        Get a visual bar representation of the value.
        
        Args:
            width: Width of the bar in characters.
            
        Returns:
            str: Visual bar representation.
        """
        percent = self.get_percent()
        filled = int(width * percent / 100)
        empty = width - filled
        
        return "█" * filled + "░" * empty


@dataclass
class State:
    """
    Represents the overall state of the LivingAI system.
    
    Attributes:
        variables: Dictionary of state variables.
        activity: Current activity.
        last_updated: Timestamp of last update.
    """
    variables: Dict[str, StateVariable] = field(default_factory=dict)
    activity: StateActivity = StateActivity.IDLE
    last_updated: float = field(default_factory=time.time)
    
    def __post_init__(self):
        """Post-initialization processing."""
        if isinstance(self.activity, str):
            self.activity = StateActivity(self.activity)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the state to a dictionary.
        
        Returns:
            Dict[str, Any]: Dictionary representation.
        """
        return {
            "variables": {name: var.to_dict() for name, var in self.variables.items()},
            "activity": self.activity.value,
            "last_updated": self.last_updated,
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
        for name, var_data in data.get("variables", {}).items():
            variables[name] = StateVariable.from_dict(var_data)
        
        return cls(
            variables=variables,
            activity=data.get("activity", StateActivity.IDLE.value),
            last_updated=data.get("last_updated", time.time()),
        )
    
    def get_variable(self, name: str) -> Optional[StateVariable]:
        """
        Get a state variable by name.
        
        Args:
            name: Name of the variable.
            
        Returns:
            Optional[StateVariable]: The variable, or None if not found.
        """
        return self.variables.get(name)
    
    def set_variable(
        self,
        name: str,
        value: float,
        var_type: Optional[StateVariableType] = None
    ) -> None:
        """
        Set a state variable.
        
        Args:
            name: Name of the variable.
            value: Value to set.
            var_type: Optional type of the variable.
        """
        if name not in self.variables:
            # Create new variable
            if var_type is None:
                var_type = StateVariableType.ENERGY
            
            self.variables[name] = StateVariable(
                name=name,
                var_type=var_type,
                value=value,
            )
        else:
            # Update existing variable
            self.variables[name].value = value
            self.variables[name].last_updated = time.time()
        
        self.last_updated = time.time()
    
    def update_activity(self, activity: StateActivity) -> None:
        """
        Update the current activity.
        
        Args:
            activity: New activity.
        """
        self.activity = activity
        self.last_updated = time.time()
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the current state.
        
        Returns:
            Dict[str, Any]: State summary.
        """
        return {
            "activity": self.activity.value,
            "variables": {
                name: {
                    "value": var.value,
                    "percent": var.get_percent(),
                    "bar": var.get_bar(),
                }
                for name, var in self.variables.items()
            },
            "last_updated": self.last_updated,
        }


@dataclass
class StateHistory:
    """
    Represents the history of state changes.
    
    Attributes:
        states: List of historical states.
        max_size: Maximum number of states to keep.
    """
    states: List[State] = field(default_factory=list)
    max_size: int = 100
    
    def add_state(self, state: State) -> None:
        """
        Add a state to the history.
        
        Args:
            state: State to add.
        """
        self.states.append(state)
        
        # Trim if over max size
        if len(self.states) > self.max_size:
            self.states = self.states[-self.max_size:]
    
    def get_states(self) -> List[State]:
        """
        Get all states in the history.
        
        Returns:
            List[State]: List of historical states.
        """
        return self.states.copy()
    
    def get_state_at(self, timestamp: float) -> Optional[State]:
        """
        Get the state at or before a specific timestamp.
        
        Args:
            timestamp: Timestamp to search for.
            
        Returns:
            Optional[State]: State at or before the timestamp, or None if not found.
        """
        for state in reversed(self.states):
            if state.last_updated <= timestamp:
                return state
        
        return None
    
    def clear(self) -> None:
        """Clear the history."""
        self.states = []
    
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
        
        first_timestamp = self.states[0].last_updated
        last_timestamp = self.states[-1].last_updated
        duration = last_timestamp - first_timestamp
        
        # Activity distribution
        activity_distribution = {}
        for state in self.states:
            activity = state.activity.value
            activity_distribution[activity] = activity_distribution.get(activity, 0) + 1
        
        # Variable averages
        variable_averages = {}
        for state in self.states:
            for name, var in state.variables.items():
                if name not in variable_averages:
                    variable_averages[name] = []
                variable_averages[name].append(var.value)
        
        # Calculate averages
        for name in variable_averages:
            values = variable_averages[name]
            variable_averages[name] = sum(values) / len(values) if values else 0.0
        
        return {
            "total_states": len(self.states),
            "duration": duration,
            "activity_distribution": activity_distribution,
            "variable_averages": variable_averages,
        }
