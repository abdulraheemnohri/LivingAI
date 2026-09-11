# LivingAI Idle Manager
import logging
from typing import Any


class IdleManager:
    """Handles background tasks during idle mode (consolidation, goal review, DB maintenance)."""

    def __init__(self, app: Any = None, config: Any = None, audit_logger: Any = None):
        self.app = app
        self.config = config
        self.audit_logger = audit_logger

    def run(self) -> None:
        if self.audit_logger:
            self.audit_logger.log("IDLE_START", "Starting idle processing")

        if self.app and hasattr(self.app, 'platform'):
            battery = self.app.platform.check_battery()
            pct = battery.get("percentage", 100)
            if pct < 20 and battery.get("status") != "CHARGING":
                logging.info("Skipping idle processing due to low battery")
                return

        if self.app:
            if hasattr(self.app, 'memory_manager'):
                self.app.memory_manager.consolidate()
            if hasattr(self.app, 'learning_engine'):
                self.app.learning_engine.consolidate()

        if self.audit_logger:
            self.audit_logger.log("IDLE_COMPLETE", "Completed idle processing")
