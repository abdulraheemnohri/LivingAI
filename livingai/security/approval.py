"""
LivingAI Approval Manager
=======================

Manages user approvals for actions that require human confirmation.
"""

import logging
import time
import uuid
from typing import Dict, Any, Optional, List
from enum import Enum
from dataclasses import dataclass, field
from queue import Queue
from threading import Lock

from .policy import RiskLevel


class ApprovalStatus(Enum):
    """Status of an approval request."""
    PENDING = "pending"     # Waiting for user response
    APPROVED = "approved"   # User approved
    DENIED = "denied"       # User denied
    EXPIRED = "expired"     # Request expired
    CANCELLED = "cancelled" # Request was cancelled


class ApprovalType(Enum):
    """Type of approval."""
    ONCE = "once"           # Approve this specific action once
    RULE = "rule"           # Approve all similar actions
    ALWAYS = "always"       # Always allow this action


@dataclass
class ApprovalRequest:
    """
    Represents a request for user approval.
    
    Attributes:
        id: Unique request ID
        action: Action being requested
        tool: Tool name (if applicable)
        args: Arguments for the action
        risk: Risk level
        agent_id: ID of requesting agent
        task_id: ID of requesting task
        goal_id: ID of goal
        profile: Permission profile in use
        created_at: Timestamp when request was created
        expires_at: Timestamp when request expires
        status: Current status
        approval_type: Type of approval granted
        response_at: Timestamp when user responded
        reason: Reason for approval/denial
    """
    id: str
    action: str
    tool: Optional[str] = None
    args: Dict[str, Any] = field(default_factory=dict)
    risk: RiskLevel = RiskLevel.LOW
    agent_id: Optional[str] = None
    task_id: Optional[str] = None
    goal_id: Optional[str] = None
    profile: str = "safe"
    created_at: float = field(default_factory=time.time)
    expires_at: float = field(default=0.0)
    status: ApprovalStatus = ApprovalStatus.PENDING
    approval_type: Optional[ApprovalType] = None
    response_at: Optional[float] = None
    reason: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'action': self.action,
            'tool': self.tool,
            'args': self.args,
            'risk': self.risk.value,
            'agent_id': self.agent_id,
            'task_id': self.task_id,
            'goal_id': self.goal_id,
            'profile': self.profile,
            'created_at': self.created_at,
            'expires_at': self.expires_at,
            'status': self.status.value,
            'approval_type': self.approval_type.value if self.approval_type else None,
            'response_at': self.response_at,
            'reason': self.reason
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ApprovalRequest':
        """Create from dictionary."""
        request = cls(
            id=data.get('id', str(uuid.uuid4())),
            action=data.get('action', ''),
            tool=data.get('tool'),
            args=data.get('args', {}),
            risk=RiskLevel(data.get('risk', 'low')),
            agent_id=data.get('agent_id'),
            task_id=data.get('task_id'),
            goal_id=data.get('goal_id'),
            profile=data.get('profile', 'safe'),
            created_at=data.get('created_at', time.time()),
            expires_at=data.get('expires_at', time.time() + 300),  # Default 5 minutes
            status=ApprovalStatus(data.get('status', 'pending')),
            approval_type=ApprovalType(data.get('approval_type')) if data.get('approval_type') else None,
            response_at=data.get('response_at'),
            reason=data.get('reason')
        )
        return request
    
    def is_expired(self) -> bool:
        """Check if request has expired."""
        return time.time() > self.expires_at
    
    def is_pending(self) -> bool:
        """Check if request is still pending."""
        return self.status == ApprovalStatus.PENDING and not self.is_expired()


@dataclass
class ApprovalRule:
    """
    Represents a persistent approval rule.
    
    Attributes:
        id: Unique rule ID
        action_pattern: Pattern to match actions
        tool_pattern: Pattern to match tools
        risk_threshold: Maximum risk level
        created_at: When rule was created
        expires_at: When rule expires (0 = never)
        created_by: Who created the rule
        description: Rule description
    """
    id: str
    action_pattern: str
    tool_pattern: Optional[str] = None
    risk_threshold: RiskLevel = RiskLevel.HIGH
    created_at: float = field(default_factory=time.time)
    expires_at: float = 0.0
    created_by: str = "system"
    description: str = ""
    
    def matches(self, action: str, tool: Optional[str] = None, risk: RiskLevel = RiskLevel.LOW) -> bool:
        """
        Check if this rule matches the given action/tool/risk.
        
        Args:
            action: Action to check
            tool: Tool name
            risk: Risk level
            
        Returns:
            True if rule matches
        """
        # Check if expired
        if self.expires_at > 0 and time.time() > self.expires_at:
            return False
        
        # Check action pattern
        import re
        if '*' in self.action_pattern:
            pattern = self.action_pattern.replace('*', '.*')
            if not re.match(pattern, action):
                return False
        elif self.action_pattern != action:
            return False
        
        # Check tool pattern
        if self.tool_pattern:
            if '*' in self.tool_pattern:
                pattern = self.tool_pattern.replace('*', '.*')
                if tool and not re.match(pattern, tool):
                    return False
            elif tool and self.tool_pattern != tool:
                return False
        
        # Check risk threshold
        risk_order = {
            RiskLevel.LOW: 0,
            RiskLevel.MEDIUM: 1,
            RiskLevel.HIGH: 2,
            RiskLevel.CRITICAL: 3
        }
        if risk_order.get(risk, 0) > risk_order.get(self.risk_threshold, 0):
            return False
        
        return True


class ApprovalManager:
    """
    Manages user approvals for actions requiring human confirmation.
    
    Responsibilities:
    - Queue approval requests
    - Track approval status
    - Manage approval rules
    - Handle user responses
    - Expire old requests
    """
    
    def __init__(self, timeout: float = 300.0):
        """
        Initialize the ApprovalManager.
        
        Args:
            timeout: Default timeout for approval requests in seconds
        """
        self._requests: Dict[str, ApprovalRequest] = {}
        self._rules: Dict[str, ApprovalRule] = {}
        self._queue = Queue()
        self._timeout = timeout
        self._lock = Lock()
        self.logger = logging.getLogger(__name__)
    
    def request_approval(
        self,
        action: str,
        tool: Optional[str] = None,
        args: Dict[str, Any] = None,
        risk: RiskLevel = RiskLevel.MEDIUM,
        agent_id: Optional[str] = None,
        task_id: Optional[str] = None,
        goal_id: Optional[str] = None,
        profile: str = "safe"
    ) -> ApprovalRequest:
        """
        Request user approval for an action.
        
        Args:
            action: Action being requested
            tool: Tool name
            args: Action arguments
            risk: Risk level
            agent_id: Requesting agent ID
            task_id: Requesting task ID
            goal_id: Goal ID
            profile: Permission profile
            
        Returns:
            ApprovalRequest object
        """
        request_id = str(uuid.uuid4())
        expires_at = time.time() + self._timeout
        
        request = ApprovalRequest(
            id=request_id,
            action=action,
            tool=tool,
            args=args or {},
            risk=risk,
            agent_id=agent_id,
            task_id=task_id,
            goal_id=goal_id,
            profile=profile,
            created_at=time.time(),
            expires_at=expires_at
        )
        
        with self._lock:
            self._requests[request_id] = request
            self._queue.put(request)
        
        self.logger.info(f"Approval requested: {action} (risk: {risk.value}, id: {request_id})")
        
        return request
    
    def check_rule(self, action: str, tool: Optional[str] = None, risk: RiskLevel = RiskLevel.LOW) -> bool:
        """
        Check if an action is approved by an existing rule.
        
        Args:
            action: Action to check
            tool: Tool name
            risk: Risk level
            
        Returns:
            True if action is approved by a rule
        """
        with self._lock:
            for rule in self._rules.values():
                if rule.matches(action, tool, risk):
                    self.logger.debug(f"Action approved by rule: {action} -> {rule.id}")
                    return True
        return False
    
    def is_approved(self, request_id: str) -> bool:
        """
        Check if a request is approved.
        
        Args:
            request_id: Request ID
            
        Returns:
            True if approved
        """
        with self._lock:
            request = self._requests.get(request_id)
            if not request:
                return False
            
            # Check if expired
            if request.is_expired():
                request.status = ApprovalStatus.EXPIRED
                return False
            
            return request.status == ApprovalStatus.APPROVED
    
    def is_denied(self, request_id: str) -> bool:
        """
        Check if a request is denied.
        
        Args:
            request_id: Request ID
            
        Returns:
            True if denied or expired
        """
        with self._lock:
            request = self._requests.get(request_id)
            if not request:
                return True  # Unknown request = denied
            
            if request.is_expired():
                request.status = ApprovalStatus.EXPIRED
                return True
            
            return request.status in [ApprovalStatus.DENIED, ApprovalStatus.CANCELLED]
    
    def approve(self, request_id: str, approval_type: ApprovalType = ApprovalType.ONCE, reason: str = "") -> bool:
        """
        Approve a request.
        
        Args:
            request_id: Request ID
            approval_type: Type of approval
            reason: Reason for approval
            
        Returns:
            True if request was found and approved
        """
        with self._lock:
            request = self._requests.get(request_id)
            if not request or not request.is_pending():
                return False
            
            request.status = ApprovalStatus.APPROVED
            request.approval_type = approval_type
            request.response_at = time.time()
            request.reason = reason
            
            # If this is a rule approval, create a rule
            if approval_type == ApprovalType.RULE:
                rule_id = str(uuid.uuid4())
                rule = ApprovalRule(
                    id=rule_id,
                    action_pattern=request.action,
                    tool_pattern=request.tool,
                    risk_threshold=request.risk,
                    created_by="user",
                    description=f"Auto-created from approval: {request.action}"
                )
                self._rules[rule_id] = rule
                self.logger.info(f"Created approval rule from request: {rule_id}")
            
            self.logger.info(f"Request approved: {request_id} (type: {approval_type.value})")
            return True
    
    def deny(self, request_id: str, reason: str = "") -> bool:
        """
        Deny a request.
        
        Args:
            request_id: Request ID
            reason: Reason for denial
            
        Returns:
            True if request was found and denied
        """
        with self._lock:
            request = self._requests.get(request_id)
            if not request or not request.is_pending():
                return False
            
            request.status = ApprovalStatus.DENIED
            request.response_at = time.time()
            request.reason = reason
            
            self.logger.info(f"Request denied: {request_id} (reason: {reason})")
            return True
    
    def cancel(self, request_id: str, reason: str = "") -> bool:
        """
        Cancel a pending request.
        
        Args:
            request_id: Request ID
            reason: Reason for cancellation
            
        Returns:
            True if request was found and cancelled
        """
        with self._lock:
            request = self._requests.get(request_id)
            if not request or not request.is_pending():
                return False
            
            request.status = ApprovalStatus.CANCELLED
            request.response_at = time.time()
            request.reason = reason
            
            self.logger.info(f"Request cancelled: {request_id} (reason: {reason})")
            return True
    
    def get_request(self, request_id: str) -> Optional[ApprovalRequest]:
        """
        Get a specific approval request.
        
        Args:
            request_id: Request ID
            
        Returns:
            ApprovalRequest or None
        """
        with self._lock:
            request = self._requests.get(request_id)
            if request and request.is_expired():
                request.status = ApprovalStatus.EXPIRED
            return request
    
    def get_pending_requests(self) -> List[ApprovalRequest]:
        """
        Get all pending approval requests.
        
        Returns:
            List of pending ApprovalRequest objects
        """
        with self._lock:
            return [r for r in self._requests.values() if r.is_pending()]
    
    def get_all_requests(self) -> List[ApprovalRequest]:
        """
        Get all approval requests.
        
        Returns:
            List of all ApprovalRequest objects
        """
        with self._lock:
            # Expire old requests
            for request in self._requests.values():
                if request.is_expired():
                    request.status = ApprovalStatus.EXPIRED
            return list(self._requests.values())
    
    def cleanup_expired(self) -> int:
        """
        Clean up expired requests.
        
        Returns:
            Number of requests removed
        """
        with self._lock:
            expired_ids = [
                req_id for req_id, req in self._requests.items()
                if req.is_expired()
            ]
            for req_id in expired_ids:
                self._requests[req_id].status = ApprovalStatus.EXPIRED
                del self._requests[req_id]
            
            if expired_ids:
                self.logger.info(f"Cleaned up {len(expired_ids)} expired approval requests")
            
            return len(expired_ids)
    
    def add_rule(
        self,
        action_pattern: str,
        tool_pattern: Optional[str] = None,
        risk_threshold: RiskLevel = RiskLevel.HIGH,
        expires_at: float = 0.0,
        description: str = ""
    ) -> ApprovalRule:
        """
        Add a new approval rule.
        
        Args:
            action_pattern: Pattern to match actions (supports * wildcard)
            tool_pattern: Pattern to match tools (supports * wildcard)
            risk_threshold: Maximum risk level
            expires_at: When rule expires (0 = never)
            description: Rule description
            
        Returns:
            Created ApprovalRule
        """
        rule_id = str(uuid.uuid4())
        rule = ApprovalRule(
            id=rule_id,
            action_pattern=action_pattern,
            tool_pattern=tool_pattern,
            risk_threshold=risk_threshold,
            created_at=time.time(),
            expires_at=expires_at,
            created_by="user",
            description=description
        )
        
        with self._lock:
            self._rules[rule_id] = rule
        
        self.logger.info(f"Added approval rule: {rule_id} - {action_pattern}")
        return rule
    
    def remove_rule(self, rule_id: str) -> bool:
        """
        Remove an approval rule.
        
        Args:
            rule_id: Rule ID
            
        Returns:
            True if rule was removed
        """
        with self._lock:
            if rule_id in self._rules:
                del self._rules[rule_id]
                self.logger.info(f"Removed approval rule: {rule_id}")
                return True
            return False
    
    def list_rules(self) -> List[ApprovalRule]:
        """
        List all approval rules.
        
        Returns:
            List of ApprovalRule objects
        """
        with self._lock:
            # Remove expired rules
            expired_ids = [
                rule_id for rule_id, rule in self._rules.items()
                if rule.expires_at > 0 and time.time() > rule.expires_at
            ]
            for rule_id in expired_ids:
                del self._rules[rule_id]
            
            return list(self._rules.values())
    
    def get_next_request(self) -> Optional[ApprovalRequest]:
        """
        Get the next pending approval request from the queue.
        
        Returns:
            Next ApprovalRequest or None
        """
        try:
            request = self._queue.get_nowait()
            if request.is_expired():
                request.status = ApprovalStatus.EXPIRED
                return self.get_next_request()  # Try next
            return request
        except:
            return None
    
    def wait_for_approval(self, request_id: str, timeout: Optional[float] = None) -> Optional[ApprovalRequest]:
        """
        Wait for a specific request to be approved or denied.
        
        Args:
            request_id: Request ID
            timeout: Maximum time to wait in seconds
            
        Returns:
            ApprovalRequest with final status, or None if timed out
        """
        start_time = time.time()
        while True:
            with self._lock:
                request = self._requests.get(request_id)
                if not request:
                    return None
                
                if not request.is_pending():
                    return request
            
            # Check timeout
            if timeout is not None and (time.time() - start_time) > timeout:
                return None
            
            # Wait a bit
            time.sleep(0.5)
