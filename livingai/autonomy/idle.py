# LivingAI Idle Manager
# ======================
# This module manages idle-mode tasks for LivingAI.

import logging
import time
from typing import Dict, Any, Optional, List, Callable
from enum import Enum

# Local imports
from ..config import ConfigManager
from ..security.audit import AuditLogger


class IdleTaskType(Enum):
    """Types of idle tasks."""
    MEMORY_CONSOLIDATION = "memory_consolidation"
    SKILL_VALIDATION = "skill_validation"
    GOAL_REVIEW = "goal_review"
    LESSON_GENERATION = "lesson_generation"
    WORKSPACE_ORGANIZATION = "workspace_organization"
    TASK_PREPARATION = "task_preparation"
    DATABASE_MAINTENANCE = "database_maintenance"
    LOG_COMPRESSION = "log_compression"
    CLEANUP = "cleanup"


class IdleManager:
    """
    Manages idle-mode tasks for LivingAI.
    
    Responsibilities:
    - Run tasks when the system is idle
    - Manage idle task queue
    - Track idle task execution
    - Handle idle mode transitions
    """
    
    def __init__(
        self,
        app: Any,
        config: ConfigManager,
        audit_logger: AuditLogger
    ):
        """
        Initialize the IdleManager.
        
        Args:
            app: The LivingAI application instance.
            config: Configuration manager.
            audit_logger: Audit logger for tracking actions.
        """
        self.app = app
        self.config = config
        self.audit_logger = audit_logger
        
        # Idle state
        self._is_idle = False
        self._last_idle_time: Optional[float] = None
        self._last_activity_time: Optional[float] = None
        self._idle_start_time: Optional[float] = None
        
        # Task queue
        self._task_queue: List[Dict[str, Any]] = []
        self._completed_tasks: List[Dict[str, Any]] = []
        self._failed_tasks: List[Dict[str, Any]] = []
        
        # Task handlers
        self._task_handlers = {
            IdleTaskType.MEMORY_CONSOLIDATION: self._handle_memory_consolidation,
            IdleTaskType.SKILL_VALIDATION: self._handle_skill_validation,
            IdleTaskType.GOAL_REVIEW: self._handle_goal_review,
            IdleTaskType.LESSON_GENERATION: self._handle_lesson_generation,
            IdleTaskType.WORKSPACE_ORGANIZATION: self._handle_workspace_organization,
            IdleTaskType.TASK_PREPARATION: self._handle_task_preparation,
            IdleTaskType.DATABASE_MAINTENANCE: self._handle_database_maintenance,
            IdleTaskType.LOG_COMPRESSION: self._handle_log_compression,
            IdleTaskType.CLEANUP: self._handle_cleanup,
        }
        
        logging.info("IdleManager initialized")
    
    def enter_idle_mode(self) -> None:
        """Enter idle mode."""
        self._is_idle = True
        self._idle_start_time = time.time()
        self._last_idle_time = time.time()
        
        self.audit_logger.log("IDLE_ENTER", "Entered idle mode")
        logging.info("Entered idle mode")
    
    def exit_idle_mode(self) -> None:
        """Exit idle mode."""
        self._is_idle = False
        
        if self._idle_start_time:
            duration = time.time() - self._idle_start_time
            self.audit_logger.log(
                "IDLE_EXIT",
                f"Exited idle mode after {duration:.2f}s"
            )
        
        logging.info("Exited idle mode")
    
    def is_idle(self) -> bool:
        """
        Check if the system is currently idle.
        
        Returns:
            bool: True if idle, False otherwise.
        """
        return self._is_idle
    
    def get_idle_duration(self) -> float:
        """
        Get the duration of the current idle period.
        
        Returns:
            float: Idle duration in seconds.
        """
        if self._idle_start_time is None:
            return 0.0
        
        return time.time() - self._idle_start_time
    
    def update_last_activity(self) -> None:
        """Update the timestamp of the last activity."""
        self._last_activity_time = time.time()
        
        # If we were idle, exit idle mode
        if self._is_idle:
            self.exit_idle_mode()
    
    def should_enter_idle(self) -> bool:
        """
        Determine if we should enter idle mode.
        
        Returns:
            bool: True if we should enter idle, False otherwise.
        """
        if self._is_idle:
            return False
        
        if self._last_activity_time is None:
            return False
        
        idle_timeout = self.config.get("autonomy.idle_timeout", 300)  # 5 minutes
        time_since_activity = time.time() - self._last_activity_time
        
        return time_since_activity >= idle_timeout
    
    def run(self) -> Dict[str, Any]:
        """
        Run idle-mode tasks.
        
        Returns:
            Dict[str, Any]: Result of idle tasks execution.
        """
        if not self._is_idle:
            self.enter_idle_mode()
        
        self.audit_logger.log("IDLE_RUN_START", "Starting idle tasks")
        start_time = time.time()
        
        results = {
            "start_time": start_time,
            "tasks_run": 0,
            "tasks_completed": 0,
            "tasks_failed": 0,
            "duration": 0.0,
        }
        
        try:
            # Check if we should run idle tasks
            if not self._should_run_idle_tasks():
                return results
            
            # Get tasks to run
            tasks_to_run = self._get_tasks_to_run()
            
            for task in tasks_to_run:
                results["tasks_run"] += 1
                
                try:
                    # Execute the task
                    task_result = self._execute_task(task)
                    
                    if task_result.get("success", False):
                        results["tasks_completed"] += 1
                        self._completed_tasks.append({
                            "task": task,
                            "result": task_result,
                            "timestamp": time.time(),
                        })
                    else:
                        results["tasks_failed"] += 1
                        self._failed_tasks.append({
                            "task": task,
                            "result": task_result,
                            "timestamp": time.time(),
                        })
                
                except Exception as e:
                    results["tasks_failed"] += 1
                    self._failed_tasks.append({
                        "task": task,
                        "error": str(e),
                        "timestamp": time.time(),
                    })
                    logging.error(f"Idle task failed: {e}")
            
            results["duration"] = time.time() - start_time
            
            self.audit_logger.log(
                "IDLE_RUN_SUCCESS",
                f"Completed {results['tasks_completed']} tasks in {results['duration']:.2f}s"
            )
            
            return results
        
        except Exception as e:
            results["error"] = str(e)
            results["duration"] = time.time() - start_time
            
            self.audit_logger.log("IDLE_RUN_FAIL", str(e))
            logging.error(f"Idle run failed: {e}")
            
            return results
    
    def _should_run_idle_tasks(self) -> bool:
        """
        Determine if we should run idle tasks.
        
        Returns:
            bool: True if we should run idle tasks, False otherwise.
        """
        # Check battery level
        min_battery = self.config.get("battery.min_percentage", 20)
        
        # In a real implementation, we would check the actual battery level
        # For now, we'll assume it's okay
        
        # Check if we're charging (if required)
        charging_required = self.config.get("battery.charging_required", False)
        
        # In a real implementation, we would check if we're charging
        
        # For now, just return True
        return True
    
    def _get_tasks_to_run(self) -> List[Dict[str, Any]]:
        """
        Get the list of tasks to run during idle mode.
        
        Returns:
            List[Dict[str, Any]]: List of tasks to run.
        """
        # Get all task types
        task_types = list(IdleTaskType)
        
        # Get the interval for each task type
        intervals = {
            IdleTaskType.MEMORY_CONSOLIDATION: self.config.get(
                "autonomy.memory_consolidation_interval", 3600
            ),  # 1 hour
            IdleTaskType.SKILL_VALIDATION: self.config.get(
                "autonomy.skill_validation_interval", 7200
            ),  # 2 hours
            IdleTaskType.GOAL_REVIEW: self.config.get(
                "autonomy.goal_review_interval", 10800
            ),  # 3 hours
            IdleTaskType.LESSON_GENERATION: self.config.get(
                "autonomy.lesson_generation_interval", 1800
            ),  # 30 minutes
            IdleTaskType.WORKSPACE_ORGANIZATION: self.config.get(
                "autonomy.workspace_organization_interval", 3600
            ),  # 1 hour
            IdleTaskType.TASK_PREPARATION: self.config.get(
                "autonomy.task_preparation_interval", 1800
            ),  # 30 minutes
            IdleTaskType.DATABASE_MAINTENANCE: self.config.get(
                "autonomy.database_maintenance_interval", 86400
            ),  # 24 hours
            IdleTaskType.LOG_COMPRESSION: self.config.get(
                "autonomy.log_compression_interval", 86400
            ),  # 24 hours
            IdleTaskType.CLEANUP: self.config.get(
                "autonomy.cleanup_interval", 43200
            ),  # 12 hours
        }
        
        # Check which tasks should run
        tasks_to_run = []
        
        for task_type in task_types:
            interval = intervals.get(task_type, 3600)
            
            # Check if enough time has passed since last run
            if self._should_run_task(task_type, interval):
                tasks_to_run.append({
                    "type": task_type,
                    "interval": interval,
                    "last_run": self._get_last_run_time(task_type),
                })
        
        return tasks_to_run
    
    def _should_run_task(self, task_type: IdleTaskType, interval: float) -> bool:
        """
        Determine if a specific task should run.
        
        Args:
            task_type: Type of the task.
            interval: Interval between runs in seconds.
            
        Returns:
            bool: True if the task should run, False otherwise.
        """
        last_run = self._get_last_run_time(task_type)
        
        if last_run is None:
            return True
        
        time_since_run = time.time() - last_run
        
        return time_since_run >= interval
    
    def _get_last_run_time(self, task_type: IdleTaskType) -> Optional[float]:
        """
        Get the last run time for a task type.
        
        Args:
            task_type: Type of the task.
            
        Returns:
            Optional[float]: Last run time, or None if never run.
        """
        # Check completed tasks
        for task_record in reversed(self._completed_tasks):
            if task_record.get("task", {}).get("type") == task_type:
                return task_record.get("timestamp")
        
        return None
    
    def _execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute an idle task.
        
        Args:
            task: Task to execute.
            
        Returns:
            Dict[str, Any]: Task execution result.
        """
        task_type = task.get("type")
        
        if not task_type:
            return {"success": False, "error": "No task type specified"}
        
        try:
            task_type_enum = IdleTaskType(task_type)
        except ValueError:
            return {"success": False, "error": f"Unknown task type: {task_type}"}
        
        # Get the handler for this task type
        handler = self._task_handlers.get(task_type_enum)
        
        if not handler:
            return {"success": False, "error": f"No handler for task type: {task_type}"}
        
        # Execute the handler
        try:
            result = handler()
            return {"success": True, "result": result}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _handle_memory_consolidation(self) -> Dict[str, Any]:
        """
        Handle memory consolidation task.
        
        Returns:
            Dict[str, Any]: Result of memory consolidation.
        """
        if not self.app or not hasattr(self.app, "memory_manager"):
            return {"status": "skipped", "reason": "Memory manager not available"}
        
        return self.app.memory_manager.consolidate()
    
    def _handle_skill_validation(self) -> Dict[str, Any]:
        """
        Handle skill validation task.
        
        Returns:
            Dict[str, Any]: Result of skill validation.
        """
        if not self.app or not hasattr(self.app, "skill_manager"):
            return {"status": "skipped", "reason": "Skill manager not available"}
        
        # In a real implementation, this would validate all skills
        return {"status": "completed", "skills_validated": 0}
    
    def _handle_goal_review(self) -> Dict[str, Any]:
        """
        Handle goal review task.
        
        Returns:
            Dict[str, Any]: Result of goal review.
        """
        if not self.app or not hasattr(self.app, "goal_manager"):
            return {"status": "skipped", "reason": "Goal manager not available"}
        
        # In a real implementation, this would review all goals
        goals = self.app.goal_manager.list()
        
        return {
            "status": "completed",
            "goals_reviewed": len(goals),
            "active_goals": len([g for g in goals if g.get("status") == "active"]),
            "completed_goals": len([g for g in goals if g.get("status") == "completed"]),
        }
    
    def _handle_lesson_generation(self) -> Dict[str, Any]:
        """
        Handle lesson generation task.
        
        Returns:
            Dict[str, Any]: Result of lesson generation.
        """
        if not self.app or not hasattr(self.app, "learning_engine"):
            return {"status": "skipped", "reason": "Learning engine not available"}
        
        # In a real implementation, this would generate lessons from recent interactions
        return {"status": "completed", "lessons_generated": 0}
    
    def _handle_workspace_organization(self) -> Dict[str, Any]:
        """
        Handle workspace organization task.
        
        Returns:
            Dict[str, Any]: Result of workspace organization.
        """
        # In a real implementation, this would organize the workspace
        return {"status": "completed", "files_organized": 0}
    
    def _handle_task_preparation(self) -> Dict[str, Any]:
        """
        Handle task preparation task.
        
        Returns:
            Dict[str, Any]: Result of task preparation.
        """
        # In a real implementation, this would prepare tasks for future execution
        return {"status": "completed", "tasks_prepared": 0}
    
    def _handle_database_maintenance(self) -> Dict[str, Any]:
        """
        Handle database maintenance task.
        
        Returns:
            Dict[str, Any]: Result of database maintenance.
        """
        if not self.app or not hasattr(self.app, "memory_manager"):
            return {"status": "skipped", "reason": "Memory manager not available"}
        
        # In a real implementation, this would perform database maintenance
        return {"status": "completed", "database_optimized": True}
    
    def _handle_log_compression(self) -> Dict[str, Any]:
        """
        Handle log compression task.
        
        Returns:
            Dict[str, Any]: Result of log compression.
        """
        # In a real implementation, this would compress old log files
        return {"status": "completed", "logs_compressed": 0}
    
    def _handle_cleanup(self) -> Dict[str, Any]:
        """
        Handle cleanup task.
        
        Returns:
            Dict[str, Any]: Result of cleanup.
        """
        # In a real implementation, this would clean up temporary files
        return {"status": "completed", "files_cleaned": 0}
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get the current status of the idle manager.
        
        Returns:
            Dict[str, Any]: Idle manager status.
        """
        return {
            "is_idle": self._is_idle,
            "idle_duration": self.get_idle_duration(),
            "last_idle_time": self._last_idle_time,
            "last_activity_time": self._last_activity_time,
            "tasks_completed": len(self._completed_tasks),
            "tasks_failed": len(self._failed_tasks),
        }
    
    def get_completed_tasks(self) -> List[Dict[str, Any]]:
        """
        Get the list of completed idle tasks.
        
        Returns:
            List[Dict[str, Any]]: List of completed tasks.
        """
        return self._completed_tasks.copy()
    
    def get_failed_tasks(self) -> List[Dict[str, Any]]:
        """
        Get the list of failed idle tasks.
        
        Returns:
            List[Dict[str, Any]]: List of failed tasks.
        """
        return self._failed_tasks.copy()
    
    def clear_history(self) -> None:
        """Clear the idle task history."""
        self._completed_tasks = []
        self._failed_tasks = []
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about idle tasks.
        
        Returns:
            Dict[str, Any]: Idle task statistics.
        """
        return {
            "total_completed": len(self._completed_tasks),
            "total_failed": len(self._failed_tasks),
            "success_rate": (
                len(self._completed_tasks) / (len(self._completed_tasks) + len(self._failed_tasks))
                if (len(self._completed_tasks) + len(self._failed_tasks)) > 0
                else 0.0
            ),
        }
