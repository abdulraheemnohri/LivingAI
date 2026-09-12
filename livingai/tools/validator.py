"""
LivingAI Tool Validator
=====================

Validates tool inputs, outputs, and execution results.
"""

import logging
import re
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
from enum import Enum

from .permissions import ToolPermissionManager


class ValidationStatus(Enum):
    VALID = "valid"
    INVALID = "invalid"
    WARNING = "warning"


@dataclass
class ValidationResult:
    status: ValidationStatus = ValidationStatus.VALID
    message: str = ""
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    data: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_valid(self) -> bool:
        return self.status == ValidationStatus.VALID
    
    @property
    def has_errors(self) -> bool:
        return len(self.errors) > 0
    
    @property
    def has_warnings(self) -> bool:
        return len(self.warnings) > 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'status': self.status.value,
            'message': self.message,
            'errors': self.errors,
            'warnings': self.warnings,
            'data': self.data
        }


class ToolValidator:
    def __init__(self, permission_manager: ToolPermissionManager = None):
        self.permission_manager = permission_manager
        self.logger = logging.getLogger(__name__)
        self._schemas: Dict[str, Dict[str, Any]] = {}
        self._custom_validators: Dict[str, Callable] = {}
    
    def validate_input(
        self,
        tool_name: str,
        method: str,
        args: Dict[str, Any] = None,
        kwargs: Dict[str, Any] = None
    ) -> ValidationResult:
        args = args or {}
        kwargs = kwargs or {}
        all_args = {**args, **kwargs}
        result = ValidationResult()
        
        danger_result = self._check_dangerous_patterns(all_args)
        if not danger_result.is_valid:
            result.status = danger_result.status
            result.errors.extend(danger_result.errors)
        
        if self.permission_manager:
            perm_check = self.permission_manager.check_tool_access(
                tool_name, method, all_args
            )
            if not perm_check.get('allowed', False):
                result.status = ValidationStatus.INVALID
                result.errors.append(perm_check.get('reason', 'Permission denied'))
        
        if result.is_valid:
            result.message = "Input validation passed"
        elif result.has_errors:
            result.message = f"Input validation failed with {len(result.errors)} error(s)"
        else:
            result.message = f"Input validation passed with {len(result.warnings)} warning(s)"
        return result
    
    def validate_output(
        self,
        tool_name: str,
        method: str,
        output: Any
    ) -> ValidationResult:
        result = ValidationResult()
        if output is None:
            result.status = ValidationStatus.WARNING
            result.warnings.append("Output is None")
            return result
        if isinstance(output, str):
            danger_result = self._check_dangerous_patterns({'output': output})
            if not danger_result.is_valid:
                result.status = danger_result.status
                result.errors.extend(danger_result.errors)
        output_str = str(output)
        if len(output_str) > 10 * 1024 * 1024:
            result.status = ValidationStatus.WARNING
            result.warnings.append(f"Output is very large: {len(output_str)} bytes")
        if result.is_valid:
            result.message = "Output validation passed"
        elif result.has_errors:
            result.message = f"Output validation failed with {len(result.errors)} error(s)"
        else:
            result.message = f"Output validation passed with {len(result.warnings)} warning(s)"
        return result
    
    def _check_dangerous_patterns(self, data: Dict[str, Any]) -> ValidationResult:
        result = ValidationResult()
        dangerous_patterns = [
            (r'[;&|]`', "Command injection pattern detected"),
            (r'\$\(', "Command substitution detected"),
            (r'\$\{', "Command substitution detected"),
            (r'\.\./', "Path traversal pattern detected"),
            (r'/\.\./', "Path traversal pattern detected"),
            (r'rm\s+-rf', "Dangerous rm -rf command detected"),
            (r'rm\s+-r', "Dangerous rm -r command detected"),
            (r'dd\s+if=', "Dangerous dd command detected"),
            (r'chmod\s+777', "Dangerous chmod detected"),
            (r'wget\s+', "Network download detected"),
            (r'curl\s+', "Network download detected"),
            (r'^/etc/', "System configuration path detected"),
            (r'^/usr/', "System directory path detected"),
            (r'^/var/', "System directory path detected"),
            (r'sudo\s+', "Sudo command detected"),
            (r'su\s+', "Su command detected"),
        ]
        
        def check_value(value: Any, path: str = "") -> None:
            if isinstance(value, str):
                for pattern, message in dangerous_patterns:
                    if re.search(pattern, value):
                        result.status = ValidationStatus.INVALID
                        result.errors.append(f"{message} in {path}: '{value[:50]}...'")
            elif isinstance(value, dict):
                for k, v in value.items():
                    check_value(v, f"{path}.{k}" if path else k)
            elif isinstance(value, list):
                for i, v in enumerate(value):
                    check_value(v, f"{path}[{i}]")
        
        check_value(data)
        return result
    
    def sanitize_input(self, data: Any) -> Any:
        if isinstance(data, str):
            sanitized = data
            sanitized = re.sub(r'[;&|]`', '', sanitized)
            sanitized = re.sub(r'\$\(', '', sanitized)
            sanitized = re.sub(r'\$\{', '', sanitized)
            return sanitized
        elif isinstance(data, dict):
            return {k: self.sanitize_input(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self.sanitize_input(item) for item in data]
        else:
            return data
