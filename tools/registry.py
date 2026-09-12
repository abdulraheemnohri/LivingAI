"""
Tool Registry Module

Manages the registration and discovery of AI tools in the LivingAI system.
This module provides a centralized registry for all available tools.

Author: Abdulraheem Nohari
"""

from typing import Dict, List, Optional, Type, Any
from dataclasses import dataclass, field
from enum import Enum
import importlib
import inspect
import logging

logger = logging.getLogger(__name__)


class ToolCategory(Enum):
    """Categories for AI tools"""
    CODE = "code"
    ANALYSIS = "analysis"
    CREATIVE = "creative"
    DATA = "data"
    SYSTEM = "system"
    UTILITY = "utility"
    NETWORK = "network"
    FILE = "file"
    DATABASE = "database"
    AI = "ai"


@dataclass
class ToolInfo:
    """Information about a registered tool"""
    name: str
    description: str
    category: ToolCategory
    tool_class: Optional[Type] = None
    version: str = "1.0.0"
    author: str = "LivingAI"
    tags: List[str] = field(default_factory=list)
    is_async: bool = False
    is_enabled: bool = True
    requires_permissions: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'name': self.name,
            'description': self.description,
            'category': self.category.value,
            'version': self.version,
            'author': self.author,
            'tags': self.tags,
            'is_async': self.is_async,
            'is_enabled': self.is_enabled,
            'requires_permissions': self.requires_permissions,
        }


class ToolRegistry:
    """
    Central registry for AI tools.
    
    This class manages the registration, discovery, and retrieval of tools
    in the LivingAI system. It supports lazy loading and dynamic registration.
    """
    
    _instance: Optional['ToolRegistry'] = None
    
    def __new__(cls) -> 'ToolRegistry':
        """Singleton pattern"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize the registry"""
        if self._initialized:
            return
        
        self._tools: Dict[str, ToolInfo] = {}
        self._categories: Dict[ToolCategory, List[str]] = {cat: [] for cat in ToolCategory}
        self._initialized = True
        
        # Register built-in tools
        self._register_builtin_tools()
    
    def _register_builtin_tools(self):
        """Register built-in tools"""
        # These will be registered dynamically from the tools package
        pass
    
    def register(self, 
                 name: str, 
                 description: str, 
                 category: ToolCategory,
                 tool_class: Optional[Type] = None,
                 version: str = "1.0.0",
                 author: str = "LivingAI",
                 tags: Optional[List[str]] = None,
                 is_async: bool = False,
                 is_enabled: bool = True,
                 requires_permissions: Optional[List[str]] = None) -> ToolInfo:
        """
        Register a new tool.
        
        Args:
            name: Unique name of the tool
            description: Description of what the tool does
            category: Category of the tool
            tool_class: Optional class implementing the tool
            version: Version of the tool
            author: Author of the tool
            tags: List of tags for the tool
            is_async: Whether the tool runs asynchronously
            is_enabled: Whether the tool is enabled
            requires_permissions: List of required permissions
            
        Returns:
            ToolInfo object for the registered tool
        """
        if name in self._tools:
            logger.warning(f"Tool '{name}' is already registered. Overwriting.")
        
        tool_info = ToolInfo(
            name=name,
            description=description,
            category=category,
            tool_class=tool_class,
            version=version,
            author=author,
            tags=tags or [],
            is_async=is_async,
            is_enabled=is_enabled,
            requires_permissions=requires_permissions or [],
        )
        
        self._tools[name] = tool_info
        self._categories[category].append(name)
        
        logger.info(f"Registered tool: {name} (category: {category.value})")
        
        return tool_info
    
    def get(self, name: str) -> Optional[ToolInfo]:
        """
        Get a registered tool by name.
        
        Args:
            name: Name of the tool to retrieve
            
        Returns:
            ToolInfo object or None if not found
        """
        return self._tools.get(name)
    
    def get_all(self) -> List[ToolInfo]:
        """
        Get all registered tools.
        
        Returns:
            List of all ToolInfo objects
        """
        return list(self._tools.values())
    
    def get_by_category(self, category: ToolCategory) -> List[ToolInfo]:
        """
        Get all tools in a specific category.
        
        Args:
            category: Category to filter by
            
        Returns:
            List of ToolInfo objects in the category
        """
        return [self._tools[name] for name in self._categories.get(category, []) 
                if name in self._tools]
    
    def get_enabled(self) -> List[ToolInfo]:
        """
        Get all enabled tools.
        
        Returns:
            List of enabled ToolInfo objects
        """
        return [tool for tool in self._tools.values() if tool.is_enabled]
    
    def unregister(self, name: str) -> bool:
        """
        Unregister a tool.
        
        Args:
            name: Name of the tool to unregister
            
        Returns:
            True if tool was unregistered, False if not found
        """
        if name not in self._tools:
            return False
        
        tool_info = self._tools[name]
        self._categories[tool_info.category].remove(name)
        del self._tools[name]
        
        logger.info(f"Unregistered tool: {name}")
        return True
    
    def has_tool(self, name: str) -> bool:
        """
        Check if a tool is registered.
        
        Args:
            name: Name of the tool to check
            
        Returns:
            True if tool is registered
        """
        return name in self._tools
    
    def search(self, query: str) -> List[ToolInfo]:
        """
        Search for tools by name or description.
        
        Args:
            query: Search query
            
        Returns:
            List of matching ToolInfo objects
        """
        query_lower = query.lower()
        return [tool for tool in self._tools.values()
                if query_lower in tool.name.lower() or 
                   query_lower in tool.description.lower() or
                   any(query_lower in tag.lower() for tag in tool.tags)]
    
    def clear(self):
        """Clear all registered tools"""
        self._tools.clear()
        for category in self._categories:
            self._categories[category].clear()
        logger.info("Cleared all registered tools")
    
    @property
    def count(self) -> int:
        """Get the number of registered tools"""
        return len(self._tools)
    
    @property
    def categories(self) -> List[ToolCategory]:
        """Get all available categories"""
        return list(self._categories.keys())


# Global registry instance
registry = ToolRegistry()


def get_registry() -> ToolRegistry:
    """Get the global tool registry instance"""
    return registry
