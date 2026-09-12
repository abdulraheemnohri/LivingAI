"""
LivingAI Security Policy
=======================

Defines security policies, risk levels, and permission profiles for LivingAI.
"""

import logging
from typing import Dict, Any, Optional, List
from enum import Enum
from dataclasses import dataclass, field


class RiskLevel(Enum):
    """
    Risk levels for tools and operations.
    
    CRITICAL: Operations that can cause irreversible damage or compromise system security
    HIGH: Operations that can cause significant damage or data loss
    MEDIUM: Operations that require caution and confirmation
    LOW: Safe operations with minimal risk
    """
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class PermissionProfile(Enum):
    """
    Permission profiles for different user types.
    """
    ADMIN = "admin"
    DEVELOPER = "developer"
    USER = "user"
    GUEST = "guest"
    SANDBOX = "sandbox"


@dataclass
class SecurityPolicy:
    """
    Security policy configuration.
    """
    name: str
    description: str = ""
    risk_level: RiskLevel = RiskLevel.MEDIUM
    allowed_actions: List[str] = field(default_factory=list)
    blocked_actions: List[str] = field(default_factory=list)
    requires_confirmation: bool = True
    max_retries: int = 3
    timeout: float = 30.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'description': self.description,
            'risk_level': self.risk_level.value,
            'allowed_actions': self.allowed_actions,
            'blocked_actions': self.blocked_actions,
            'requires_confirmation': self.requires_confirmation,
            'max_retries': self.max_retries,
            'timeout': self.timeout
        }


# Default security policies
DEFAULT_POLICIES: Dict[str, Dict[str, Any]] = {
    'filesystem': {
        'risk_level': RiskLevel.MEDIUM,
        'allowed_actions': ['read', 'list', 'exists', 'stat'],
        'blocked_actions': ['delete', 'remove', 'rm', 'chmod', 'chown'],
        'requires_confirmation': True
    },
    'terminal': {
        'risk_level': RiskLevel.CRITICAL,
        'allowed_actions': [],
        'blocked_actions': ['*'],
        'requires_confirmation': True
    },
    'network': {
        'risk_level': RiskLevel.HIGH,
        'allowed_actions': ['get', 'post'],
        'blocked_actions': ['delete', 'put', 'patch'],
        'requires_confirmation': True
    },
    'memory': {
        'risk_level': RiskLevel.LOW,
        'allowed_actions': ['*'],
        'blocked_actions': [],
        'requires_confirmation': False
    }
}


class SecurityPolicyManager:
    """
    Manages security policies for LivingAI.
    """
    
    def __init__(self):
        self._policies: Dict[str, SecurityPolicy] = {}
        self.logger = logging.getLogger(__name__)
        self._load_default_policies()
    
    def _load_default_policies(self) -> None:
        """Load default security policies."""
        for name, settings in DEFAULT_POLICIES.items():
            policy = SecurityPolicy(name=name, **settings)
            self._policies[name] = policy
    
    def get_policy(self, name: str) -> Optional[SecurityPolicy]:
        """Get a security policy by name."""
        return self._policies.get(name)
    
    def check_action(
        self,
        policy_name: str,
        action: str
    ) -> Dict[str, Any]:
        """
        Check if an action is allowed by a policy.
        
        Args:
            policy_name: Name of the policy
            action: Action to check
            
        Returns:
            Dictionary with allowed status and details
        """
        policy = self.get_policy(policy_name)
        
        if not policy:
            return {
                'allowed': False,
                'reason': f"Policy '{policy_name}' not found"
            }
        
        # Check if action is explicitly blocked
        if action in policy.blocked_actions or '*' in policy.blocked_actions:
            return {
                'allowed': False,
                'reason': f"Action '{action}' is blocked by policy '{policy_name}'",
                'risk_level': policy.risk_level.value
            }
        
        # Check if action is explicitly allowed or if all actions are allowed
        if policy.allowed_actions == ['*'] or action in policy.allowed_actions:
            return {
                'allowed': True,
                'reason': f"Action '{action}' is allowed by policy '{policy_name}'",
                'risk_level': policy.risk_level.value,
                'requires_confirmation': policy.requires_confirmation
            }
        
        # If action is not in allowed list and not explicitly blocked
        return {
            'allowed': False,
            'reason': f"Action '{action}' is not allowed by policy '{policy_name}'",
            'risk_level': policy.risk_level.value
        }
    
    def list_policies(self) -> List[str]:
        """List all policy names."""
        return list(self._policies.keys())
    
    def add_policy(self, policy: SecurityPolicy) -> None:
        """Add a new security policy."""
        self._policies[policy.name] = policy
        self.logger.info(f"Added security policy: {policy.name}")
    
    def remove_policy(self, name: str) -> bool:
        """Remove a security policy."""
        if name in self._policies:
            del self._policies[name]
            self.logger.info(f"Removed security policy: {name}")
            return True
        return False
