# LivingAI Skill Sandbox
# ========================
# This module provides a sandboxed environment for executing skills.

import logging
import sys
import io
import time
import builtins
from typing import Dict, Any, Optional, Tuple, List
from contextlib import redirect_stdout, redirect_stderr

# Local imports
from ..config import ConfigManager
from ..security.audit import AuditLogger


class SkillSandbox:
    """
    Provides a sandboxed environment for executing skills.
    """
    
    DEFAULT_TIMEOUT = 5.0
    DEFAULT_MEMORY_LIMIT = 100 * 1024 * 1024
    DEFAULT_CPU_LIMIT = 1.0
    
    def __init__(
        self,
        config: ConfigManager,
        audit_logger: AuditLogger
    ):
        self.config = config
        self.audit_logger = audit_logger
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
        self.audit_logger.log("SANDBOX_EXECUTE_START", "Starting sandboxed execution")
        start_time = time.time()
        
        try:
            env = self._prepare_environment(input_data, permissions)
            compiled_code = self._compile_code(code)
            result = self._execute_with_timeout(
                compiled_code,
                env,
                self.timeout
            )
            output = self._process_result(result)
            violations = self._check_violations(output)
            
            if violations:
                output["violations"] = violations
                output["status"] = "violation"
            else:
                output["status"] = "success"
            
            output["duration"] = time.time() - start_time
            self.audit_logger.log("SANDBOX_EXECUTE_SUCCESS", f"Executed in {output['duration']:.2f}s")
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
        env = {
            "__builtins__": self._create_safe_builtins(permissions),
            "input": input_data,
        }
        env.update(self._create_safe_modules(permissions))
        return env
    
    def _create_safe_builtins(self, permissions: Dict[str, Any]) -> Dict[str, Any]:
        safe_builtins = {}
        safe_names = [
            "abs", "all", "any", "ascii", "bin", "bool", "bytearray", "bytes",
            "callable", "chr", "classmethod", "complex", "delattr",
            "dict", "dir", "divmod", "enumerate", "filter", "float", "format",
            "frozenset", "getattr", "hasattr", "hash", "help", "hex",
            "id", "input", "int", "isinstance", "issubclass", "iter", "len",
            "list", "map", "max", "min", "memoryview", "next", "object",
            "oct", "ord", "pow", "print", "property", "range", "repr",
            "reversed", "round", "set", "setattr", "slice", "sorted", "staticmethod",
            "str", "sum", "super", "tuple", "type", "zip",
            "Exception", "ValueError", "TypeError", "IndexError", "KeyError", "AttributeError"
        ]
        
        dangerous = {"open", "compile", "eval", "exec", "globals", "locals", "vars"}

        for name in safe_names:
            if name in dangerous:
                continue
            if hasattr(builtins, name):
                safe_builtins[name] = getattr(builtins, name)
        
        return safe_builtins
    
    def _create_safe_modules(self, permissions: Dict[str, Any]) -> Dict[str, Any]:
        safe_modules = {}
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
        try:
            wrapped_code = f"""
try:
    {code}
    _res_val = result if 'result' in dir() else None
except Exception as _e:
    result = {{'error': str(_e)}}
else:
    result = {{'output': _res_val if '_res_val' in dir() else None}}
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
        import threading
        import queue
        
        result_queue = queue.Queue()
        
        def run_code():
            try:
                stdout_capture = io.StringIO()
                stderr_capture = io.StringIO()
                
                with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
                    exec(compiled_code, env)
                
                result = env.get("result", {})
                if not isinstance(result, dict):
                    result = {"output": result}
                result["stdout"] = stdout_capture.getvalue()
                result["stderr"] = stderr_capture.getvalue()
                result_queue.put(result)
            except Exception as e:
                result_queue.put({"error": str(e)})
        
        thread = threading.Thread(target=run_code)
        thread.daemon = True
        thread.start()
        thread.join(timeout=timeout)
        
        if thread.is_alive():
            return {"error": "Execution timed out", "timeout": True}
        
        try:
            return result_queue.get_nowait()
        except queue.Empty:
            return {"error": "No result returned"}
    
    def _process_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        processed = {
            "output": result.get("output"),
            "stdout": result.get("stdout", ""),
            "stderr": result.get("stderr", ""),
            "error": result.get("error"),
        }
        if "output" in processed and processed["output"] is not None:
            processed["output"] = self._clean_output(processed["output"])
        return processed
    
    def _clean_output(self, output: Any) -> Any:
        if isinstance(output, str):
            max_length = self.config.get("skills.max_output_length", 10000)
            if len(output) > max_length:
                return output[:max_length] + "... (truncated)"
        if isinstance(output, dict):
            return {k: self._clean_output(v) for k, v in output.items()}
        elif isinstance(output, list):
            return [self._clean_output(item) for item in output]
        return output
    
    def _check_violations(self, result: Dict[str, Any]) -> List[str]:
        violations = []
        if result.get("error"):
            violations.append("execution_error")
        if result.get("timeout"):
            violations.append("timeout")
        if result.get("stderr"):
            violations.append("stderr_output")
        return violations

    def get_sandbox_info(self) -> Dict[str, Any]:
        return {"timeout": self.timeout, "memory_limit": self.memory_limit, "cpu_limit": self.cpu_limit}

    def set_timeout(self, timeout: float) -> None:
        self.timeout = timeout

    def set_memory_limit(self, memory_limit: int) -> None:
        self.memory_limit = memory_limit

    def set_cpu_limit(self, cpu_limit: float) -> None:
        self.cpu_limit = cpu_limit
