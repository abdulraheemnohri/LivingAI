# LivingAI Screen Perception
from typing import Dict, Any


class ScreenPerception:
    """Handles Android screen inspection integration if permitted."""

    @staticmethod
    def get_screen_text() -> Dict[str, Any]:
        return {
            "status": "UNAVAILABLE",
            "reason": "Android accessibility permission/component required.",
            "text": "",
        }
