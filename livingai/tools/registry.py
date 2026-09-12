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
        self.register_tool_type(
            name='filesystem',
            tool_type=ToolType.FILESYSTEM,
            description='Filesystem operations (read, write, delete, list)',
            methods=['read', 'write', 'delete', 'list', 'exists', 'stat', 'is_file', 'is_dir'],
            risk=RiskLevel.MEDIUM,
            permissions=['filesystem.read', 'filesystem.write', 'filesystem.delete'],
            category='filesystem'
        )
        self.register_tool_type(
            name='file_inspector',
            tool_type=ToolType.FILESYSTEM,
            description='Inspect file content and metadata',
            methods=['inspect', 'get_size', 'get_type', 'get_encoding'],
            risk=RiskLevel.LOW,
            permissions=['filesystem.read'],
            category='filesystem'
        )
        self.register_tool_type(
            name='terminal',
            tool_type=ToolType.TERMINAL,
            description='Terminal command execution',
            methods=['execute', 'run', 'shell'],
            risk=RiskLevel.CRITICAL,
            permissions=['terminal.execute'],
            category='system'
        )
        self.register_tool_type(
            name='sqlite',
            tool_type=ToolType.DATABASE,
            description='SQLite database operations',
            methods=['query', 'execute', 'read', 'write', 'select', 'insert', 'update', 'delete'],
            risk=RiskLevel.MEDIUM,
            permissions=['database.read', 'database.write'],
            category='database'
        )
        self.register_tool_type(
            name='memory',
            tool_type=ToolType.MEMORY,
            description='Memory management operations',
            methods=['add', 'search', 'get', 'update', 'delete', 'list'],
            risk=RiskLevel.LOW,
            permissions=['memory.read', 'memory.write'],
            category='memory'
        )
        self.register_tool_type(
            name='skills',
            tool_type=ToolType.SKILLS,
            description='Skill management operations',
            methods=['load', 'unload', 'list', 'execute', 'validate'],
            risk=RiskLevel.LOW,
            permissions=['skills.read', 'skills.execute'],
            category='skills'
        )
        self.register_tool_type(
            name='goals',
            tool_type=ToolType.GOALS,
            description='Goal management operations',
            methods=['create', 'read', 'update', 'delete', 'list', 'search'],
            risk=RiskLevel.LOW,
            permissions=['goals.read', 'goals.write'],
            category='goals'
        )
        self.register_tool_type(
            name='tasks',
            tool_type=ToolType.TASKS,
            description='Task management operations',
            methods=['create', 'read', 'update', 'delete', 'list', 'search', 'execute'],
            risk=RiskLevel.LOW,
            permissions=['tasks.read', 'tasks.write', 'tasks.execute'],
            category='tasks'
        )
        self.register_tool_type(
            name='calculator',
            tool_type=ToolType.CALCULATOR,
            description='Mathematical calculations',
            methods=['calculate', 'add', 'subtract', 'multiply', 'divide', 'power', 'sqrt'],
            risk=RiskLevel.LOW,
            permissions=[],
            category='utility'
        )
        self.register_tool_type(
            name='datetime',
            tool_type=ToolType.DATETIME,
            description='Date and time operations',
            methods=['now', 'format', 'parse', 'add', 'subtract', 'difference'],
            risk=RiskLevel.LOW,
            permissions=[],
            category='utility'
        )
        self.register_tool_type(
            name='text_processor',
            tool_type=ToolType.TEXT_PROCESSOR,
            description='Text processing operations',
            methods=['extract', 'replace', 'split', 'join', 'count', 'find', 'contains'],
            risk=RiskLevel.LOW,
            permissions=[],
            category='utility'
        )
        self.register_tool_type(
            name='archive_manager',
            tool_type=ToolType.ARCHIVE_MANAGER,
            description='Archive file management',
            methods=['create', 'extract', 'list', 'delete'],
            risk=RiskLevel.MEDIUM,
            permissions=['filesystem.read', 'filesystem.write'],
            category='filesystem'
        )
        self.register_tool_type(
            name='workspace',
            tool_type=ToolType.WORKSPACE,
            description='Workspace management',
            methods=['create', 'delete', 'list', 'switch', 'current'],
            risk=RiskLevel.LOW,
            permissions=['filesystem.read'],
            category='workspace'
        )
        self.register_tool_type(
            name='backup',
            tool_type=ToolType.BACKUP,
            description='Backup and restore operations',
            methods=['create', 'restore', 'list', 'delete', 'verify'],
            risk=RiskLevel.MEDIUM,
            permissions=['filesystem.read', 'filesystem.write'],
            category='system'
        )
        self.register_tool_type(
            name='logs',
            tool_type=ToolType.LOGS,
            description='Log management operations',
            methods=['read', 'search', 'filter', 'export', 'delete'],
            risk=RiskLevel.LOW,
            permissions=['logs.read'],
            category='system'
        )
        self.register_tool_type(
            name='termux_api',
            tool_type=ToolType.TERMUX_API,
            description='Termux API integration',
            methods=['battery', 'notification', 'toast', 'clipboard', 'vibration', 'location', 'device_info'],
            risk=RiskLevel.LOW,
            permissions=['termux.api'],
            category='termux'
        )
    
    def register_tool_type(
        self,
        name: str,
        tool_type: ToolType,
        description: str = "",
        methods: List[str] = None,
        risk: RiskLevel = RiskLevel.MEDIUM,
        permissions: List[str] = None,
        category: str = "general",
        version: str = "1.0.0"
    ) -> ToolInfo:
        info = ToolInfo(
            name=name,
            tool_type=tool_type,
            description=description,
            methods=methods or [],
            risk=risk,
            permissions=permissions or [],
            category=category,
            version=version
        )
        self._tool_info[name] = info
        if category not in self._categories:
            self._categories[category] = []
        if name not in self._categories[category]:
            self._categories[category].append(name)
        self.logger.info(f"Registered tool type: {name}")
        return info
    
    def register_tool_instance(self, name: str, tool_instance: Any) -> None:
        self._tools[name] = tool_instance
        self.logger.info(f"Registered tool instance: {name}")
    
    def get_tool(self, name: str) -> Optional[Any]:
        if name in self._tools:
            return self._tools[name]
        if not self._loaded_modules.get(name, False):
            self._load_tool_module(name)
            self._loaded_modules[name] = True
        return self._tools.get(name)
    
    def _load_tool_module(self, name: str) -> bool:
        try:
            module_name = f"livingai.tools.{name}"
            module = importlib.import_module(module_name)
            class_name = name.title().replace('_', '')
            tool_class = getattr(module, class_name, None)
            if tool_class:
                tool_instance = tool_class()
                self._tools[name] = tool_instance
                self.logger.info(f"Loaded tool module: {module_name}")
                return True
        except ImportError as e:
            self.logger.warning(f"Could not import tool module {name}: {e}")
        except Exception as e:
            self.logger.error(f"Error loading tool {name}: {e}")
        return False
    
    def get_tool_info(self, name: str) -> Optional[ToolInfo]:
        return self._tool_info.get(name)
    
    def list_tools(self, tool_type: ToolType = None, category: str = None) -> List[str]:
        tools = list(self._tool_info.keys())
        if tool_type:
            tools = [t for t in tools if self._tool_info[t].tool_type == tool_type]
        if category:
            tools = [t for t in tools if self._tool_info[t].category == category]
        return tools
    
    def list_tools_by_category(self, category: str) -> List[str]:
        return self._categories.get(category, [])
    
    def list_categories(self) -> List[str]:
        return list(self._categories.keys())
    
    def list_tool_types(self) -> List[ToolType]:
        return list(ToolType)
    
    def has_tool(self, name: str) -> bool:
        return name in self._tool_info or name in self._tools
    
    def get_tool_methods(self, name: str) -> List[str]:
        info = self._tool_info.get(name)
        if info:
            return info.methods
        tool = self._tools.get(name)
        if tool:
            return [m for m in dir(tool) if not m.startswith('_') and callable(getattr(tool, m))]
        return []
    
    def search_tools(self, query: str) -> List[Dict[str, Any]]:
        query = query.lower()
        results = []
        for name, info in self._tool_info.items():
            if query in name.lower() or query in info.description.lower():
                results.append(info.to_dict())
        return results
    
    def get_tool_risk(self, name: str) -> RiskLevel:
        info = self._tool_info.get(name)
        if info:
            return info.risk
        return RiskLevel.MEDIUM
    
    def reload_tools(self) -> None:
        self._tools.clear()
        self._loaded_modules.clear()
        self._register_builtin_tools()
        self.logger.info("Tools reloaded")
    
    def get_tool_count(self) -> int:
        return len(self._tool_info)
