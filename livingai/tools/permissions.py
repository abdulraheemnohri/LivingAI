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
    DENIED = "denied"       # Tool is completely denied
    READ_ONLY = "read_only" # Only read operations allowed
    RESTRICTED = "restricted" # Restricted operations only
    FULL = "full"           # Full access to tool
