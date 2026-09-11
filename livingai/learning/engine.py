# LivingAI Learning Engine
# ========================
# This module implements the learning pipeline for LivingAI.

import logging
import time
from typing import Dict, Any, Optional, List

# Local imports
from .lessons import LessonManager
from .evaluator import OutcomeEvaluator
from ..config import ConfigManager
from ..memory.manager import MemoryManager
from ..security.audit import AuditLogger


class LearningEngine:
    """
    Implements the learning pipeline for LivingAI.
    
    The learning pipeline follows this process:
    Experience -> Outcome -> Evaluation -> Lesson Candidate -> Validation -> Memory/Skill Update
    
    Responsibilities:
    - Process experiences and outcomes
    - Extract lessons from interactions
    - Validate and store lessons
    - Update knowledge based on lessons
    - Manage learning state
    """
    
    def __init__(
        self,
        memory_manager: Optional[MemoryManager] = None,
        config: Optional[ConfigManager] = None,
        audit_logger: Optional[AuditLogger] = None
    ):
        """
        Initialize the LearningEngine.
        
        Args:
            memory_manager: Memory manager for storing lessons.
            config: Configuration manager.
            audit_logger: Audit logger for tracking actions.
        """
        self.memory_manager = memory_manager
        self.config = config
        self.audit_logger = audit_logger
        
        # Initialize components
        self.lesson_manager = LessonManager(
            memory_manager=self.memory_manager,
            config=self.config,
            audit_logger=self.audit_logger
        )
        self.outcome_evaluator = OutcomeEvaluator(
            config=self.config,
            audit_logger=self.audit_logger
        )
        
        # Learning state
        self._learning_history: List[Dict[str, Any]] = []
        self._current_lesson: Optional[Dict[str, Any]] = None
        self._lessons_learned = 0
        self._last_learning_time = time.time()
        
        logging.info("LearningEngine initialized")
    
    def set_memory_manager(self, memory_manager: MemoryManager) -> None:
        """
        Set the memory manager (for lazy initialization).
        
        Args:
            memory_manager: Memory manager instance.
        """
        self.memory_manager = memory_manager
        self.lesson_manager.set_memory_manager(memory_manager)
    
    def process_experience(
        self,
        context: Dict[str, Any],
        actions: List[Dict[str, Any]],
        observations: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process an experience through the learning pipeline.
        
        Args:
            context: The context of the experience.
            actions: Actions that were taken.
            observations: Observations from the actions.
            
        Returns:
            Dict[str, Any]: Learning results.
        """
        self.audit_logger.log("LEARNING_START", "Starting learning process")
        start_time = time.time()
        
        try:
            # Step 1: Evaluate the outcome
            evaluation = self.outcome_evaluator.evaluate(
                context=context,
                actions=actions,
                observations=observations
            )
            
            # Step 2: Extract lesson candidates
            lesson_candidates = self._extract_lesson_candidates(
                context=context,
                actions=actions,
                observations=observations,
                evaluation=evaluation
            )
            
            # Step 3: Validate lesson candidates
            validated_lessons = []
            for candidate in lesson_candidates:
                validated = self._validate_lesson_candidate(candidate)
                if validated:
                    validated_lessons.append(validated)
            
            # Step 4: Store validated lessons
            stored_lessons = []
            for lesson in validated_lessons:
                lesson_id = self.lesson_manager.add_lesson(lesson)
                stored_lessons.append({
                    **lesson,
                    "id": lesson_id,
                    "stored_at": time.time()
                })
            
            # Step 5: Update knowledge based on lessons
            knowledge_updates = self._update_knowledge(stored_lessons)
            
            # Record the learning operation
            learning_result = {
                "timestamp": time.time(),
                "context": context,
                "actions": actions,
                "observations": observations,
                "evaluation": evaluation,
                "lesson_candidates": lesson_candidates,
                "validated_lessons": validated_lessons,
                "stored_lessons": stored_lessons,
                "knowledge_updates": knowledge_updates,
                "duration": time.time() - start_time,
            }
            
            self._learning_history.append(learning_result)
            self._lessons_learned += len(stored_lessons)
            self._last_learning_time = time.time()
            
            self.audit_logger.log(
                "LEARNING_SUCCESS",
                f"Learned {len(stored_lessons)} lessons in {learning_result['duration']:.2f}s"
            )
            
            return learning_result
        
        except Exception as e:
            self.audit_logger.log("LEARNING_FAIL", str(e))
            logging.error(f"Learning failed: {e}")
            return {
                "error": str(e),
                "lessons_learned": 0,
            }
    
    def _extract_lesson_candidates(
        self,
        context: Dict[str, Any],
        actions: List[Dict[str, Any]],
        observations: Dict[str, Any],
        evaluation: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Extract lesson candidates from an experience.
        
        Args:
            context: The context of the experience.
            actions: Actions that were taken.
            observations: Observations from the actions.
            evaluation: Evaluation of the outcome.
            
        Returns:
            List[Dict[str, Any]]: List of lesson candidates.
        """
        candidates = []
        
        # Extract lessons from successful actions
        successful_actions = [
            action for action in actions if action.get("status") == "success"
        ]
        
        for action in successful_actions:
            candidate = self._create_lesson_from_action(action, evaluation)
            if candidate:
                candidates.append(candidate)
        
        # Extract lessons from failed actions
        failed_actions = [
            action for action in actions if action.get("status") == "failed"
        ]
        
        for action in failed_actions:
            candidate = self._create_lesson_from_failure(action, evaluation)
            if candidate:
                candidates.append(candidate)
        
        # Extract lessons from observations
        if observations:
            candidate = self._create_lesson_from_observations(observations, evaluation)
            if candidate:
                candidates.append(candidate)
        
        return candidates
    
    def _create_lesson_from_action(
        self,
        action: Dict[str, Any],
        evaluation: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Create a lesson candidate from a successful action.
        
        Args:
            action: The successful action.
            evaluation: Evaluation of the outcome.
            
        Returns:
            Optional[Dict[str, Any]]: Lesson candidate, or None if none created.
        """
        # Check if the action was effective
        if evaluation.get("effectiveness", 0) > 0.7:
            return {
                "type": "positive",
                "source": "action",
                "action": action.get("action", "unknown"),
                "description": f"Action '{action.get('action')}' was effective",
                "outcome": "success",
                "confidence": evaluation.get("effectiveness", 0.7),
                "importance": self._calculate_importance(evaluation),
                "context": {
                    "action_id": action.get("id"),
                    "action_type": action.get("type"),
                },
            }
        
        return None
    
    def _create_lesson_from_failure(
        self,
        action: Dict[str, Any],
        evaluation: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Create a lesson candidate from a failed action.
        
        Args:
            action: The failed action.
            evaluation: Evaluation of the outcome.
            
        Returns:
            Optional[Dict[str, Any]]: Lesson candidate, or None if none created.
        """
        # Always create a lesson from failures
        return {
            "type": "negative",
            "source": "action_failure",
            "action": action.get("action", "unknown"),
            "description": f"Action '{action.get('action')}' failed",
            "outcome": "failure",
            "confidence": 0.9,
            "importance": MemoryImportance.HIGH.value,
            "context": {
                "action_id": action.get("id"),
                "action_type": action.get("type"),
                "error": action.get("error", "unknown"),
            },
        }
    
    def _create_lesson_from_observations(
        self,
        observations: Dict[str, Any],
        evaluation: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Create a lesson candidate from observations.
        
        Args:
            observations: Observations from actions.
            evaluation: Evaluation of the outcome.
            
        Returns:
            Optional[Dict[str, Any]]: Lesson candidate, or None if none created.
        """
        # Check if there are meaningful observations
        if observations.get("actions"):
            return {
                "type": "observation",
                "source": "observation",
                "description": f"Observed {len(observations.get('actions', []))} actions",
                "outcome": evaluation.get("outcome", "neutral"),
                "confidence": evaluation.get("confidence", 0.5),
                "importance": self._calculate_importance(evaluation),
                "context": {
                    "observation_count": len(observations.get("actions", [])),
                },
            }
        
        return None
    
    def _calculate_importance(self, evaluation: Dict[str, Any]) -> str:
        """
        Calculate the importance level for a lesson.
        
        Args:
            evaluation: Evaluation of the outcome.
            
        Returns:
            str: Importance level ("critical", "high", "medium", "low").
        """
        effectiveness = evaluation.get("effectiveness", 0)
        impact = evaluation.get("impact", 0)
        
        # Simple heuristic
        if effectiveness > 0.8 and impact > 0.8:
            return "critical"
        elif effectiveness > 0.6 or impact > 0.6:
            return "high"
        elif effectiveness > 0.4 or impact > 0.4:
            return "medium"
        else:
            return "low"
    
    def _validate_lesson_candidate(self, candidate: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Validate a lesson candidate.
        
        Args:
            candidate: Lesson candidate to validate.
            
        Returns:
            Optional[Dict[str, Any]]: Validated lesson, or None if invalid.
        """
        # Basic validation
        if not candidate.get("description"):
            return None
        
        # Check confidence
        if candidate.get("confidence", 0) < 0.3:
            return None
        
        # Check importance
        if candidate.get("importance", "low") == "low" and candidate.get("type") != "negative":
            return None
        
        # Add validation timestamp
        candidate["validated_at"] = time.time()
        candidate["validated"] = True
        
        return candidate
    
    def _update_knowledge(self, lessons: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Update knowledge based on learned lessons.
        
        Args:
            lessons: List of validated lessons.
            
        Returns:
            List[Dict[str, Any]]: Knowledge updates performed.
        """
        updates = []
        
        for lesson in lessons:
            # Update memories
            if self.memory_manager:
                memory_data = {
                    "content": f"Lesson: {lesson.get('description')}",
                    "type": "lesson",
                    "importance": lesson.get("importance", "medium"),
                    "relevance": lesson.get("confidence", 0.5),
                    "recency": 1.0,
                    "confidence": lesson.get("confidence", 0.5),
                    "metadata": {
                        "lesson_type": lesson.get("type"),
                        "source": lesson.get("source"),
                        "outcome": lesson.get("outcome"),
                    },
                }
                
                memory_id = self.memory_manager.add(memory_data)
                updates.append({
                    "type": "memory",
                    "memory_id": memory_id,
                    "lesson_id": lesson.get("id"),
                })
        
        return updates
    
    def status(self) -> Dict[str, Any]:
        """
        Get the current learning status.
        
        Returns:
            Dict[str, Any]: Learning status.
        """
        return {
            "lessons_learned": self._lessons_learned,
            "last_learning_time": self._last_learning_time,
            "learning_history_count": len(self._learning_history),
            "lesson_manager": self.lesson_manager.get_stats(),
        }
    
    def review(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Review recent lessons.
        
        Args:
            limit: Maximum number of lessons to review.
            
        Returns:
            List[Dict[str, Any]]: Recent lessons.
        """
        return self.lesson_manager.list_lessons(limit)
    
    def consolidate(self) -> Dict[str, Any]:
        """
        Consolidate learned knowledge.
        
        Returns:
            Dict[str, Any]: Consolidation results.
        """
        return self.lesson_manager.consolidate_lessons()
    
    def list_lessons(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        List all lessons.
        
        Args:
            limit: Maximum number of lessons to return.
            
        Returns:
            List[Dict[str, Any]]: List of lessons.
        """
        return self.lesson_manager.list_lessons(limit)
    
    def get_learning_history(self) -> List[Dict[str, Any]]:
        """
        Get the history of learning operations.
        
        Returns:
            List[Dict[str, Any]]: Learning history.
        """
        return self._learning_history.copy()
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about learning.
        
        Returns:
            Dict[str, Any]: Learning statistics.
        """
        if not self._learning_history:
            return {
                "total_operations": 0,
                "total_lessons_learned": 0,
                "avg_lessons_per_operation": 0.0,
                "avg_duration": 0.0,
            }
        
        total_operations = len(self._learning_history)
        total_lessons = sum(
            len(op.get("stored_lessons", [])) for op in self._learning_history
        )
        avg_lessons = total_lessons / total_operations if total_operations > 0 else 0.0
        avg_duration = sum(
            op.get("duration", 0) for op in self._learning_history
        ) / total_operations
        
        return {
            "total_operations": total_operations,
            "total_lessons_learned": total_lessons,
            "avg_lessons_per_operation": avg_lessons,
            "avg_duration": avg_duration,
        }
    
    def clear_history(self) -> None:
        """Clear the learning history."""
        self._learning_history = []
        self._lessons_learned = 0
