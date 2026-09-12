"""
Tool Validator Module

Validates AI tools, their inputs, outputs, and configurations.
This module provides comprehensive validation for the LivingAI tool system.

Author: Abdulraheem Nohari
"""

import inspect
import logging
import re
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple, Type, Union
from enum import Enum

from .registry import ToolRegistry, ToolInfo, ToolCategory
from .sandbox import ToolSandbox

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Base exception for validation errors"""
    pass


class InvalidToolError(ValidationError):
    """Raised when a tool is invalid"""
    pass


class InvalidInputError(ValidationError):
    """Raised when input is invalid"""
    pass


class InvalidOutputError(ValidationError):
    """Raised when output is invalid"""
    pass


class SecurityError(ValidationError):
    """Raised when a security issue is detected"""
    pass


class ValidationLevel(Enum):
    """Levels of validation strictness"""
    STRICT = "strict"
    NORMAL = "normal"
    LENIENT = "lenient"
    NONE = "none"


class ValidationStatus(Enum):
    """Status of validation"""
    VALID = "valid"
    INVALID = "invalid"
    WARNING = "warning"


@dataclass
class ValidationResult:
    """Result of a validation check"""
    is_valid: bool
    status: ValidationStatus
    message: str
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    details: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'is_valid': self.is_valid,
            'status': self.status.value,
            'message': self.message,
            'errors': self.errors,
            'warnings': self.warnings,
            'details': self.details,
        }
    
    def merge(self, other: 'ValidationResult') -> 'ValidationResult':
        """
        Merge with another validation result.
        
        Args:
            other: Another ValidationResult
            
        Returns:
            Merged ValidationResult
        """
        new_errors = self.errors + other.errors
        new_warnings = self.warnings + other.warnings
        
        if not self.is_valid or not other.is_valid:
            is_valid = False
            status = ValidationStatus.INVALID
        elif new_warnings:
            is_valid = True
            status = ValidationStatus.WARNING
        else:
            is_valid = True
            status = ValidationStatus.VALID
        
        return ValidationResult(
            is_valid=is_valid,
            status=status,
            message=f"{self.message}; {other.message}",
            errors=new_errors,
            warnings=new_warnings,
            details={**self.details, **other.details},
        )


@dataclass
class ValidationRule:
    """A validation rule for tool inputs"""
    name: str
    validator: Callable[[Any], bool]
    message: str
    is_required: bool = True
    
    def validate(self, value: Any) -> Tuple[bool, Optional[str]]:
        """
        Validate a value against this rule.
        
        Args:
            value: Value to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            is_valid = self.validator(value)
            if not is_valid:
                return False, self.message
            return True, None
        except Exception as e:
            return False, f"{self.message}: {str(e)}"


class InputValidator:
    """Validates tool inputs"""
    
    def __init__(self):
        """Initialize the input validator"""
        self._rules: Dict[str, List[ValidationRule]] = {}
        self._type_validators: Dict[Type, ValidationRule] = {}
        
        # Register default type validators
        self._register_default_validators()
    
    def _register_default_validators(self):
        """Register default type validators"""
        # String validators
        self.register_type(str, lambda x: isinstance(x, str))
        
        # Integer validators
        self.register_type(int, lambda x: isinstance(x, int))
        
        # Float validators
        self.register_type(float, lambda x: isinstance(x, (int, float)))
        
        # Boolean validators
        self.register_type(bool, lambda x: isinstance(x, bool))
        
        # List validators
        self.register_type(list, lambda x: isinstance(x, list))
        
        # Dict validators
        self.register_type(dict, lambda x: isinstance(x, dict))
        
        # None validators
        self.register_type(type(None), lambda x: x is None)
    
    def register_rule(self, 
                     param_name: str, 
                     rule: ValidationRule) -> 'InputValidator':
        """
        Register a validation rule for a parameter.
        
        Args:
            param_name: Name of the parameter
            rule: ValidationRule to register
            
        Returns:
            Self for chaining
        """
        if param_name not in self._rules:
            self._rules[param_name] = []
        self._rules[param_name].append(rule)
        return self
    
    def register_type(self, 
                     data_type: Type, 
                     validator: Callable[[Any], bool]) -> 'InputValidator':
        """
        Register a type validator.
        
        Args:
            data_type: Type to validate
            validator: Validator function
            
        Returns:
            Self for chaining
        """
        self._type_validators[data_type] = ValidationRule(
            name=f"type:{data_type.__name__}",
            validator=validator,
            message=f"Value must be of type {data_type.__name__}",
        )
        return self
    
    def validate(self, 
                 param_name: str, 
                 value: Any, 
                 expected_type: Optional[Type] = None) -> ValidationResult:
        """
        Validate a parameter value.
        
        Args:
            param_name: Name of the parameter
            value: Value to validate
            expected_type: Optional expected type
            
        Returns:
            ValidationResult
        """
        errors = []
        warnings = []
        
        # Check type
        if expected_type is not None:
            type_validator = self._type_validators.get(expected_type)
            if type_validator:
                is_valid, error = type_validator.validate(value)
                if not is_valid:
                    errors.append(error or "")
        
        # Check custom rules
        if param_name in self._rules:
            for rule in self._rules[param_name]:
                is_valid, error = rule.validate(value)
                if not is_valid:
                    if rule.is_required:
                        errors.append(error or "")
                    else:
                        warnings.append(error or "")
        
        if errors:
            return ValidationResult(
                is_valid=False,
                status=ValidationStatus.INVALID,
                message=f"Validation failed for '{param_name}'",
                errors=errors,
                warnings=warnings,
            )
        
        if warnings:
            return ValidationResult(
                is_valid=True,
                status=ValidationStatus.WARNING,
                message=f"Validation passed with warnings for '{param_name}'",
                warnings=warnings,
            )
        
        return ValidationResult(
            is_valid=True,
            status=ValidationStatus.VALID,
            message=f"Validation passed for '{param_name}'",
        )
    
    def validate_dict(self, 
                      params: Dict[str, Any],
                      expected_types: Optional[Dict[str, Type]] = None) -> ValidationResult:
        """
        Validate a dictionary of parameters.
        
        Args:
            params: Dictionary of parameters to validate
            expected_types: Optional dictionary of expected types
            
        Returns:
            ValidationResult
        """
        combined_result = ValidationResult(
            is_valid=True,
            status=ValidationStatus.VALID,
            message="All validations passed",
        )
        
        for param_name, value in params.items():
            expected_type = None
            if expected_types and param_name in expected_types:
                expected_type = expected_types[param_name]
            
            result = self.validate(param_name, value, expected_type)
            combined_result = combined_result.merge(result)
        
        return combined_result


class ToolValidator:
    """
    Validates AI tools and their configurations.
    
    This class provides comprehensive validation for tools including:
    - Tool class validation
    - Input validation
    - Output validation
    - Security validation
    - Configuration validation
    """
    
    def __init__(self, 
                 registry: Optional[ToolRegistry] = None,
                 sandbox: Optional[ToolSandbox] = None,
                 level: ValidationLevel = ValidationLevel.NORMAL):
        """
        Initialize the tool validator.
        
        Args:
            registry: Tool registry instance
            sandbox: Tool sandbox instance
            level: Validation level
        """
        self.registry = registry or ToolRegistry()
        self.sandbox = sandbox or ToolSandbox()
        self.level = level
        self.input_validator = InputValidator()
        
        # Security patterns
        self._dangerous_patterns = [
            r'eval\(',
            r'exec\(',
            r'__import__\(',
            r'open\(',
            r'subprocess\.\w+\(',
            r'os\.\w+\(',
            r'sys\.\w+\(',
            r'pickle\.\w+\(',
            r'marshal\.\w+\(',
        ]
        
        self._dangerous_modules = {
            'os', 'sys', 'subprocess', 'shutil', 'socket',
            'pickle', 'marshal', 'ctypes', 'multiprocessing',
            'threading', 'asyncio', 'http', 'urllib', 'ftplib',
        }
    
    def validate_tool_class(self, tool_class: Type) -> ValidationResult:
        """
        Validate a tool class.
        
        Args:
            tool_class: Tool class to validate
            
        Returns:
            ValidationResult
        """
        errors = []
        warnings = []
        
        # Check if it's callable
        if not callable(tool_class):
            errors.append("Tool class is not callable")
        
        # Check if it has required methods
        if inspect.isclass(tool_class):
            required_methods = ['execute', 'run']
            has_required = any(hasattr(tool_class, method) for method in required_methods)
            if not has_required:
                warnings.append("Tool class should have an 'execute' or 'run' method")
        
        # Check for dangerous patterns in source code
        try:
            source = inspect.getsource(tool_class)
            for pattern in self._dangerous_patterns:
                if re.search(pattern, source):
                    if self.level == ValidationLevel.STRICT:
                        errors.append(f"Dangerous pattern detected: {pattern}")
                    else:
                        warnings.append(f"Potential security issue: {pattern}")
        except (TypeError, OSError):
            # Can't get source for built-in types
            pass
        
        # Check imports
        try:
            if inspect.isclass(tool_class):
                module = inspect.getmodule(tool_class)
                if module:
                    module_name = module.__name__
                    for dangerous_module in self._dangerous_modules:
                        if module_name.startswith(dangerous_module):
                            if self.level == ValidationLevel.STRICT:
                                errors.append(f"Dangerous module import: {dangerous_module}")
                            else:
                                warnings.append(f"Potential security issue: module {dangerous_module}")
        except Exception:
            pass
        
        if errors:
            return ValidationResult(
                is_valid=False,
                status=ValidationStatus.INVALID,
                message="Tool class validation failed",
                errors=errors,
                warnings=warnings,
            )
        
        if warnings:
            return ValidationResult(
                is_valid=True,
                status=ValidationStatus.WARNING,
                message="Tool class validation passed with warnings",
                warnings=warnings,
            )
        
        return ValidationResult(
            is_valid=True,
            status=ValidationStatus.VALID,
            message="Tool class validation passed",
        )
    
    def validate_tool_registration(self, tool_name: str) -> ValidationResult:
        """
        Validate a registered tool.
        
        Args:
            tool_name: Name of the tool to validate
            
        Returns:
            ValidationResult
        """
        tool_info = self.registry.get(tool_name)
        
        if tool_info is None:
            return ValidationResult(
                is_valid=False,
                status=ValidationStatus.INVALID,
                message=f"Tool '{tool_name}' is not registered",
            )
        
        errors = []
        warnings = []
        
        # Validate name
        if not tool_name or not isinstance(tool_name, str):
            errors.append("Tool name must be a non-empty string")
        elif len(tool_name) > 100:
            warnings.append("Tool name is too long (max 100 characters)")
        
        # Validate description
        if not tool_info.description or not isinstance(tool_info.description, str):
            warnings.append("Tool description should be a non-empty string")
        
        # Validate category
        if not isinstance(tool_info.category, ToolCategory):
            errors.append("Tool category must be a ToolCategory enum")
        
        # Validate tool class if provided
        if tool_info.tool_class:
            class_result = self.validate_tool_class(tool_info.tool_class)
            if not class_result.is_valid:
                errors.extend(class_result.errors)
                warnings.extend(class_result.warnings)
        
        if errors:
            return ValidationResult(
                is_valid=False,
                status=ValidationStatus.INVALID,
                message=f"Tool '{tool_name}' validation failed",
                errors=errors,
                warnings=warnings,
            )
        
        if warnings:
            return ValidationResult(
                is_valid=True,
                status=ValidationStatus.WARNING,
                message=f"Tool '{tool_name}' validation passed with warnings",
                warnings=warnings,
            )
        
        return ValidationResult(
            is_valid=True,
            status=ValidationStatus.VALID,
            message=f"Tool '{tool_name}' validation passed",
        )
    
    def validate_input(self, 
                      tool_name: str, 
                      args: Tuple = (),
                      kwargs: Dict = None) -> ValidationResult:
        """
        Validate input for a tool.
        
        Args:
            tool_name: Name of the tool
            args: Positional arguments
            kwargs: Keyword arguments
            
        Returns:
            ValidationResult
        """
        kwargs = kwargs or {}
        
        # Get tool info for expected parameters
        tool_info = self.registry.get(tool_name)
        
        # For now, do basic validation
        # More specific validation can be added based on tool metadata
        
        errors = []
        warnings = []
        
        # Check for None values in kwargs
        for key, value in kwargs.items():
            if value is None:
                warnings.append(f"Parameter '{key}' has None value")
        
        # Check for circular references
        try:
            import json
            json.dumps(args)
            json.dumps(kwargs)
        except (TypeError, ValueError) as e:
            errors.append(f"Input contains non-serializable data: {e}")
        
        if errors:
            return ValidationResult(
                is_valid=False,
                status=ValidationStatus.INVALID,
                message=f"Input validation failed for tool '{tool_name}'",
                errors=errors,
                warnings=warnings,
            )
        
        if warnings:
            return ValidationResult(
                is_valid=True,
                status=ValidationStatus.WARNING,
                message=f"Input validation passed with warnings for tool '{tool_name}'",
                warnings=warnings,
            )
        
        return ValidationResult(
            is_valid=True,
            status=ValidationStatus.VALID,
            message=f"Input validation passed for tool '{tool_name}'",
        )
    
    def validate_output(self, 
                        tool_name: str, 
                        output: Any) -> ValidationResult:
        """
        Validate output from a tool.
        
        Args:
            tool_name: Name of the tool
            output: Output to validate
            
        Returns:
            ValidationResult
        """
        errors = []
        warnings = []
        
        # Check for None output
        if output is None:
            warnings.append("Tool returned None output")
        
        # Check for circular references
        try:
            import json
            json.dumps(output)
        except (TypeError, ValueError) as e:
            errors.append(f"Output contains non-serializable data: {e}")
        
        # Check output size
        try:
            output_str = str(output)
            if len(output_str) > 1000000:  # 1MB limit
                errors.append("Output is too large (max 1MB)")
        except Exception:
            pass
        
        if errors:
            return ValidationResult(
                is_valid=False,
                status=ValidationStatus.INVALID,
                message=f"Output validation failed for tool '{tool_name}'",
                errors=errors,
                warnings=warnings,
            )
        
        if warnings:
            return ValidationResult(
                is_valid=True,
                status=ValidationStatus.WARNING,
                message=f"Output validation passed with warnings for tool '{tool_name}'",
                warnings=warnings,
            )
        
        return ValidationResult(
            is_valid=True,
            status=ValidationStatus.VALID,
            message=f"Output validation passed for tool '{tool_name}'",
        )
    
    def validate_all_tools(self) -> Dict[str, ValidationResult]:
        """
        Validate all registered tools.
        
        Returns:
            Dictionary of tool names to validation results
        """
        results = {}
        
        for tool_info in self.registry.get_all():
            result = self.validate_tool_registration(tool_info.name)
            results[tool_info.name] = result
        
        return results
    
    def set_validation_level(self, level: ValidationLevel):
        """
        Set the validation level.
        
        Args:
            level: Validation level to set
        """
        self.level = level
        logger.info(f"Validation level set to {level.value}")
    
    def add_dangerous_pattern(self, pattern: str) -> None:
        """
        Add a dangerous pattern to check for.
        
        Args:
            pattern: Regex pattern to add
        """
        self._dangerous_patterns.append(pattern)
        logger.info(f"Added dangerous pattern: {pattern}")
    
    def add_dangerous_module(self, module_name: str) -> None:
        """
        Add a dangerous module to check for.
        
        Args:
            module_name: Module name to add
        """
        self._dangerous_modules.add(module_name)
        logger.info(f"Added dangerous module: {module_name}")


# Global validator instance
validator = ToolValidator()


def get_validator() -> ToolValidator:
    """Get the global tool validator instance"""
    return validator
