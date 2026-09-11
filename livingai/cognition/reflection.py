# LivingAI Reflection Engine
# ==========================
# This module handles reflection and learning from interactions.

import logging
import time
from typing import Dict, Any, Optional, List

# Local imports
from ..config import ConfigManager
from ..memory.manager import MemoryManager
from ..security.audit import AuditLogger


class ReflectionEngine:
    """
    Handles reflection and learning from interactions.
    
    Responsibilities:
    - Reflect on interactions
    - Extract lessons
    - Update memories
    - Improve future responses
    """
    
    def __init__(
        self,
        memory_manager: Optional[MemoryManager] = None,
        config: Optional[ConfigManager] = None,
        audit_logger: Optional[AuditLogger] = None
    ):
        """
        Initialize the ReflectionEngine.
        
        Args:
            memory_manager: Memory manager for storing reflections.
            config: Configuration manager.
            audit_logger: Audit logger for tracking actions.
        """
        self.memory_manager = memory_manager
        self.config = config
        self.audit_logger = audit_logger
        
        # Reflection state
        self._reflection_history: List[Dict[str, Any]] = []
        self._current_reflection: Optional[Dict[str, Any]] = None
        
        logging.info("ReflectionEngine initialized")
    
    def set_memory_manager(self, memory_manager: MemoryManager) -> None:
        """
        Set the memory manager (for lazy initialization).
        
        Args:
            memory_manager: Memory manager instance.
        """
        self.memory_manager = memory_manager
    
    def reflect(
        self,
        context: Dict[str, Any],
        actions: List[Dict[str, Any]],
        observations: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Reflect on an interaction.
        
        Args:
            context: The full context of the interaction.
            actions: Actions that were taken.
            observations: Observations from the actions.
            
        Returns:
            Dict[str, Any]: Reflection results.
        """
        self.audit_logger.log("REFLECTION_START", "Starting reflection")
        start_time = time.time()
        
        try:
            reflection = {
                "timestamp": time.time(),
                "context": context,
                "actions": actions,
                "observations": observations,
                "insights": [],
                "lessons": [],
                "memory_updates": [],
            }
            
            # Analyze the interaction
            analysis = self._analyze_interaction(context, actions, observations)
            reflection["analysis"] = analysis
            
            # Extract insights
            insights = self._extract_insights(context, actions, observations, analysis)
            reflection["insights"].extend(insights)
            
            # Extract lessons
            lessons = self._extract_lessons(context, actions, observations, analysis)
            reflection["lessons"].extend(lessons)
            
            # Update memories
            memory_updates = self._update_memories(context, actions, observations, analysis)
            reflection["memory_updates"].extend(memory_updates)
            
            # Store the reflection
            self._reflection_history.append(reflection)
            self._current_reflection = reflection
            
            reflection["duration"] = time.time() - start_time
            
            self.audit_logger.log(
                "REFLECTION_SUCCESS",
                f"Completed in {reflection['duration']:.2f}s"
            )
            
            return reflection
            
        except Exception as e:
            self.audit_logger.log("REFLECTION_FAIL", str(e))
            logging.error(f"Reflection failed: {e}")
            return {
                "error": str(e),
                "insights": [],
                "lessons": [],
                "memory_updates": [],
            }
    
    def _analyze_interaction(
        self,
        context: Dict[str, Any],
        actions: List[Dict[str, Any]],
        observations: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze the interaction for reflection.
        
        Args:
            context: The full context.
            actions: Actions that were taken.
            observations: Observations from the actions.
            
        Returns:
            Dict[str, Any]: Analysis results.
        """
        analysis = {
            "success": True,
            "action_count": len(actions),
            "observation_count": len(observations.get("actions", [])),
            "input_type": context.get("perception", {}).get("type", "unknown"),
        }
        
        # Check if actions were successful
        if actions:
            successful_actions = sum(
                1 for action in actions if action.get("status") == "success"
            )
            analysis["success_rate"] = successful_actions / len(actions)
            analysis["success"] = analysis["success_rate"] >= 0.5
        
        # Analyze the response quality
        response = context.get("thoughts", {}).get("response", "")
        analysis["response_length"] = len(response)
        analysis["response_quality"] = self._estimate_response_quality(response)
        
        return analysis
    
    def _estimate_response_quality(self, response: str) -> float:
        """
        Estimate the quality of a response.
        
        Args:
            response: The response text.
            
        Returns:
            float: Quality score (0.0 to 1.0).
        """
        # Simple heuristic - in a real implementation, this would be more sophisticated
        if not response:
            return 0.0
        
        # Check for completeness
        if response.endswith("?") or response.endswith("...") or len(response) < 10:
            return 0.5
        
        # Check for coherence
        sentences = response.split(".")
        if len(sentences) >= 3:
            return 0.9
        elif len(sentences) >= 2:
            return 0.7
        else:
            return 0.6
    
    def _extract_insights(
        self,
        context: Dict[str, Any],
        actions: List[Dict[str, Any]],
        observations: Dict[str, Any],
        analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Extract insights from the interaction.
        
        Args:
            context: The full context.
            actions: Actions that were taken.
            observations: Observations from the actions.
            analysis: Analysis of the interaction.
            
        Returns:
            List[Dict[str, Any]]: Extracted insights.
        """
        insights = []
        
        # Check for successful patterns
        if analysis.get("success", False):
            insights.append({
                "type": "success_pattern",
                "description": "Interaction was successful",
                "confidence": analysis.get("success_rate", 1.0),
            })
        
        # Check for action patterns
        if actions:
            action_types = [action.get("type", "unknown") for action in actions]
            insights.append({
                "type": "action_pattern",
                "description": f"Used action types: {', '.join(set(action_types))}",
                "confidence": 0.8,
            })
        
        # Check for response patterns
        response = context.get("thoughts", {}).get("response", "")
        if response:
            insights.append({
                "type": "response_pattern",
                "description": f"Response length: {len(response)} characters",
                "confidence": 0.7,
            })
        
        return insights
    
    def _extract_lessons(
        self,
        context: Dict[str, Any],
        actions: List[Dict[str, Any]],
        observations: Dict[str, Any],
        analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Extract lessons from the interaction.
        
        Args:
            context: The full context.
            actions: Actions that were taken.
            observations: Observations from the actions.
            analysis: Analysis of the interaction.
            
        Returns:
            List[Dict[str, Any]]: Extracted lessons.
        """
        lessons = []
        
        # Check for failed actions
        failed_actions = [
            action for action in actions if action.get("status") == "failed"
        ]
        
        for action in failed_actions:
            lessons.append({
                "type": "failure_lesson",
                "description": f"Action failed: {action.get('action', 'unknown')}",
                "severity": "high",
                "suggested_action": "Avoid similar actions in the future",
            })
        
        # Check for low-quality responses
        if analysis.get("response_quality", 1.0) < 0.6:
            lessons.append({
                "type": "quality_lesson",
                "description": "Response quality was low",
                "severity": "medium",
                "suggested_action": "Improve response generation",
            })
        
        # Check for successful patterns that could be reused
        if analysis.get("success", False) and analysis.get("success_rate", 0) > 0.8:
            lessons.append({
                "type": "success_lesson",
                "description": "Interaction was highly successful",
                "severity": "low",
                "suggested_action": "Reuse this approach for similar situations",
            })
        
        return lessons
    
    def _update_memories(
        self,
        context: Dict[str, Any],
        actions: List[Dict[str, Any]],
        observations: Dict[str, Any],
        analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Update memories based on the interaction.
        
        Args:
            context: The full context.
            actions: Actions that were taken.
            observations: Observations from the actions.
            analysis: Analysis of the interaction.
            
        Returns:
            List[Dict[str, Any]]: Memory updates.
        """
        updates = []
        
        if not self.memory_manager:
            return updates
        
        # Store the interaction in memory
        user_input = context.get("perception", {}).get("raw_input", "")
        response = context.get("thoughts", {}).get("response", "")
        
        # Create a conversation memory
        conversation_memory = {
            "content": f"User: {user_input}\nAI: {response}",
            "type": "conversation",
            "importance": 0.8,
            "relevance": 0.9,
            "recency": 1.0,
            "confidence": analysis.get("response_quality", 0.7),
            "metadata": {
                "timestamp": time.time(),
                "success": analysis.get("success", False),
                "action_count": analysis.get("action_count", 0),
            },
        }
        
        # Add to memory
        memory_id = self.memory_manager.add(conversation_memory)
        updates.append({
            "type": "conversation",
            "memory_id": memory_id,
            "description": "Stored conversation in memory",
        })
        
        # Store action results if there were actions
        if actions:
            action_memory = {
                "content": f"Actions taken: {', '.join(action.get('action', '') for action in actions)}",
                "type": "action",
                "importance": 0.7,
                "relevance": 0.8,
                "recency": 1.0,
                "confidence": analysis.get("success_rate", 0.5),
                "metadata": {
                    "timestamp": time.time(),
                    "success_rate": analysis.get("success_rate", 0.5),
                },
            }
            
            memory_id = self.memory_manager.add(action_memory)
            updates.append({
                "type": "action",
                "memory_id": memory_id,
                "description": "Stored action results in memory",
            })
        
        return updates
    
    def get_reflection_history(self) -> List[Dict[str, Any]]:
        """
        Get the history of reflections.
        
        Returns:
            List[Dict[str, Any]]: Reflection history.
        """
        return self._reflection_history.copy()
    
    def get_current_reflection(self) -> Optional[Dict[str, Any]]:
        """
        Get the current reflection.
        
        Returns:
            Optional[Dict[str, Any]]: Current reflection, or None.
        """
        return self._current_reflection
    
    def clear_reflection_history(self) -> None:
        """Clear the reflection history."""
        self._reflection_history = []
        self._current_reflection = None
    
    def get_reflection_stats(self) -> Dict[str, Any]:
        """
        Get statistics about reflections.
        
        Returns:
            Dict[str, Any]: Reflection statistics.
        """
        if not self._reflection_history:
            return {
                "total": 0,
                "avg_duration": 0,
                "total_insights": 0,
                "total_lessons": 0,
            }
        
        total = len(self._reflection_history)
        avg_duration = sum(
            r.get("duration", 0) for r in self._reflection_history
        ) / total
        total_insights = sum(
            len(r.get("insights", [])) for r in self._reflection_history
        )
        total_lessons = sum(
            len(r.get("lessons", [])) for r in self._reflection_history
        )
        
        return {
            "total": total,
            "avg_duration": avg_duration,
            "total_insights": total_insights,
            "total_lessons": total_lessons,
        }
    
    def get_recent_lessons(self, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get recent lessons learned.
        
        Args:
            limit: Maximum number of lessons to return.
            
        Returns:
            List[Dict[str, Any]]: Recent lessons.
        """
        lessons = []
        
        for reflection in reversed(self._reflection_history):
            lessons.extend(reflection.get("lessons", []))
            if len(lessons) >= limit:
                break
        
        return lessons[:limit]
