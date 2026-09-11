# LivingAI Skill Validator
# ========================
# This module validates skills for safety and correctness.

import logging
import re
from typing import Dict, Any, Optional, List, Tuple

# Local imports
from ..config import ConfigManager
from ..security.audit import AuditLogger


class SkillValidator:
    """
    Validates skills for safety and correctness.
    
    Responsibilities:
    - Validate skill names
    - Validate skill code
    - Check for unsafe operations
    - Validate permissions
    - Validate input/output schemas
    """
    
    # Patterns that indicate potentially unsafe code
    UNSAFE_PATTERNS = [
        # File system operations
        r'\bopen\s*\(',
        r'\bfile\s*\(',
        r'\bshutil\.',
        r'\bos\.',
        r'\bsys\.',
        r'\bsubprocess\.',
        r'\bexec\s*\(',
        r'\beval\s*\(',
        r'\b__import__\s*\(',
        
        # Network operations
        r'\bsocket\.',
        r'\brequests\.',
        r'\burllib\.',
        r'\bhttp\.',
        
        # System operations
        r'\bos\.system\s*\(',
        r'\bos\.popen\s*\(',
        r'\bos\.exec',
        r'\bexit\s*\(',
        r'\bquit\s*\(',
        
        # Dangerous built-ins
        r'\bcompile\s*\(',
        r'\bglobals\s*\(',
        r'\blocals\s*\(',
        r'\bvars\s*\(',
        r'\bdir\s*\(',
        
        # Shell commands
        r'\brm\s+',
        r'\bdd\s+',
        r'\bformat\s+',
        r'\bchmod\s+',
        r'\bchown\s+',
        
        # Python-specific dangerous operations
        r'\b__builtins__\b',
        r'\b__code__\b',
        r'\b__class__\b',
        r'\b__bases__\b',
        r'\b__subclasses__\s*\(',
        
        # Import statements that could be dangerous
        r'\bimport\s+ctypes\b',
        r'\bimport\s+multiprocessing\b',
        r'\bimport\s+threading\b',
        r'\bimport\s+socket\b',
        r'\bimport\s+subprocess\b',
    ]
    
    # Allowed modules for skills
    ALLOWED_MODULES = [
        "math",
        "random",
        "string",
        "re",
        "json",
        "datetime",
        "collections",
        "itertools",
        "functools",
        "operator",
        "copy",
        "decimal",
        "fractions",
        "numbers",
        "statistics",
        "textwrap",
        "unicodedata",
        "stringprep",
    ]
    
    # Blocked modules
    BLOCKED_MODULES = [
        "os",
        "sys",
        "subprocess",
        "shutil",
        "socket",
        "http",
        "urllib",
        "ftplib",
        "smtplib",
        "poplib",
        "imaplib",
        "nntplib",
        "telnetlib",
        "ssl",
        "ctypes",
        "multiprocessing",
        "threading",
        "concurrent",
        "pickle",
        "shelve",
        "marshal",
        "dbm",
        "sqlite3",
        "code",
        "codeop",
        "importlib",
        "runpy",
        "builtins",
        "__builtin__",
    ]
    
    def __init__(
        self,
        config: ConfigManager,
        audit_logger: AuditLogger
    ):
        """
        Initialize the SkillValidator.
        
        Args:
            config: Configuration manager.
            audit_logger: Audit logger for tracking actions.
        """
        self.config = config
        self.audit_logger = audit_logger
        
        logging.info("SkillValidator initialized")
    
    def validate(self, skill_data: Dict[str, Any]) -> bool:
        """
        Validate a skill.
        
        Args:
            skill_data: Skill data to validate.
            
        Returns:
            bool: True if valid, False otherwise.
        """
        self.audit_logger.log("SKILL_VALIDATE_START", f"Validating skill {skill_data.get('name', 'unknown')}")
        
        try:
            # Validate name
            if not self._validate_name(skill_data.get("name", "")):
                return False
            
            # Validate description
            if not self._validate_description(skill_data.get("description", "")):
                return False
            
            # Validate code
            code = skill_data.get("code", "")
            if code and not self._validate_code(code):
                return False
            
            # Validate permissions
            if not self._validate_permissions(skill_data):
                return False
            
            # Validate validation rules
            if "validation" in skill_data and not self._validate_validation(skill_data["validation"]):
                return False
            
            # Validate examples
            if "examples" in skill_data and not self._validate_examples(skill_data["examples"]):
                return False
            
            self.audit_logger.log("SKILL_VALIDATE_SUCCESS", f"Skill {skill_data.get('name', 'unknown')} validated")
            return True
            
        except Exception as e:
            self.audit_logger.log("SKILL_VALIDATE_FAIL", str(e))
            logging.error(f"Skill validation failed: {e}")
            return False
    
    def _validate_name(self, name: str) -> bool:
        """
        Validate a skill name.
        
        Args:
            name: Skill name to validate.
            
        Returns:
            bool: True if valid, False otherwise.
        """
        if not name:
            return False
        
        # Check length
        if len(name) > 50:
            return False
        
        # Check for invalid characters
        invalid_chars = ["/", "\\", ":", "*", "?", "\"", "<", ">", "|"]
        if any(char in name for char in invalid_chars):
            return False
        
        # Check if name is a path
        if ".." in name or name.startswith("/") or name.startswith("\\"):
            return False
        
        return True
    
    def _validate_description(self, description: str) -> bool:
        """
        Validate a skill description.
        
        Args:
            description: Skill description to validate.
            
        Returns:
            bool: True if valid, False otherwise.
        """
        # Description is optional, but if present, check length
        if description and len(description) > 500:
            return False
        
        return True
    
    def _validate_code(self, code: str) -> bool:
        """
        Validate skill code for safety.
        
        Args:
            code: Skill code to validate.
            
        Returns:
            bool: True if safe, False otherwise.
        """
        # Check for unsafe patterns
        for pattern in self.UNSAFE_PATTERNS:
            if re.search(pattern, code, re.IGNORECASE):
                logging.warning(f"Unsafe pattern detected: {pattern}")
                return False
        
        # Check for blocked imports
        for module in self.BLOCKED_MODULES:
            if f"import {module}" in code or f"from {module} import" in code:
                logging.warning(f"Blocked module detected: {module}")
                return False
        
        # Check for allowed modules only (if strict mode is enabled)
        if self.config.get("skills.strict_mode", False):
            for module in self.ALLOWED_MODULES:
                if f"import {module}" in code or f"from {module} import" in code:
                    continue
                # Check for any other imports
                import_pattern = r'\bimport\s+([a-zA-Z_][a-zA-Z0-9_]*)'
                matches = re.findall(import_pattern, code)
                for match in matches:
                    if match not in self.ALLOWED_MODULES:
                        logging.warning(f"Non-allowed module detected: {match}")
                        return False
        
        return True
    
    def _validate_permissions(self, skill_data: Dict[str, Any]) -> bool:
        """
        Validate skill permissions.
        
        Args:
            skill_data: Skill data to validate.
            
        Returns:
            bool: True if permissions are valid, False otherwise.
        """
        # Check if sandboxed
        if not skill_data.get("sandboxed", True):
            # If not sandboxed, must have explicit permissions
            if skill_data.get("allow_network", False):
                logging.warning("Non-sandboxed skill with network access")
                return False
            if skill_data.get("allow_filesystem", False):
                logging.warning("Non-sandboxed skill with filesystem access")
                return False
            if skill_data.get("allow_shell", False):
                logging.warning("Non-sandboxed skill with shell access")
                return False
        
        return True
    
    def _validate_validation(self, validation: Dict[str, Any]) -> bool:
        """
        Validate skill validation rules.
        
        Args:
            validation: Validation rules to validate.
            
        Returns:
            bool: True if valid, False otherwise.
        """
        # Basic validation
        if not isinstance(validation, dict):
            return False
        
        # Check for valid keys
        valid_keys = ["input_schema", "output_schema", "required_fields", "max_length"]
        for key in validation.keys():
            if key not in valid_keys:
                return False
        
        return True
    
    def _validate_examples(self, examples: List[Dict[str, Any]]) -> bool:
        """
        Validate skill examples.
        
        Args:
            examples: Examples to validate.
            
        Returns:
            bool: True if valid, False otherwise.
        """
        if not isinstance(examples, list):
            return False
        
        for example in examples:
            if not isinstance(example, dict):
                return False
            
            # Check for required keys
            if "input" not in example or "output" not in example:
                return False
        
        return True
    
    def check_unsafe_patterns(self, code: str) -> List[str]:
        """
        Check code for unsafe patterns and return any found.
        
        Args:
            code: Code to check.
            
        Returns:
            List[str]: List of unsafe patterns found.
        """
        unsafe_patterns = []
        
        for pattern in self.UNSAFE_PATTERNS:
            if re.search(pattern, code, re.IGNORECASE):
                unsafe_patterns.append(pattern)
        
        return unsafe_patterns
    
    def check_blocked_modules(self, code: str) -> List[str]:
        """
        Check code for blocked module imports and return any found.
        
        Args:
            code: Code to check.
            
        Returns:
            List[str]: List of blocked modules found.
        """
        blocked_modules = []
        
        for module in self.BLOCKED_MODULES:
            if f"import {module}" in code or f"from {module} import" in code:
                blocked_modules.append(module)
        
        return blocked_modules
    
    def get_validation_report(self, skill_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a detailed validation report for a skill.
        
        Args:
            skill_data: Skill data to validate.
            
        Returns:
            Dict[str, Any]: Validation report.
        """
        report = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "info": [],
        }
        
        # Validate name
        name = skill_data.get("name", "")
        if not self._validate_name(name):
            report["valid"] = False
            report["errors"].append("Invalid skill name")
        
        # Validate description
        description = skill_data.get("description", "")
        if not self._validate_description(description):
            report["valid"] = False
            report["errors"].append("Invalid skill description")
        
        # Validate code
        code = skill_data.get("code", "")
        if code:
            unsafe_patterns = self.check_unsafe_patterns(code)
            if unsafe_patterns:
                report["valid"] = False
                report["errors"].append(f"Unsafe patterns detected: {unsafe_patterns}")
            
            blocked_modules = self.check_blocked_modules(code)
            if blocked_modules:
                report["valid"] = False
                report["errors"].append(f"Blocked modules detected: {blocked_modules}")
        
        # Validate permissions
        if not self._validate_permissions(skill_data):
            report["valid"] = False
            report["errors"].append("Invalid permissions")
        
        # Validate validation rules
        if "validation" in skill_data:
            if not self._validate_validation(skill_data["validation"]):
                report["valid"] = False
                report["errors"].append("Invalid validation rules")
        
        # Validate examples
        if "examples" in skill_data:
            if not self._validate_examples(skill_data["examples"]):
                report["valid"] = False
                report["errors"].append("Invalid examples")
        
        return report
