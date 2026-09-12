# LivingAI App: Core Application Logic
# ====================================
# This module provides the core LivingAI application class that orchestrates
# all components: cognitive engine, memory, model, skills, goals, etc.

import os
import sys
import logging
from typing import Optional, Dict, Any
from pathlib import Path

# Local imports
from .config import ConfigManager
from .ai.model_manager import ModelManager
from .cognition.engine import CognitiveEngine
from .memory.manager import MemoryManager
from .learning.engine import LearningEngine
from .skills.manager import SkillManager
from .goals.manager import GoalManager
from .actions.engine import ActionEngine
from .state.engine import StateEngine
from .autonomy.daemon import Daemon
from .autonomy.idle import IdleManager
from .backup.manager import BackupManager
from .platform.termux import TermuxPlatform
from .security.audit import AuditLogger
from .app_agent_extension import add_agent_support


class LivingAIApp:
    """
    Core LivingAI application class.
    
    This class initializes and manages all components of the LivingAI system,
    including the cognitive engine, memory, model, skills, goals, and more.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the LivingAI application.
        
        Args:
            config_path: Optional path to a custom config file.
        """
        # Set up paths
        self.livingai_home = os.path.expanduser("~/.livingai")
        self.config_path = config_path or os.path.join(self.livingai_home, "config", "config.yaml")
        self.model_dir = os.path.join(self.livingai_home, "models")
        self.data_dir = os.path.join(self.livingai_home, "data")
        self.logs_dir = os.path.join(self.livingai_home, "logs")
        
        # Create directories if they don't exist
        os.makedirs(self.livingai_home, exist_ok=True)
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        os.makedirs(self.model_dir, exist_ok=True)
        os.maked
irs(self.data_dir, exist_ok=True)
        os.makedirs(self.logs_dir, exist_ok=True)
        
        # Set up logging
        self._setup_logging()
        
        # Initialize components
        self.config = ConfigManager(self.config_path)
        self.platform = TermuxPlatform()
        self.audit_logger = AuditLogger(self.logs_dir)
        
        # Initialize model manager
        self.model_manager = ModelManager(
            model_dir=self.model_dir,
            config=self.config,
            platform=self.platform,
            audit_logger=self.audit_logger
        )
        
        # Initialize cognitive engine (depends on model manager)
        self.cognitive_engine = CognitiveEngine(
            model_manager=self.model_manager,
            config=self.config,
            audit_logger=self.audit_logger
        )
        
        # Initialize memory manager
        self.memory_manager = MemoryManager(
            db_path=os.path.join(self.data_dir, "livingai.db"),
            config=self.config,
            audit_logger=self.audit_logger
        )
        
        # Initialize learning engine
        self.learning_engine = LearningEngine(
            memory_manager=self.memory_manager,
            config=self.config,
            audit_logger=self.audit_logger
        )
        
        # Initialize skill manager
        self.skill_manager = SkillManager(
            skills_dir=os.path.join(self.livingai_home, "skills"),
            config=self.config,
            audit_logger=self.audit_logger
        )
        
        # Initialize goal manager
        self.goal_manager = GoalManager(
            memory_manager=self.memory_manager,
            config=self.config,
            audit_logger=self.audit_logger
        )
        
        # Initialize action engine
        self.action_engine = ActionEngine(
            config=self.config,
            audit_logger=self.audit_logger
        )
        
        # Initialize state engine
        self.state_engine
 = StateEngine(
            config=self.config,
            audit_logger=self.audit_logger
        )
        
        # Initialize backup manager
        self.backup_manager = BackupManager(
            backup_dir=os.path.join(self.livingai_home, "backups"),
            config=self.config,
            audit_logger=self.audit_logger
        )
        
        # Initialize daemon
        self.daemon = Daemon(
            app=self,
            config=self.config,
            audit_logger=self.audit_logger
        )
        
        # Initialize idle manager
        self.idle = IdleManager(
            app=self,
            config=self.config,
            audit_logger=self.audit_logger
        )
        
        # Initialize agent support
        add_agent_support(self)
        
        # Log initialization
        self.audit_logger.log("APP_INIT", "LivingAI application initialized")
        logging.info("LivingAI application initialized")
    
    def _setup_logging(self) -> None:
        """Set up logging configuration."""
        log_level = os.getenv("LIVINGAI_LOG_LEVEL", "INFO").upper()
        log_file = os.path.join(self.logs_dir, "livingai.log")
        
        logging.basicConfig(
            level=getattr(logging, log_level, logging.INFO),
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        # Suppress some third-party logs
        logging.getLogger("transformers").setLevel(logging.WARNING)
        logging.getLogger("huggingface_hub").setLevel(logging.WARNING)
    
    def run(self) -> None:
        """
        Run the LivingAI application in interactive mode.
        """
        from .ui.terminal import TerminalUI
        ui = TerminalUI(self)
        ui.run_interactive_mode()
    
    def process_query(self, query: str, **kwargs) -> str:
        """
        Process a query through the cognitive engine.
        
        Args:
            query: The user
's query or prompt.
            **kwargs: Additional arguments for processing.
            
        Returns:
            str: The AI's response.
        """
        return self.cognitive_engine.process(query, **kwargs)
    
    def process_streaming(self, query: str, **kwargs) -> Any:
        """
        Process a query with streaming output.
        
        Args:
            query: The user's query or prompt.
            **kwargs: Additional arguments for processing.
            
        Returns:
            Generator or similar for streaming output.
        """
        return self.cognitive_engine.process_streaming(query, **kwargs)
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get the current status of the LivingAI system.
        
        Returns:
            Dict[str, Any]: Status information including model, memory, goals, etc.
        """
        status = {
            "model": self.model_manager.get_status(),
            "memory": self.memory_manager.get_stats(),
            "goals": self.goal_manager.get_active_goals(),
            "skills": self.skill_manager.get_skill_count(),
            "state": self.state_engine.get_state(),
            "platform": self.platform.get_info(),
        }
        return status
    
    def shutdown(self) -> None:
        """Cleanly shutdown the LivingAI application."""
        self.audit_logger.log("APP_SHUTDOWN", "LivingAI application shutting down")
        self.model_manager.unload()
        logging.info("LivingAI application shut down")
    
    def run_doctor(self) -> Dict[str, Any]:
        """
        Run system diagnostics.
        
        Returns:
            Dict[str, Any]: Diagnostic results.
        """
        diagnostics = {
            "termux": self.platform.check_termux(),
            "android": self.platform.check_android(),
            "python": self.platform.check_python(),
            "model": self.model_manager.doctor(),
            "memory": self.memory_manager.doctor(),
      
      "storage": self.platform.check_storage(),
            "battery": self.platform.check_battery(),
        }
        return diagnostics
    
    def run_benchmark(self) -> Dict[str, Any]:
        """
        Run performance benchmarks.
        
        Returns:
            Dict[str, Any]: Benchmark results.
        """
        return self.model_manager.benchmark()


# Global app instance (for convenience in some cases)
_app_instance: Optional[LivingAIApp] = None


def get_app() -> LivingAIApp:
    """
    Get the global LivingAI app instance, creating it if necessary.
    
    Returns:
        LivingAIApp: The application instance.
    """
    global _app_instance
    if _app_instance is None:
        _app_instance = LivingAIApp()
    return _app_instance


def reset_app() -> None:
    """Reset the global app instance."""
    global _app_instance
    if _app_instance is not None:
        _app_instance.shutdown()
        _app_instance = None
