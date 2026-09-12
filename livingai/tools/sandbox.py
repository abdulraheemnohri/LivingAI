"""
LivingAI Tool Sandbox
====================

Provides a safe execution environment for tools with restrictions and monitoring.
"""

import logging
import os
import sys
import time
import tempfile
import shlex
import subprocess
import resource
from typing import Dict, Any, Optional, List, Callable, Tuple
from dataclasses import dataclass, field
from pathlib import Path
from contextlib import contextmanager
import threading

from .permissions import ToolPermissionManager, ToolPermission
from livingai.security.policy import RiskLevel


@dataclass
class SandboxResult:
    output: str
    error: Optional[str] = None
    returncode: int = 0
    execution_time: float = 0.0
    resource_usage: Dict[str, Any] = field(default_factory=dict)
    violated_restrictions: List[str] = field(default_factory=list)
    was_killed: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'output': self.output,
            'error': self.error,
            'returncode': self.returncode,
            'execution_time': self.execution_time,
            'resource_usage': self.resource_usage,
            'violated_restrictions': self.violated_restrictions,
            'was_killed': self.was_killed
        }
    
    @property
    def success(self) -> bool:
        return self.returncode == 0 and not self.was_killed and not self.violated_restrictions


@dataclass
class SandboxConfig:
    max_execution_time: float = 30.0
    max_memory: int = 256 * 1024 * 1024
    max_cpu_time: float = 60.0
    max_output_size: int = 1024 * 1024
    allowed_paths: List[str] = field(default_factory=list)
    blocked_paths: List[str] = field(default_factory=list)
    allowed_commands: List[str] = field(default_factory=list)
    blocked_commands: List[str] = field(default_factory=list)
    network_access: bool = False
    filesystem_write: bool = True
    subprocess_allowed: bool = False