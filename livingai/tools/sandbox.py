"""
LivingAI Tool Sandbox
====================

Provides a safe execution environment for tools with restrictions and monitoring.
"""

import logging
import os
import sys
import time
import tempfile
import shlex
import subprocess
import resource
from typing import Dict, Any, Optional, List, Callable, Tuple
from dataclasses import dataclass, field
from pathlib import Path
from contextlib import contextmanager
import threading

from .permissions import ToolPermissionManager, ToolPermission
from livingai.security.policy import RiskLevel


@dataclass
class SandboxResult:
    """Result of a sandboxed tool execution."""
    output: str
    error: Optional[str] = None
    returncode: int = 0
    execution_time: float = 0.0
    resource_usage: Dict[str, Any] = field(default_factory=dict)
    violated_restrictions: List[str] = field(default_factory=list)
    was_killed: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'output': self.output,
            'error': self.error,
            'returncode': self.returncode,
            'execution_time': self.execution_time,
            'resource_usage': self.resource_usage,
            'violated_restrictions': self.violated_restrictions,
            'was_killed': self.was_killed
        }
    
    @property
    def success(self) -> bool:
        """Check if execution was successful."""
        return self.returncode == 0 and not self.was_killed and not self.violated_restrictions


@dataclass
class SandboxConfig:
    """Configuration for the sandbox environment."""
    max_execution_time: float = 30.0
    max_memory: int = 256 * 1024 * 1024
    max_cpu_time: float = 60.0
    max_output_size: int = 1024 * 1024
    allowed_paths: List[str] = field(default_factory=list)
    blocked_paths: List[str] = field(default_factory=list)
    allowed_commands: List[str] = field(default_factory=list)
    blocked_commands: List[str] = field(default_factory=list)
    network_access: bool = False
    filesystem_write: bool = True
    subprocess_allowed: bool = False
    
    @classmethod
    def safe_default(cls) -> 'SandboxConfig':
        """Create a safe default sandbox configuration."""
        return cls(
            max_execution_time=10.0,
            max_memory=128 * 1024 * 1024,
            max_cpu_time=30.0,
            max_output_size=512 * 1024,
            blocked_paths=[
                '/', '/bin', '/sbin', '/usr', '/etc', '/var',
                '/proc', '/sys', '/dev', '/boot', '/root'
            ],
            blocked_commands=[
                'rm', 'mv', 'cp', 'dd', 'chmod', 'chown', 'su',
                'sudo', 'kill', 'pkill', 'killall', 'apt', 'yum',
                'dnf', 'pip', 'npm', 'yarn', 'wget', 'curl',
                'ssh', 'scp', 'rsync', 'nc', 'netcat', 'telnet',
                'python', 'python3', 'bash', 'sh', 'zsh', 'fish'
            ],
            network_access=False,
            filesystem_write=False,
            subprocess_allowed=False
        )
    
    @classmethod
    def restricted_default(cls) -> 'SandboxConfig':
        """Create a restricted but functional sandbox configuration."""
        return cls(
            max_execution_time=30.0,
            max_memory=256 * 1024 * 1024,
            max_cpu_time=60.0,
            max_output_size=1024 * 1024,
            allowed_paths=[
                os.path.expanduser('~/.livingai'),
                os.path.expanduser('~/Downloads'),
                os.path.expanduser('~/Documents')
            ],
            blocked_paths=[
                '/', '/bin', '/sbin', '/usr', '/etc', '/var',
                '/proc', '/sys', '/dev', '/boot', '/root'
            ],
            allowed_commands=[
                'ls', 'pwd', 'cat', 'grep', 'find', 'head',
                'tail', 'wc', 'sort', 'uniq', 'cut', 'awk',
                'sed', 'echo', 'test', 'stat', 'file'
            ],
            blocked_commands=[
                'rm', 'mv', 'cp', 'dd', 'chmod', 'chown', 'su',
                'sudo', 'kill', 'pkill', 'killall', 'apt',
                'yum', 'dnf', 'pip', 'npm', 'yarn'
            ],
            network_access=False,
            filesystem_write=True,
            subprocess_allowed=False
        )
    
    @classmethod
    def developer_default(cls) -> 'SandboxConfig':
        """Create a developer-friendly sandbox configuration."""
        return cls(
            max_execution_time=60.0,
            max_memory=512 * 1024 * 1024,
            max_cpu_time=120.0,
            max_output_size=2 * 1024 * 1024,
            allowed_paths=[
                os.path.expanduser('~/.livingai'),
                os.path.expanduser('~/'),
                '/tmp'
            ],
            blocked_paths=[
                '/', '/bin', '/sbin', '/usr', '/etc', '/var',
                '/proc', '/sys', '/dev', '/boot', '/root'
            ],
            allowed_commands=[
                'ls', 'pwd', 'cat', 'grep', 'find', 'head',
                'tail', 'wc', 'sort', 'uniq', 'cut', 'awk',
                'sed', 'echo', 'test', 'stat', 'file', 'mv',
                'cp', 'mkdir', 'rmdir', 'touch'
            ],
            blocked_commands=[
                'rm', 'dd', 'chmod', 'chown', 'su',
                'sudo', 'kill', 'pkill', 'killall', 'apt',
                'yum', 'dnf', 'pip', 'npm', 'yarn',
                'wget', 'curl', 'ssh', 'scp'
            ],
            network_access=True,
            filesystem_write=True,
            subprocess_allowed=True
        )


class SandboxViolation(Exception):
    """Exception raised when a sandbox restriction is violated."""
    pass


class ToolSandbox:
    """
    Provides a safe execution environment for tools.
    
    Responsibilities:
    - Restrict filesystem access
    - Limit resource usage
    - Block dangerous commands
    - Monitor execution
    - Sanitize inputs and outputs
    """
    
    def __init__(
        self,
        config: SandboxConfig = None,
        permission_manager: ToolPermissionManager = None
    ):
        self.config = config or SandboxConfig.safe_default()
        self.permission_manager = permission_manager
        self.logger = logging.getLogger(__name__)
        self._temp_dir = tempfile.mkdtemp(prefix='livingai_sandbox_')
        self._lock = threading.Lock()
        self._setup_resource_limits()
    
    def _setup_resource_limits(self) -> None:
        try:
            soft, hard = resource.getrlimit(resource.RLIMIT_AS)
            resource.setrlimit(
                resource.RLIMIT_AS,
                (self.config.max_memory, self.config.max_memory * 2)
            )
            soft, hard = resource.getrlimit(resource.RLIMIT_CPU)
            resource.setrlimit(
                resource.RLIMIT_CPU,
                (int(self.config.max_cpu_time), int(self.config.max_cpu_time * 2))
            )
        except (resource.error, ValueError) as e:
            self.logger.warning(f"Could not set resource limits: {e}")
    
    def execute(
        self,
        tool_name: str,
        method: str,
        args: Dict[str, Any] = None,
        kwargs: Dict[str, Any] = None
    ) -> SandboxResult:
        start_time = time.time()
        args = args or {}
        kwargs = kwargs or {}
        
        result = SandboxResult(
            output="",
            returncode=0,
            execution_time=0.0,
            resource_usage={}
        )
        
        try:
            if self.permission_manager:
                perm_check = self.permission_manager.check_tool_access(
                    tool_name, method, args
                )
                if not perm_check.get('allowed', False):
                    result.error = perm_check.get('reason', 'Permission denied')
                    result.returncode = 1
                    return result
            
            tool = self._get_tool(tool_name)
            if not tool:
                result.error = f"Tool '{tool_name}' not found"
                result.returncode = 1
                return result
            
            method_func = getattr(tool, method, None)
            if not method_func or not callable(method_func):
                result.error = f"Method '{method}' not found in tool '{tool_name}'"
                result.returncode = 1
                return result
            
            if not self._validate_arguments(tool_name, method, args, kwargs):
                result.error = "Argument validation failed"
                result.returncode = 1
                return result
            
            try:
                output = self._execute_with_timeout(
                    method_func, args, kwargs, self.config.max_execution_time
                )
                result.output = str(output) if output is not None else ""
            except TimeoutError:
                result.error = f"Execution timed out after {self.config.max_execution_time} seconds"
                result.returncode = 1
                result.was_killed = True
                return result
        except SandboxViolation as e:
            result.error = str(e)
            result.returncode = 1
            result.violated_restrictions.append(str(e))
            return result
        except Exception as e:
            result.error = str(e)
            result.returncode = 1
            return result
        finally:
            result.execution_time = time.time() - start_time
        
        return result
    
    def execute_command(
        self,
        command: str,
        timeout: float = None
    ) -> SandboxResult:
        start_time = time.time()
        timeout = timeout or self.config.max_execution_time
        
        result = SandboxResult(
            output="",
            returncode=0,
            execution_time=0.0
        )
        
        try:
            parsed = shlex.split(command)
            cmd = parsed[0]
            
            if not self._is_command_allowed(cmd):
                result.error = f"Command '{cmd}' is not allowed in sandbox"
                result.returncode = 1
                result.violated_restrictions.append(f"blocked_command:{cmd}")
                return result
            
            for arg in parsed[1:]:
                if arg.startswith('/') or '..' in arg:
                    if not self._is_path_allowed(arg):
                        result.error = f"Path '{arg}' is not allowed in sandbox"
                        result.returncode = 1
                        result.violated_restrictions.append(f"blocked_path:{arg}")
                        return result
            
            try:
                proc = subprocess.Popen(
                    parsed,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    cwd=self._temp_dir,
                    env=self._get_safe_env()
                )
                
                try:
                    stdout, stderr = proc.communicate(timeout=timeout)
                    result.output = stdout.decode('utf-8', errors='replace')
                    result.error = stderr.decode('utf-8', errors='replace')
                    result.returncode = proc.returncode
                except subprocess.TimeoutExpired:
                    proc.kill()
                    stdout, stderr = proc.communicate()
                    result.output = stdout.decode('utf-8', errors='replace') if stdout else ""
                    result.error = f"Command timed out after {timeout} seconds"
                    result.returncode = 1
                    result.was_killed = True
            except OSError as e:
                result.error = f"Command execution failed: {e}"
                result.returncode = 1
        except SandboxViolation as e:
            result.error = str(e)
            result.returncode = 1
            result.violated_restrictions.append(str(e))
        except Exception as e:
            result.error = str(e)
            result.returncode = 1
        finally:
            result.execution_time = time.time() - start_time
        
        if len(result.output) > self.config.max_output_size:
            result.output = result.output[:self.config.max_output_size] + f"\n\n[Output truncated. Total size: {len(result.output)} bytes]"
        if len(result.error or "") > self.config.max_output_size:
            result.error = (result.error or "")[:self.config.max_output_size] + f"\n\n[Error truncated]"
        
        return result
    
    def _get_tool(self, tool_name: str) -> Any:
        from livingai.agents.tool_registry import ToolRegistry
        registry = ToolRegistry()
        return registry.get_tool(tool_name)
    
    def _is_command_allowed(self, command: str) -> bool:
        for blocked in self.config.blocked_commands:
            if command == blocked or command.endswith(f"/{blocked}"):
                return False
        if self.config.allowed_commands:
            return command in self.config.allowed_commands
        return True
    
    def _is_path_allowed(self, path: str) -> bool:
        path = os.path.abspath(os.path.normpath(path))
        for blocked in self.config.blocked_paths:
            blocked = os.path.abspath(os.path.normpath(blocked))
            if path == blocked or path.startswith(blocked + '/'):
                return False
        if self.config.allowed_paths:
            for allowed in self.config.allowed_paths:
                allowed = os.path.abspath(os.path.normpath(allowed))
                if path == allowed or path.startswith(allowed + '/'):
                    return True
            return False
        return True
    
    def _validate_arguments(
        self,
        tool_name: str,
        method: str,
        args: Dict[str, Any],
        kwargs: Dict[str, Any]
    ) -> bool:
        all_args = {**args, **kwargs}
        for arg_name, arg_value in all_args.items():
            if isinstance(arg_value, str):
                if arg_value.startswith('/') or '..' in arg_value or arg_value.endswith('/'):
                    if not self._is_path_allowed(arg_value):
                        raise SandboxViolation(f"Path argument '{arg_name}={arg_value}' is not allowed")
        return True
    
    def _get_safe_env(self) -> Dict[str, str]:
        env = os.environ.copy()
        dangerous_vars = [
            'PATH', 'LD_PRELOAD', 'LD_LIBRARY_PATH',
            'PYTHONPATH', 'CLASSPATH', 'PERL5LIB',
            'HOME', 'USER', 'SHELL', 'TERM'
        ]
        for var in dangerous_vars:
            if var in env:
                del env[var]
        env['PATH'] = '/usr/bin:/bin'
        env['HOME'] = self._temp_dir
        env['USER'] = 'sandbox'
        return env
    
    def _execute_with_timeout(
        self,
        func: Callable,
        args: Dict[str, Any],
        kwargs: Dict[str, Any],
        timeout: float
    ) -> Any:
        import threading
        result = [None]
        exception = [None]
        
        def target():
            try:
                result[0] = func(*args, **kwargs)
            except Exception as e:
                exception[0] = e
        
        thread = threading.Thread(target=target)
        thread.daemon = True
        thread.start()
        thread.join(timeout=timeout)
        
        if thread.is_alive():
            raise TimeoutError(f"Execution timed out after {timeout} seconds")
        if exception[0]:
            raise exception[0]
        return result[0]
    
    def validate_path(self, path: str, operation: str = 'read') -> bool:
        if not self._is_path_allowed(path):
            return False
        if operation == 'write' and not self.config.filesystem_write:
            return False
        if operation == 'execute' and not self.config.subprocess_allowed:
            return False
        return True
    
    def get_config(self) -> SandboxConfig:
        return self.config
    
    def set_config(self, config: SandboxConfig) -> None:
        self.config = config
        self._setup_resource_limits()
        self.logger.info("Sandbox configuration updated")
    
    def cleanup(self) -> None:
        try:
            import shutil
            shutil.rmtree(self._temp_dir, ignore_errors=True)
        except Exception as e:
            self.logger.warning(f"Failed to cleanup sandbox temp dir: {e}")
    
    @contextmanager
    def sandbox_context(self, config: SandboxConfig = None):
        old_config = self.config
        if config:
            self.config = config
            self._setup_resource_limits()
        try:
            yield self
        finally:
            self.config = old_config
            self._setup_resource_limits()
