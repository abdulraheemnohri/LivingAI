# LivingAI Skill Executor
# ========================
# This module executes skills in a sandboxed environment.

import logging
import time
from typing import Dict, Any, Optional, List

# Local imports
from .sandbox import SkillSandbox
from ..config import ConfigManager
from ..security.audit import AuditLogger


class SkillExecutor:
    """
    Executes skills in a sandboxed environment.
    
    Responsibilities:
    - Execute skill code
    - Manage execution context
    - Handle execution results
    - Enforce execution policies
    """
    
    def __init__(
        self,
        sandbox: SkillSandbox,
        config: ConfigManager,
        audit_logger: AuditLogger
    ):
        """
        Initialize the SkillExecutor.
        
        Args:
            sandbox: Sandbox for executing code.
            config: Configuration manager.
            audit_logger: Audit logger for tracking actions.
        """
        self.sandbox = sandbox
        self.config = config
        self.audit_logger = audit_logger
        
        # Execution state
        self._execution_history: Dict[str, List[Dict[str, Any]]] = {}
        self._last_execution_time: float = 0.0
        self._total_executions: int = 0
        
        logging.info("SkillExecutor initialized")
    
    def execute(
        self,
        name: str,
        code: str,
        input_data: Dict[str, Any],
        permissions: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute a skill.
        
        Args:
            name: Name of the skill.
            code: Python code to execute.
            input_data: Input data for the skill.
            permissions: Execution permissions.
            
        Returns:
            Dict[str, Any]: Execution results.
        """
        self.audit_logger.log(
            "SKILL_EXECUTE_START",
            f"Executing skill {name}"
        )
        start_time = time.time()
        
        try:
            # Pre-execution checks
            if not self._pre_execute_checks(name, code, permissions):
                return {
                    "status": "denied",
                    "error": "Pre-execution checks failed",
                    "duration": time.time() - start_time,
                }
            
            # Execute in sandbox
            result = self.sandbox.execute(code, input_data, permissions)
            
            # Post-execution processing
            processed_result = self._post_execute_processing(name, result)
            
            # Record execution
            self._record_execution(name, processed_result)
            
            processed_result["duration"] = time.time() - start_time
            
            self.audit_logger.log(
                "SKILL_EXECUTE_SUCCESS",
                f"Executed skill {name} in {processed_result['duration']:.2f}s"
            )
            
            return processed_result
            
        except Exception as e:
            self.audit_logger.log(
                "SKILL_EXECUTE_FAIL",
                f"Execution failed for skill {name}: {str(e)}"
            )
            return {
                "status": "error",
                "error": str(e),
                "duration": time.time() - start_time,
            }
    
    def _pre_execute_checks(
        self,
        name: str,
        code: str,
        permissions: Dict[str, Any]
    ) -> bool:
        """
        Perform pre-execution checks.
        
        Args:
            name: Name of the skill.
            code: Code to execute.
            permissions: Execution permissions.
            
        Returns:
            bool: True if checks passed, False otherwise.
        """
        # Check if skill is enabled
        if not permissions.get("enabled", True):
            logging.warning(f"Skill {name} is disabled")
            return False
        
        # Check rate limiting
        if not self._check_rate_limit(name):
            logging.warning(f"Rate limit exceeded for skill {name}")
            return False
        
        # Check code length
        max_code_length = self.config.get("skills.max_code_length", 10000)
        if len(code) > max_code_length:
            logging.warning(f"Code too long for skill {name}")
            return False
        
        return True
    
    def _check_rate_limit(self, name: str) -> bool:
        """
        Check if the skill has exceeded its rate limit.
        
        Args:
            name: Name of the skill.
            
        Returns:
            bool: True if under rate limit, False otherwise.
        """
        # Get rate limit configuration
        rate_limit = self.config.get("skills.rate_limit", 10)  # 10 executions per minute
        window_seconds = 60  # 1 minute window
        
        # Get execution history for this skill
        executions = self._execution_history.get(name, [])
        
        # Remove old executions
        current_time = time.time()
        recent_executions = [
            e for e in executions
            if current_time - e.get("timestamp", 0) <= window_seconds
        ]
        
        # Update history
        self._execution_history[name] = recent_executions
        
        # Check if under limit
        return len(recent_executions) < rate_limit
    
    def _post_execute_processing(
        self,
        name: str,
        result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process the execution result.
        
        Args:
            name: Name of the skill.
            result: Raw execution result.
            
        Returns:
            Dict[str, Any]: Processed result.
        """
        processed = result.copy()
        
        # Add skill name to result
        processed["skill"] = name
        
        # Add timestamp
        processed["timestamp"] = time.time()
        
        # Process output
        if "output" in processed:
            processed["output"] = self._process_output(processed["output"])
        
        # Process error
        if "error" in processed:
            processed["error"] = self._process_error(processed["error"])
        
        return processed
    
    def _process_output(self, output: Any) -> Any:
        """
        Process the skill output.
        
        Args:
            output: Raw output from the skill.
            
        Returns:
            Any: Processed output.
        """
        # If it's a string, clean it up
        if isinstance(output, str):
            output = output.strip()
            if not output:
                return None
        
        return output
    
    def _process_error(self, error: str) -> str:
        """
        Process an execution error.
        
        Args:
            error: Error message.
            
        Returns:
            str: Processed error message.
        """
        # Clean up the error message
        error = error.strip()
        
        # Remove traceback if present
        if "Traceback" in error:
            lines = error.split('\n')
            error = lines[-1] if lines else error
        
        return error
    
    def _record_execution(self, name: str, result: Dict[str, Any]) -> None:
        """
        Record an execution in the history.
        
        Args:
            name: Name of the skill.
            result: Execution result.
        """
        if name not in self._execution_history:
            self._execution_history[name] = []
        
        self._execution_history[name].append({
            "timestamp": time.time(),
            "result": result,
        })
        
        # Clean up old history
        if len(self._execution_history[name]) > 100:
            self._execution_history[name] = self._execution_history[name][-50:]
        
        self._last_execution_time = time.time()
        self._total_executions += 1
    
    def get_execution_history(self, name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get the execution history.
        
        Args:
            name: Optional skill name to get history for.
            
        Returns:
            Dict[str, Any]: Execution history.
        """
        if name:
            return {
                name: self._execution_history.get(name, [])
            }
        else:
            return self._execution_history.copy()
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get execution statistics.
        
        Returns:
            Dict[str, Any]: Execution statistics.
        """
        total_executions = sum(
            len(executions) for executions in self._execution_history.values()
        )
        
        return {
            "total_executions": total_executions + self._total_executions,
            "last_execution_time": self._last_execution_time,
            "skills_executed": list(self._execution_history.keys()),
        }
    
    def clear_history(self, name: Optional[str] = None) -> None:
        """
        Clear the execution history.
        
        Args:
            name: Optional skill name to clear history for.
        """
        if name:
            if name in self._execution_history:
                del self._execution_history[name]
        else:
            self._execution_history = {}
    
    def get_recent_executions(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent executions across all skills.
        
        Args:
            limit: Maximum number of executions to return.
            
        Returns:
            List[Dict[str, Any]]: Recent executions.
        """
        all_executions = []
        
        for skill_name, executions in self._execution_history.items():
            for execution in executions:
                all_executions.append({
                    "skill": skill_name,
                    **execution
                })
        
        # Sort by timestamp (newest first)
        all_executions.sort(key=lambda x: x.get("timestamp", 0), reverse=True)
        
        return all_executions[:limit]
    
    def get_success_rate(self, name: str) -> float:
        """
        Get the success rate for a skill.
        
        Args:
            name: Name of the skill.
            
        Returns:
            float: Success rate (0.0 to 1.0).
        """
        executions = self._execution_history.get(name, [])
        
        if not executions:
            return 0.0
        
        successful = sum(
            1 for e in executions
            if e.get("result", {}).get("status") == "success"
        )
        
        return successful / len(executions)
    
    def get_average_duration(self, name: str) -> float:
        """
        Get the average execution duration for a skill.
        
        Args:
            name: Name of the skill.
            
        Returns:
            float: Average duration in seconds.
        """
        executions = self._execution_history.get(name, [])
        
        if not executions:
            return 0.0
        
        total_duration = sum(
            e.get("result", {}).get("duration", 0)
            for e in executions
        )
        
        return total_duration / len(executions)
