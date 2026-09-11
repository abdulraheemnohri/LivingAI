# LivingAI Action Engine
# ======================
# This module manages actions for the LivingAI system.

import logging
import time
from typing import Dict, Any, Optional, List, Tuple
from enum import Enum

# Local imports
from .policy import ActionPolicy
from .executor import ActionExecutor
from .confirmation import ActionConfirmation
from ..config import ConfigManager
from ..security.audit import AuditLogger


class ActionRiskLevel(Enum):
    """Risk levels for actions."""
    LOW = "low"           # Safe, read-only operations
    MEDIUM = "medium"     # Potentially destructive but recoverable
    HIGH = "high"         # Destructive operations
    CRITICAL = "critical" # Irreversible or system-critical operations


class ActionStatus(Enum):
    """Status of an action."""
    PENDING = "pending"     # Action has not been executed yet
    EXECUTING = "executing" # Action is currently executing
    COMPLETED = "completed" # Action completed successfully
    FAILED = "failed"       # Action failed
    DENIED = "denied"       # Action was denied
    CANCELLED = "cancelled" # Action was cancelled


class ActionEngine:
    """
    Manages actions for the LivingAI system.
    
    Responsibilities:
    - Process action requests
    - Check action permissions
    - Execute actions
    - Handle confirmations
    - Track action history
    """
    
    def __init__(
        self,
        config: ConfigManager,
        audit_logger: AuditLogger
    ):
        """
        Initialize the ActionEngine.
        
        Args:
            config: Configuration manager.
            audit_logger: Audit logger for tracking actions.
        """
        self.config = config
        self.audit_logger = audit_logger
        
        # Initialize components
        self.policy = ActionPolicy(config, audit_logger)
        self.executor = ActionExecutor(config, audit_logger)
        self.confirmation = ActionConfirmation(config, audit_logger)
        
        # Action state
        self._action_history: List[Dict[str, Any]] = []
        self._pending_actions: Dict[str, Dict[str, Any]] = {}
        self._active_actions: Dict[str, Dict[str, Any]] = {}
        
        logging.info("ActionEngine initialized")
    
    def process_action(
        self,
        action: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process an action request.
        
        Args:
            action: Action to process.
            context: Optional context for the action.
            
        Returns:
            Dict[str, Any]: Action result.
        """
        self.audit_logger.log(
            "ACTION_PROCESS_START",
            f"Processing action: {action.get('command', 'unknown')}"
        )
        start_time = time.time()
        
        try:
            # Step 1: Validate the action
            validation = self._validate_action(action)
            if not validation.get("valid", False):
                return {
                    "status": ActionStatus.DENIED.value,
                    "error": validation.get("error", "Invalid action"),
                    "action": action,
                    "duration": time.time() - start_time,
                }
            
            # Step 2: Check permissions
            permission = self.policy.check_permission(action)
            if not permission.get("allowed", False):
                return {
                    "status": ActionStatus.DENIED.value,
                    "error": permission.get("reason", "Permission denied"),
                    "action": action,
                    "duration": time.time() - start_time,
                }
            
            # Step 3: Determine risk level
            risk_level = self._determine_risk_level(action)
            
            # Step 4: Check if confirmation is needed
            if self._needs_confirmation(risk_level, action):
                # Request confirmation
                confirmation_result = self.confirmation.request_confirmation(
                    action=action,
                    risk_level=risk_level,
                    context=context
                )
                
                if not confirmation_result.get("confirmed", False):
                    return {
                        "status": ActionStatus.DENIED.value,
                        "error": "Action not confirmed",
                        "action": action,
                        "risk_level": risk_level.value,
                        "duration": time.time() - start_time,
                    }
            
            # Step 5: Execute the action
            result = self.executor.execute(action, context)
            
            # Step 6: Record the action
            self._record_action(action, result, risk_level, start_time)
            
            result["risk_level"] = risk_level.value
            result["duration"] = time.time() - start_time
            
            self.audit_logger.log(
                "ACTION_PROCESS_SUCCESS",
                f"Processed action: {action.get('command', 'unknown')}"
            )
            
            return result
            
        except Exception as e:
            self.audit_logger.log("ACTION_PROCESS_FAIL", str(e))
            return {
                "status": ActionStatus.FAILED.value,
                "error": str(e),
                "action": action,
                "duration": time.time() - start_time,
            }
    
    def _validate_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate an action.
        
        Args:
            action: Action to validate.
            
        Returns:
            Dict[str, Any]: Validation result.
        """
        # Check for required fields
        if "command" not in action:
            return {"valid": False, "error": "Missing command"}
        
        # Check command type
        command = action.get("command", "")
        if not isinstance(command, str):
            return {"valid": False, "error": "Command must be a string"}
        
        # Check command length
        max_length = self.config.get("actions.max_command_length", 1000)
        if len(command) > max_length:
            return {"valid": False, "error": f"Command too long (max {max_length} chars)"}
        
        return {"valid": True}
    
    def _determine_risk_level(self, action: Dict[str, Any]) -> ActionRiskLevel:
        """
        Determine the risk level of an action.
        
        Args:
            action: Action to evaluate.
            
        Returns:
            ActionRiskLevel: The risk level.
        """
        command = action.get("command", "").lower()
        
        # Check for critical operations
        critical_patterns = [
            "rm -rf",
            "dd ",
            "format ",
            "chmod ",
            "chown ",
            ":(){ :;};",  # Fork bomb
            "mkfs",
            "fdisk",
            "parted",
        ]
        
        for pattern in critical_patterns:
            if pattern in command:
                return ActionRiskLevel.CRITICAL
        
        # Check for high-risk operations
        high_patterns = [
            "rm ",
            "mv ",
            "cp ",
            "kill",
            "pkill",
            "killall",
            "apt",
            "yum",
            "dnf",
            "pip install",
            "git reset",
            "git push --force",
        ]
        
        for pattern in high_patterns:
            if pattern in command:
                return ActionRiskLevel.HIGH
        
        # Check for medium-risk operations
        medium_patterns = [
            "touch ",
            "mkdir ",
            "echo ",
            "cat ",
            "grep ",
            "find ",
            "sed ",
            "awk ",
        ]
        
        for pattern in medium_patterns:
            if pattern in command:
                return ActionRiskLevel.MEDIUM
        
        # Default to low risk
        return ActionRiskLevel.LOW
    
    def _needs_confirmation(
        self,
        risk_level: ActionRiskLevel,
        action: Dict[str, Any]
    ) -> bool:
        """
        Determine if an action needs confirmation.
        
        Args:
            risk_level: Risk level of the action.
            action: The action to check.
            
        Returns:
            bool: True if confirmation is needed, False otherwise.
        """
        # Check configuration
        auto_allow_low = self.config.get("actions.auto_allow_low_risk", True)
        confirm_medium = self.config.get("actions.confirm_medium_risk", True)
        confirm_high = self.config.get("actions.confirm_high_risk", True)
        
        if risk_level == ActionRiskLevel.CRITICAL:
            return True
        elif risk_level == ActionRiskLevel.HIGH:
            return confirm_high
        elif risk_level == ActionRiskLevel.MEDIUM:
            return confirm_medium
        else:  # LOW
            return not auto_allow_low
    
    def _record_action(
        self,
        action: Dict[str, Any],
        result: Dict[str, Any],
        risk_level: ActionRiskLevel,
        start_time: float
    ) -> None:
        """
        Record an action in the history.
        
        Args:
            action: The action that was processed.
            result: The result of the action.
            risk_level: Risk level of the action.
            start_time: Start time of the action.
        """
        record = {
            "timestamp": time.time(),
            "action": action,
            "result": result,
            "risk_level": risk_level.value,
            "duration": time.time() - start_time,
        }
        
        self._action_history.append(record)
        
        # Clean up old history
        if len(self._action_history) > 100:
            self._action_history = self._action_history[-50:]
    
    def execute_action(
        self,
        command: str,
        args: Optional[List[str]] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute a command as an action.
        
        Args:
            command: Command to execute.
            args: Optional arguments for the command.
            context: Optional context for the action.
            
        Returns:
            Dict[str, Any]: Action result.
        """
        action = {
            "command": command,
            "args": args or [],
        }
        
        return self.process_action(action, context)
    
    def batch_execute(
        self,
        actions: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Execute a batch of actions.
        
        Args:
            actions: List of actions to execute.
            context: Optional context for the actions.
            
        Returns:
            List[Dict[str, Any]]: List of action results.
        """
        results = []
        
        for action in actions:
            result = self.process_action(action, context)
            results.append(result)
            
            # Check if we should stop (e.g., if an action failed)
            if result.get("status") in [ActionStatus.FAILED.value, ActionStatus.DENIED.value]:
                if self.config.get("actions.stop_on_failure", False):
                    break
        
        return results
    
    def get_action_history(self) -> List[Dict[str, Any]]:
        """
        Get the history of actions.
        
        Returns:
            List[Dict[str, Any]]: Action history.
        """
        return self._action_history.copy()
    
    def get_pending_actions(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all pending actions.
        
        Returns:
            Dict[str, Dict[str, Any]]: Pending actions.
        """
        return self._pending_actions.copy()
    
    def get_active_actions(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all active actions.
        
        Returns:
            Dict[str, Dict[str, Any]]: Active actions.
        """
        return self._active_actions.copy()
    
    def cancel_action(self, action_id: str) -> bool:
        """
        Cancel a pending or active action.
        
        Args:
            action_id: ID of the action to cancel.
            
        Returns:
            bool: True if cancellation succeeded, False otherwise.
        """
        # Check pending actions
        if action_id in self._pending_actions:
            del self._pending_actions[action_id]
            return True
        
        # Check active actions
        if action_id in self._active_actions:
            # In a real implementation, we would try to stop the action
            # For now, just remove it from the active list
            del self._active_actions[action_id]
            return True
        
        return False
    
    def clear_history(self) -> None:
        """Clear the action history."""
        self._action_history = []
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get action statistics.
        
        Returns:
            Dict[str, Any]: Action statistics.
        """
        if not self._action_history:
            return {
                "total_actions": 0,
                "by_status": {},
                "by_risk_level": {},
                "avg_duration": 0.0,
            }
        
        by_status = {}
        by_risk_level = {}
        total_duration = 0.0
        
        for record in self._action_history:
            # By status
            status = record.get("result", {}).get("status", "unknown")
            by_status[status] = by_status.get(status, 0) + 1
            
            # By risk level
            risk_level = record.get("risk_level", "unknown")
            by_risk_level[risk_level] = by_risk_level.get(risk_level, 0) + 1
            
            # Total duration
            total_duration += record.get("duration", 0)
        
        return {
            "total_actions": len(self._action_history),
            "by_status": by_status,
            "by_risk_level": by_risk_level,
            "avg_duration": total_duration / len(self._action_history),
        }
    
    def show_allowlist(self) -> None:
        """Display the action allowlist."""
        allowlist = self.policy.get_allowlist()
        
        print("\n" + "=" * 50)
        print("ACTION ALLOWLIST")
        print("=" * 50)
        
        for category, commands in allowlist.items():
            print(f"\n{category.upper()}:")
            for cmd in commands:
                print(f"  - {cmd}")
        
        print("=" * 50 + "\n")
    
    def manage_confirmations(self) -> None:
        """Manage action confirmation settings."""
        # This would typically show an interactive menu
        # For now, just show current settings
        settings = {
            "auto_allow_low_risk": self.config.get("actions.auto_allow_low_risk", True),
            "confirm_medium_risk": self.config.get("actions.confirm_medium_risk", True),
            "confirm_high_risk": self.config.get("actions.confirm_high_risk", True),
        }
        
        print("\n" + "=" * 50)
        print("CONFIRMATION SETTINGS")
        print("=" * 50)
        
        for setting, value in settings.items():
            print(f"{setting}: {'Yes' if value else 'No'}")
        
        print("=" * 50 + "\n")
