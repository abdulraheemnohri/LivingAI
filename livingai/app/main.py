"""
LivingAI Application
===================

Main application class for LivingAI.
"""

import logging
from typing import Dict, Any, Optional

from livingai.agentic_loop import AgenticLoop
from livingai.tools.integration import ToolsIntegration
from livingai.agents.manager import AgentManager


class LivingAIApp:
    """
    Main application class for LivingAI.
    
    Provides a unified interface to all LivingAI functionality.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the LivingAI application.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.loop = AgenticLoop(self.config)
        self.tools = ToolsIntegration(self.config)
        self.agents = AgentManager()
        
        self.logger.info("LivingAIApp initialized")
    
    def start(self, interval: float = 1.0) -> None:
        """
        Start the agentic loop.
        
        Args:
            interval: Time between cycles in seconds
        """
        self.logger.info(f"Starting LivingAI with interval={interval}s")
        self.loop.run_continuous(interval)
    
    def stop(self) -> None:
        """Stop the agentic loop."""
        self.logger.info("Stopping LivingAI")
        self.loop.stop()
    
    def run_once(self) -> None:
        """Run one cycle of the agentic loop."""
        self.logger.info("Running one cycle")
        self.loop.run_once()
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get the current status of the application.
        
        Returns:
            Status dictionary
        """
        return {
            'loop_status': self.loop.get_stats(),
            'tools_status': self.tools.get_stats(),
            'agents': self.agents.list_agents()
        }


# Global instance
app = LivingAIApp()
