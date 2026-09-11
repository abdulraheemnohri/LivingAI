# LivingAI Context Builder
# ========================
# This module builds context for the cognitive engine from various sources.

import logging
import time
from typing import Dict, Any, Optional, List

# Local imports
from ..config import ConfigManager
from ..memory.manager import MemoryManager
from ..security.audit import AuditLogger


class ContextBuilder:
    """
    Builds context for the cognitive engine by combining:
    - Current input
    - Relevant memories
    - Conversation history
    - System state
    - Active goals
    """
    
    def __init__(
        self,
        memory_manager: Optional[MemoryManager] = None,
        config: Optional[ConfigManager] = None,
        audit_logger: Optional[AuditLogger] = None
    ):
        """
        Initialize the ContextBuilder.
        
        Args:
            memory_manager: Memory manager for retrieving memories.
            config: Configuration manager.
            audit_logger: Audit logger for tracking actions.
        """
        self.memory_manager = memory_manager
        self.config = config
        self.audit_logger = audit_logger
        
        # Context components
        self._conversation_history: List[Dict[str, Any]] = []
        self._system_state: Dict[str, Any] = {}
        self._active_goals: List[Dict[str, Any]] = []
        
        logging.info("ContextBuilder initialized")
    
    def set_memory_manager(self, memory_manager: MemoryManager) -> None:
        """
        Set the memory manager (for lazy initialization).
        
        Args:
            memory_manager: Memory manager instance.
        """
        self.memory_manager = memory_manager
    
    def build(
        self,
        perception: Dict[str, Any],
        memory_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Build a full context for the cognitive engine.
        
        Args:
            perception: The perception result from the input.
            memory_context: Optional pre-retrieved memory context.
            
        Returns:
            Dict[str, Any]: Full context for processing.
        """
        self.audit_logger.log("CONTEXT_BUILD_START", "Building context")
        
        context = {
            "timestamp": time.time(),
            "perception": perception,
            "memory": memory_context or self._get_memory_context(perception),
            "conversation": self._get_conversation_context(),
            "system": self._get_system_context(),
            "goals": self._get_goals_context(),
        }
        
        self.audit_logger.log("CONTEXT_BUILD_SUCCESS", "Context built")
        return context
    
    def _get_memory_context(self, perception: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get relevant memories for the current context.
        
        Args:
            perception: The perception result.
            
        Returns:
            Dict[str, Any]: Memory context.
        """
        if not self.memory_manager:
            return {"memories": [], "query": ""}
        
        query = perception.get("raw_input", "")
        memories = self.memory_manager.search(query, limit=5)
        
        return {
            "memories": memories,
            "query": query,
        }
    
    def _get_conversation_context(self) -> Dict[str, Any]:
        """
        Get the current conversation context.
        
        Returns:
            Dict[str, Any]: Conversation context.
        """
        # In a real implementation, this would track the conversation history
        # For now, return a placeholder
        return {
            "history": self._conversation_history,
            "current_length": len(self._conversation_history),
        }
    
    def _get_system_context(self) -> Dict[str, Any]:
        """
        Get the current system context.
        
        Returns:
            Dict[str, Any]: System context.
        """
        # In a real implementation, this would include:
        # - Current time
        # - Device status
        # - Available resources
        # - Network status
        
        return {
            "timestamp": time.time(),
            "state": self._system_state,
        }
    
    def _get_goals_context(self) -> Dict[str, Any]:
        """
        Get the current goals context.
        
        Returns:
            Dict[str, Any]: Goals context.
        """
        # In a real implementation, this would retrieve active goals
        return {
            "active_goals": self._active_goals,
            "count": len(self._active_goals),
        }
    
    def update_conversation_history(self, message: Dict[str, Any]) -> None:
        """
        Update the conversation history.
        
        Args:
            message: Message to add to history (should have 'role' and 'content').
        """
        self._conversation_history.append(message)
        
        # Keep history to a reasonable size
        max_history = self.config.get("memory.context_window", 10) if self.config else 10
        if len(self._conversation_history) > max_history:
            self._conversation_history = self._conversation_history[-max_history:]
    
    def update_system_state(self, state: Dict[str, Any]) -> None:
        """
        Update the system state.
        
        Args:
            state: New system state.
        """
        self._system_state.update(state)
    
    def update_active_goals(self, goals: List[Dict[str, Any]]) -> None:
        """
        Update the active goals.
        
        Args:
            goals: List of active goals.
        """
        self._active_goals = goals
    
    def clear_context(self) -> None:
        """Clear all context components."""
        self._conversation_history = []
        self._system_state = {}
        self._active_goals = []
    
    def get_context_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the current context.
        
        Returns:
            Dict[str, Any]: Context summary.
        """
        return {
            "conversation_length": len(self._conversation_history),
            "system_state_keys": list(self._system_state.keys()),
            "active_goals_count": len(self._active_goals),
        }
