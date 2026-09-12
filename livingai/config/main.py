"""
LivingAI Configuration
======================

Configuration management for LivingAI.
"""

import json
import os
from typing import Dict, Any, Optional
from dataclasses import dataclass, field, asdict


@dataclass
class Config:
    """
    Configuration for LivingAI.
    
    Attributes:
        sandbox_config: Configuration for the sandbox environment
        tool_permissions: Permission configuration for tools
        agent_config: Configuration for agents
        memory_config: Configuration for memory
        learning_config: Configuration for learning
    """
    sandbox_config: Dict[str, Any] = field(default_factory=dict)
    tool_permissions: Dict[str, Any] = field(default_factory=dict)
    agent_config: Dict[str, Any] = field(default_factory=dict)
    memory_config: Dict[str, Any] = field(default_factory=dict)
    learning_config: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def load(cls, path: str) -> 'Config':
        """
        Load configuration from a JSON file.
        
        Args:
            path: Path to the configuration file
            
        Returns:
            Config instance
        """
        if not os.path.exists(path):
            return cls()
        
        with open(path, 'r') as f:
            data = json.load(f)
        
        return cls(**data)
    
    def save(self, path: str) -> None:
        """
        Save configuration to a JSON file.
        
        Args:
            path: Path to save the configuration file
        """
        data = self.to_dict()
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'sandbox_config': self.sandbox_config,
            'tool_permissions': self.tool_permissions,
            'agent_config': self.agent_config,
            'memory_config': self.memory_config,
            'learning_config': self.learning_config
        }
    
    @classmethod
    def default(cls) -> 'Config':
        """Create a default configuration."""
        return cls(
            sandbox_config={
                'max_execution_time': 30.0,
                'max_memory': 256 * 1024 * 1024,
                'max_cpu_time': 60.0
            },
            tool_permissions={
                'default': 'restricted'
            },
            agent_config={
                'max_agents': 10,
                'max_tasks_per_agent': 100
            },
            memory_config={
                'max_memory_size': 10000,
                'max_context_length': 4096
            },
            learning_config={
                'enabled': True,
                'model_update_interval': 100
            }
        )
