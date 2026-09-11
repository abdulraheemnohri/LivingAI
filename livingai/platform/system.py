# LivingAI System Information Utilities
import os
import sys
import platform
from typing import Dict, Any


class SystemInfo:
    """Provides platform details, architecture, RAM, and hardware diagnostic profile."""

    @staticmethod
    def get_system_summary() -> Dict[str, Any]:
        return {
            "os": sys.platform,
            "architecture": platform.machine(),
            "python_version": platform.python_version(),
            "cpu_count": os.cpu_count() or 1,
        }

    @staticmethod
    def get_hardware_profile(available_ram_gb: float) -> str:
        if available_ram_gb < 3.0:
            return "LOW_MEMORY"
        elif available_ram_gb < 6.0:
            return "BALANCED"
        else:
            return "PERFORMANCE"
