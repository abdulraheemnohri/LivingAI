# LivingAI Task Scheduler
import time
from typing import List, Dict, Any, Callable


class TaskScheduler:
    """Schedules recurring tasks for memory consolidation, backups, and goal tracking."""

    def __init__(self):
        self.tasks: List[Dict[str, Any]] = []

    def schedule(self, name: str, interval_seconds: int, func: Callable) -> None:
        self.tasks.append({
            "name": name,
            "interval": interval_seconds,
            "func": func,
            "last_run": time.time()
        })

    def tick(self) -> None:
        now = time.time()
        for task in self.tasks:
            if now - task["last_run"] >= task["interval"]:
                try:
                    task["func"]()
                except Exception as e:
                    pass
                task["last_run"] = now
