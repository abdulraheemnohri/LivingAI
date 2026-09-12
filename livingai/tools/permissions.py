"""
LivingAI Tool Permission Manager
===============================

Manages permissions for individual tools and tool categories.
"""

import logging
from typing import Dict, Any, Optional, List, Set
from enum import Enum
from dataclasses import dataclass, field

from livingai.security.policy import RiskLevel, PermissionProfile


class ToolPermission(Enum):
    """Permission levels for tools."""
    DENIED = "denied"
    READ_ONLY = "read_only"
    RESTRICTED = "restricted"
    FULL = "full"


@dataclass
class ToolPermissionConfig:
    name: str
    permission: ToolPermission = ToolPermission.RESTRICTED
    allowed_methods: Set[str] = field(default_factory=set)
    blocked_methods: Set[str] = field(default_factory=set)
    allowed_args: Set[str] = field(default_factory=set)
    blocked_args: Set[str] = field(default_factory=set)
    risk: RiskLevel = RiskLevel.MEDIUM
    requires_confirmation: bool = True
    max_retries: int = 3
    timeout: int = 30
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'permission': self.permission.value,
            'allowed_methods': list(self.allowed_methods),
            'blocked_methods': list(self.blocked_methods),
            'allowed_args': list(self.allowed_args),
            'blocked_args': list(self.blocked_args),
            'risk': self.risk.value,
            'requires_confirmation': self.requires_confirmation,
            'max_retries': self.max_retries,
            'timeout': self.timeout
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ToolPermissionConfig':
        return cls(
            name=data.get('name', ''),
            permission=ToolPermission(data.get('permission', 'restricted')),
            allowed_methods=set(data.get('allowed_methods', [])),
            blocked_methods=set(data.get('blocked_methods', [])),
            allowed_args=set(data.get('allowed_args', [])),
            blocked_args=set(data.get('blocked_args', [])),
            risk=RiskLevel(data.get('risk', 'medium')),
            requires_confirmation=data.get('requires_confirmation', True),
            max_retries=data.get('max_retries', 3),
            timeout=data.get('timeout', 30)
        )


DEFAULT_TOOL_PERMISSIONS = {
    'filesystem': {
        'permission': ToolPermission.RESTRICTED,
        'allowed_methods': {'read', 'list', 'exists', 'stat', 'is_file', 'is_dir'},
        'blocked_methods': {'delete', 'remove', 'rm', 'rmdir', 'chmod', 'chown'},
        'risk': RiskLevel.MEDIUM,
        'requires_confirmation': True
    },
    'filesystem.read': {
        'permission': ToolPermission.FULL,
        'risk': RiskLevel.LOW,
        'requires_confirmation': False
    },
    'filesystem.write': {
        'permission': ToolPermission.RESTRICTED,
        'allowed_methods': {'write', 'save', 'create'},
        'blocked_methods': {'overwrite'},
        'risk': RiskLevel.MEDIUM,
        'requires_confirmation': True
    },
    'filesystem.delete': {
        'permission': ToolPermission.RESTRICTED,
        'allowed_methods': {'delete', 'remove', 'rm'},
        'blocked_methods': {'rm -rf', 'rm -r'},
        'blocked_args': {'path': ['/', '/home', '/etc', '/usr', '/var', '/bin', '/sbin']},
        'risk': RiskLevel.HIGH,
        'requires_confirmation': True
    },
    'file_inspector': {
        'permission': ToolPermission.FULL,
        'risk': RiskLevel.LOW,
        'requires_confirmation': False
    },
    'terminal': {
        'permission': ToolPermission.DENIED,
        'risk': RiskLevel.CRITICAL,
        'requires_confirmation': True
    },
    'terminal.safe': {
        'permission': ToolPermission.RESTRICTED,
        'allowed_methods': {'ls', 'pwd', 'cat', 'grep', 'find', 'head', 'tail'},
        'blocked_methods': {'rm', 'mv', 'cp', 'dd', 'chmod', 'su', 'sudo'},
        'risk': RiskLevel.MEDIUM,
        'requires_confirmation': False
    },
    'sqlite': {
        'permission': ToolPermission.RESTRICTED,
        'allowed_methods': {'read', 'query', 'select'},
        'blocked_methods': {'write', 'delete', 'drop', 'execute'},
        'risk': RiskLevel.MEDIUM,
        'requires_confirmation': True
    },
    'sqlite.read': {
        'permission': ToolPermission.FULL,
        'risk': RiskLevel.LOW,
        'requires_confirmation': False
    },
    'memory': {
        'permission': ToolPermission.FULL,
        'risk': RiskLevel.LOW,
        'requires_confirmation': False
    },
    'skills': {
        'permission': ToolPermission.FULL,
        'risk': RiskLevel.LOW,
        'requires_confirmation': False
    },
    'goals': {
        'permission': ToolPermission.FULL,
        'risk': RiskLevel.LOW,
        'requires_confirmation': False
    },
    'tasks': {
        'permission': ToolPermission.FULL,
        'risk': RiskLevel.LOW,
        'requires_confirmation': False
    },
    'calculator': {
        'permission': ToolPermission.FULL,
        'risk': RiskLevel.LOW,
        'requires_confirmation': False
    },
    'datetime': {
        'permission': ToolPermission.FULL,
        'risk': RiskLevel.LOW,
        'requires_confirmation': False
    },
    'text_processor': {
        'permission': ToolPermission.FULL,
        'risk': RiskLevel.LOW,
        'requires_confirmation': False
    },
    'archive_manager': {
        'permission': ToolPermission.RESTRICTED,
        'allowed_methods': {'create', 'extract', 'list'},
        'blocked_methods': {'delete_archive'},
        'risk': RiskLevel.MEDIUM,
        'requires_confirmation': True
    },
    'workspace': {
        'permission': ToolPermission.FULL,
        'risk': RiskLevel.LOW,
        'requires_confirmation': False
    },
    'backup': {
        'permission': ToolPermission.RESTRICTED,
        'allowed_methods': {'create', 'list', 'restore'},
        'blocked_methods': {'delete'},
        'risk': RiskLevel.MEDIUM,
        'requires_confirmation': True
    },
    'logs': {
        'permission': ToolPermission.READ_ONLY,
        'risk': RiskLevel.LOW,
        'requires_confirmation': False
    }
}


class ToolPermissionManager:
    def __init__(self, config: Any = None):
        self.config = config
        self._permissions = {}
        self._profile_overrides = {}
        self.logger = logging.getLogger(__name__)
        self._load_default_permissions()
    
    def _load_default_permissions(self):
        for tool_name, settings in DEFAULT_TOOL_PERMISSIONS.items():
            perm_config = ToolPermissionConfig(name=tool_name, **settings)
            self._permissions[tool_name] = perm_config
    
    def get_permission(self, tool_name: str) -> ToolPermissionConfig:
        if tool_name not in self._permissions:
            self._permissions[tool_name] = ToolPermissionConfig(
                name=tool_name,
                permission=ToolPermission.RESTRICTED,
                risk=RiskLevel.MEDIUM,
                requires_confirmation=True
            )
        return self._permissions[tool_name]
    
    def check_tool_access(self, tool_name: str, method: Optional[str] = None, args: Optional[Dict[str, Any]] = None, profile: Optional[PermissionProfile] = None) -> Dict[str, Any]:
        perm = self.get_permission(tool_name)
        if perm.permission == ToolPermission.DENIED:
            return {'allowed': False, 'permission': perm.permission.value, 'risk': perm.risk.value, 'requires_confirmation': False, 'reason': f"Tool '{tool_name}' is denied"}
        if method:
            if method in perm.blocked_methods:
                return {'allowed': False, 'permission': perm.permission.value, 'risk': perm.risk.value, 'requires_confirmation': False, 'reason': f"Method '{method}' is blocked for tool '{tool_name}'", 'blocked_method': method}
            if perm.allowed_methods and method not in perm.allowed_methods:
                return {'allowed': False, 'permission': perm.permission.value, 'risk': perm.risk.value, 'requires_confirmation': False, 'reason': f"Method '{method}' is not allowed for tool '{tool_name}'", 'blocked_method': method}
        if args:
            for arg_name, arg_value in args.items():
                if arg_name in perm.blocked_args:
                    return {'allowed': False, 'permission': perm.permission.value, 'risk': perm.risk.value, 'requires_confirmation': False, 'reason': f"Argument '{arg_name}' is blocked for tool '{tool_name}'", 'blocked_arg': arg_name}
                if arg_name in perm.blocked_args and isinstance(perm.blocked_args[arg_name], list):
                    if arg_value in perm.blocked_args[arg_name]:
                        return {'allowed': False, 'permission': perm.permission.value, 'risk': perm.risk.value, 'requires_confirmation': False, 'reason': f"Argument '{arg_name}={arg_value}' is blocked for tool '{tool_name}'", 'blocked_arg': arg_name}
        return {'allowed': True, 'permission': perm.permission.value, 'risk': perm.risk.value, 'requires_confirmation': perm.requires_confirmation, 'reason': 'Access allowed'}
    
    def set_permission(self, tool_name: str, permission: ToolPermission, allowed_methods: List[str] = None, blocked_methods: List[str] = None, allowed_args: List[str] = None, blocked_args: List[str] = None, risk: RiskLevel = None, requires_confirmation: bool = None) -> ToolPermissionConfig:
        if tool_name not in self._permissions:
            self._permissions[tool_name] = ToolPermissionConfig(name=tool_name)
        perm = self._permissions[tool_name]
        if permission is not None:
            perm.permission = permission
        if allowed_methods is not None:
            perm.allowed_methods = set(allowed_methods)
        if blocked_methods is not None:
            perm.blocked_methods = set(blocked_methods)
        if allowed_args is not None:
            perm.allowed_args = set(allowed_args)
        if blocked_args is not None:
            perm.blocked_args = blocked_args
        if risk is not None:
            perm.risk = risk
        if requires_confirmation is not None:
            perm.requires_confirmation = requires_confirmation
        self.logger.info(f"Updated permission for tool: {tool_name}")
        return perm
    
    def set_profile_override(self, profile: PermissionProfile, tool_name: str, permission: ToolPermission, allowed_methods: List[str] = None, blocked_methods: List[str] = None):
        if profile.value not in self._profile_overrides:
            self._profile_overrides[profile.value] = {}
        if tool_name not in self._profile_overrides[profile.value]:
            self._profile_overrides[profile.value][tool_name] = ToolPermissionConfig(name=tool_name)
        perm = self._profile_overrides[profile.value][tool_name]
        perm.permission = permission
        if allowed_methods is not None:
            perm.allowed_methods = set(allowed_methods)
        if blocked_methods is not None:
            perm.blocked_methods = set(blocked_methods)
        self.logger.info(f"Set profile override: {profile.value} -> {tool_name}")
    
    def get_permission_for_profile(self, tool_name: str, profile: PermissionProfile) -> ToolPermissionConfig:
        if profile.value in self._profile_overrides:
            if tool_name in self._profile_overrides[profile.value]:
                return self._profile_overrides[profile.value][tool_name]
        return self.get_permission(tool_name)
    
    def list_all_permissions(self) -> Dict[str, Dict[str, Any]]:
        return {name: perm.to_dict() for name, perm in self._permissions.items()}
    
    def list_tools_by_risk(self, risk: RiskLevel) -> List[str]:
        return [name for name, perm in self._permissions.items() if perm.risk == risk]
    
    def list_allowed_tools(self, profile: PermissionProfile = None) -> List[str]:
        allowed = []
        for name, perm in self._permissions.items():
            if profile:
                perm = self.get_permission_for_profile(name, profile)
            if perm.permission != ToolPermission.DENIED:
                allowed.append(name)
        return allowed
    
    def list_blocked_tools(self) -> List[str]:
        return [name for name, perm in self._permissions.items() if perm.permission == ToolPermission.DENIED]
    
    def reset_to_defaults(self):
        self._permissions.clear()
        self._profile_overrides.clear()
        self._load_default_permissions()
        self.logger.info("Tool permissions reset to defaults")
