# LivingAI Permission Manager
import logging
from typing import Dict, Any, List, Optional


class PermissionManager:
    """
    Manages action permission levels and risk policies across system and Android APIs.

    Permissions tracked:
    - STORAGE: Local file access
    - CAMERA: Termux camera photo access
    - LOCATION: GPS / network location access
    - MICROPHONE: Audio recording / STT
    - NOTIFICATION: Android toast and status notifications
    - CLIPBOARD: System clipboard read / write
    - SHELL_EXECUTION: Terminal command execution
    """

    ANDROID_PERMISSIONS = {
        "storage": "android.permission.READ_EXTERNAL_STORAGE",
        "camera": "android.permission.CAMERA",
        "location": "android.permission.ACCESS_FINE_LOCATION",
        "microphone": "android.permission.RECORD_AUDIO",
        "notification": "android.permission.POST_NOTIFICATIONS",
        "clipboard": "android.permission.READ_CLIPBOARD",
    }

    def __init__(self, config: Any = None):
        self.config = config
        self._granted_permissions: Dict[str, bool] = {
            "storage": True,
            "notification": True,
            "clipboard": True,
            "camera": False,
            "location": False,
            "microphone": False,
            "shell_execution": True,
        }

    def check_permission(self, command: str, risk_level: str) -> bool:
        risk_level = risk_level.upper()
        if risk_level == "LOW":
            return True
        elif risk_level in ("MEDIUM", "HIGH"):
            return True
        elif risk_level == "CRITICAL":
            return False
        return False

    def is_android_permission_granted(self, perm_name: str) -> bool:
        return self._granted_permissions.get(perm_name.lower(), False)

    def grant_permission(self, perm_name: str) -> None:
        self._granted_permissions[perm_name.lower()] = True
        logging.info(f"Granted permission: {perm_name}")

    def revoke_permission(self, perm_name: str) -> None:
        self._granted_permissions[perm_name.lower()] = False
        logging.info(f"Revoked permission: {perm_name}")

    def get_permission_summary(self) -> Dict[str, bool]:
        return self._granted_permissions.copy()
