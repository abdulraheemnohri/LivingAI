"""
LivingAI Learning System
=======================

Learning system for LivingAI agents.
"""

import logging
import time
from typing import Dict, Any, Optional, List


class LearningSystem:
    """
    Manages learning for LivingAI agents.
    
    Responsibilities:
    - Track experiences
    - Update models based on feedback
    - Improve tool usage patterns
    """
    
    def __init__(self):
        self._experiences: List[Dict[str, Any]] = []
        self._model_updates: List[Dict[str, Any]] = []
        self.logger = logging.getLogger(__name__)
    
    async def learn_from_experience(
        self,
        experience: str,
        context: Dict[str, Any] = None
    ) -> None:
        """
        Learn from an experience.
        
        Args:
            experience: Description of the experience
            context: Additional context
        """
        entry = {
            'timestamp': time.time(),
            'experience': experience,
            'context': context or {}
        }
        self._experiences.append(entry)
        self.logger.debug(f"Learned from experience: {experience[:50]}...")
    
    async def update_models(self) -> None:
        """
        Update models based on recent experiences.
        """
        if not self._experiences:
            return
        
        # Process recent experiences
        recent = self._experiences[-10:]  # Last 10 experiences
        
        for exp in recent:
            # Extract learning points
            update = {
                'timestamp': exp['timestamp'],
                'source': exp['experience'][:100],
                'context': exp['context']
            }
            self._model_updates.append(update)
        
        self.logger.info(f"Updated models with {len(recent)} experiences")
    
    def get_experiences(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent experiences."""
        return self._experiences[-limit:]
    
    def get_model_updates(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent model updates."""
        return self._model_updates[-limit:]
    
    def clear_experiences(self) -> None:
        """Clear all experiences."""
        self._experiences.clear()
        self.logger.info("Cleared all experiences")
