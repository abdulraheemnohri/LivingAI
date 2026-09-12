"""
LivingAI Tools Integration
==========================

Integrates the tools system with the agentic AI loop.
Provides seamless tool execution for agents.
"""

import logging
from typing import Dict, Any, Optional, List

from .executor import ToolExecutor
from .registry import ToolRegistry
from .permissions import ToolPermissionManager
from .sandbox import ToolSandbox, SandboxConfig
from .validator import ToolValidator


class ToolsIntegration:
    """
    Integrates the tools system with LivingAI agents.
    
    Responsibilities:
    - Provide unified tool access for agents
    - Manage tool execution pipeline
    - Handle tool permissions and validation
    - Integrate with agent memory and learning
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the ToolsIntegration.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Initialize all components
        self.registry = ToolRegistry()
        self.permission_manager = ToolPermissionManager()
        self.sandbox = ToolSandbox()
        self.validator = ToolValidator(permission_manager=self.permission_manager)
        self.executor = ToolExecutor(
            sandbox=self.sandbox,
            permission_manager=self.permission_manager,
            config=self.config
        )
        
        # Register hooks for agent integration
        self._register_agent_hooks()
        
        self.logger.info("ToolsIntegration initialized")
    
    def _register_agent_hooks(self) -> None:
        """Register hooks for agent-specific functionality."""
        # Hook to log tool executions for agent memory
        def log_execution(execution: Any, context: Dict[str, Any] = None) -> None:
            if context:
                agent_id = context.get('agent_id', 'unknown')
                task_id = context.get('task_id', 'unknown')
                self.logger.info(
                    f"Agent {agent_id} executed tool: {execution.tool_name}.{execution.method}"
                )
        
        self.executor.register_hook('post_execute', log_execution, 'agent_logger', 10)
    
    def execute_tool(
        self,
        tool_name: str,
        method: str = None,
        args: Dict[str, Any] = None,
        kwargs: Dict[str, Any] = None,
        context: Dict[str, Any] = None
    ) -> Any:
        """
        Execute a tool for an agent.
        
        Args:
            tool_name: Name of the tool
            method: Method to call
            args: Positional arguments
            kwargs: Keyword arguments
            context: Execution context (agent_id, task_id, etc.)
            
        Returns:
            Tool execution result
        """
        return self.executor.execute(
            tool_name=tool_name,
            method=method,
            args=args,
            kwargs=kwargs,
            context=context
        )
    
    def execute_command(
        self,
        command: str,
        context: Dict[str, Any] = None
    ) -> Any:
        """
        Execute a shell command for an agent.
        
        Args:
            command: Command to execute
            context: Execution context
            
        Returns:
            Command execution result
        """
        return self.executor.execute_command(command, context)
    
    def list_available_tools(self) -> List[str]:
        """
        List all available tools.
        
        Returns:
            List of tool names
        """
        return self.registry.list_tools()
    
    def get_tool_info(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a specific tool.
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            Tool information dictionary or None
        """
        info = self.registry.get_tool_info(tool_name)
        if info:
            return info.to_dict()
        return None
    
    def get_tool_methods(self, tool_name: str) -> List[str]:
        """
        Get available methods for a tool.
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            List of method names
        """
        return self.registry.get_tool_methods(tool_name)
    
    def validate_tool_call(
        self,
        tool_name: str,
        method: str,
        args: Dict[str, Any] = None,
        kwargs: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Validate a tool call before execution.
        
        Args:
            tool_name: Name of the tool
            method: Method to call
            args: Positional arguments
            kwargs: Keyword arguments
            
        Returns:
            Validation result
        """
        return self.validator.validate_input(tool_name, method, args, kwargs).to_dict()
    
    def check_tool_permission(
        self,
        tool_name: str,
        method: str = None,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Check if an agent has permission to use a tool.
        
        Args:
            tool_name: Name of the tool
            method: Method to call
            context: Execution context
            
        Returns:
            Permission check result
        """
        return self.permission_manager.check_tool_access(tool_name, method, None, context)
    
    def set_sandbox_config(self, config: SandboxConfig) -> None:
        """
        Set the sandbox configuration.
        
        Args:
            config: Sandbox configuration
        """
        self.sandbox.set_config(config)
        self.logger.info("Sandbox configuration updated")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get tools integration statistics.
        
        Returns:
            Statistics dictionary
        """
        return {
            'available_tools': len(self.list_available_tools()),
            'executor_stats': self.executor.get_stats(),
            'registry_count': self.registry.get_tool_count()
        }
    
    def cleanup(self) -> None:
        """Clean up resources."""
        self.sandbox.cleanup()
        self.logger.info("ToolsIntegration cleanup complete")


# Global instance for convenience
tools_integration = ToolsIntegration()
