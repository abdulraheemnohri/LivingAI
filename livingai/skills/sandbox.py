# LivingAI Skill Sandbox
# ========================
# This module provides a sandboxed environment for executing skills.

import logging
import sys
import io
import time
from typing import Dict, Any, Optional, Tuple
from contextlib import redirect_stdout, redirect_stderr

# Local imports
from ..config import ConfigManager
from ..security.audit import AuditLogger


class SkillSandbox:
    """
    Provides a sandboxed environment for executing skills.
    
    Responsibilities:
    - Create isolated execution environments
    - Limit resource usage
    - Restrict dangerous operations
    - Capture output and errors
    - Enforce timeouts
    """
    
    # Default resource limits
    DEFAULT_TIMEOUT = 5.0  # seconds
    DEFAULT_MEMORY_LIMIT = 100 * 1024 * 1024  # 100MB
    DEFAULT_CPU_LIMIT = 1.0  # 1 CPU core
    
    def __init__(
        self,
        config: ConfigManager,
        audit_logger: AuditLogger
    ):
        """
        Initialize the SkillSandbox.
        
        Args:
            config: Configuration manager.
            audit_logger: Audit logger for tracking actions.
        """
        self.config = config
        self.audit_logger = audit_logger
        
        # Get configuration values
        self.timeout = self.config.get("skills.timeout", self.DEFAULT_TIMEOUT)
        self.memory_limit = self.config.get("skills.memory_limit", self.DEFAULT_MEMORY_LIMIT)
        self.cpu_limit = self.config.get("skills.cpu_limit", self.DEFAULT_CPU_LIMIT)
        
        logging.info("SkillSandbox initialized")
    
    def execute(
        self,
        code: str,
        input_data: Dict[str, Any],
        permissions: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute code in the sandbox.
        
        Args:
            code: Python code to execute.
            input_data: Input data for the code.
            permissions: Permissions for the execution.
            
        Returns:
            Dict[str, Any]: Execution results.
        """
        self.audit_logger.log("SANDBOX_EXECUTE_START", "Starting sandboxed execution")
        start_time = time.time()
        
        try:
            # Prepare the execution environment
            env = self._prepare_environment(input_data, permissions)
            
            # Compile the code
            compiled_code = self._compile_code(code)
            
            # Execute with timeout
            result = self._execute_with_timeout(
                compiled_code,
                env,
                self.timeout
            )
            
            # Process the result
            output = self._process_result(result)
            
            # Check for violations
            violations = self._check_violations(output)
            
            if violations:
                output["violations"] = violations
                output["status"] = "violation"
            else:
                output["status"] = "success"
            
            output["duration"] = time.time() - start_time
            
            self.audit_logger.log(
                "SANDBOX_EXECUTE_SUCCESS",
                f"Executed in {output['duration']:.2f}s"
            )
            
            return output
            
        except Exception as e:
            self.audit_logger.log("SANDBOX_EXECUTE_FAIL", str(e))
            return {
                "status": "error",
                "error": str(e),
                "duration": time.time() - start_time,
            }
    
    def _prepare_environment(
        self,
        input_data: Dict[str, Any],
        permissions: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Prepare the execution environment.
        
        Args:
            input_data: Input data for the code.
            permissions: Permissions for the execution.
            
        Returns:
            Dict[str, Any]: Execution environment.
        """
        # Create a safe environment
        env = {
            "__builtins__": self._create_safe_builtins(permissions),
            "input": input_data,
            "result": None,
        }
        
        # Add safe modules
        env.update(self._create_safe_modules(permissions))
        
        return env
    
    def _create_safe_builtins(self, permissions: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a safe version of __builtins__.
        
        Args:
            permissions: Execution permissions.
            
        Returns:
            Dict[str, Any]: Safe builtins.
        """
        # Start with an empty dict
        safe_builtins = {}
        
        # Add safe built-in functions
        safe_functions = [
            "abs", "all", "any", "ascii", "bin", "bool", "bytearray", "bytes",
            "callable", "chr", "classmethod", "compile", "complex", "delattr",
            "dict", "dir", "divmod", "enumerate", "filter", "float", "format",
            "frozenset", "getattr", "globals", "hasattr", "hash", "help", "hex",
            "id", "input", "int", "isinstance", "issubclass", "iter", "len",
            "list", "locals", "map", "max", "min", "memoryview", "next", "object",
            "oct", "open", "ord", "pow", "print", "property", "range", "repr",
            "reversed", "round", "set", "setattr", "slice", "sorted", "staticmethod",
            "str", "sum", "super", "tuple", "type", "vars", "zip",
        ]
        
        # Only add functions that are safe
        for func_name in safe_functions:
            if hasattr(__builtins__, func_name):
                func = getattr(__builtins__, func_name)
                
                # Skip dangerous functions
                if func_name in ["open", "compile", "eval", "exec", "globals", "locals", "vars"]:
                    continue
                
                safe_builtins[func_name] = func
        
        # Add safe exceptions
        safe_builtins["Exception"] = Exception
        safe_builtins["ValueError"] = ValueError
        safe_builtins["TypeError"] = TypeError
        safe_builtins["IndexError"] = IndexError
        safe_builtins["KeyError"] = KeyError
        safe_builtins["AttributeError"] = AttributeError
        
        return safe_builtins
    
    def _create_safe_modules(self, permissions: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create safe module imports.
        
        Args:
            permissions: Execution permissions.
            
        Returns:
            Dict[str, Any]: Safe modules.
        """
        safe_modules = {}
        
        # List of safe modules
        safe_module_names = [
            "math", "random", "string", "re", "json", "datetime",
            "collections", "itertools", "functools", "operator", "copy",
            "decimal", "fractions", "numbers", "statistics", "textwrap",
            "unicodedata", "stringprep",
        ]
        
        for module_name in safe_module_names:
            try:
                module = __import__(module_name)
                safe_modules[module_name] = module
            except ImportError:
                pass
        
        return safe_modules
    
    def _compile_code(self, code: str) -> Any:
        """
        Compile the code for execution.
        
        Args:
            code: Python code to compile.
            
        Returns:
            Compiled code object.
        """
        try:
            # Add a wrapper to capture the result
            wrapped_code = f"""
try:
    {code}
except Exception as e:
    result = {{'error': str(e)}}
else:
    result = {{'output': locals().get('result', None)}}
"""
            return compile(wrapped_code, "<skill>", "exec")
        except SyntaxError as e:
            raise ValueError(f"Syntax error in code: {e}")
    
    def _execute_with_timeout(
        self,
        compiled_code: Any,
        env: Dict[str, Any],
        timeout: float
    ) -> Dict[str, Any]:
        """
        Execute code with a timeout.
        
        Args:
            compiled_code: Compiled code to execute.
            env: Execution environment.
            timeout: Timeout in seconds.
            
        Returns:
            Dict[str, Any]: Execution result.
        """
        import threading
        import queue
        
        # Create a queue for the result
        result_queue = queue.Queue()
        
        def run_code():
            try:
                # Redirect stdout and stderr
                stdout_capture = io.StringIO()
                stderr_capture = io.StringIO()
                
                with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
                    exec(compiled_code, env)
                
                # Get the result
                result = env.get("result", {})
                
                # Add captured output
                result["stdout"] = stdout_capture.getvalue()
                result["stderr"] = stderr_capture.getvalue()
                
                result_queue.put(result)
            except Exception as e:
                result_queue.put({"error": str(e)})
        
        # Run the code in a thread
        thread = threading.Thread(target=run_code)
        thread.daemon = True
        thread.start()
        
        # Wait for the thread to complete or timeout
        thread.join(timeout=timeout)
        
        if thread.is_alive():
            # Timeout occurred
            return {"error": "Execution timed out", "timeout": True}
        
        # Get the result from the queue
        try:
            return result_queue.get_nowait()
        except queue.Empty:
            return {"error": "No result returned"}
    
    def _process_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process the execution result.
        
        Args:
            result: Raw execution result.
            
        Returns:
            Dict[str, Any]: Processed result.
        """
        processed = {
            "output": result.get("output"),
            "stdout": result.get("stdout", ""),
            "stderr": result.get("stderr", ""),
            "error": result.get("error"),
        }
        
        # Clean up the output
        if "output" in processed and processed["output"] is not None:
            processed["output"] = self._clean_output(processed["output"])
        
        return processed
    
    def _clean_output(self, output: Any) -> Any:
        """
        Clean up the output for safety.
        
        Args:
            output: Output to clean.
            
        Returns:
            Any: Cleaned output.
        """
        # If it's a string, truncate if too long
        if isinstance(output, str):
            max_length = self.config.get("skills.max_output_length", 10000)
            if len(output) > max_length:
                return output[:max_length] + "... (truncated)"
        
        # If it's a dict or list, clean recursively
        if isinstance(output, dict):
            return {k: self._clean_output(v) for k, v in output.items()}
        elif isinstance(output, list):
            return [self._clean_output(item) for item in output]
        
        return output
    
    def _check_violations(self, result: Dict[str, Any]) -> List[str]:
        """
        Check the result for violations.
        
        Args:
            result: Execution result to check.
            
        Returns:
            List[str]: List of violations found.
        """
        violations = []
        
        # Check for errors
        if result.get("error"):
            violations.append("execution_error")
        
        # Check for timeout
        if result.get("timeout"):
            violations.append("timeout")
        
        # Check for stderr output
        if result.get("stderr"):
            violations.append("stderr_output")
        
        return violations
    
    def get_sandbox_info(self) -> Dict[str, Any]:
        """
        Get information about the sandbox configuration.
        
        Returns:
            Dict[str, Any]: Sandbox information.
        """
        return {
            "timeout": self.timeout,
            "memory_limit": self.memory_limit,
            "cpu_limit": self.cpu_limit,
        }
    
    def set_timeout(self, timeout: float) -> None:
        """
        Set the execution timeout.
        
        Args:
            timeout: Timeout in seconds.
        """
        self.timeout = timeout
    
    def set_memory_limit(self, memory_limit: int) -> None:
        """
        Set the memory limit.
        
        Args:
            memory_limit: Memory limit in bytes.
        """
        self.memory_limit = memory_limit
    
    def set_cpu_limit(self, cpu_limit: float) -> None:
        """
        Set the CPU limit.
        
        Args:
            cpu_limit: CPU limit (number of cores).
        """
        self.cpu_limit = cpu_limit
