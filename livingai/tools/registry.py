"""
LivingAI Tool Registry
=====================

Central registry for all available tools in the LivingAI system.
"""

import logging
import inspect
from typing import Dict, Any, Optional, List, Callable, Type, Union
from dataclasses import dataclass, field
from enum import Enum
import importlib

from livingai.security.policy import RiskLevel


class ToolType(Enum):
    FILESYSTEM = "filesystem"
    TERMINAL = "terminal"
    DATABASE = "database"
    MEMORY = "memory"
    SKILLS = "skills"
    GOALS = "goals"
    TASKS = "tasks"
    CALCULATOR = "calculator"
    DATETIME = "datetime"
    TEXT_PROCESSOR = "text_processor"
    ARCHIVE_MANAGER = "archive_manager"
    WORKSPACE = "workspace"
    BACKUP = "backup"
    LOGS = "logs"
    TERMUX_API = "termux_api"
    CUSTOM = "custom"


@dataclass
class ToolInfo:
    name: str
    tool_type: ToolType
    description: str = ""
    methods: List[str] = field(default_factory=list)
    risk: RiskLevel = RiskLevel.MEDIUM
    permissions: List[str] = field(default_factory=list)
    category: str = "general"
    version: str = "1.0.0"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'tool_type': self.tool_type.value,
            'description': self.description,
            'methods': self.methods,
            'risk': self.risk.value,
            'permissions': self.permissions,
            'category': self.category,
            'version': self.version
        }


class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, Any] = {}
        self._tool_info: Dict[str, ToolInfo] = {}
        self._categories: Dict[str, List[str]] = {}
        self._loaded_modules: Dict[str, bool] = {}
        self.logger = logging.getLogger(__name__)
        self._register_builtin_tools()
    
    def _register_builtin_tools(self) -> None:
        from livingai.security.policy import RiskLevel
        tool_types = [
            ('filesystem', 'Filesystem operations', ['read', 'write', 'delete', 'list', 'exists', 'stat', 'is_file', 'is_dir'], RiskLevel.MEDIUM, ['filesystem.read', 'filesystem.write', 'filesystem.delete'], 'filesystem'),
            ('file_inspector', 'Inspect file content and metadata', ['inspect', 'get_size', 'get_type', 'get_encoding'], RiskLevel.LOW, ['filesystem.read'], 'filesystem'),
            ('terminal', 'Terminal command execution', ['execute', 'run', 'shell'], RiskLevel.CRITICAL, ['terminal.execute'], 'system'),
            ('sqlite', 'SQLite database operations', ['query', 'execute', 'read', 'write', 'select', 'insert', 'update', 'delete'], RiskLevel.MEDIUM, ['database.read', 'database.write'], 'database'),
            ('memory', 'Memory management operations', ['add', 'search', 'get', 'update', 'delete', 'list'], RiskLevel.LOW, ['memory.read', 'memory.write'], 'memory'),
            ('skills', 'Skill management operations', ['load', 'unload', 'list', 'execute', 'validate'], RiskLevel.LOW, ['skills.read', 'skills.execute'], 'skills'),
            ('goals', 'Goal management operations', ['create', 'read', 'update', 'delete', 'list', 'search'], RiskLevel.LOW, ['goals.read', 'goals.write'], 'goals'),
            ('tasks', 'Task management operations', ['create', 'read', 'update', 'delete', 'list', 'search', 'execute'], RiskLevel.LOW, ['tasks.read', 'tasks.write', 'tasks.execute'], 'tasks'),
            ('calculator', 'Mathematical calculations', ['calculate', 'add', 'subtract', 'multiply', 'divide', 'power', 'sqrt'], RiskLevel.LOW, [], 'utility'),
            ('datetime', 'Date and time operations', ['now', 'format', 'parse', 'add', 'subtract', 'difference'], RiskLevel.LOW, [], 'utility'),
            ('text_processor', 'Text processing operations', ['extract', 'replace', 'split', 'join', 'count', 'find', 'contains'], RiskLevel.LOW, [], 'utility'),
            ('archive_manager', 'Archive file management', ['create', 'extract', 'list', 'delete'], RiskLevel.MEDIUM, ['filesystem.read', 'filesystem.write'], 'filesystem'),
            ('workspace', 'Workspace management', ['create', 'delete', 'list', 'switch', 'current'], RiskLevel.LOW, ['filesystem.read'], 'workspace'),
            ('backup', 'Backup and restore operations', ['create', 'restore', 'list', 'delete', 'verify'], RiskLevel.MEDIUM, ['filesystem.read', 'filesystem.write'], 'system'),
            ('logs', 'Log management operations', ['read', 'search', 'filter', 'export', 'delete'], RiskLevel.LOW, ['logs.read'], 'system'),
            ('termux_api', 'Termux API integration', ['battery', 'notification', 'toast', 'clipboard', 'vibration', 'location', 'device_info'], RiskLevel.LOW, ['termux.api'], 'termux')
        ]
        for name, desc, methods, risk, perms, category in tool_types:
            self.register_tool_type(name, name.upper(), desc, methods, risk, perms, category)
    
    def register_tool_type(self, name, tool_type, description="", methods=None, risk=RiskLevel.MEDIUM, permissions=None, category="general", version="1.0.0") -> 'ToolInfo':
        info = ToolInfo(name=name, tool_type=tool_type, description=description, methods=methods or [], risk=risk, permissions=permissions or [], category=category, version=version)
        self._tool_info[name] = info
        if category not in self._categories:
            self._categories[category] = []
        if name not in self._categories[category]:
            self._categories[category].append(name)
        return info
    
    def register_tool_instance(self, name: str, tool_instance: Any) -> None:
        self._tools[name] = tool_instance
    
    def get_tool(self, name: str) -> Optional[Any]:
        if name in self._tools:
            return self._tools[name]
        if not self._loaded_modules.get(name, False):
            self._load_tool_module(name)
            self._loaded_modules[name] = True
        return self._tools.get(name)
    
    def _load_tool_module(self, name: str) -> bool:
        try:
            module = importlib.import_module(f"livingai.tools.{name}")
            class_name = name.title().replace('_', '')
            tool_class = getattr(module, class_name, None)
            if tool_class:
                self._tools[name] = tool_class()
                return True
        except Exception:
            pass
        return False
    
    def list_tools(self, tool_type=None, category=None) -> List[str]:
        tools = list(self._tool_info.keys())
        if tool_type:
            tools = [t for t in tools if self._tool_info[t].tool_type == tool_type]
        if category:
            tools = [t for t in tools if self._tool_info[t].category == category]
        return tools
    
    def get_tool_info(self, name: str) -> Optional[ToolInfo]:
        return self._tool_info.get(name)
    
    def has_tool(self, name: str) -> bool:
        return name in self._tool_info or name in self._tools
