# LivingAI Lesson Manager
# ========================
# This module manages lessons learned by the LivingAI system.

import logging
import time
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum

# Local imports
from ..config import ConfigManager
from ..memory.manager import MemoryManager
from ..security.audit import AuditLogger


class LessonType(Enum):
    """Types of lessons."""
    POSITIVE = "positive"       # Successful actions or outcomes
    NEGATIVE = "negative"       # Failed actions or mistakes
    OBSERVATION = "observation" # Observations and insights
    PATTERN = "pattern"         # Recognized patterns
    RULE = "rule"               # Learned rules or constraints


class LessonStatus(Enum):
    """Status of a lesson."""
    NEW = "new"                 # Recently learned
    VALIDATED = "validated"     # Validated as useful
    CONSOLIDATED = "consolidated" # Consolidated into long-term knowledge
    ARCHIVED = "archived"       # Archived but available
    DEPRECATED = "deprecated"   # No longer considered valid


@dataclass
class Lesson:
    """
    Represents a lesson learned by the LivingAI system.
    
    Attributes:
        id: Unique identifier for the lesson.
        description: Description of the lesson.
        lesson_type: Type of lesson (from LessonType enum).
        source: Source of the lesson (e.g., "action", "observation").
        outcome: Outcome associated with the lesson.
        confidence: Confidence in the lesson (0.0 to 1.0).
        importance: Importance of the lesson.
        status: Current status of the lesson.
        context: Context in which the lesson was learned.
        metadata: Additional metadata.
        created_at: Timestamp when the lesson was created.
        updated_at: Timestamp when the lesson was last updated.
    """
    id: Optional[int] = None
    description: str = ""
    lesson_type: LessonType = LessonType.OBSERVATION
    source: str = ""
    outcome: str = ""
    confidence: float = 0.5
    importance: str = "medium"
    status: LessonStatus = LessonStatus.NEW
    context: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    
    def __post_init__(self):
        """Post-initialization processing."""
        if isinstance(self.lesson_type, str):
            self.lesson_type = LessonType(self.lesson_type)
        if isinstance(self.status, str):
            self.status = LessonStatus(self.status)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the lesson to a dictionary.
        
        Returns:
            Dict[str, Any]: Dictionary representation of the lesson.
        """
        return {
            "id": self.id,
            "description": self.description,
            "lesson_type": self.lesson_type.value,
            "source": self.source,
            "outcome": self.outcome,
            "confidence": self.confidence,
            "importance": self.importance,
            "status": self.status.value,
            "context": self.context,
            "metadata": self.metadata,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Lesson":
        """
        Create a Lesson from a dictionary.
        
        Args:
            data: Dictionary with lesson data.
            
        Returns:
            Lesson: Lesson instance.
        """
        return cls(
            id=data.get("id"),
            description=data.get("description", ""),
            lesson_type=data.get("lesson_type", LessonType.OBSERVATION.value),
            source=data.get("source", ""),
            outcome=data.get("outcome", ""),
            confidence=data.get("confidence", 0.5),
            importance=data.get("importance", "medium"),
            status=data.get("status", LessonStatus.NEW.value),
            context=data.get("context", {}),
            metadata=data.get("metadata", {}),
            created_at=data.get("created_at", time.time()),
            updated_at=data.get("updated_at", time.time()),
        )


class LessonManager:
    """
    Manages lessons learned by the LivingAI system.
    
    Responsibilities:
    - CRUD operations for lessons
    - Lesson search and retrieval
    - Lesson validation
    - Lesson consolidation
    - Lesson statistics
    """
    
    def __init__(
        self,
        memory_manager: Optional[MemoryManager] = None,
        config: Optional[ConfigManager] = None,
        audit_logger: Optional[AuditLogger] = None
    ):
        """
        Initialize the LessonManager.
        
        Args:
            memory_manager: Memory manager for storing lessons.
            config: Configuration manager.
            audit_logger: Audit logger for tracking actions.
        """
        self.memory_manager = memory_manager
        self.config = config
        self.audit_logger = audit_logger
        
        # Lesson storage (in a real implementation, this would use a database)
        self._lessons: Dict[int, Lesson] = {}
        self._next_id = 1
        self._lesson_index: Dict[str, List[int]] = {}
        
        logging.info("LessonManager initialized")
    
    def set_memory_manager(self, memory_manager: MemoryManager) -> None:
        """
        Set the memory manager (for lazy initialization).
        
        Args:
            memory_manager: Memory manager instance.
        """
        self.memory_manager = memory_manager
    
    def add_lesson(self, lesson_data: Dict[str, Any]) -> int:
        """
        Add a new lesson.
        
        Args:
            lesson_data: Dictionary with lesson data.
            
        Returns:
            int: ID of the created lesson.
        """
        # Convert dict to Lesson object
        lesson = Lesson.from_dict(lesson_data)
        
        # Assign ID
        lesson.id = self._next_id
        self._next_id += 1
        
        # Store the lesson
        self._lessons[lesson.id] = lesson
        
        # Update index
        self._update_index(lesson)
        
        # Store in memory if available
        if self.memory_manager:
            memory_data = {
                "content": f"Lesson: {lesson.description}",
                "type": "lesson",
                "importance": lesson.importance,
                "relevance": lesson.confidence,
                "recency": 1.0,
                "confidence": lesson.confidence,
                "metadata": {
                    "lesson_id": lesson.id,
                    "lesson_type": lesson.lesson_type.value,
                    "source": lesson.source,
                    "outcome": lesson.outcome,
                },
            }
            self.memory_manager.add(memory_data)
        
        self.audit_logger.log(
            "LESSON_ADD",
            f"Added lesson {lesson.id} of type {lesson.lesson_type.value}"
        )
        
        return lesson.id
    
    def get_lesson(self, lesson_id: int) -> Optional[Lesson]:
        """
        Get a lesson by ID.
        
        Args:
            lesson_id: ID of the lesson to retrieve.
            
        Returns:
            Optional[Lesson]: The lesson, or None if not found.
        """
        return self._lessons.get(lesson_id)
    
    def update_lesson(self, lesson: Lesson) -> bool:
        """
        Update a lesson.
        
        Args:
            lesson: Lesson to update.
            
        Returns:
            bool: True if update succeeded, False otherwise.
        """
        if lesson.id is None or lesson.id not in self._lessons:
            return False
        
        # Update the lesson
        self._lessons[lesson.id] = lesson
        lesson.updated_at = time.time()
        
        # Update index
        self._update_index(lesson)
        
        self.audit_logger.log(
            "LESSON_UPDATE",
            f"Updated lesson {lesson.id}"
        )
        
        return True
    
    def delete_lesson(self, lesson_id: int) -> bool:
        """
        Delete a lesson.
        
        Args:
            lesson_id: ID of the lesson to delete.
            
        Returns:
            bool: True if deletion succeeded, False otherwise.
        """
        if lesson_id not in self._lessons:
            return False
        
        # Remove from index
        lesson = self._lessons[lesson_id]
        self._remove_from_index(lesson)
        
        # Delete the lesson
        del self._lessons[lesson_id]
        
        self.audit_logger.log(
            "LESSON_DELETE",
            f"Deleted lesson {lesson_id}"
        )
        
        return True
    
    def list_lessons(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        List all lessons.
        
        Args:
            limit: Maximum number of lessons to return.
            
        Returns:
            List[Dict[str, Any]]: List of lessons.
        """
        lessons = list(self._lessons.values())
        
        # Sort by created_at (newest first)
        lessons.sort(key=lambda x: x.created_at, reverse=True)
        
        if limit is not None:
            lessons = lessons[:limit]
        
        return [lesson.to_dict() for lesson in lessons]
    
    def search_lessons(
        self,
        query: str,
        lesson_type: Optional[LessonType] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search for lessons matching a query.
        
        Args:
            query: Search query.
            lesson_type: Optional lesson type filter.
            limit: Maximum number of results to return.
            
        Returns:
            List[Dict[str, Any]]: List of matching lessons.
        """
        # Search the index
        query_lower = query.lower()
        
        if query_lower in self._lesson_index:
            lesson_ids = self._lesson_index[query_lower]
        else:
            lesson_ids = []
        
        # Filter by type if specified
        if lesson_type is not None:
            lesson_ids = [
                lid for lid in lesson_ids
                if self._lessons[lid].lesson_type == lesson_type
            ]
        
        # Get the lessons
        lessons = [self._lessons[lid] for lid in lesson_ids if lid in self._lessons]
        
        # Sort by relevance (confidence * importance)
        lessons.sort(
            key=lambda x: x.confidence * self._get_importance_weight(x.importance),
            reverse=True
        )
        
        return [lesson.to_dict() for lesson in lessons[:limit]]
    
    def _update_index(self, lesson: Lesson) -> None:
        """
        Update the lesson index with terms from the lesson.
        
        Args:
            lesson: Lesson to index.
        """
        # Index the description
        terms = lesson.description.lower().split()
        
        for term in terms:
            if term not in self._lesson_index:
                self._lesson_index[term] = []
            
            if lesson.id is not None and lesson.id not in self._lesson_index[term]:
                self._lesson_index[term].append(lesson.id)
    
    def _remove_from_index(self, lesson: Lesson) -> None:
        """
        Remove a lesson from the index.
        
        Args:
            lesson: Lesson to remove from index.
        """
        # Remove from all terms in the description
        terms = lesson.description.lower().split()
        
        for term in terms:
            if term in self._lesson_index:
                if lesson.id in self._lesson_index[term]:
                    self._lesson_index[term].remove(lesson.id)
                
                # Clean up empty entries
                if not self._lesson_index[term]:
                    del self._lesson_index[term]
    
    def _get_importance_weight(self, importance: str) -> float:
        """
        Get the weight for an importance level.
        
        Args:
            importance: Importance level.
            
        Returns:
            float: Weight (0.0 to 1.0).
        """
        weights = {
            "critical": 1.0,
            "high": 0.8,
            "medium": 0.5,
            "low": 0.2,
        }
        return weights.get(importance.lower(), 0.5)
    
    def consolidate_lessons(self) -> Dict[str, Any]:
        """
        Consolidate lessons (deduplicate, merge, archive).
        
        Returns:
            Dict[str, Any]: Consolidation results.
        """
        self.audit_logger.log("LESSON_CONSOLIDATE_START", "Starting lesson consolidation")
        start_time = time.time()
        
        results = {
            "deduplicated": 0,
            "merged": 0,
            "archived": 0,
            "deprecated": 0,
            "duration": 0.0,
        }
        
        try:
            # Step 1: Deduplicate lessons
            dedup_count = self._deduplicate_lessons()
            results["deduplicated"] = dedup_count
            
            # Step 2: Merge similar lessons
            merge_count = self._merge_similar_lessons()
            results["merged"] = merge_count
            
            # Step 3: Archive old lessons
            archive_count = self._archive_old_lessons()
            results["archived"] = archive_count
            
            # Step 4: Deprecate outdated lessons
            deprecate_count = self._deprecate_outdated_lessons()
            results["deprecated"] = deprecate_count
            
            results["duration"] = time.time() - start_time
            
            self.audit_logger.log(
                "LESSON_CONSOLIDATE_SUCCESS",
                f"Consolidated in {results['duration']:.2f}s"
            )
            
            return results
        
        except Exception as e:
            self.audit_logger.log("LESSON_CONSOLIDATE_FAIL", str(e))
            logging.error(f"Lesson consolidation failed: {e}")
            results["error"] = str(e)
            results["duration"] = time.time() - start_time
            return results
    
    def _deduplicate_lessons(self) -> int:
        """
        Deduplicate lessons with identical content.
        
        Returns:
            int: Number of duplicates removed.
        """
        # Group lessons by description
        description_groups = {}
        for lesson_id, lesson in self._lessons.items():
            description = lesson.description.strip()
            if description not in description_groups:
                description_groups[description] = []
            description_groups[description].append(lesson_id)
        
        duplicates_removed = 0
        
        for description, group in description_groups.items():
            if len(group) > 1:
                # Keep the first lesson (oldest)
                keep_id = min(group)
                
                # Delete the others
                for lesson_id in group:
                    if lesson_id != keep_id:
                        self.delete_lesson(lesson_id)
                        duplicates_removed += 1
        
        return duplicates_removed
    
    def _merge_similar_lessons(self) -> int:
        """
        Merge similar lessons.
        
        Returns:
            int: Number of merges performed.
        """
        # Simple implementation: just return 0 for now
        # In a real implementation, this would find and merge similar lessons
        return 0
    
    def _archive_old_lessons(self) -> int:
        """
        Archive old lessons that haven't been used recently.
        
        Returns:
            int: Number of lessons archived.
        """
        archived_count = 0
        
        for lesson_id, lesson in self._lessons.items():
            # Check if lesson is old (created more than 30 days ago)
            # For now, we'll use a simple heuristic
            if lesson.status == LessonStatus.NEW and lesson.created_at < time.time() - (30 * 24 * 60 * 60):
                lesson.status = LessonStatus.ARCHIVED
                self.update_lesson(lesson)
                archived_count += 1
        
        return archived_count
    
    def _deprecate_outdated_lessons(self) -> int:
        """
        Deprecate lessons that are no longer valid.
        
        Returns:
            int: Number of lessons deprecated.
        """
        deprecated_count = 0
        
        for lesson_id, lesson in self._lessons.items():
            # Check if lesson is outdated
            # In a real implementation, this would check the lesson's validity
            if lesson.status == LessonStatus.VALIDATED and lesson.confidence < 0.3:
                lesson.status = LessonStatus.DEPRECATED
                self.update_lesson(lesson)
                deprecated_count += 1
        
        return deprecated_count
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about lessons.
        
        Returns:
            Dict[str, Any]: Lesson statistics.
        """
        if not self._lessons:
            return {
                "total": 0,
                "by_type": {},
                "by_status": {},
                "by_outcome": {},
                "avg_confidence": 0.0,
            }
        
        by_type = {}
        by_status = {}
        by_outcome = {}
        total_confidence = 0.0
        
        for lesson in self._lessons.values():
            # By type
            type_key = lesson.lesson_type.value
            by_type[type_key] = by_type.get(type_key, 0) + 1
            
            # By status
            status_key = lesson.status.value
            by_status[status_key] = by_status.get(status_key, 0) + 1
            
            # By outcome
            outcome_key = lesson.outcome
            by_outcome[outcome_key] = by_outcome.get(outcome_key, 0) + 1
            
            # Total confidence
            total_confidence += lesson.confidence
        
        avg_confidence = total_confidence / len(self._lessons)
        
        return {
            "total": len(self._lessons),
            "by_type": by_type,
            "by_status": by_status,
            "by_outcome": by_outcome,
            "avg_confidence": avg_confidence,
        }
    
    def get_lesson_types(self) -> List[str]:
        """
        Get all lesson types.
        
        Returns:
            List[str]: List of lesson type values.
        """
        return [lt.value for lt in LessonType]
    
    def get_lesson_statuses(self) -> List[str]:
        """
        Get all lesson statuses.
        
        Returns:
            List[str]: List of lesson status values.
        """
        return [ls.value for ls in LessonStatus]
    
    def clear_all(self) -> None:
        """Clear all lessons."""
        self._lessons = {}
        self._next_id = 1
        self._lesson_index = {}
