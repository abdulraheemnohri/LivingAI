# LivingAI Action Confirmation
# ================================
# This module handles action confirmations for risky operations.

import logging
from typing import Dict, Any, Optional, List
from enum import Enum

# Local imports
from ..config import ConfigManager
from ..security.audit import AuditLogger


class ConfirmationLevel(Enum):
    """Confirmation levels for actions."""
    NONE = "none"           # No confirmation needed
    SIMPLE = "simple"       # Simple yes/no confirmation
    DETAILED = "detailed"   # Detailed confirmation with explanation
    ALWAYS = "always"       # Always require confirmation


class ActionConfirmation:
    """
    Handles action confirmations for risky operations.
    
    Responsibilities:
    - Request confirmation for actions
    - Manage confirmation policies
    - Handle confirmation responses
    - Track confirmation history
    """
    
    def __init__(
        self,
        config: ConfigManager,
        audit_logger: AuditLogger
    ):
        """
        Initialize the ActionConfirmation.
        
        Args:
            config: Configuration manager.
            audit_logger: Audit logger for tracking actions.
        """
        self.config = config
        self.audit_logger = audit_logger
        
        # Confirmation state
        self._confirmation_history: List[Dict[str, Any]] = []
        self._pending_confirmations: Dict[str, Dict[str, Any]] = {}
        
        logging.info("ActionConfirmation initialized")
    
    def request_confirmation(
        self,
        action: Dict[str, Any],
        risk_level: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Request confirmation for an action.
        
        Args:
            action: Action to confirm.
            risk_level: Risk level of the action.
            context: Optional context for the action.
            
        Returns:
            Dict[str, Any]: Confirmation result.
        """
        self.audit_logger.log(
            "CONFIRMATION_REQUEST",
            f"Requesting confirmation for action: {action.get('command', 'unknown')}"
        )
        
        # Generate confirmation ID
        confirmation_id = self._generate_confirmation_id()
        
        # Create confirmation request
        request = {
            "id": confirmation_id,
            "action": action,
            "risk_level": risk_level,
            "context": context,
            "timestamp": logging.getLogger().handlers[0].formatter.formatTime(time.time()),
            "status": "pending",
        }
        
        # Store pending confirmation
        self._pending_confirmations[confirmation_id] = request
        
        # Determine confirmation level
        confirmation_level = self._get_confirmation_level(risk_level)
        
        # Display confirmation prompt
        self._display_confirmation_prompt(request, confirmation_level)
        
        # In a real implementation, this would wait for user input
        # For now, we'll simulate based on configuration
        
        # Check if auto-confirm is enabled for this risk level
        if self._should_auto_confirm(risk_level):
            return {
                "confirmed": True,
                "confirmation_id": confirmation_id,
                "auto_confirmed": True,
            }
        
        # Otherwise, return pending
        return {
            "confirmed": False,
            "confirmation_id": confirmation_id,
            "pending": True,
        }
    
    def _generate_confirmation_id(self) -> str:
        """
        Generate a unique confirmation ID.
        
        Returns:
            str: Unique confirmation ID.
        """
        import time
        import random
        
        timestamp = int(time.time() * 1000)
        random_num = random.randint(0, 9999)
        
        return f"conf-{timestamp}-{random_num}"
    
    def _get_confirmation_level(self, risk_level: str) -> ConfirmationLevel:
        """
        Get the confirmation level for a risk level.
        
        Args:
            risk_level: Risk level of the action.
            
        Returns:
            ConfirmationLevel: Confirmation level.
        """
        # Map risk levels to confirmation levels
        risk_to_confirmation = {
            "low": ConfirmationLevel.NONE,
            "medium": ConfirmationLevel.SIMPLE,
            "high": ConfirmationLevel.DETAILED,
            "critical": ConfirmationLevel.ALWAYS,
        }
        
        return risk_to_confirmation.get(risk_level.lower(), ConfirmationLevel.SIMPLE)
    
    def _should_auto_confirm(self, risk_level: str) -> bool:
        """
        Determine if an action should be auto-confirmed.
        
        Args:
            risk_level: Risk level of the action.
            
        Returns:
            bool: True if should auto-confirm, False otherwise.
        """
        # Check configuration
        if risk_level == "low":
            return self.config.get("actions.auto_allow_low_risk", True)
        elif risk_level == "medium":
            return not self.config.get("actions.confirm_medium_risk", True)
        elif risk_level == "high":
            return not self.config.get("actions.confirm_high_risk", True)
        else:  # critical
            return False
    
    def _display_confirmation_prompt(
        self,
        request: Dict[str, Any],
        confirmation_level: ConfirmationLevel
    ) -> None:
        """
        Display a confirmation prompt to the user.
        
        Args:
            request: Confirmation request.
            confirmation_level: Level of confirmation required.
        """
        action = request.get("action", {})
        command = action.get("command", "unknown")
        risk_level = request.get("risk_level", "unknown")
        
        print("\n" + "=" * 60)
        print("ACTION CONFIRMATION REQUIRED")
        print("=" * 60)
        
        # Risk level indicator
        risk_indicators = {
            "low": "ℹ️",
            "medium": "⚠️",
            "high": "🔴",
            "critical": "💀",
        }
        
        indicator = risk_indicators.get(risk_level, "❓")
        print(f"{indicator} Risk Level: {risk_level.upper()}")
        
        print(f"\nCommand: {command}")
        
        if confirmation_level == ConfirmationLevel.DETAILED:
            print("\nThis action may have significant consequences.")
            print("Please review carefully before confirming.")
        
        print("\n[1] Allow")
        print("[2] Deny")
        
        if confirmation_level in [ConfirmationLevel.DETAILED, ConfirmationLevel.ALWAYS]:
            print("[3] Always allow this command")
        
        print("=" * 60 + "\n")
    
    def confirm(self, confirmation_id: str) -> bool:
        """
        Confirm a pending action.
        
        Args:
            confirmation_id: ID of the confirmation to confirm.
            
        Returns:
            bool: True if confirmation succeeded, False otherwise.
        """
        if confirmation_id not in self._pending_confirmations:
            return False
        
        request = self._pending_confirmations[confirmation_id]
        request["status"] = "confirmed"
        request["confirmed_at"] = time.time()
        
        # Record the confirmation
        self._record_confirmation(request, confirmed=True)
        
        # Remove from pending
        del self._pending_confirmations[confirmation_id]
        
        self.audit_logger.log(
            "CONFIRMATION_CONFIRM",
            f"Confirmed action: {request.get('action', {}).get('command', 'unknown')}"
        )
        
        return True
    
    def deny(self, confirmation_id: str) -> bool:
        """
        Deny a pending action.
        
        Args:
            confirmation_id: ID of the confirmation to deny.
            
        Returns:
            bool: True if denial succeeded, False otherwise.
        """
        if confirmation_id not in self._pending_confirmations:
            return False
        
        request = self._pending_confirmations[confirmation_id]
        request["status"] = "denied"
        request["denied_at"] = time.time()
        
        # Record the confirmation
        self._record_confirmation(request, confirmed=False)
        
        # Remove from pending
        del self._pending_confirmations[confirmation_id]
        
        self.audit_logger.log(
            "CONFIRMATION_DENY",
            f"Denied action: {request.get('action', {}).get('command', 'unknown')}"
        )
        
        return True
    
    def always_allow(self, confirmation_id: str) -> bool:
        """
        Always allow a command (add to allowlist).
        
        Args:
            confirmation_id: ID of the confirmation.
            
        Returns:
            bool: True if always-allow succeeded, False otherwise.
        """
        if confirmation_id not in self._pending_confirmations:
            return False
        
        request = self._pending_confirmations[confirmation_id]
        action = request.get("action", {})
        command = action.get("command", "")
        
        # Extract base command
        base_command = command.split()[0] if command else ""
        
        # Add to allowlist
        # In a real implementation, this would update the ActionPolicy
        
        # Record the confirmation
        self._record_confirmation(request, confirmed=True, always_allow=True)
        
        # Remove from pending
        del self._pending_confirmations[confirmation_id]
        
        self.audit_logger.log(
            "CONFIRMATION_ALWAYS_ALLOW",
            f"Always allowed command: {base_command}"
        )
        
        return True
    
    def _record_confirmation(
        self,
        request: Dict[str, Any],
        confirmed: bool,
        always_allow: bool = False
    ) -> None:
        """
        Record a confirmation in the history.
        
        Args:
            request: Confirmation request.
            confirmed: Whether the action was confirmed.
            always_allow: Whether to always allow this command.
        """
        record = {
            "timestamp": time.time(),
            "request": request,
            "confirmed": confirmed,
            "always_allow": always_allow,
        }
        
        self._confirmation_history.append(record)
        
        # Clean up old history
        if len(self._confirmation_history) > 100:
            self._confirmation_history = self._confirmation_history[-50:]
    
    def get_pending_confirmations(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all pending confirmations.
        
        Returns:
            Dict[str, Dict[str, Any]]: Pending confirmations.
        """
        return self._pending_confirmations.copy()
    
    def get_confirmation_history(self) -> List[Dict[str, Any]]:
        """
        Get the history of confirmations.
        
        Returns:
            List[Dict[str, Any]]: Confirmation history.
        """
        return self._confirmation_history.copy()
    
    def clear_history(self) -> None:
        """Clear the confirmation history."""
        self._confirmation_history = []
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get confirmation statistics.
        
        Returns:
            Dict[str, Any]: Confirmation statistics.
        """
        if not self._confirmation_history:
            return {
                "total_confirmations": 0,
                "confirmed": 0,
                "denied": 0,
                "always_allow": 0,
            }
        
        confirmed = sum(1 for r in self._confirmation_history if r.get("confirmed", False))
        denied = sum(1 for r in self._confirmation_history if not r.get("confirmed", False))
        always_allow = sum(1 for r in self._confirmation_history if r.get("always_allow", False))
        
        return {
            "total_confirmations": len(self._confirmation_history),
            "confirmed": confirmed,
            "denied": denied,
            "always_allow": always_allow,
        }
    
    def set_confirmation_level(
        self,
        risk_level: str,
        confirmation_level: ConfirmationLevel
    ) -> None:
        """
        Set the confirmation level for a risk level.
        
        Args:
            risk_level: Risk level to set confirmation for.
            confirmation_level: Confirmation level to set.
        """
        # In a real implementation, this would update the configuration
        pass
    
    def set_auto_confirm(
        self,
        risk_level: str,
        auto_confirm: bool
    ) -> None:
        """
        Set whether to auto-confirm actions for a risk level.
        
        Args:
            risk_level: Risk level to set auto-confirm for.
            auto_confirm: Whether to auto-confirm.
        """
        # In a real implementation, this would update the configuration
        pass
