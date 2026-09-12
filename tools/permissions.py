"""
Tool Permissions Module

Manages permissions for AI tools in the LivingAI system.
This module provides fine-grained permission control for tool execution.

Author: Abdulraheem Nohari
"""

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set
from enum import Enum

logger = logging.getLogger(__name__)


class PermissionLevel(Enum):
    """Permission levels for tools"""
    DENIED = "denied"
    READ_ONLY = "read_only"
    READ_WRITE = "read_write"
    FULL_ACCESS = "full_access"


class PermissionType(Enum):
    """Types of permissions"""
    FILE_SYSTEM = "file_system"
    NETWORK = "network"
    DATABASE = "database"
    SYSTEM = "system"
    USER_DATA = "user_data"
    CAMERA = "camera"
    MICROPHONE = "microphone"
    LOCATION = "location"
    STORAGE = "storage"
    CONTACTS = "contacts"
    CALENDAR = "calendar"
    SENSORS = "sensors"
    NOTIFICATIONS = "notifications"
    CUSTOM = "custom"


@dataclass
class Permission:
    """Represents a permission for a tool"""
    name: str
    permission_type: PermissionType
    level: PermissionLevel = PermissionLevel.FULL_ACCESS
    description: str = ""
    is_granted: bool = False
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'name': self.name,
            'type': self.permission_type.value,
            'level': self.level.value,
            'description': self.description,
            'is_granted': self.is_granted,
        }


@dataclass
class ToolPermission:
    """Permissions for a specific tool"""
    tool_name: str
    permissions: Dict[str, Permission] = field(default_factory=dict)
    default_level: PermissionLevel = PermissionLevel.DENIED
    
    def add_permission(self, 
                       name: str, 
                       permission_type: PermissionType,
                       level: PermissionLevel = PermissionLevel.FULL_ACCESS,
                       description: str = "") -> 'ToolPermission':
        """
        Add a permission to this tool.
        
        Args:
            name: Name of the permission
            permission_type: Type of permission
            level: Permission level
            description: Description of the permission
            
        Returns:
            Self for chaining
        """
        self.permissions[name] = Permission(
            name=name,
            permission_type=permission_type,
            level=level,
            description=description,
        )
        return self
    
    def check_permission(self, permission_name: str) -> bool:
        """
        Check if a permission is granted.
        
        Args:
            permission_name: Name of the permission to check
            
        Returns:
            True if permission is granted
        """
        perm = self.permissions.get(permission_name)
        if perm is None:
            return False
        return perm.is_granted and perm.level != PermissionLevel.DENIED
    
    def check_level(self, permission_name: str, required_level: PermissionLevel) -> bool:
        """
        Check if a permission has at least the required level.
        
        Args:
            permission_name: Name of the permission
            required_level: Required permission level
            
        Returns:
            True if permission level is sufficient
        """
        perm = self.permissions.get(permission_name)
        if perm is None:
            return False
        
        level_order = {
            PermissionLevel.DENIED: 0,
            PermissionLevel.READ_ONLY: 1,
            PermissionLevel.READ_WRITE: 2,
            PermissionLevel.FULL_ACCESS: 3,
        }
        
        return perm.is_granted and level_order[perm.level] >= level_order[required_level]
    
    def grant_permission(self, permission_name: str) -> bool:
        """
        Grant a permission.
        
        Args:
            permission_name: Name of the permission to grant
            
        Returns:
            True if permission was granted
        """
        if permission_name in self.permissions:
            self.permissions[permission_name].is_granted = True
            return True
        return False
    
    def revoke_permission(self, permission_name: str) -> bool:
        """
        Revoke a permission.
        
        Args:
            permission_name: Name of the permission to revoke
            
        Returns:
            True if permission was revoked
        """
        if permission_name in self.permissions:
            self.permissions[permission_name].is_granted = False
            return True
        return False
    
    def get_permission(self, permission_name: str) -> Optional[Permission]:
        """
        Get a permission by name.
        
        Args:
            permission_name: Name of the permission
            
        Returns:
            Permission object or None
        """
        return self.permissions.get(permission_name)
    
    def get_all_permissions(self) -> List[Permission]:
        """
        Get all permissions for this tool.
        
        Returns:
            List of all Permission objects
        """
        return list(self.permissions.values())


class ToolPermissions:
    """
    Manager for tool permissions.
    
    This class manages permissions for all tools in the system,
    providing centralized control over what tools can do.
    """
    
    def __init__(self):
        """Initialize the permissions manager"""
        self._tool_permissions: Dict[str, ToolPermission] = {}
        self._global_permissions: Dict[str, bool] = {}
        self._default_tool_permission = PermissionLevel.DENIED
    
    def register_tool(self, tool_name: str) -> ToolPermission:
        """
        Register permissions for a tool.
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            ToolPermission object for the tool
        """
        if tool_name not in self._tool_permissions:
            self._tool_permissions[tool_name] = ToolPermission(
                tool_name=tool_name,
                default_level=self._default_tool_permission,
            )
        return self._tool_permissions[tool_name]
    
    def check_permission(self, tool_name: str, permission_name: str) -> bool:
        """
        Check if a tool has a specific permission.
        
        Args:
            tool_name: Name of the tool
            permission_name: Name of the permission
            
        Returns:
            True if permission is granted
        """
        # Check global permissions first
        if permission_name in self._global_permissions:
            return self._global_permissions[permission_name]
        
        # Check tool-specific permissions
        tool_perm = self._tool_permissions.get(tool_name)
        if tool_perm:
            return tool_perm.check_permission(permission_name)
        
        # Check global permission by type
        return self._check_global_permission_type(permission_name)
    
    def _check_global_permission_type(self, permission_name: str) -> bool:
        """
        Check global permission by type.
        
        Args:
            permission_name: Name of the permission
            
        Returns:
            True if permission type is globally allowed
        """
        # Map permission names to types
        permission_type_map = {
            'read_file': PermissionType.FILE_SYSTEM,
            'write_file': PermissionType.FILE_SYSTEM,
            'delete_file': PermissionType.FILE_SYSTEM,
            'network_access': PermissionType.NETWORK,
            'database_access': PermissionType.DATABASE,
            'camera_access': PermissionType.CAMERA,
            'microphone_access': PermissionType.MICROPHONE,
            'location_access': PermissionType.LOCATION,
            'storage_access': PermissionType.STORAGE,
        }
        
        perm_type = permission_type_map.get(permission_name)
        if perm_type:
            return self._global_permissions.get(perm_type.value, False)
        
        return False
    
    def set_global_permission(self, permission_name: str, is_granted: bool) -> None:
        """
        Set a global permission.
        
        Args:
            permission_name: Name of the permission
            is_granted: Whether to grant the permission
        """
        self._global_permissions[permission_name] = is_granted
        logger.info(f"Set global permission '{permission_name}' to {is_granted}")
    
    def set_tool_permission(self, 
                           tool_name: str, 
                           permission_name: str, 
                           is_granted: bool) -> bool:
        """
        Set a permission for a specific tool.
        
        Args:
            tool_name: Name of the tool
            permission_name: Name of the permission
            is_granted: Whether to grant the permission
            
        Returns:
            True if permission was set
        """
        tool_perm = self._tool_permissions.get(tool_name)
        if tool_perm:
            if is_granted:
                return tool_perm.grant_permission(permission_name)
            else:
                return tool_perm.revoke_permission(permission_name)
        return False
    
    def get_tool_permissions(self, tool_name: str) -> Optional[ToolPermission]:
        """
        Get permissions for a tool.
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            ToolPermission object or None
        """
        return self._tool_permissions.get(tool_name)
    
    def get_all_tool_names(self) -> List[str]:
        """
        Get all registered tool names.
        
        Returns:
            List of tool names
        """
        return list(self._tool_permissions.keys())
    
    def grant_all_tool_permissions(self, tool_name: str) -> None:
        """
        Grant all permissions to a tool.
        
        Args:
            tool_name: Name of the tool
        """
        tool_perm = self._tool_permissions.get(tool_name)
        if tool_perm:
            for perm_name in tool_perm.permissions:
                tool_perm.grant_permission(perm_name)
            logger.info(f"Granted all permissions to tool '{tool_name}'")
    
    def revoke_all_tool_permissions(self, tool_name: str) -> None:
        """
        Revoke all permissions from a tool.
        
        Args:
            tool_name: Name of the tool
        """
        tool_perm = self._tool_permissions.get(tool_name)
        if tool_perm:
            for perm_name in tool_perm.permissions:
                tool_perm.revoke_permission(perm_name)
            logger.info(f"Revoked all permissions from tool '{tool_name}'")
    
    def set_default_tool_permission(self, level: PermissionLevel) -> None:
        """
        Set the default permission level for new tools.
        
        Args:
            level: Default permission level
        """
        self._default_tool_permission = level
        logger.info(f"Set default tool permission to {level.value}")
    
    def clear_all_permissions(self) -> None:
        """Clear all permissions"""
        self._tool_permissions.clear()
        self._global_permissions.clear()
        logger.info("Cleared all permissions")
    
    def check_tool_has_permissions(self, 
                                   tool_name: str, 
                                   required_permissions: List[str]) -> bool:
        """
        Check if a tool has all required permissions.
        
        Args:
            tool_name: Name of the tool
            required_permissions: List of required permission names
            
        Returns:
            True if tool has all required permissions
        """
        for perm_name in required_permissions:
            if not self.check_permission(tool_name, perm_name):
                return False
        return True
    
    def get_permission_report(self) -> Dict[str, Any]:
        """
        Get a report of all permissions.
        
        Returns:
            Dictionary with permission report
        """
        report = {
            'tools': {},
            'global_permissions': self._global_permissions.copy(),
            'default_tool_permission': self._default_tool_permission.value,
        }
        
        for tool_name, tool_perm in self._tool_permissions.items():
            report['tools'][tool_name] = {
                'permissions': {name: perm.to_dict() 
                              for name, perm in tool_perm.permissions.items()},
                'default_level': tool_perm.default_level.value,
            }
        
        return report


# Global permissions manager instance
permissions_manager = ToolPermissions()


def get_permissions() -> ToolPermissions:
    """Get the global permissions manager instance"""
    return permissions_manager
