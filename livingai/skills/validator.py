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
    """
    
    UNSAFE_PATTERNS = [
        r'\bopen\s*\(', r'\bfile\s*\(', r'\bshutil\.', r'\bos\.', r'\bsys\.',
        r'\bsubprocess\.', r'\bexec\s*\(', r'\beval\s*\(', r'\b__import__\s*\(',
        r'\bsocket\.', r'\brequests\.', r'\burllib\.', r'\bhttp\.',
        r'\bos\.system\s*\(', r'\bos\.popen\s*\(', r'\bos\.exec', r'\bexit\s*\(', r'\bquit\s*\(',
        r'\bcompile\s*\(', r'\bglobals\s*\(', r'\blocals\s*\(', r'\bvars\s*\(', r'\bdir\s*\(',
        r'\brm\s+', r'\bdd\s+', r'\bformat\s+', r'\bchmod\s+', r'\bchown\s+',
        r'\b__builtins__\b', r'\b__code__\b', r'\b__class__\b', r'\b__bases__\b', r'\b__subclasses__\s*\(',
        r'\bimport\s+ctypes\b', r'\bimport\s+multiprocessing\b', r'\bimport\s+threading\b', r'\bimport\s+socket\b', r'\bimport\s+subprocess\b',
    ]
    
    ALLOWED_MODULES = [
        "math", "random", "string", "re", "json", "datetime",
        "collections", "itertools", "functools", "operator", "copy",
        "decimal", "fractions", "numbers", "statistics", "textwrap",
        "unicodedata", "stringprep",
    ]
    
    BLOCKED_MODULES = [
        "os", "sys", "subprocess", "shutil", "socket", "http", "urllib",
        "ftplib", "smtplib", "poplib", "imaplib", "nntplib", "telnetlib", "ssl",
        "ctypes", "multiprocessing", "threading", "concurrent", "pickle",
        "shelve", "marshal", "dbm", "sqlite3", "code", "codeop", "importlib",
        "runpy", "builtins", "__builtin__",
    ]
    
    def __init__(self, config: ConfigManager, audit_logger: AuditLogger):
        self.config = config
        self.audit_logger = audit_logger
        logging.info("SkillValidator initialized")

    def validate_code(self, code: str) -> Tuple[bool, List[str]]:
        errors = []
        unsafe = self.check_unsafe_patterns(code)
        if unsafe:
            errors.append(f"Unsafe patterns: {unsafe}")
        blocked = self.check_blocked_modules(code)
        if blocked:
            errors.append(f"Blocked modules: {blocked}")
        return len(errors) == 0, errors

    def validate(self, skill_data: Dict[str, Any]) -> bool:
        self.audit_logger.log("SKILL_VALIDATE_START", f"Validating skill {skill_data.get('name', 'unknown')}")
        try:
            name = skill_data.get("name", "")
            if not name or len(name) > 50:
                return False
            code = skill_data.get("code", "")
            if code:
                valid, _ = self.validate_code(code)
                if not valid:
                    return False
            return True
        except Exception as e:
            logging.error(f"Skill validation failed: {e}")
            return False

    def check_unsafe_patterns(self, code: str) -> List[str]:
        unsafe_patterns = []
        for pattern in self.UNSAFE_PATTERNS:
            if re.search(pattern, code, re.IGNORECASE):
                unsafe_patterns.append(pattern)
        return unsafe_patterns
    
    def check_blocked_modules(self, code: str) -> List[str]:
        blocked_modules = []
        for module in self.BLOCKED_MODULES:
            if f"import {module}" in code or f"from {module} import" in code:
                blocked_modules.append(module)
        return blocked_modules
