# LivingAI Action Executor
# =========================
# This module executes actions in the system.

import os
import subprocess
import logging
import time
from typing import Dict, Any, Optional, Tuple, List

# Local imports
from ..config import ConfigManager
from ..security.audit import AuditLogger


class ActionExecutor:
    """
    Executes actions in the system.
    
    Responsibilities:
    - Execute shell commands
    - Execute Python code
    - Capture output and errors
    - Enforce timeouts
    - Handle execution results
    """
    
    # Default timeout for actions
    DEFAULT_TIMEOUT = 30.0  # seconds
    
    def __init__(
        self,
        config: ConfigManager,
        audit_logger: AuditLogger
    ):
        """
        Initialize the ActionExecutor.
        
        Args:
            config: Configuration manager.
            audit_logger: Audit logger for tracking actions.
        """
        self.config = config
        self.audit_logger = audit_logger
        
        # Get configuration values
        self.timeout = self.config.get("actions.timeout", self.DEFAULT_TIMEOUT)
        self.shell = self.config.get("actions.shell", "/bin/sh")
        
        # Execution state
        self._execution_history: List[Dict[str, Any]] = []
        
        logging.info("ActionExecutor initialized")
    
    def execute(
        self,
        action: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute an action.
        
        Args:
            action: Action to execute.
            context: Optional context for the action.
            
        Returns:
            Dict[str, Any]: Execution result.
        """
        self.audit_logger.log(
            "ACTION_EXECUTE_START",
            f"Executing action: {action.get('command', 'unknown')}"
        )
        start_time = time.time()
        
        try:
            command = action.get("command", "")
            args = action.get("args", [])
            
            # Check if this is a shell command or Python code
            if action.get("type") == "python" or command.startswith("python"):
                result = self._execute_python(command, context)
            else:
                result = self._execute_shell(command, args, context)
            
            # Process the result
            processed_result = self._process_result(result, action)
            
            # Record the execution
            self._record_execution(action, processed_result, start_time)
            
            self.audit_logger.log(
                "ACTION_EXECUTE_SUCCESS",
                f"Executed action: {action.get('command', 'unknown')}"
            )
            
            return processed_result
            
        except Exception as e:
            self.audit_logger.log("ACTION_EXECUTE_FAIL", str(e))
            return {
                "status": "error",
                "error": str(e),
                "action": action,
                "duration": time.time() - start_time,
            }
    
    def _execute_shell(
        self,
        command: str,
        args: list,
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Execute a shell command.
        
        Args:
            command: Command to execute.
            args: Arguments for the command.
            context: Optional context for the action.
            
        Returns:
            Dict[str, Any]: Execution result.
        """
        # Build the full command
        if args:
            full_command = [command] + args
        else:
            # Parse the command string
            full_command = self._parse_command(command)
        
        try:
            # Execute the command
            process = subprocess.Popen(
                full_command,
                shell=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=os.getcwd(),
                env=os.environ.copy(),
            )
            
            # Wait for completion with timeout
            try:
                stdout, stderr = process.communicate(timeout=self.timeout)
            except subprocess.TimeoutExpired:
                process.kill()
                stdout, stderr = process.communicate()
                return {
                    "status": "timeout",
                    "stdout": stdout,
                    "stderr": stderr,
                    "returncode": process.returncode,
                }
            
            return {
                "status": "completed",
                "stdout": stdout,
                "stderr": stderr,
                "returncode": process.returncode,
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
            }
    
    def _execute_python(
        self,
        code: str,
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Execute Python code.
        
        Args:
            code: Python code to execute.
            context: Optional context for the action.
            
        Returns:
            Dict[str, Any]: Execution result.
        """
        try:
            # Prepare the execution environment
            env = self._prepare_python_environment(context)
            
            # Execute the code
            exec_result = self._execute_code_safely(code, env)
            
            return {
                "status": "completed",
                "output": exec_result.get("output"),
                "error": exec_result.get("error"),
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
            }
    
    def _parse_command(self, command: str) -> list:
        """
        Parse a command string into a list of arguments.
        
        Args:
            command: Command string to parse.
            
        Returns:
            list: List of command arguments.
        """
        # Simple parsing - in a real implementation, use shlex.split
        import shlex
        return shlex.split(command)
    
    def _prepare_python_environment(
        self,
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Prepare the Python execution environment.
        
        Args:
            context: Optional context for the action.
            
        Returns:
            Dict[str, Any]: Execution environment.
        """
        env = {
            "__builtins__": __builtins__,
            "input": context or {},
            "result": None,
        }
        
        # Add safe modules
        safe_modules = [
            "math", "random", "string", "re", "json", "datetime",
            "collections", "itertools", "functools", "operator",
        ]
        
        for module_name in safe_modules:
            try:
                module = __import__(module_name)
                env[module_name] = module
            except ImportError:
                pass
        
        return env
    
    def _execute_code_safely(
        self,
        code: str,
        env: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute Python code safely.
        
        Args:
            code: Python code to execute.
            env: Execution environment.
            
        Returns:
            Dict[str, Any]: Execution result.
        """
        try:
            # Compile the code
            compiled_code = compile(code, "<action>", "exec")
            
            # Execute the code
            exec(compiled_code, env)
            
            # Get the result
            result = env.get("result")
            
            return {
                "output": result,
            }
            
        except Exception as e:
            return {
                "error": str(e),
            }
    
    def _process_result(
        self,
        result: Dict[str, Any],
        action: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process the execution result.
        
        Args:
            result: Raw execution result.
            action: The action that was executed.
            
        Returns:
            Dict[str, Any]: Processed result.
        """
        processed = result.copy()
        
        # Add action to result
        processed["action"] = action
        
        # Process stdout
        if "stdout" in processed:
            processed["stdout"] = self._clean_output(processed["stdout"])
        
        # Process stderr
        if "stderr" in processed:
            processed["stderr"] = self._clean_output(processed["stderr"])
        
        # Determine status
        if processed.get("status") == "completed":
            if processed.get("returncode") != 0:
                processed["status"] = "failed"
        
        return processed
    
    def _clean_output(self, output: str) -> str:
        """
        Clean up command output.
        
        Args:
            output: Output to clean.
            
        Returns:
            str: Cleaned output.
        """
        if not output:
            return ""
        
        # Remove trailing whitespace
        output = output.rstrip()
        
        # Truncate if too long
        max_length = self.config.get("actions.max_output_length", 10000)
        if len(output) > max_length:
            output = output[:max_length] + "... (truncated)"
        
        return output
    
    def _record_execution(
        self,
        action: Dict[str, Any],
        result: Dict[str, Any],
        start_time: float
    ) -> None:
        """
        Record an execution in the history.
        
        Args:
            action: The action that was executed.
            result: The result of the execution.
            start_time: Start time of the execution.
        """
        record = {
            "timestamp": time.time(),
            "action": action,
            "result": result,
            "duration": time.time() - start_time,
        }
        
        self._execution_history.append(record)
        
        # Clean up old history
        if len(self._execution_history) > 100:
            self._execution_history = self._execution_history[-50:]
    
    def get_execution_history(self) -> List[Dict[str, Any]]:
        """
        Get the execution history.
        
        Returns:
            List[Dict[str, Any]]: Execution history.
        """
        return self._execution_history.copy()
    
    def clear_history(self) -> None:
        """Clear the execution history."""
        self._execution_history = []
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get execution statistics.
        
        Returns:
            Dict[str, Any]: Execution statistics.
        """
        if not self._execution_history:
            return {
                "total_executions": 0,
                "by_status": {},
                "avg_duration": 0.0,
            }
        
        by_status = {}
        total_duration = 0.0
        
        for record in self._execution_history:
            status = record.get("result", {}).get("status", "unknown")
            by_status[status] = by_status.get(status, 0) + 1
            total_duration += record.get("duration", 0)
        
        return {
            "total_executions": len(self._execution_history),
            "by_status": by_status,
            "avg_duration": total_duration / len(self._execution_history),
        }
    
    def set_timeout(self, timeout: float) -> None:
        """
        Set the execution timeout.
        
        Args:
            timeout: Timeout in seconds.
        """
        self.timeout = timeout
    
    def set_shell(self, shell: str) -> None:
        """
        Set the shell to use for command execution.
        
        Args:
            shell: Path to the shell executable.
        """
        self.shell = shell
