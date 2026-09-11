# LivingAI API Endpoint Handlers
import json
from typing import Dict, Any


class APIHandlers:
    """Handles REST API requests from Web UI and Android Client App."""

    def __init__(self, app: Any):
        self.app = app

    def handle_status(self) -> Dict[str, Any]:
        return self.app.get_status()

    def handle_chat(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        query = payload.get("query", "")
        if not query:
            return {"error": "Missing query parameter"}
        response = self.app.process_query(query)
        return {"query": query, "response": response}

    def handle_memory_list(self) -> Dict[str, Any]:
        memories = self.app.memory_manager.list_all()
        return {"count": len(memories), "memories": [m.to_dict() for m in memories]}

    def handle_goals_list(self) -> Dict[str, Any]:
        goals = self.app.goal_manager.get_active_goals()
        return {"count": len(goals), "goals": goals}

    def handle_skills_list(self) -> Dict[str, Any]:
        skills = self.app.skill_manager.list()
        return {"count": len(skills), "skills": skills}

    def handle_doctor(self) -> Dict[str, Any]:
        return self.app.run_doctor()
