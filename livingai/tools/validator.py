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
from livingai.security.policy import RiskLevel


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
    def __init__(self, permission_manager=None):
        self.permission_manager = permission_manager
        self.logger = logging.getLogger(__name__)
        self._schemas = {}
        self._custom_validators = {}
        self._load_default_schemas()
    
    def _load_default_schemas(self):
        self._schemas['filesystem'] = {
            'read': {'type': 'object', 'properties': {'path': {'type': 'string', 'minLength': 1}}, 'required': ['path']},
            'write': {'type': 'object', 'properties': {'path': {'type': 'string', 'minLength': 1}, 'content': {'type': 'string'}}, 'required': ['path', 'content']},
            'delete': {'type': 'object', 'properties': {'path': {'type': 'string', 'minLength': 1}}, 'required': ['path']}
        }
        self._schemas['terminal'] = {
            'execute': {'type': 'object', 'properties': {'command': {'type': 'string', 'minLength': 1}}, 'required': ['command']}
        }
        self._schemas['sqlite'] = {
            'query': {'type': 'object', 'properties': {'sql': {'type': 'string', 'minLength': 1}}, 'required': ['sql']}
        }
        self._schemas['memory'] = {
            'add': {'type': 'object', 'properties': {'content': {'type': 'string'}}, 'required': ['content']},
            'search': {'type': 'object', 'properties': {'query': {'type': 'string'}}, 'required': ['query']}
        }
    
    def register_schema(self, tool_name, schema):
        if tool_name not in self._schemas:
            self._schemas[tool_name] = {}
        self._schemas[tool_name].update(schema)
    
    def register_validator(self, tool_name, validator):
        self._custom_validators[tool_name] = validator
    
    def validate_input(self, tool_name, method, args=None, kwargs=None):
        args = args or {}
        kwargs = kwargs or {}
        all_args = {**args, **kwargs}
        result = ValidationResult()
        if tool_name in self._custom_validators:
            custom_result = self._custom_validators[tool_name](all_args)
            if not custom_result.is_valid:
                result.status = custom_result.status
                result.errors.extend(custom_result.errors)
                return result
        if tool_name in self._schemas:
            method_schema = self._schemas[tool_name].get(method)
            if method_schema:
                schema_result = self._validate_schema(all_args, method_schema)
                if not schema_result.is_valid:
                    result.status = schema_result.status
                    result.errors.extend(schema_result.errors)
        danger_result = self._check_dangerous_patterns(all_args)
        if not danger_result.is_valid:
            result.status = danger_result.status
            result.errors.extend(danger_result.errors)
        if self.permission_manager:
            perm_check = self.permission_manager.check_tool_access(tool_name, method, all_args)
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
    
    def validate_output(self, tool_name, method, output):
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
    
    def validate_execution(self, tool_name, method, args=None, kwargs=None, output=None, error=None):
        result = ValidationResult()
        input_result = self.validate_input(tool_name, method, args, kwargs)
        if not input_result.is_valid:
            result.status = input_result.status
            result.errors.extend(input_result.errors)
            result.warnings.extend(input_result.warnings)
        if error:
            error_result = self._check_dangerous_patterns({'error': error})
            if not error_result.is_valid:
                result.status = ValidationStatus.INVALID
                result.errors.append(f"Execution error contains dangerous pattern")
        if output is not None:
            output_result = self.validate_output(tool_name, method, output)
            if not output_result.is_valid:
                result.status = output_result.status
                result.errors.extend(output_result.errors)
                result.warnings.extend(output_result.warnings)
        if result.is_valid:
            result.message = "Execution validation passed"
        elif result.has_errors:
            result.message = f"Execution validation failed with {len(result.errors)} error(s)"
        else:
            result.message = f"Execution validation passed with {len(result.warnings)} warning(s)"
        return result
    
    def _validate_schema(self, data, schema):
        result = ValidationResult()
        try:
            schema_type = schema.get('type', 'object')
            if schema_type == 'object':
                if not isinstance(data, dict):
                    result.status = ValidationStatus.INVALID
                    result.errors.append(f"Expected object, got {type(data).__name__}")
                    return result
                for prop in schema.get('required', []):
                    if prop not in data:
                        result.status = ValidationStatus.INVALID
                        result.errors.append(f"Missing required property: {prop}")
                for prop, prop_schema in schema.get('properties', {}).items():
                    if prop in data:
                        prop_result = self._validate_schema(data[prop], prop_schema)
                        if not prop_result.is_valid:
                            result.status = ValidationStatus.INVALID
                            for err in prop_result.errors:
                                result.errors.append(f"Property '{prop}': {err}")
            elif schema_type == 'array':
                if not isinstance(data, list):
                    result.status = ValidationStatus.INVALID
                    result.errors.append(f"Expected array, got {type(data).__name__}")
                    return result
            elif schema_type == 'string':
                if not isinstance(data, str):
                    result.status = ValidationStatus.INVALID
                    result.errors.append(f"Expected string, got {type(data).__name__}")
                elif schema.get('minLength') is not None and len(data) < schema['minLength']:
                    result.status = ValidationStatus.INVALID
                    result.errors.append(f"String too short")
            elif schema_type == 'number':
                if not isinstance(data, (int, float)):
                    result.status = ValidationStatus.INVALID
                    result.errors.append(f"Expected number, got {type(data).__name__}")
            elif schema_type == 'boolean':
                if not isinstance(data, bool):
                    result.status = ValidationStatus.INVALID
                    result.errors.append(f"Expected boolean, got {type(data).__name__}")
        except Exception as e:
            result.status = ValidationStatus.INVALID
            result.errors.append(f"Schema validation error: {e}")
        return result
    
    def _check_dangerous_patterns(self, data):
        result = ValidationResult()
        dangerous_patterns = [
            (r'[;&|]', "Command injection pattern detected"),
            (r'rm\s+-rf', "Dangerous rm -rf command detected"),
            (r'rm\s+-r', "Dangerous rm -r command detected"),
            (r'dd\s+if=', "Dangerous dd command detected"),
            (r'chmod\s+777', "Dangerous chmod detected"),
            (r'^/etc/', "System configuration path detected"),
            (r'^/usr/', "System directory path detected"),
            (r'^/bin/', "System binary path detected"),
            (r'sudo\s+', "Sudo command detected"),
            (r'kill\s+', "Kill command detected"),
            (r'apt\s+', "APT package command detected"),
            (r'pip\s+', "Pip package command detected")
        ]
        def check_value(value, path=""):
            if isinstance(value, str):
                for pattern, message in dangerous_patterns:
                    if re.search(pattern, value):
                        result.status = ValidationStatus.INVALID
                        result.errors.append(f"{message} in {path}")
            elif isinstance(value, dict):
                for k, v in value.items():
                    check_value(v, f"{path}.{k}" if path else k)
            elif isinstance(value, list):
                for i, v in enumerate(value):
                    check_value(v, f"{path}[{i}]")
        check_value(data)
        return result
    
    def sanitize_input(self, data):
        if isinstance(data, str):
            sanitized = data
            sanitized = re.sub(r'[;&|]', '', sanitized)
            return sanitized
        elif isinstance(data, dict):
            return {k: self.sanitize_input(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self.sanitize_input(item) for item in data]
        else:
            return data
    
    def sanitize_output(self, data):
        if isinstance(data, str):
            return data
        elif isinstance(data, dict):
            return {k: self.sanitize_output(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self.sanitize_output(item) for item in data]
        else:
            return data
    
    def get_schema(self, tool_name, method=None):
        if tool_name in self._schemas:
            if method:
                return self._schemas[tool_name].get(method)
            return self._schemas[tool_name]
        return None
