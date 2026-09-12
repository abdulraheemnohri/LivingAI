"""
LivingAI Security Policy Manager
===============================

Manages security policies, risk classification, and permission profiles.
"""

import logging
from typing import Dict, Any, Optional, List, Set
from enum import Enum
from dataclasses import dataclass, field


class RiskLevel(Enum):
    """Security risk levels for actions."""
    LOW = "low"           # Safe, read-only operations
    MEDIUM = "medium"     # File modifications, requires confirmation
    HIGH = "high"         # System changes, requires confirmation
    CRITICAL = "critical" # Dangerous, blocked by default


class PermissionProfile(Enum):
    """Predefined permission profiles."""
    READ_ONLY = "read_only"           # Only read operations
    SAFE = "safe"                     # Safe productivity operations
    PRODUCTIVITY = "productivity"     # Productivity tools
    FILE_MANAGER = "file_manager"     # File management operations
    DEVELOPER = "developer"           # Developer operations
    AUTONOMOUS = "autonomous"         # Full autonomy (dangerous)
    CUSTOM = "custom"                 # Custom configuration


@dataclass
class SecurityPolicy:
    """
    Represents a security policy for the system.
    
    Attributes:
        profile: Permission profile
        allowed_tools: Set of allowed tool names
        blocked_tools: Set of blocked tool names
        max_risk: Maximum allowed risk level
        require_confirmation: Whether to require user confirmation
        allowed_actions: Set of allowed action types
        blocked_actions: Set of blocked action types
        max_retries: Maximum retry attempts
        max_runtime: Maximum runtime in seconds
        network_access: Whether network access is allowed
        filesystem_access: Whether filesystem access is allowed
        terminal_access: Whether terminal access is allowed
    """
    profile: PermissionProfile = PermissionProfile.SAFE
    allowed_tools: Set[str] = field(default_factory=set)
    blocked_tools: Set[str] = field(default_factory=set)
    max_risk: RiskLevel = RiskLevel.MEDIUM
    require_confirmation: bool = True
    allowed_actions: Set[str] = field(default_factory=set)
    blocked_actions: Set[str] = field(default_factory=set)
    max_retries: int = 3
    max_runtime: int = 3600  # 1 hour
    network_access: bool = False
    filesystem_access: bool = True
    terminal_access: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert policy to dictionary."""
        return {
            'profile': self.profile.value,
            'allowed_tools': list(self.allowed_tools),
            'blocked_tools': list(self.blocked_tools),
            'max_risk': self.max_risk.value,
            'require_confirmation': self.require_confirmation,
            'allowed_actions': list(self.allowed_actions),
            'blocked_actions': list(self.blocked_actions),
            'max_retries': self.max_retries,
            'max_runtime': self.max_runtime,
            'network_access': self.network_access,
            'filesystem_access': self.filesystem_access,
            'terminal_access': self.terminal_access
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SecurityPolicy':
        """Create policy from dictionary."""
        policy = cls()
        
        if 'profile' in data:
            policy.profile = PermissionProfile(data['profile'])
        if 'allowed_tools' in data:
            policy.allowed_tools = set(data['allowed_tools'])
        if 'blocked_tools' in data:
            policy.blocked_tools = set(data['blocked_tools'])
        if 'max_risk' in data:
            policy.max_risk = RiskLevel(data['max_risk'])
        if 'require_confirmation' in data:
            policy.require_confirmation = bool(data['require_confirmation'])
        if 'allowed_actions' in data:
            policy.allowed_actions = set(data['allowed_actions'])
        if 'blocked_actions' in data:
            policy.blocked_actions = set(data['blocked_actions'])
        if 'max_retries' in data:
            policy.max_retries = int(data['max_retries'])
        if 'max_runtime' in data:
            policy.max_runtime = int(data['max_runtime'])
        if 'network_access' in data:
            policy.network_access = bool(data['network_access'])
        if 'filesystem_access' in data:
            policy.filesystem_access = bool(data['filesystem_access'])
        if 'terminal_access' in data:
            policy.terminal_access = bool(data['terminal_access'])
        
        return policy


# Predefined permission profiles
PREDEFINED_PROFILES: Dict[PermissionProfile, Dict[str, Any]] = {
    PermissionProfile.READ_ONLY: {
        'max_risk': RiskLevel.LOW,
        'require_confirmation': False,
        'allowed_tools': {
            'filesystem.read',
            'file_inspector',
            'memory',
            'calculator',
            'datetime',
            'text_processor'
        },
        'blocked_tools': {
            'filesystem.write',
            'filesystem.delete',
            'terminal',
            'sqlite.write'
        },
        'allowed_actions': {'read', 'list', 'search', 'calculate'},
        'blocked_actions': {'write', 'delete', 'execute', 'modify'},
        'network_access': False,
        'filesystem_access': True,
        'terminal_access': False
    },
    PermissionProfile.SAFE: {
        'max_risk': RiskLevel.MEDIUM,
        'require_confirmation': True,
        'allowed_tools': {
            'filesystem.read',
            'filesystem.write',
            'file_inspector',
            'memory',
            'skills',
            'goals',
            'tasks',
            'calculator',
            'datetime',
            'text_processor',
            'archive_manager',
            'workspace'
        },
        'blocked_tools': {
            'terminal',
            'sqlite.write'
        },
        'allowed_actions': {'read', 'list', 'search', 'calculate', 'create', 'move', 'copy'},
        'blocked_actions': {'delete', 'execute', 'remove', 'rm', 'dd'},
        'network_access': False,
        'filesystem_access': True,
        'terminal_access': False
    },
    PermissionProfile.PRODUCTIVITY: {
        'max_risk': RiskLevel.HIGH,
        'require_confirmation': True,
        'allowed_tools': {
            'filesystem.read',
            'filesystem.write',
            'filesystem.delete',
            'file_inspector',
            'memory',
            'skills',
            'goals',
            'tasks',
            'calculator',
            'datetime',
            'text_processor',
            'archive_manager',
            'workspace',
            'backup',
            'logs'
        },
        'blocked_tools': {'terminal'},
        'allowed_actions': {'read', 'list', 'search', 'calculate', 'create', 'move', 'copy', 'delete'},
        'blocked_actions': {'execute', 'chmod', 'chown', 'su'},
        'network_access': False,
        'filesystem_access': True,
        'terminal_access': False
    },
    PermissionProfile.FILE_MANAGER: {
        'max_risk': RiskLevel.HIGH,
        'require_confirmation': False,
        'allowed_tools': {
            'filesystem.read',
            'filesystem.write',
            'filesystem.delete',
            'file_inspector',
            'memory',
            'calculator',
            'datetime',
            'text_processor',
            'archive_manager',
            'workspace',
            'backup'
        },
        'blocked_tools': {'terminal', 'sqlite.write'},
        'allowed_actions': {'read', 'list', 'search', 'calculate', 'create', 'move', 'copy', 'delete'},
        'blocked_actions': {'execute', 'chmod', 'chown'},
        'network_access': False,
        'filesystem_access': True,
        'terminal_access': False
    },
    PermissionProfile.DEVELOPER: {
        'max_risk': RiskLevel.HIGH,
        'require_confirmation': False,
        'allowed_tools': set(),  # All tools allowed by default
        'blocked_tools': {'terminal.su', 'terminal.dd'},
        'allowed_actions': set(),  # All actions allowed by default
        'blocked_actions': {'su', 'dd', 'rm -rf', 'format'},
        'network_access': True,
        'filesystem_access': True,
        'terminal_access': True
    },
    PermissionProfile.AUTONOMOUS: {
        'max_risk': RiskLevel.CRITICAL,
        'require_confirmation': False,
        'allowed_tools': set(),  # All tools allowed
        'blocked_tools': set(),
        'allowed_actions': set(),  # All actions allowed
        'blocked_actions': set(),
        'network_access': True,
        'filesystem_access': True,
        'terminal_access': True
    }
}


class SecurityPolicyManager:
    """
    Manages security policies and permission profiles for the LivingAI system.
    
    Responsibilities:
    - Load and manage security policies
    - Classify action risk levels
    - Check permissions
    - Validate actions against policies
    """
    
    def __init__(self, config: Any = None):
        """
        Initialize the SecurityPolicyManager.
        
        Args:
            config: Configuration manager
        """
        self.config = config
        self._policies: Dict[str, SecurityPolicy] = {}
        self._default_profile = PermissionProfile.SAFE
        self.logger = logging.getLogger(__name__)
        
        # Load default profiles
        self._load_predefined_profiles()
    
    def _load_predefined_profiles(self) -> None:
        """Load predefined permission profiles."""
        for profile, settings in PREDEFINED_PROFILES.items():
            policy = SecurityPolicy(profile=profile, **settings)
            self._policies[profile.value] = policy
    
    def get_policy(self, profile: Optional[PermissionProfile] = None) -> SecurityPolicy:
        """
        Get a security policy by profile.
        
        Args:
            profile: Permission profile (defaults to default profile)
            
        Returns:
            SecurityPolicy object
        """
        profile = profile or self._default_profile
        
        if profile.value not in self._policies:
            # Create a new policy from predefined settings
            if profile in PREDEFINED_PROFILES:
                self._policies[profile.value] = SecurityPolicy(profile=profile, **PREDEFINED_PROFILES[profile])
            else:
                # Create a custom policy
                self._policies[profile.value] = SecurityPolicy(profile=profile)
        
        return self._policies[profile.value]
    
    def set_default_profile(self, profile: PermissionProfile) -> None:
        """
        Set the default permission profile.
        
        Args:
            profile: Permission profile to use as default
        """
        self._default_profile = profile
        self.logger.info(f"Default security profile set to: {profile.value}")
    
    def classify_risk(self, action: str, tool: Optional[str] = None, args: Optional[Dict[str, Any]] = None) -> RiskLevel:
        """
        Classify the risk level of an action.
        
        Args:
            action: Action type or command
            tool: Tool name (optional)
            args: Tool arguments (optional)
            
        Returns:
            RiskLevel classification
        """
        # Convert to lowercase for comparison
        action_lower = action.lower()
        
        # CRITICAL risk actions
        critical_actions = {
            'rm -rf', 'rm -r', 'rm -f',
            'dd', 'mkfs', 'format',
            'chmod 777', 'chown', 'chgrp',
            'su', 'sudo',
            'kill -9', 'pkill',
            'apt install', 'apt remove', 'apt purge',
            'pip install', 'pip uninstall',
            'wget', 'curl',
            'mv / ', 'cp / ',
            'echo > ', 'cat > ',
            ':() { :|:& };:'  # Fork bomb
        }
        
        for critical in critical_actions:
            if critical in action_lower:
                return RiskLevel.CRITICAL
        
        # HIGH risk actions
        high_actions = {
            'rm', 'remove', 'delete',
            'chmod', 'chown', 'chgrp',
            'mv', 'move',
            'cp', 'copy',
            'kill', 'pkill', 'killall',
            'apt', 'pip', 'npm', 'yarn',
            'git reset', 'git clean',
            'dd', 'mkfs'
        }
        
        for high in high_actions:
            if high in action_lower:
                return RiskLevel.HIGH
        
        # MEDIUM risk actions
        medium_actions = {
            'write', 'save', 'create',
            'modify', 'edit', 'update',
            'touch', 'mkdir', 'rmdir',
            'git add', 'git commit', 'git push',
            'echo', 'cat', 'grep'
        }
        
        for medium in medium_actions:
            if medium in action_lower:
                return RiskLevel.MEDIUM
        
        # Check tool-specific risk
        if tool:
            tool_risk = self._get_tool_risk(tool)
            if tool_risk:
                return tool_risk
        
        # Default to LOW risk
        return RiskLevel.LOW
    
    def _get_tool_risk(self, tool_name: str) -> Optional[RiskLevel]:
        """
        Get the risk level for a specific tool.
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            RiskLevel or None if not classified
        """
        tool_lower = tool_name.lower()
        
        # Critical tools
        if any(t in tool_lower for t in ['terminal', 'shell', 'exec', 'system', 'popen']):
            return RiskLevel.CRITICAL
        
        # High risk tools
        if any(t in tool_lower for t in ['filesystem.write', 'filesystem.delete', 'delete', 'remove']):
            return RiskLevel.HIGH
        
        # Medium risk tools
        if any(t in tool_lower for t in ['filesystem', 'file', 'sqlite']):
            return RiskLevel.MEDIUM
        
        # Low risk tools
        if any(t in tool_lower for t in ['memory', 'calculator', 'datetime', 'text']):
            return RiskLevel.LOW
        
        return None
    
    def check_permission(
        self,
        action: str,
        tool: Optional[str] = None,
        profile: Optional[PermissionProfile] = None,
        args: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Check if an action is permitted under a given profile.
        
        Args:
            action: Action type
            tool: Tool name
            profile: Permission profile (defaults to default)
            args: Tool arguments
            
        Returns:
            Dictionary with:
            - allowed: bool
            - risk: RiskLevel
            - requires_confirmation: bool
            - reason: str (if denied)
        """
        profile = profile or self._default_profile
        policy = self.get_policy(profile)
        
        # Classify risk
        risk = self.classify_risk(action, tool, args)
        
        # Check if risk exceeds policy max
        risk_order = {
            RiskLevel.LOW: 0,
            RiskLevel.MEDIUM: 1,
            RiskLevel.HIGH: 2,
            RiskLevel.CRITICAL: 3
        }
        
        if risk_order.get(risk, 0) > risk_order.get(policy.max_risk, 0):
            return {
                'allowed': False,
                'risk': risk.value,
                'requires_confirmation': False,
                'reason': f"Risk level {risk.value} exceeds policy max {policy.max_risk.value}"
            }
        
        # Check if tool is blocked
        if tool and tool in policy.blocked_tools:
            return {
                'allowed': False,
                'risk': risk.value,
                'requires_confirmation': False,
                'reason': f"Tool '{tool}' is blocked by policy"
            }
        
        # Check if tool is allowed (if allowed_tools is specified)
        if policy.allowed_tools and tool and tool not in policy.allowed_tools:
            return {
                'allowed': False,
                'risk': risk.value,
                'requires_confirmation': False,
                'reason': f"Tool '{tool}' is not in allowed tools list"
            }
        
        # Check if action is blocked
        if action in policy.blocked_actions:
            return {
                'allowed': False,
                'risk': risk.value,
                'requires_confirmation': False,
                'reason': f"Action '{action}' is blocked by policy"
            }
        
        # Check if action is allowed (if allowed_actions is specified)
        if policy.allowed_actions and action not in policy.allowed_actions:
            return {
                'allowed': False,
                'risk': risk.value,
                'requires_confirmation': False,
                'reason': f"Action '{action}' is not in allowed actions list"
            }
        
        # Check access requirements
        if action in ['network', 'http', 'fetch', 'download'] and not policy.network_access:
            return {
                'allowed': False,
                'risk': risk.value,
                'requires_confirmation': False,
                'reason': "Network access is disabled by policy"
            }
        
        if action in ['filesystem', 'file', 'read', 'write'] and not policy.filesystem_access:
            return {
                'allowed': False,
                'risk': risk.value,
                'requires_confirmation': False,
                'reason': "Filesystem access is disabled by policy"
            }
        
        if action in ['terminal', 'shell', 'exec'] and not policy.terminal_access:
            return {
                'allowed': False,
                'risk': risk.value,
                'requires_confirmation': False,
                'reason': "Terminal access is disabled by policy"
            }
        
        # Determine if confirmation is required
        requires_confirmation = policy.require_confirmation and risk in [RiskLevel.MEDIUM, RiskLevel.HIGH]
        
        return {
            'allowed': True,
            'risk': risk.value,
            'requires_confirmation': requires_confirmation,
            'reason': 'Action permitted'
        }
    
    def get_risk_levels(self) -> List[str]:
        """Get list of all risk levels."""
        return [level.value for level in RiskLevel]
    
    def get_permission_profiles(self) -> List[str]:
        """Get list of all permission profiles."""
        return [profile.value for profile in PermissionProfile]
    
    def create_custom_policy(
        self,
        name: str,
        max_risk: RiskLevel = RiskLevel.MEDIUM,
        require_confirmation: bool = True,
        allowed_tools: List[str] = None,
        blocked_tools: List[str] = None,
        allowed_actions: List[str] = None,
        blocked_actions: List[str] = None,
        network_access: bool = False,
        filesystem_access: bool = True,
        terminal_access: bool = False
    ) -> SecurityPolicy:
        """
        Create a custom security policy.
        
        Args:
            name: Policy name
            max_risk: Maximum allowed risk level
            require_confirmation: Whether to require confirmation
            allowed_tools: List of allowed tools
            blocked_tools: List of blocked tools
            allowed_actions: List of allowed actions
            blocked_actions: List of blocked actions
            network_access: Whether network access is allowed
            filesystem_access: Whether filesystem access is allowed
            terminal_access: Whether terminal access is allowed
            
        Returns:
            Created SecurityPolicy
        """
        policy = SecurityPolicy(
            profile=PermissionProfile.CUSTOM,
            max_risk=max_risk,
            require_confirmation=require_confirmation,
            allowed_tools=set(allowed_tools or []),
            blocked_tools=set(blocked_tools or []),
            allowed_actions=set(allowed_actions or []),
            blocked_actions=set(blocked_actions or []),
            network_access=network_access,
            filesystem_access=filesystem_access,
            terminal_access=terminal_access
        )
        
        self._policies[name] = policy
        self.logger.info(f"Custom security policy created: {name}")
        
        return policy
