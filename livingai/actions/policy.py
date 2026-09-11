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
    
    Responsibilities:
    - Define allowlists and blocklists
    - Check action permissions
    - Manage permission rules
    - Handle permission overrides
    """
    
    # Default allowlist for safe commands
    DEFAULT_ALLOWLIST = {
        "read": [
            "ls",
            "pwd",
            "cat",
            "head",
            "tail",
            "less",
            "more",
            "grep",
            "find",
            "locate",
            "which",
            "whereis",
            "file",
            "stat",
            "du",
            "df",
            "date",
            "cal",
            "whoami",
            "uname",
            "echo",
            "printf",
            "wc",
            "sort",
            "uniq",
            "cut",
            "awk",
            "sed",
            "tr",
            "nl",
            "od",
            "xxd",
            "base64",
            "md5sum",
            "sha1sum",
            "sha256sum",
            "cksum",
            "sum",
        ],
        "system": [
            "free",
            "top",
            "htop",
            "ps",
            "kill",
            "pkill",
            "killall",
            "nice",
            "renice",
            "ionice",
            "chrt",
        ],
        "network": [
            "ping",
            "ifconfig",
            "ip",
            "netstat",
            "ss",
            "dig",
            "nslookup",
            "host",
            "curl",
            "wget",
            "ftp",
            "sftp",
            "scp",
            "ssh",
        ],
        "development": [
            "python",
            "python3",
            "pip",
            "pip3",
            "git",
            "svn",
            "hg",
            "make",
            "cmake",
            "gcc",
            "g++",
            "clang",
            "clang++",
            "javac",
            "java",
            "node",
            "npm",
            "yarn",
            "ruby",
            "perl",
            "php",
            "go",
            "rustc",
            "cargo",
        ],
        "filesystem": [
            "touch",
            "mkdir",
            "rmdir",
            "cp",
            "mv",
            "ln",
            "chmod",
            "chown",
            "chgrp",
            "umask",
            "dd",
            "genisoimage",
            "mkisofs",
            "mount",
            "umount",
        ],
    }
    
    # Default blocklist for dangerous commands
    DEFAULT_BLOCKLIST = [
        "rm -rf",
        "rm -r",
        "dd ",
        "mkfs",
        "fdisk",
        "parted",
        "format",
        ":(){ :;};",  # Fork bomb
        "> /dev/sda",
        "mv / /dev/null",
        "chmod -R",
        "passwd",
        "su",
        "sudo",
        "visudo",
        "useradd",
        "userdel",
        "usermod",
        "groupadd",
        "groupdel",
        "groupmod",
        "crontab",
        "at",
        "batch",
        "wall",
        "write",
        "mesg",
        "talk",
        "mail",
        "mut",
        "elinks",
        "lynx",
        "w3m",
        "links",
        "nc",
        "netcat",
        "nmap",
        "hping",
        "arpspoof",
        "ettercap",
        "tcpdump",
        "wireshark",
        "tshark",
        "john",
        "hashcat",
        "hydra",
        "metasploit",
        "msfconsole",
        "aircrack",
        "reaver",
        "sqlmap",
        "nikto",
        "burp",
        "nessus",
        "openvas",
    ]
    
    def __init__(
        self,
        config: ConfigManager,
        audit_logger: AuditLogger
    ):
        """
        Initialize the ActionPolicy.
        
        Args:
            config: Configuration manager.
            audit_logger: Audit logger for tracking actions.
        """
        self.config = config
        self.audit_logger = audit_logger
        
        # Initialize allowlists and blocklists
        self._allowlist = self._load_allowlist()
        self._blocklist = self._load_blocklist()
        
        # Permission overrides
        self._overrides: Dict[str, PermissionLevel] = {}
        
        logging.info("ActionPolicy initialized")
    
    def _load_allowlist(self) -> Dict[str, List[str]]:
        """
        Load the action allowlist.
        
        Returns:
            Dict[str, List[str]]: Allowlist organized by category.
        """
        # Start with defaults
        allowlist = self.DEFAULT_ALLOWLIST.copy()
        
        # Load from config if available
        config_allowlist = self.config.get("actions.allowlist", {})
        if config_allowlist:
            for category, commands in config_allowlist.items():
                if category in allowlist:
                    allowlist[category].extend(commands)
                else:
                    allowlist[category] = commands
        
        # Remove duplicates
        for category in allowlist:
            allowlist[category] = list(set(allowlist[category]))
        
        return allowlist
    
    def _load_blocklist(self) -> List[str]:
        """
        Load the action blocklist.
        
        Returns:
            List[str]: List of blocked commands.
        """
        # Start with defaults
        blocklist = self.DEFAULT_BLOCKLIST.copy()
        
        # Load from config if available
        config_blocklist = self.config.get("actions.blocklist", [])
        if config_blocklist:
            blocklist.extend(config_blocklist)
        
        # Remove duplicates
        return list(set(blocklist))
    
    def check_permission(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check if an action is permitted.
        
        Args:
            action: Action to check.
            
        Returns:
            Dict[str, Any]: Permission check result.
        """
        command = action.get("command", "")
        
        # Check overrides first
        if command in self._overrides:
            permission = self._overrides[command]
            return {
                "allowed": permission == PermissionLevel.ALLOWED,
                "level": permission.value,
                "reason": f"Override: {permission.value}",
            }
        
        # Check blocklist
        if self._is_blocked(command):
            return {
                "allowed": False,
                "level": PermissionLevel.DENIED.value,
                "reason": "Command is in blocklist",
            }
        
        # Check allowlist
        if self._is_allowed(command):
            return {
                "allowed": True,
                "level": PermissionLevel.ALLOWED.value,
                "reason": "Command is in allowlist",
            }
        
        # Default to requiring confirmation
        return {
            "allowed": False,
            "level": PermissionLevel.CONFIRM.value,
            "reason": "Command not in allowlist",
        }
    
    def _is_blocked(self, command: str) -> bool:
        """
        Check if a command is in the blocklist.
        
        Args:
            command: Command to check.
            
        Returns:
            bool: True if blocked, False otherwise.
        """
        command_lower = command.lower()
        
        for blocked in self._blocklist:
            if blocked.lower() in command_lower:
                return True
        
        return False
    
    def _is_allowed(self, command: str) -> bool:
        """
        Check if a command is in the allowlist.
        
        Args:
            command: Command to check.
            
        Returns:
            bool: True if allowed, False otherwise.
        """
        # Extract the base command (first word)
        parts = command.split()
        if not parts:
            return False
        
        base_command = parts[0]
        
        # Check all categories in allowlist
        for category, commands in self._allowlist.items():
            if base_command in commands:
                return True
        
        return False
    
    def get_allowlist(self) -> Dict[str, List[str]]:
        """
        Get the current allowlist.
        
        Returns:
            Dict[str, List[str]]: Allowlist organized by category.
        """
        return self._allowlist.copy()
    
    def get_blocklist(self) -> List[str]:
        """
        Get the current blocklist.
        
        Returns:
            List[str]: List of blocked commands.
        """
        return self._blocklist.copy()
    
    def add_to_allowlist(self, command: str, category: str = "custom") -> bool:
        """
        Add a command to the allowlist.
        
        Args:
            command: Command to add.
            category: Category to add the command to.
            
        Returns:
            bool: True if added, False otherwise.
        """
        if category not in self._allowlist:
            self._allowlist[category] = []
        
        if command not in self._allowlist[category]:
            self._allowlist[category].append(command)
            self._save_allowlist()
            return True
        
        return False
    
    def remove_from_allowlist(self, command: str, category: str = "custom") -> bool:
        """
        Remove a command from the allowlist.
        
        Args:
            command: Command to remove.
            category: Category to remove the command from.
            
        Returns:
            bool: True if removed, False otherwise.
        """
        if category in self._allowlist and command in self._allowlist[category]:
            self._allowlist[category].remove(command)
            self._save_allowlist()
            return True
        
        return False
    
    def add_to_blocklist(self, command: str) -> bool:
        """
        Add a command to the blocklist.
        
        Args:
            command: Command to block.
            
        Returns:
            bool: True if added, False otherwise.
        """
        if command not in self._blocklist:
            self._blocklist.append(command)
            self._save_blocklist()
            return True
        
        return False
    
    def remove_from_blocklist(self, command: str) -> bool:
        """
        Remove a command from the blocklist.
        
        Args:
            command: Command to unblock.
            
        Returns:
            bool: True if removed, False otherwise.
        """
        if command in self._blocklist:
            self._blocklist.remove(command)
            self._save_blocklist()
            return True
        
        return False
    
    def _save_allowlist(self) -> None:
        """Save the allowlist to configuration."""
        self.config.set("actions.allowlist", self._allowlist)
    
    def _save_blocklist(self) -> None:
        """Save the blocklist to configuration."""
        self.config.set("actions.blocklist", self._blocklist)
    
    def add_override(self, command: str, level: PermissionLevel) -> None:
        """
        Add a permission override for a command.
        
        Args:
            command: Command to override.
            level: Permission level to set.
        """
        self._overrides[command] = level
    
    def remove_override(self, command: str) -> None:
        """
        Remove a permission override for a command.
        
        Args:
            command: Command to remove override for.
        """
        if command in self._overrides:
            del self._overrides[command]
    
    def get_override(self, command: str) -> Optional[PermissionLevel]:
        """
        Get the permission override for a command.
        
        Args:
            command: Command to check.
            
        Returns:
            Optional[PermissionLevel]: Override level, or None if no override.
        """
        return self._overrides.get(command)
    
    def get_all_overrides(self) -> Dict[str, str]:
        """
        Get all permission overrides.
        
        Returns:
            Dict[str, str]: Dictionary of command to permission level.
        """
        return {cmd: level.value for cmd, level in self._overrides.items()}
    
    def clear_overrides(self) -> None:
        """Clear all permission overrides."""
        self._overrides = {}
    
    def reload(self) -> None:
        """Reload allowlists and blocklists from configuration."""
        self._allowlist = self._load_allowlist()
        self._blocklist = self._load_blocklist()
        logging.info("ActionPolicy reloaded")
    
    def get_permission_stats(self) -> Dict[str, Any]:
        """
        Get statistics about permissions.
        
        Returns:
            Dict[str, Any]: Permission statistics.
        """
        return {
            "allowlist_categories": len(self._allowlist),
            "total_allowed_commands": sum(len(cmds) for cmds in self._allowlist.values()),
            "blocklist_size": len(self._blocklist),
            "overrides_size": len(self._overrides),
        }
