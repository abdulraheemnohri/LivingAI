# LivingAI Memory Models
# =======================
# This module defines the data models for the memory system.

from enum import Enum
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
import time


class MemoryType(Enum):
    """Types of memories in the LivingAI system."""
    WORKING = "working"           # Short-term, temporary
    SHORT_TERM = "short_term"     # Recent interactions
    LONG_TERM = "long_term"       # Persistent knowledge
    EPISODIC = "episodic"         # Events and experiences
    SEMANTIC = "semantic"         # Facts and concepts
    PROCEDURAL = "procedural"     # Skills and procedures
    PREFERENCE = "preference"     # User preferences
    GOAL = "goal"                 # Goals and tasks
    LESSON = "lesson"             # Learned lessons
    CONVERSATION = "conversation" # Conversation history
    ACTION = "action"             # Action results
    OBSERVATION = "observation"   # Observations
    REFLECTION = "reflection"     # Reflections


class MemoryStatus(Enum):
    """Status of a memory."""
    ACTIVE = "active"             # Currently in use
    ARCHIVED = "archived"         # Archived but available
    CONSOLIDATED = "consolidated" # Consolidated into long-term memory
    FORGOTTEN = "forgotten"       # Marked as forgotten


class MemoryImportance(Enum):
    """Importance levels for memories."""
    CRITICAL = "critical"         # Essential information
    HIGH = "high"                 # Important information
    MEDIUM = "medium"             # Useful information
    LOW = "low"                   # Less important information


@dataclass
class Memory:
    """
    Represents a memory in the LivingAI system.
    
    Attributes:
        id: Unique identifier for the memory.
        content: The content of the memory.
        memory_type: Type of memory (from MemoryType enum).
        importance: Importance level (from MemoryImportance enum).
        relevance: Relevance score (0.0 to 1.0).
        recency: Recency score (0.0 to 1.0).
        confidence: Confidence in the memory (0.0 to 1.0).
        frequency: How often this memory is accessed.
        status: Current status of the memory.
        metadata: Additional metadata about the memory.
        created_at: Timestamp when the memory was created.
        updated_at: Timestamp when the memory was last updated.
    """
    id: Optional[int] = None
    content: str = ""
    memory_type: MemoryType = MemoryType.WORKING
    importance: MemoryImportance = MemoryImportance.MEDIUM
    relevance: float = 0.5
    recency: float = 1.0
    confidence: float = 0.5
    frequency: int = 1
    status: MemoryStatus = MemoryStatus.ACTIVE
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    
    def __post_init__(self):
        """Post-initialization processing."""
        if isinstance(self.memory_type, str):
            self.memory_type = MemoryType(self.memory_type)
        if isinstance(self.importance, str):
            self.importance = MemoryImportance(self.importance)
        if isinstance(self.status, str):
            self.status = MemoryStatus(self.status)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the memory to a dictionary.
        
        Returns:
            Dict[str, Any]: Dictionary representation of the memory.
        """
        return {
            "id": self.id,
            "content": self.content,
            "memory_type": self.memory_type.value,
            "importance": self.importance.value,
            "relevance": self.relevance,
            "recency": self.recency,
            "confidence": self.confidence,
            "frequency": self.frequency,
            "status": self.status.value,
            "metadata": self.metadata,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Memory":
        """
        Create a Memory from a dictionary.
        
        Args:
            data: Dictionary with memory data.
            
        Returns:
            Memory: Memory instance.
        """
        return cls(
            id=data.get("id"),
            content=data.get("content", ""),
            memory_type=data.get("memory_type", MemoryType.WORKING.value),
            importance=data.get("importance", MemoryImportance.MEDIUM.value),
            relevance=data.get("relevance", 0.5),
            recency=data.get("recency", 1.0),
            confidence=data.get("confidence", 0.5),
            frequency=data.get("frequency", 1),
            status=data.get("status", MemoryStatus.ACTIVE.value),
            metadata=data.get("metadata", {}),
            created_at=data.get("created_at", time.time()),
            updated_at=data.get("updated_at", time.time()),
        )
    
    def get_ranking_score(self) -> float:
        """
        Calculate a ranking score for this memory.
        
        The score is based on:
        - Relevance
        - Importance
        - Recency
        - Confidence
        - Frequency
        
        Returns:
            float: Ranking score (0.0 to 1.0).
        """
        # Weight factors
        weights = {
            "relevance": 0.3,
            "importance": 0.25,
            "recency": 0.2,
            "confidence": 0.15,
            "frequency": 0.1,
        }
        
        # Importance weight
        importance_weight = {
            MemoryImportance.CRITICAL: 1.0,
            MemoryImportance.HIGH: 0.8,
            MemoryImportance.MEDIUM: 0.5,
            MemoryImportance.LOW: 0.2,
        }.get(self.importance, 0.5)
        
        # Calculate weighted score
        score = (
            weights["relevance"] * self.relevance +
            weights["importance"] * importance_weight +
            weights["recency"] * self.recency +
            weights["confidence"] * self.confidence +
            weights["frequency"] * min(self.frequency / 10, 1.0)  # Normalize frequency
        )
        
        return min(max(score, 0.0), 1.0)
    
    def update_recency(self) -> None:
        """Update the recency score (decay over time)."""
        # Simple recency decay: reduce by 10% each time it's accessed
        # In a real implementation, this would be time-based
        self.recency = max(self.recency * 0.9, 0.1)
        self.updated_at = time.time()
    
    def increment_frequency(self) -> None:
        """Increment the frequency counter."""
        self.frequency += 1
        self.updated_at = time.time()
    
    def update_relevance(self, new_relevance: float) -> None:
        """
        Update the relevance score.
        
        Args:
            new_relevance: New relevance score (0.0 to 1.0).
        """
        self.relevance = min(max(new_relevance, 0.0), 1.0)
        self.updated_at = time.time()
    
    def update_confidence(self, new_confidence: float) -> None:
        """
        Update the confidence score.
        
        Args:
            new_confidence: New confidence score (0.0 to 1.0).
        """
        self.confidence = min(max(new_confidence, 0.0), 1.0)
        self.updated_at = time.time()


@dataclass
class MemorySearchResult:
    """
    Represents a search result from the memory system.
    
    Attributes:
        memory: The matching memory.
        score: The ranking score for this result.
        matches: List of matching terms or patterns.
    """
    memory: Memory
    score: float = 0.0
    matches: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the search result to a dictionary.
        
        Returns:
            Dict[str, Any]: Dictionary representation of the search result.
        """
        return {
            "memory": self.memory.to_dict(),
            "score": self.score,
            "matches": self.matches,
        }


@dataclass
class MemoryStats:
    """
    Statistics about the memory system.
    
    Attributes:
        total_memories: Total number of memories.
        by_type: Count of memories by type.
        by_status: Count of memories by status.
        by_importance: Count of memories by importance.
        avg_relevance: Average relevance score.
        avg_confidence: Average confidence score.
    """
    total_memories: int = 0
    by_type: Dict[str, int] = field(default_factory=dict)
    by_status: Dict[str, int] = field(default_factory=dict)
    by_importance: Dict[str, int] = field(default_factory=dict)
    avg_relevance: float = 0.0
    avg_confidence: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the stats to a dictionary.
        
        Returns:
            Dict[str, Any]: Dictionary representation of the stats.
        """
        return {
            "total_memories": self.total_memories,
            "by_type": self.by_type,
            "by_status": self.by_status,
            "by_importance": self.by_importance,
            "avg_relevance": self.avg_relevance,
            "avg_confidence": self.avg_confidence,
        }
