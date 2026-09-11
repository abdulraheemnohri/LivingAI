# LivingAI Termux Platform Integration
import os
import shutil
import subprocess
import logging
from typing import Dict, Any, Tuple, Optional


class TermuxPlatform:
    """Provides Termux environment detection, package checking, and API access."""

    def __init__(self) -> None:
        self.is_termux = self.check_termux()

    def check_termux(self) -> bool:
        prefix = os.environ.get("PREFIX", "")
        return "com.termux" in prefix or shutil.which("termux-info") is not None

    def check_android(self) -> Dict[str, Any]:
        try:
            version = subprocess.check_output(["getprop", "ro.build.version.release"], text=True, stderr=subprocess.DEVNULL).strip()
            sdk = subprocess.check_output(["getprop", "ro.build.version.sdk"], text=True, stderr=subprocess.DEVNULL).strip()
            return {"version": version or "13", "sdk": sdk or "33"}
        except Exception:
            return {"version": "Unknown", "sdk": "Unknown"}

    def check_python(self) -> Tuple[int, int]:
        import sys
        return (sys.version_info.major, sys.version_info.minor)

    def check_storage(self) -> Dict[str, Any]:
        try:
            stat = os.statvfs(os.path.expanduser("~"))
            available_bytes = stat.f_bavail * stat.f_frsize
            available_gb = available_bytes / (1024 ** 3)
            return {"available_bytes": available_bytes, "available_gb": round(available_gb, 2)}
        except Exception:
            return {"available_bytes": 10 * 1024 ** 3, "available_gb": 10.0}

    def get_available_storage(self) -> float:
        return self.check_storage().get("available_gb", 10.0) * 1024  # in MB

    def check_battery(self) -> Dict[str, Any]:
        if shutil.which("termux-battery-status"):
            try:
                import json
                out = subprocess.check_output(["termux-battery-status"], text=True, stderr=subprocess.DEVNULL)
                return json.loads(out)
            except Exception:
                pass
        return {"percentage": 100, "plugged": "PLUGGED_AC", "status": "CHARGING"}

    def check_network(self) -> bool:
        import socket
        try:
            socket.create_connection(("8.8.8.8", 53), timeout=3)
            return True
        except OSError:
            return False

    def check_termux_api(self) -> bool:
        return shutil.which("termux-battery-status") is not None or shutil.which("termux-toast") is not None

    def get_info(self) -> Dict[str, Any]:
        import psutil
        ram_gb = round(psutil.virtual_memory().total / (1024 ** 3), 2) if hasattr(psutil, 'virtual_memory') else 4.0
        avail_ram_gb = round(psutil.virtual_memory().available / (1024 ** 3), 2) if hasattr(psutil, 'virtual_memory') else 2.0
        return {
            "is_termux": self.is_termux,
            "cpu_cores": os.cpu_count() or 4,
            "total_ram_gb": ram_gb,
            "available_ram_gb": avail_ram_gb,
            "available_storage_gb": self.check_storage().get("available_gb", 10.0),
            "battery": self.check_battery(),
            "termux_api": self.check_termux_api(),
        }
