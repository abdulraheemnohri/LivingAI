"""
LivingAI Memory Manager
======================

Manages memory for LivingAI agents.
"""

import logging
import time
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field


@dataclass
class MemoryEntry:
    """Represents a memory entry."""
    id: str
    content: str
    context: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    tags: List[str] = field(default_factory=list)
    importance: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'content': self.content,
            'context': self.context,
            'timestamp': self.timestamp,
            'tags': self.tags,
            'importance': self.importance
        }


class MemoryManager:
    """
    Manages memory for LivingAI agents.
    """
    
    def __init__(self):
        self._memories: Dict[str, MemoryEntry] = {}
        self._context: Dict[str, Any] = {}
        self.logger = logging.getLogger(__name__)
        self._next_id = 1
    
    def add_memory(
        self,
        content: str,
        context: Dict[str, Any] = None,
        tags: List[str] = None,
        importance: float = 0.0
    ) -> MemoryEntry:
        """
        Add a memory entry.
        
        Args:
            content: The memory content
            context: Additional context
            tags: Tags for categorization
            importance: Importance score (0-1)
            
        Returns:
            The created memory entry
        """
        memory_id = f"mem_{self._next_id}"
        self._next_id += 1
        
        entry = MemoryEntry(
            id=memory_id,
            content=content,
            context=context or {},
            tags=tags or [],
            importance=importance
        )
        self._memories[memory_id] = entry
        self.logger.debug(f"Added memory: {memory_id}")
        return entry
    
    def add_experience(
        self,
        action_description: str,
        result: Any = None,
        success: bool = True
    ) -> MemoryEntry:
        """
        Add an experience to memory.
        
        Args:
            action_description: Description of the action
            result: Result of the action
            success: Whether the action was successful
            
        Returns:
            The created memory entry
        """
        tags = ['experience', 'action']
        if success:
            tags.append('success')
        else:
            tags.append('failure')
        
        importance = 0.8 if success else 0.5
        
        return self.add_memory(
            content=f"Action: {action_description}\nResult: {str(result)[:500]}",
            context={'action': action_description, 'result': result, 'success': success},
            tags=tags,
            importance=importance
        )
    
    def get_memory(self, memory_id: str) -> Optional[MemoryEntry]:
        """Get a memory entry by ID."""
        return self._memories.get(memory_id)
    
    def search_memories(
        self,
        query: str = None,
        tags: List[str] = None,
        limit: int = 10
    ) -> List[MemoryEntry]:
        """
        Search memory entries.
        
        Args:
            query: Text to search for
            tags: Tags to filter by
            limit: Maximum number of results
            
        Returns:
            List of matching memory entries
        """
        results = []
        
        for entry in self._memories.values():
            # Filter by tags
            if tags:
                if not any(tag in entry.tags for tag in tags):
                    continue
            
            # Filter by query
            if query:
                if query.lower() not in entry.content.lower():
                    continue
            
            results.append(entry)
        
        # Sort by importance and timestamp
        results.sort(key=lambda e: (e.importance, e.timestamp), reverse=True)
        return results[:limit]
    
    def get_context(self) -> Dict[str, Any]:
        """Get the current memory context."""
        return self._context
    
    def update_context(self, key: str, value: Any) -> None:
        """Update the memory context."""
        self._context[key] = value
        self.logger.debug(f"Updated context: {key}")
    
    def clear_context(self) -> None:
        """Clear the memory context."""
        self._context.clear()
        self.logger.debug("Cleared memory context")
    
    def list_memories(self, limit: int = 100) -> List[MemoryEntry]:
        """List all memory entries."""
        return list(self._memories.values())[:limit]
    
    def clear_memories(self) -> None:
        """Clear all memory entries."""
        self._memories.clear()
        self.logger.info("Cleared all memories")
