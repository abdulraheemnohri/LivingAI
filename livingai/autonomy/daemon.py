# LivingAI Daemon
# ================
# This module implements the background daemon for LivingAI.

import os
import sys
import time
import logging
import threading
import signal
from typing import Dict, Any, Optional, List, Callable
from enum import Enum

# Local imports
from ..config import ConfigManager
from ..security.audit import AuditLogger
from .idle import IdleManager
from .scheduler import TaskScheduler


class DaemonStatus(Enum):
    """Status of the daemon."""
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    PAUSED = "paused"
    ERROR = "error"


class Daemon:
    """
    Implements the background daemon for LivingAI.
    
    Responsibilities:
    - Run in the background
    - Monitor system state
    - Execute periodic tasks
    - Manage idle mode
    - Handle graceful shutdown
    """
    
    def __init__(
        self,
        app: Any,
        config: ConfigManager,
        audit_logger: AuditLogger
    ):
        """
        Initialize the Daemon.
        
        Args:
            app: The LivingAI application instance.
            config: Configuration manager.
            audit_logger: Audit logger for tracking actions.
        """
        self.app = app
        self.config = config
        self.audit_logger = audit_logger
        
        # Daemon state
        self._status = DaemonStatus.STOPPED
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._pause_event = threading.Event()
        self._start_time: Optional[float] = None
        self._last_activity_time: Optional[float] = None
        
        # Initialize components
        self.idle_manager = IdleManager(
            app=self.app,
            config=self.config,
            audit_logger=self.audit_logger
        )
        self.scheduler = TaskScheduler(
            config=self.config,
            audit_logger=self.audit_logger
        )
        
        # Register signal handlers
        self._register_signal_handlers()
        
        logging.info("Daemon initialized")
    
    def _register_signal_handlers(self) -> None:
        """Register signal handlers for graceful shutdown."""
        try:
            signal.signal(signal.SIGINT, self._handle_signal)
            signal.signal(signal.SIGTERM, self._handle_signal)
        except Exception as e:
            logging.warning(f"Failed to register signal handlers: {e}")
    
    def _handle_signal(self, signum: int, frame: Any) -> None:
        """
        Handle a signal for graceful shutdown.
        
        Args:
            signum: Signal number.
            frame: Signal frame.
        """
        logging.info(f"Received signal {signum}, stopping daemon...")
        self.stop()
    
    def start(self) -> bool:
        """
        Start the daemon.
        
        Returns:
            bool: True if daemon started successfully, False otherwise.
        """
        if self._status == DaemonStatus.RUNNING:
            logging.warning("Daemon is already running")
            return False
        
        if self._status == DaemonStatus.STARTING:
            logging.warning("Daemon is already starting")
            return False
        
        self._status = DaemonStatus.STARTING
        self._stop_event.clear()
        self._pause_event.clear()
        self._start_time = time.time()
        self._last_activity_time = time.time()
        
        # Create and start the daemon thread
        self._thread = threading.Thread(
            target=self._run,
            daemon=True,
            name="LivingAI-Daemon"
        )
        self._thread.start()
        
        # Wait for the daemon to start
        time.sleep(0.1)
        
        if self._status == DaemonStatus.RUNNING:
            self.audit_logger.log("DAEMON_START", "Daemon started successfully")
            return True
        else:
            self._status = DaemonStatus.ERROR
            logging.error("Failed to start daemon")
            return False
    
    def _run(self) -> None:
        """Main daemon loop."""
        try:
            self._status = DaemonStatus.RUNNING
            self.audit_logger.log("DAEMON_RUN_START", "Daemon main loop started")
            
            while not self._stop_event.is_set():
                # Check if paused
                if self._pause_event.is_set():
                    time.sleep(0.1)
                    continue
                
                # Update last activity time
                self._last_activity_time = time.time()
                
                # Run the main loop
                self._main_loop()
                
                # Sleep for a short time
                sleep_time = self.config.get("autonomy.daemon_sleep_interval", 1.0)
                time.sleep(sleep_time)
            
            # Cleanup
            self._status = DaemonStatus.STOPPED
            self.audit_logger.log("DAEMON_RUN_END", "Daemon main loop ended")
            
        except Exception as e:
            self._status = DaemonStatus.ERROR
            self.audit_logger.log("DAEMON_RUN_ERROR", str(e))
            logging.error(f"Daemon error: {e}")
    
    def _main_loop(self) -> None:
        """Main daemon loop logic."""
        try:
            # Check system health
            self._check_system_health()
            
            # Run scheduled tasks
            self.scheduler.run_pending_tasks()
            
            # Check if we should run idle tasks
            if self._should_run_idle_tasks():
                self.idle_manager.run()
            
            # Check battery and thermal conditions
            if self._should_stop_for_safety():
                self.pause()
            
        except Exception as e:
            logging.error(f"Daemon main loop error: {e}")
    
    def _check_system_health(self) -> None:
        """Check the health of the system."""
        # In a real implementation, this would check:
        # - Battery level
        # - Thermal status
        # - Memory usage
        # - CPU usage
        # - Storage space
        
        # For now, just log
        self.audit_logger.log("DAEMON_HEALTH_CHECK", "System health check performed")
    
    def _should_run_idle_tasks(self) -> bool:
        """
        Determine if we should run idle tasks.
        
        Returns:
            bool: True if idle tasks should run, False otherwise.
        """
        # Check if enough time has passed since last activity
        idle_interval = self.config.get("autonomy.idle_interval", 300)  # 5 minutes
        
        if self._last_activity_time is None:
            return False
        
        time_since_activity = time.time() - self._last_activity_time
        
        return time_since_activity >= idle_interval
    
    def _should_stop_for_safety(self) -> bool:
        """
        Determine if we should stop for safety reasons.
        
        Returns:
            bool: True if we should stop, False otherwise.
        """
        # Check battery level
        min_battery = self.config.get("battery.min_percentage", 20)
        
        # In a real implementation, we would check the actual battery level
        # For now, we'll assume it's okay
        
        # Check thermal status
        # In a real implementation, we would check the thermal status
        
        return False
    
    def stop(self) -> bool:
        """
        Stop the daemon.
        
        Returns:
            bool: True if daemon stopped successfully, False otherwise.
        """
        if self._status == DaemonStatus.STOPPED:
            logging.warning("Daemon is already stopped")
            return False
        
        if self._status == DaemonStatus.STOPPING:
            logging.warning("Daemon is already stopping")
            return False
        
        self._status = DaemonStatus.STOPPING
        self._stop_event.set()
        
        # Wait for the thread to stop
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=5.0)
        
        if self._status == DaemonStatus.STOPPED:
            self.audit_logger.log("DAEMON_STOP", "Daemon stopped successfully")
            return True
        else:
            self._status = DaemonStatus.ERROR
            logging.error("Failed to stop daemon")
            return False
    
    def pause(self) -> bool:
        """
        Pause the daemon.
        
        Returns:
            bool: True if daemon paused successfully, False otherwise.
        """
        if self._status != DaemonStatus.RUNNING:
            logging.warning("Daemon is not running")
            return False
        
        self._pause_event.set()
        self._status = DaemonStatus.PAUSED
        self.audit_logger.log("DAEMON_PAUSE", "Daemon paused")
        return True
    
    def resume(self) -> bool:
        """
        Resume the daemon.
        
        Returns:
            bool: True if daemon resumed successfully, False otherwise.
        """
        if self._status != DaemonStatus.PAUSED:
            logging.warning("Daemon is not paused")
            return False
        
        self._pause_event.clear()
        self._status = DaemonStatus.RUNNING
        self.audit_logger.log("DAEMON_RESUME", "Daemon resumed")
        return True
    
    def restart(self) -> bool:
        """
        Restart the daemon.
        
        Returns:
            bool: True if daemon restarted successfully, False otherwise.
        """
        if not self.stop():
            return False
        
        time.sleep(0.5)
        return self.start()
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get the current status of the daemon.
        
        Returns:
            Dict[str, Any]: Daemon status.
        """
        uptime = 0.0
        if self._start_time:
            uptime = time.time() - self._start_time
        
        return {
            "status": self._status.value,
            "uptime": uptime,
            "start_time": self._start_time,
            "last_activity_time": self._last_activity_time,
            "thread_alive": self._thread.is_alive() if self._thread else False,
            "idle_manager": self.idle_manager.get_status(),
            "scheduler": self.scheduler.get_status(),
        }
    
    def is_running(self) -> bool:
        """
        Check if the daemon is running.
        
        Returns:
            bool: True if daemon is running, False otherwise.
        """
        return self._status == DaemonStatus.RUNNING
    
    def is_stopped(self) -> bool:
        """
        Check if the daemon is stopped.
        
        Returns:
            bool: True if daemon is stopped, False otherwise.
        """
        return self._status == DaemonStatus.STOPPED
    
    def is_paused(self) -> bool:
        """
        Check if the daemon is paused.
        
        Returns:
            bool: True if daemon is paused, False otherwise.
        """
        return self._status == DaemonStatus.PAUSED
    
    def get_uptime(self) -> float:
        """
        Get the daemon uptime in seconds.
        
        Returns:
            float: Uptime in seconds.
        """
        if self._start_time is None:
            return 0.0
        
        return time.time() - self._start_time
    
    def run_idle_tasks(self) -> Dict[str, Any]:
        """
        Manually run idle tasks.
        
        Returns:
            Dict[str, Any]: Result of idle tasks.
        """
        return self.idle_manager.run()
    
    def schedule_task(
        self,
        task: Callable,
        delay: float = 0.0,
        interval: Optional[float] = None,
        name: Optional[str] = None
    ) -> str:
        """
        Schedule a task for future execution.
        
        Args:
            task: Task to execute (callable).
            delay: Delay before first execution in seconds.
            interval: Optional interval for repeating tasks in seconds.
            name: Optional name for the task.
            
        Returns:
            str: Task ID.
        """
        return self.scheduler.schedule_task(task, delay, interval, name)
    
    def cancel_task(self, task_id: str) -> bool:
        """
        Cancel a scheduled task.
        
        Args:
            task_id: ID of the task to cancel.
            
        Returns:
            bool: True if task was cancelled, False otherwise.
        """
        return self.scheduler.cancel_task(task_id)
    
    def get_scheduled_tasks(self) -> List[Dict[str, Any]]:
        """
        Get all scheduled tasks.
        
        Returns:
            List[Dict[str, Any]]: List of scheduled tasks.
        """
        return self.scheduler.get_scheduled_tasks()
    
    def clear_tasks(self) -> None:
        """Clear all scheduled tasks."""
        self.scheduler.clear_tasks()
