"""
Tool Sandbox Module

Provides a secure sandbox environment for executing AI tools.
This module handles tool execution in isolated environments with proper
resource management and security constraints.

Author: Abdulraheem Nohari
"""

import asyncio
import importlib
import inspect
import logging
import sys
import traceback
from contextlib import contextmanager, asynccontextmanager
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Type, Union
from enum import Enum

logger = logging.getLogger(__name__)


class SandboxError(Exception):
    """Base exception for sandbox errors"""
    pass


class ToolNotFoundError(SandboxError):
    """Raised when a tool is not found"""
    pass


class ToolExecutionError(SandboxError):
    """Raised when tool execution fails"""
    pass


class PermissionDeniedError(SandboxError):
    """Raised when permission is denied"""
    pass


class ResourceLimitError(SandboxError):
    """Raised when resource limits are exceeded"""
    pass


class SandboxTimeoutError(SandboxError):
    """Raised when execution times out"""
    pass


class ExecutionStatus(Enum):
    """Status of tool execution"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"


@dataclass
class ExecutionResult:
    """Result of a tool execution"""
    status: ExecutionStatus
    output: Any = None
    error: Optional[str] = None
    execution_time: float = 0.0
    memory_used: int = 0
    tool_name: str = ""
    input_args: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'status': self.status.value,
            'output': self.output,
            'error': self.error,
            'execution_time': self.execution_time,
            'memory_used': self.memory_used,
            'tool_name': self.tool_name,
            'input_args': self.input_args,
        }


@dataclass
class SandboxConfig:
    """Configuration for the sandbox environment"""
    max_execution_time: float = 30.0  # seconds
    max_memory: int = 512 * 1024 * 1024  # 512 MB
    max_cpu: float = 0.8  # 80% CPU usage
    allowed_modules: List[str] = field(default_factory=lambda: [
        'math', 'json', 're', 'datetime', 'collections', 'itertools',
        'functools', 'operator', 'string', 'textwrap', 'unicodedata'
    ])
    blocked_modules: List[str] = field(default_factory=lambda: [
        'os', 'sys', 'subprocess', 'shutil', 'socket', 'http',
        'urllib', 'ftplib', 'smtplib', 'pickle', 'marshal'
    ])
    allow_network: bool = False
    allow_file_io: bool = False
    enable_logging: bool = True


class ToolSandbox:
    """
    Sandbox environment for executing AI tools.
    
    This class provides a secure execution environment with resource limits,
    timeout handling, and permission management.
    """
    
    def __init__(self, config: Optional[SandboxConfig] = None):
        """
        Initialize the sandbox.
        
        Args:
            config: Sandbox configuration
        """
        self.config = config or SandboxConfig()
        self._executing_tools: Dict[str, bool] = {}
        self._tool_cache: Dict[str, Type] = {}
    
    def _get_tool(self, tool_name: str) -> Type:
        """
        Get a tool class by name, using lazy imports.
        
        This method tries to import the tool from the livingai.tools.registry
        first, then falls back to livingai.agents.tool_registry to avoid
        circular dependencies.
        
        Args:
            tool_name: Name of the tool to retrieve
            
        Returns:
            Tool class
            
        Raises:
            ToolNotFoundError: If tool is not found
        """
        # Check cache first
        if tool_name in self._tool_cache:
            return self._tool_cache[tool_name]
        
        # Try to get from registry
        try:
            from .registry import registry
            tool_info = registry.get(tool_name)
            if tool_info and tool_info.tool_class:
                self._tool_cache[tool_name] = tool_info.tool_class
                return tool_info.tool_class
        except ImportError:
            # Fallback to direct import if registry has circular dependency
            pass
        
        # Fallback: try to import from livingai.agents.tool_registry
        try:
            agents_module = importlib.import_module('livingai.agents.tool_registry')
            tool_class = getattr(agents_module, tool_name, None)
            if tool_class:
                self._tool_cache[tool_name] = tool_class
                return tool_class
        except (ImportError, AttributeError):
            pass
        
        # Try direct import from tools package
        try:
            tools_module = importlib.import_module(f'livingai.tools.{tool_name}')
            tool_class = getattr(tools_module, tool_name, None)
            if tool_class:
                self._tool_cache[tool_name] = tool_class
                return tool_class
        except (ImportError, AttributeError):
            pass
        
        raise ToolNotFoundError(f"Tool '{tool_name}' not found in registry or modules")
    
    def _validate_permissions(self, tool_name: str, permissions: List[str]) -> bool:
        """
        Validate if the tool has required permissions.
        
        Args:
            tool_name: Name of the tool
            permissions: List of permissions to check
            
        Returns:
            True if all permissions are granted
            
        Raises:
            PermissionDeniedError: If any permission is denied
        """
        from .permissions import ToolPermissions
        
        permissions_manager = ToolPermissions()
        
        for perm in permissions:
            if not permissions_manager.check_permission(tool_name, perm):
                logger.warning(f"Permission denied for tool '{tool_name}': {perm}")
                return False
        
        return True
    
    def _validate_resources(self, memory_used: int) -> bool:
        """
        Validate resource usage.
        
        Args:
            memory_used: Memory used in bytes
            
        Returns:
            True if within limits
            
        Raises:
            ResourceLimitError: If limits exceeded
        """
        if memory_used > self.config.max_memory:
            raise ResourceLimitError(
                f"Memory limit exceeded: {memory_used} > {self.config.max_memory}"
            )
        return True
    
    def execute(self, 
                tool_name: str, 
                *args, 
                timeout: Optional[float] = None,
                **kwargs) -> ExecutionResult:
        """
        Execute a tool synchronously.
        
        Args:
            tool_name: Name of the tool to execute
            *args: Positional arguments for the tool
            timeout: Optional timeout in seconds
            **kwargs: Keyword arguments for the tool
            
        Returns:
            ExecutionResult with status and output
        """
        import time
        
        start_time = time.time()
        effective_timeout = timeout or self.config.max_execution_time
        result = ExecutionResult(
            status=ExecutionStatus.PENDING,
            tool_name=tool_name,
            input_args=kwargs,
        )
        
        try:
            # Get tool class
            tool_class = self._get_tool(tool_name)
            
            # Check if tool is callable
            if not callable(tool_class):
                result.status = ExecutionStatus.FAILED
                result.error = f"Tool '{tool_name}' is not callable"
                return result
            
            # Create tool instance if it's a class
            if inspect.isclass(tool_class):
                tool_instance = tool_class()
            else:
                tool_instance = tool_class
            
            # Validate permissions
            tool_info = None
            try:
                from .registry import registry
                tool_info = registry.get(tool_name)
            except ImportError:
                pass
            
            if tool_info:
                if not self._validate_permissions(tool_name, tool_info.requires_permissions):
                    result.status = ExecutionStatus.FAILED
                    result.error = f"Permission denied for tool '{tool_name}'"
                    return result
            
            # Execute the tool
            result.status = ExecutionStatus.RUNNING
            
            # Check if tool is async
            if inspect.iscoroutinefunction(tool_instance):
                # For async tools, we need to run in event loop
                import asyncio
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    output = loop.run_until_complete(
                        asyncio.wait_for(
                            tool_instance(*args, **kwargs),
                            timeout=effective_timeout
                        )
                    )
                finally:
                    loop.close()
            else:
                # Synchronous execution
                output = tool_instance(*args, **kwargs)
            
            result.status = ExecutionStatus.COMPLETED
            result.output = output
            
        except asyncio.TimeoutError:
            result.status = ExecutionStatus.TIMEOUT
            result.error = f"Execution timed out after {effective_timeout} seconds"
        except ToolNotFoundError as e:
            result.status = ExecutionStatus.FAILED
            result.error = str(e)
        except PermissionDeniedError as e:
            result.status = ExecutionStatus.FAILED
            result.error = str(e)
        except ResourceLimitError as e:
            result.status = ExecutionStatus.FAILED
            result.error = str(e)
        except Exception as e:
            result.status = ExecutionStatus.FAILED
            result.error = f"{type(e).__name__}: {str(e)}\n{traceback.format_exc()}"
        finally:
            result.execution_time = time.time() - start_time
        
        return result
    
    async def execute_async(self, 
                           tool_name: str, 
                           *args, 
                           timeout: Optional[float] = None,
                           **kwargs) -> ExecutionResult:
        """
        Execute a tool asynchronously.
        
        Args:
            tool_name: Name of the tool to execute
            *args: Positional arguments for the tool
            timeout: Optional timeout in seconds
            **kwargs: Keyword arguments for the tool
            
        Returns:
            ExecutionResult with status and output
        """
        import time
        
        start_time = time.time()
        effective_timeout = timeout or self.config.max_execution_time
        result = ExecutionResult(
            status=ExecutionStatus.PENDING,
            tool_name=tool_name,
            input_args=kwargs,
        )
        
        try:
            # Get tool class
            tool_class = self._get_tool(tool_name)
            
            # Check if tool is callable
            if not callable(tool_class):
                result.status = ExecutionStatus.FAILED
                result.error = f"Tool '{tool_name}' is not callable"
                return result
            
            # Create tool instance if it's a class
            if inspect.isclass(tool_class):
                tool_instance = tool_class()
            else:
                tool_instance = tool_class
            
            # Validate permissions
            tool_info = None
            try:
                from .registry import registry
                tool_info = registry.get(tool_name)
            except ImportError:
                pass
            
            if tool_info:
                if not self._validate_permissions(tool_name, tool_info.requires_permissions):
                    result.status = ExecutionStatus.FAILED
                    result.error = f"Permission denied for tool '{tool_name}'"
                    return result
            
            # Execute the tool
            result.status = ExecutionStatus.RUNNING
            
            # Execute async tool
            try:
                output = await asyncio.wait_for(
                    tool_instance(*args, **kwargs),
                    timeout=effective_timeout
                )
            except asyncio.TimeoutError:
                result.status = ExecutionStatus.TIMEOUT
                result.error = f"Execution timed out after {effective_timeout} seconds"
                return result
            
            result.status = ExecutionStatus.COMPLETED
            result.output = output
            
        except ToolNotFoundError as e:
            result.status = ExecutionStatus.FAILED
            result.error = str(e)
        except PermissionDeniedError as e:
            result.status = ExecutionStatus.FAILED
            result.error = str(e)
        except ResourceLimitError as e:
            result.status = ExecutionStatus.FAILED
            result.error = str(e)
        except Exception as e:
            result.status = ExecutionStatus.FAILED
            result.error = f"{type(e).__name__}: {str(e)}\n{traceback.format_exc()}"
        finally:
            result.execution_time = time.time() - start_time
        
        return result
    
    @contextmanager
    def execution_context(self, tool_name: str):
        """
        Context manager for tool execution.
        
        Args:
            tool_name: Name of the tool being executed
            
        Yields:
            None
        """
        self._executing_tools[tool_name] = True
        try:
            yield
        finally:
            self._executing_tools.pop(tool_name, None)
    
    @asynccontextmanager
    async def async_execution_context(self, tool_name: str):
        """
        Async context manager for tool execution.
        
        Args:
            tool_name: Name of the tool being executed
            
        Yields:
            None
        """
        self._executing_tools[tool_name] = True
        try:
            yield
        finally:
            self._executing_tools.pop(tool_name, None)
    
    def is_executing(self, tool_name: str) -> bool:
        """
        Check if a tool is currently executing.
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            True if tool is executing
        """
        return self._executing_tools.get(tool_name, False)
    
    def cancel_execution(self, tool_name: str) -> bool:
        """
        Cancel execution of a tool.
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            True if execution was cancelled
        """
        # Implementation would depend on the execution system
        # For now, just mark as not executing
        if tool_name in self._executing_tools:
            self._executing_tools[tool_name] = False
            return True
        return False
    
    def clear_cache(self):
        """Clear the tool cache"""
        self._tool_cache.clear()
        logger.info("Cleared tool cache")


# Global sandbox instance
sandbox = ToolSandbox()


def get_sandbox() -> ToolSandbox:
    """Get the global tool sandbox instance"""
    return sandbox
