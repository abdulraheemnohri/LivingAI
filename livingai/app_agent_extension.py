"""
App Agent Extension
==================

Extension to LivingAIApp that adds agent management capabilities.
"""

import os
from typing import Optional


class AgentManagerWrapper:
    """
    Wrapper for AgentManager that integrates with LivingAIApp.
    
    This provides a simple interface for the app to manage agents.
    """
    
    def __init__(self, app):
        """Initialize the agent manager wrapper."""
        self.app = app
        self._agent_manager = None
    
    @property
    def agent_manager(self):
        """Get or create the agent manager."""
        if self._agent_manager is None:
            from .agents.manager import AgentManager
            db_path = os.path.expanduser('~/.livingai/data/agents.db')
            self._agent_manager = AgentManager(db_path)
        return self._agent_manager
    
    def initialize_agents(self):
        """Initialize the agent system."""
        # Ensure database exists
        db_path = os.path.expanduser('~/.livingai/data/agents.db')
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # Initialize agent manager
        _ = self.agent_manager
        
        # Load any existing agents
        return True


def add_agent_support(app):
    """
    Add agent support to a LivingAIApp instance.
    
    Args:
        app: The LivingAIApp instance to extend
    """
    # Add agent manager
    app.agent_wrapper = AgentManagerWrapper(app)
    
    # Add convenience property
    @property
    def agent_manager(app_inner):
        return app_inner.agent_wrapper.agent_manager
    
    # Initialize agents on app startup
    if hasattr(app, '_initialize_components'):
        original_init = app._initialize_components
        def new_init():
            original_init()
            app.agent_wrapper.initialize_agents()
        app._initialize_components = new_init
