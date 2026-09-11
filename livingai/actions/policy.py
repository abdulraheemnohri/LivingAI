# LivingAI Action Policy
# ========================
# This module manages action permission policies.

import logging
from typing import Dict, Any, Optional, List, Set
from enum import Enum

# Local imports
from ..config import ConfigManager
from ..security.audit import AuditLogger


class PermissionLevel(Enum):
    """Permission levels for actions."""
    ALLOWED = "allowed"       # Action is allowed
    CONFIRM = "confirm"       # Action requires confirmation
    DENIED = "denied"         # Action is denied


class ActionPolicy:
    """
    Manages action permission policies.
    """
    
    DEFAULT_ALLOWLIST = {
        "read": [
            "ls", "pwd", "cat", "head", "tail", "less", "more", "grep",
            "find", "locate", "which", "whereis", "file", "stat", "du",
            "df", "date", "cal", "whoami", "uname", "echo", "printf",
            "wc", "sort", "uniq", "cut", "awk", "sed", "tr", "nl", "od",
            "xxd", "base64", "md5sum", "sha1sum", "sha256sum", "cksum", "sum",
        ],
        "system": ["free", "top", "htop", "ps", "kill", "pkill", "killall", "nice", "renice", "ionice", "chrt"],
        "network": ["ping", "ifconfig", "ip", "netstat", "ss", "dig", "nslookup", "host", "curl", "wget", "ftp", "sftp", "scp", "ssh"],
        "development": ["python", "python3", "pip", "pip3", "git", "svn", "hg", "make", "cmake", "gcc", "g++", "clang", "clang++", "javac", "java", "node", "npm", "yarn", "ruby", "perl", "php", "go", "rustc", "cargo"],
        "filesystem": ["touch", "mkdir", "rmdir", "cp", "mv", "ln", "chmod", "chown", "chgrp", "umask", "dd", "genisoimage", "mkisofs", "mount", "umount"],
    }
    
    DEFAULT_BLOCKLIST = [
        "rm -rf", "rm -r", "dd ", "mkfs", "fdisk", "parted", "format",
        ":(){ :;};", "> /dev/sda", "mv / /dev/null", "chmod -R", "passwd",
        "su", "sudo", "visudo", "useradd", "userdel", "usermod", "groupadd",
        "groupdel", "groupmod", "crontab", "at", "batch", "wall", "write",
        "mesg", "talk", "mail", "mut", "elinks", "lynx", "w3m", "links",
        "nc", "netcat", "nmap", "hping", "arpspoof", "ettercap", "tcpdump",
        "wireshark", "tshark", "john", "hashcat", "hydra", "metasploit",
        "msfconsole", "aircrack", "reaver", "sqlmap", "nikto", "burp",
        "nessus", "openvas",
    ]
    
    def __init__(self, config: ConfigManager, audit_logger: AuditLogger):
        self.config = config
        self.audit_logger = audit_logger
        self._allowlist = self._load_allowlist()
        self._blocklist = self._load_blocklist()
        self._overrides: Dict[str, PermissionLevel] = {}
        logging.info("ActionPolicy initialized")
    
    def _load_allowlist(self) -> Dict[str, List[str]]:
        allowlist = self.DEFAULT_ALLOWLIST.copy()
        config_allowlist = self.config.get("actions.allowlist", {})
        if config_allowlist:
            for category, commands in config_allowlist.items():
                if category in allowlist:
                    allowlist[category].extend(commands)
                else:
                    allowlist[category] = commands
        for category in allowlist:
            allowlist[category] = list(set(allowlist[category]))
        return allowlist
    
    def _load_blocklist(self) -> List[str]:
        blocklist = self.DEFAULT_BLOCKLIST.copy()
        config_blocklist = self.config.get("actions.blocklist", [])
        if config_blocklist:
            blocklist.extend(config_blocklist)
        return list(set(blocklist))

    def get_risk_level(self, command: str) -> str:
        if self._is_blocked(command):
            return "CRITICAL"
        elif self._is_allowed(command):
            return "LOW"
        return "MEDIUM"
    
    def check_permission(self, action: Dict[str, Any]) -> Dict[str, Any]:
        command = action.get("command", "")
        if command in self._overrides:
            permission = self._overrides[command]
            return {"allowed": permission == PermissionLevel.ALLOWED, "level": permission.value, "reason": f"Override: {permission.value}"}
        if self._is_blocked(command):
            return {"allowed": False, "level": PermissionLevel.DENIED.value, "reason": "Command is in blocklist"}
        if self._is_allowed(command):
            return {"allowed": True, "level": PermissionLevel.ALLOWED.value, "reason": "Command is in allowlist"}
        return {"allowed": False, "level": PermissionLevel.CONFIRM.value, "reason": "Command not in allowlist"}
    
    def _is_blocked(self, command: str) -> bool:
        command_lower = command.lower()
        for blocked in self._blocklist:
            if blocked.lower() in command_lower:
                return True
        return False
    
    def _is_allowed(self, command: str) -> bool:
        parts = command.split()
        if not parts:
            return False
        base_command = parts[0]
        for category, commands in self._allowlist.items():
            if base_command in commands:
                return True
        return False

    def get_allowlist(self) -> Dict[str, List[str]]:
        return self._allowlist.copy()

    def get_blocklist(self) -> List[str]:
        return self._blocklist.copy()

    def add_to_allowlist(self, command: str, category: str = "custom") -> bool:
        if category not in self._allowlist:
            self._allowlist[category] = []
        if command not in self._allowlist[category]:
            self._allowlist[category].append(command)
            self._save_allowlist()
            return True
        return False

    def remove_from_allowlist(self, command: str, category: str = "custom") -> bool:
        if category in self._allowlist and command in self._allowlist[category]:
            self._allowlist[category].remove(command)
            self._save_allowlist()
            return True
        return False

    def add_to_blocklist(self, command: str) -> bool:
        if command not in self._blocklist:
            self._blocklist.append(command)
            self._save_blocklist()
            return True
        return False

    def remove_from_blocklist(self, command: str) -> bool:
        if command in self._blocklist:
            self._blocklist.remove(command)
            self._save_blocklist()
            return True
        return False

    def _save_allowlist(self) -> None:
        self.config.set("actions.allowlist", self._allowlist)

    def _save_blocklist(self) -> None:
        self.config.set("actions.blocklist", self._blocklist)

    def add_override(self, command: str, level: PermissionLevel) -> None:
        self._overrides[command] = level

    def remove_override(self, command: str) -> None:
        if command in self._overrides:
            del self._overrides[command]

    def get_override(self, command: str) -> Optional[PermissionLevel]:
        return self._overrides.get(command)

    def get_all_overrides(self) -> Dict[str, str]:
        return {cmd: level.value for cmd, level in self._overrides.items()}

    def clear_overrides(self) -> None:
        self._overrides = {}

    def reload(self) -> None:
        self._allowlist = self._load_allowlist()
        self._blocklist = self._load_blocklist()
        logging.info("ActionPolicy reloaded")

    def get_permission_stats(self) -> Dict[str, Any]:
        return {
            "allowlist_categories": len(self._allowlist),
            "total_allowed_commands": sum(len(cmds) for cmds in self._allowlist.values()),
            "blocklist_size": len(self._blocklist),
            "overrides_size": len(self._overrides),
        }
