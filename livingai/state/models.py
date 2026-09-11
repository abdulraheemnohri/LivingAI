# LivingAI State Models
# ======================
# This module defines the data models for the state system.

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from enum import Enum
import time
import copy


class StateVariableType(Enum):
    """Types of state variables."""
    ENERGY = "energy"
    FOCUS = "focus"
    CONFIDENCE = "confidence"
    UNCERTAINTY = "uncertainty"
    CURIOUSITY = "curiosity"
    URGENCY = "urgency"
    ATTENTION = "attention"
    SATISFACTION = "satisfaction"
    ACTIVITY = "activity"


class StateActivity(Enum):
    """Possible activity states."""
    IDLE = "idle"
    THINKING = "thinking"
    PLANNING = "planning"
    ACTING = "acting"
    LEARNING = "learning"
    REFLECTING = "reflecting"
    CONSOLIDATING = "consolidating"
    SLEEPING = "sleeping"
    WAITING = "waiting"


@dataclass
class StateVariable:
    """Represents a single state variable."""
    name: str
    var_type: StateVariableType
    value: float = 0.0
    min_value: float = 0.0
    max_value: float = 1.0
    description: str = ""
    last_updated: float = field(default_factory=time.time)
    
    def __post_init__(self):
        if isinstance(self.var_type, str):
            self.var_type = StateVariableType(self.var_type)
    
    def to_dict(self) -> Dict[str, Any]:
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
        if self.max_value == self.min_value:
            return 0
        normalized = (self.value - self.min_value) / (self.max_value - self.min_value)
        return int(normalized * 100)
    
    def get_bar(self, width: int = 20) -> str:
        percent = self.get_percent()
        filled = int(width * percent / 100)
        empty = width - filled
        return "█" * filled + "░" * empty


@dataclass
class State:
    """Represents the overall state of the LivingAI system."""
    variables: Dict[str, StateVariable] = field(default_factory=dict)
    activity: StateActivity = StateActivity.IDLE
    last_updated: float = field(default_factory=time.time)
    
    def __post_init__(self):
        if isinstance(self.activity, str):
            self.activity = StateActivity(self.activity)

    def copy(self) -> "State":
        return copy.deepcopy(self)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "variables": {name: var.to_dict() for name, var in self.variables.items()},
            "activity": self.activity.value,
            "last_updated": self.last_updated,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "State":
        variables = {}
        for name, var_data in data.get("variables", {}).items():
            variables[name] = StateVariable.from_dict(var_data)
        
        return cls(
            variables=variables,
            activity=data.get("activity", StateActivity.IDLE.value),
            last_updated=data.get("last_updated", time.time()),
        )
    
    def get_variable(self, name: str) -> Optional[StateVariable]:
        return self.variables.get(name)
    
    def set_variable(
        self,
        name: str,
        value: float,
        var_type: Optional[StateVariableType] = None
    ) -> None:
        if name not in self.variables:
            if var_type is None:
                var_type = StateVariableType.ENERGY
            self.variables[name] = StateVariable(
                name=name,
                var_type=var_type,
                value=value,
            )
        else:
            self.variables[name].value = value
            self.variables[name].last_updated = time.time()
        self.last_updated = time.time()
    
    def update_activity(self, activity: StateActivity) -> None:
        self.activity = activity
        self.last_updated = time.time()
    
    def get_summary(self) -> Dict[str, Any]:
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
    states: List[State] = field(default_factory=list)
    max_size: int = 100
    
    def add_state(self, state: State) -> None:
        self.states.append(state)
        if len(self.states) > self.max_size:
            self.states = self.states[-self.max_size:]
    
    def get_states(self) -> List[State]:
        return self.states.copy()
    
    def get_state_at(self, timestamp: float) -> Optional[State]:
        for state in reversed(self.states):
            if state.last_updated <= timestamp:
                return state
        return None
    
    def clear(self) -> None:
        self.states = []
    
    def get_stats(self) -> Dict[str, Any]:
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
        activity_distribution = {}
        for state in self.states:
            activity = state.activity.value
            activity_distribution[activity] = activity_distribution.get(activity, 0) + 1
        variable_averages = {}
        for state in self.states:
            for name, var in state.variables.items():
                if name not in variable_averages:
                    variable_averages[name] = []
                variable_averages[name].append(var.value)
        for name in variable_averages:
            values = variable_averages[name]
            variable_averages[name] = sum(values) / len(values) if values else 0.0
        return {
            "total_states": len(self.states),
            "duration": duration,
            "activity_distribution": activity_distribution,
            "variable_averages": variable_averages,
        }
