"""
Tool Registry
============

Manages tools available to agents for execution.
"""

import json
import os
import shutil
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
import subprocess


class ToolPermission(Enum):
    """Permission levels for tools."""
    DENIED = "DENIED"
    READ_ONLY = "READ_ONLY"
    SAFE = "SAFE"
    PRODUCTIVITY = "PRODUCTIVITY"
    FILE_MANAGER = "FILE_MANAGER"
    DEVELOPER = "DEVELOPER"
    AUTONOMOUS = "AUTONOMOUS"


class RiskLevel(Enum):
    """Risk levels for tools."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass
class ToolDefinition:
    """Definition of a tool."""
    name: str
    description: str
    category: str
    permission_required: ToolPermission = ToolPermission.SAFE
    risk: RiskLevel = RiskLevel.LOW
    schema: Dict[str, Any] = field(default_factory=dict)
    executor: Optional[Callable] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'permission_required': self.permission_required.value,
            'risk': self.risk.value,
            'schema': self.schema
        }


class ToolRegistry:
    """
    Registry of all available tools for agents.
    
    Manages tool definitions, permissions, and execution.
    """
    
    def __init__(self):
        """Initialize the tool registry."""
        self._tools: Dict[str, ToolDefinition] = {}
        self._permissions: Dict[str, ToolPermission] = {}
        self._execution_log: List[Dict] = []
        
        # Register built-in tools
        self._register_builtin_tools()
    
    def _register_builtin_tools(self):
        """Register all built-in tools."""
        # Filesystem tools
        self.register_tool(ToolDefinition(
            name="filesystem.list",
            description="List files in a directory",
            category="filesystem",
            permission_required=ToolPermission.READ_ONLY,
            risk=RiskLevel.LOW,
            schema={
                'type': 'object',
                'properties': {
                    'path': {'type': 'string', 'description': 'Directory path'}
                },
                'required': ['path']
            },
            executor=self._execute_filesystem_list
        ))
        
        self.register_tool(ToolDefinition(
            name="filesystem.read",
            description="Read a file",
            category="filesystem",
            permission_required=ToolPermission.READ_ONLY,
            risk=RiskLevel.LOW,
            schema={
                'type': 'object',
                'properties': {
                    'path': {'type': 'string', 'description': 'File path'}
                },
                'required': ['path']
            },
            executor=self._execute_filesystem_read
        ))
        
        self.register_tool(ToolDefinition(
            name="filesystem.write",
            description="Write to a file",
            category="filesystem",
            permission_required=ToolPermission.PRODUCTIVITY,
            risk=RiskLevel.MEDIUM,
            schema={
                'type': 'object',
                'properties': {
                    'path': {'type': 'string', 'description': 'File path'},
                    'content': {'type': 'string', 'description': 'File content'}
                },
                'required': ['path', 'content']
            },
            executor=self._execute_filesystem_write
        ))
        
        self.register_tool(ToolDefinition(
            name="filesystem.copy",
            description="Copy a file",
            category="filesystem",
            permission_required=ToolPermission.FILE_MANAGER,
            risk=RiskLevel.MEDIUM,
            schema={
                'type': 'object',
                'properties': {
                    'source': {'type': 'string', 'description': 'Source path'},
                    'destination': {'type': 'string', 'description': 'Destination path'}
                },
                'required': ['source', 'destination']
            },
            executor=self._execute_filesystem_copy
        ))
        
        self.register_tool(ToolDefinition(
            name="filesystem.move",
            description="Move a file",
            category="filesystem",
            permission_required=ToolPermission.FILE_MANAGER,
            risk=RiskLevel.HIGH,
            schema={
                'type': 'object',
                'properties': {
                    'source': {'type': 'string', 'description': 'Source path'},
                    'destination': {'type': 'string', 'description': 'Destination path'}
                },
                'required': ['source', 'destination']
            },
            executor=self._execute_filesystem_move
        ))
        
        self.register_tool(ToolDefinition(
            name="filesystem.delete",
            description="Delete a file",
            category="filesystem",
            permission_required=ToolPermission.DEVELOPER,
            risk=RiskLevel.CRITICAL,
            schema={
                'type': 'object',
                'properties': {
                    'path': {'type': 'string', 'description': 'File path'}
                },
                'required': ['path']
            },
            executor=self._execute_filesystem_delete
        ))
        
        self.register_tool(ToolDefinition(
            name="filesystem.mkdir",
            description="Create a directory",
            category="filesystem",
            permission_required=ToolPermission.PRODUCTIVITY,
            risk=RiskLevel.LOW,
            schema={
                'type': 'object',
                'properties': {
                    'path': {'type': 'string', 'description': 'Directory path'}
                },
                'required': ['path']
            },
            executor=self._execute_filesystem_mkdir
        ))
        
        self.register_tool(ToolDefinition(
            name="filesystem.stat",
            description="Get file/directory statistics",
            category="filesystem",
            permission_required=ToolPermission.READ_ONLY,
            risk=RiskLevel.LOW,
            schema={
                'type': 'object',
                'properties': {
                    'path': {'type': 'string', 'description': 'Path to stat'}
                },
                'required': ['path']
            },
            executor=self._execute_filesystem_stat
        ))
        
        # Terminal tools
        self.register_tool(ToolDefinition(
            name="terminal.execute",
            description="Execute a terminal command",
            category="terminal",
            permission_required=ToolPermission.DEVELOPER,
            risk=RiskLevel.HIGH,
            schema={
                'type': 'object',
                'properties': {
                    'command': {'type': 'string', 'description': 'Command to execute'},
                    'timeout': {'type': 'integer', 'description': 'Timeout in seconds'}
                },
                'required': ['command']
            },
            executor=self._execute_terminal_command
        ))
        
        # SQLite tools
        self.register_tool(ToolDefinition(
            name="sqlite.query",
            description="Execute a SQLite query",
            category="database",
            permission_required=ToolPermission.SAFE,
            risk=RiskLevel.LOW,
            schema={
                'type': 'object',
                'properties': {
                    'database': {'type': 'string', 'description': 'Database path'},
                    'query': {'type': 'string', 'description': 'SQL query'}
                },
                'required': ['database', 'query']
            },
            executor=self._execute_sqlite_query
        ))
        
        # Memory tools
        self.register_tool(ToolDefinition(
            name="memory.search",
            description="Search memories",
            category="memory",
            permission_required=ToolPermission.READ_ONLY,
            risk=RiskLevel.LOW,
            schema={
                'type': 'object',
                'properties': {
                    'query': {'type': 'string', 'description': 'Search query'}
                },
                'required': ['query']
            }
        ))
        
        self.register_tool(ToolDefinition(
            name="memory.add",
            description="Add a memory",
            category="memory",
            permission_required=ToolPermission.SAFE,
            risk=RiskLevel.LOW,
            schema={
                'type': 'object',
                'properties': {
                    'content': {'type': 'string', 'description': 'Memory content'}
                },
                'required': ['content']
            }
        ))
        
        # Skill tools
        self.register_tool(ToolDefinition(
            name="skill.run",
            description="Run a skill",
            category="skills",
            permission_required=ToolPermission.SAFE,
            risk=RiskLevel.MEDIUM,
            schema={
                'type': 'object',
                'properties': {
                    'skill_name': {'type': 'string', 'description': 'Skill name'},
                    'arguments': {'type': 'object', 'description': 'Skill arguments'}
                },
                'required': ['skill_name']
            }
        ))
        
        # Calculator
        self.register_tool(ToolDefinition(
            name="calculator.evaluate",
            description="Evaluate a mathematical expression",
            category="utility",
            permission_required=ToolPermission.READ_ONLY,
            risk=RiskLevel.LOW,
            schema={
                'type': 'object',
                'properties': {
                    'expression': {'type': 'string', 'description': 'Mathematical expression'}
                },
                'required': ['expression']
            },
            executor=self._execute_calculator
        ))
        
        # Date/Time
        self.register_tool(ToolDefinition(
            name="datetime.now",
            description="Get current date and time",
            category="utility",
            permission_required=ToolPermission.READ_ONLY,
            risk=RiskLevel.LOW,
            schema={
                'type': 'object',
                'properties': {}
            },
            executor=self._execute_datetime_now
        ))
    
    def register_tool(self, tool: ToolDefinition):
        """Register a new tool."""
        self._tools[tool.name] = tool
    
    def unregister_tool(self, name: str):
        """Unregister a tool."""
        self._tools.pop(name, None)
    
    def get_tool(self, name: str) -> Optional[ToolDefinition]:
        """Get a tool by name."""
        return self._tools.get(name)
    
    def list_tools(self) -> List[ToolDefinition]:
        """List all registered tools."""
        return list(self._tools.values())
    
    def list_tools_by_category(self, category: str) -> List[ToolDefinition]:
        """List tools by category."""
        return [t for t in self._tools.values() if t.category == category]
    
    def execute(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a tool with arguments.
        
        Args:
            tool_name: Name of the tool to execute
            arguments: Arguments for the tool
            
        Returns:
            Dict: Execution result
        """
        tool = self._tools.get(tool_name)
        if not tool:
            return {'success': False, 'error': f'Tool {tool_name} not found'}
        
        # Validate arguments
        validation = self._validate_arguments(tool, arguments)
        if not validation['valid']:
            return {'success': False, 'error': validation['error']}
        
        # Check permissions
        if not self._check_permissions(tool):
            return {'success': False, 'error': f'Permission denied for {tool_name}'}
        
        # Execute
        try:
            if tool.executor:
                result = tool.executor(arguments)
            else:
                result = {'success': False, 'error': f'No executor for {tool_name}'}
            
            # Log execution
            self._log_execution(tool_name, arguments, result)
            
            return result
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _validate_arguments(self, tool: ToolDefinition, arguments: Dict) -> Dict:
        """Validate tool arguments against schema."""
        # Simple validation - check required fields
        schema = tool.schema
        required = schema.get('required', [])
        
        for field in required:
            if field not in arguments:
                return {'valid': False, 'error': f'Missing required field: {field}'}
        
        return {'valid': True}
    
    def _check_permissions(self, tool: ToolDefinition) -> bool:
        """Check if tool execution is permitted."""
        # For now, allow all tools
        return True
    
    def _log_execution(self, tool_name: str, arguments: Dict, result: Dict):
        """Log tool execution."""
        self._execution_log.append({
            'tool': tool_name,
            'arguments': arguments,
            'result': result,
            'timestamp': __import__('time').time()
        })
        # Limit log size
        if len(self._execution_log) > 1000:
            self._execution_log = self._execution_log[-500:]
    
    # Filesystem executors
    def _execute_filesystem_list(self, args: Dict) -> Dict:
        """List files in a directory."""
        path = args.get('path', '.')
        try:
            files = os.listdir(path)
            return {'success': True, 'files': files, 'count': len(files)}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _execute_filesystem_read(self, args: Dict) -> Dict:
        """Read a file."""
        path = args.get('path')
        try:
            with open(path, 'r') as f:
                content = f.read()
            return {'success': True, 'content': content, 'path': path}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _execute_filesystem_write(self, args: Dict) -> Dict:
        """Write to a file."""
        path = args.get('path')
        content = args.get('content', '')
        try:
            with open(path, 'w') as f:
                f.write(content)
            return {'success': True, 'path': path, 'bytes_written': len(content)}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _execute_filesystem_copy(self, args: Dict) -> Dict:
        """Copy a file."""
        source = args.get('source')
        destination = args.get('destination')
        try:
            shutil.copy2(source, destination)
            return {'success': True, 'source': source, 'destination': destination}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _execute_filesystem_move(self, args: Dict) -> Dict:
        """Move a file."""
        source = args.get('source')
        destination = args.get('destination')
        try:
            shutil.move(source, destination)
            return {'success': True, 'source': source, 'destination': destination}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _execute_filesystem_delete(self, args: Dict) -> Dict:
        """Delete a file."""
        path = args.get('path')
        try:
            os.remove(path)
            return {'success': True, 'path': path}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _execute_filesystem_mkdir(self, args: Dict) -> Dict:
        """Create a directory."""
        path = args.get('path')
        try:
            os.makedirs(path, exist_ok=True)
            return {'success': True, 'path': path}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _execute_filesystem_stat(self, args: Dict) -> Dict:
        """Get file/directory statistics."""
        path = args.get('path')
        try:
            stat = os.stat(path)
            return {
                'success': True,
                'path': path,
                'size': stat.st_size,
                'is_dir': os.path.isdir(path),
                'is_file': os.path.isfile(path),
                'modified': stat.st_mtime
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    # Terminal executor
    def _execute_terminal_command(self, args: Dict) -> Dict:
        """Execute a terminal command."""
        command = args.get('command')
        timeout = args.get('timeout', 30)
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return {
                'success': result.returncode == 0,
                'command': command,
                'returncode': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    # SQLite executor
    def _execute_sqlite_query(self, args: Dict) -> Dict:
        """Execute a SQLite query."""
        import sqlite3
        database = args.get('database')
        query = args.get('query')
        try:
            conn = sqlite3.connect(database)
            cursor = conn.cursor()
            cursor.execute(query)
            
            if query.strip().upper().startswith('SELECT'):
                results = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]
                conn.close()
                return {
                    'success': True,
                    'results': results,
                    'columns': columns,
                    'count': len(results)
                }
            else:
                conn.commit()
                conn.close()
                return {'success': True, 'rows_affected': cursor.rowcount}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    # Calculator executor
    def _execute_calculator(self, args: Dict) -> Dict:
        """Evaluate a mathematical expression."""
        expression = args.get('expression')
        try:
            result = eval(expression, {'__builtins__': None}, {})
            return {'success': True, 'expression': expression, 'result': result}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    # DateTime executor
    def _execute_datetime_now(self, args: Dict) -> Dict:
        """Get current date and time."""
        import time
        now = time.time()
        return {
            'success': True,
            'timestamp': now,
            'iso': __import__('datetime').datetime.fromtimestamp(now).isoformat()
        }


class ToolSelector:
    """Selects appropriate tools for tasks."""
    
    def __init__(self, registry: ToolRegistry):
        self.registry = registry
    
    def select_tool(self, task: Dict) -> Optional[str]:
        """
        Select the best tool for a task.
        
        Args:
            task: Task definition
            
        Returns:
            Optional[str]: Name of the selected tool, or None
        """
        # Simple selection based on task description
        description = task.get('description', '').lower()
        title = task.get('title', '').lower()
        
        # Check for filesystem operations
        if any(word in description or word in title for word in ['list', 'read', 'write', 'copy', 'move', 'delete', 'file', 'directory']):
            if 'list' in description or 'list' in title:
                return 'filesystem.list'
            elif 'read' in description or 'read' in title:
                return 'filesystem.read'
            elif 'write' in description or 'write' in title:
                return 'filesystem.write'
            elif 'copy' in description or 'copy' in title:
                return 'filesystem.copy'
            elif 'move' in description or 'move' in title:
                return 'filesystem.move'
            elif 'delete' in description or 'delete' in title:
                return 'filesystem.delete'
        
        # Check for other tool categories
        if 'search' in description or 'search' in title:
            return 'memory.search'
        if 'calculate' in description or 'math' in description:
            return 'calculator.evaluate'
        if 'time' in description or 'date' in description:
            return 'datetime.now'
        
        return None


class ToolExecutor:
    """Executes tools with validation and error handling."""
    
    def __init__(self, registry: ToolRegistry):
        self.registry = registry
    
    def execute(self, tool_name: str, arguments: Dict) -> Dict:
        """Execute a tool with full validation."""
        return self.registry.execute(tool_name, arguments)


class ToolPermissionManager:
    """Manages tool permissions for different profiles."""
    
    PERMISSION_PROFILES = {
        'READ_ONLY': [ToolPermission.READ_ONLY],
        'SAFE': [ToolPermission.READ_ONLY, ToolPermission.SAFE],
        'PRODUCTIVITY': [ToolPermission.READ_ONLY, ToolPermission.SAFE, ToolPermission.PRODUCTIVITY],
        'FILE_MANAGER': [ToolPermission.READ_ONLY, ToolPermission.SAFE, ToolPermission.PRODUCTIVITY, ToolPermission.FILE_MANAGER],
        'DEVELOPER': [ToolPermission.READ_ONLY, ToolPermission.SAFE, ToolPermission.PRODUCTIVITY, ToolPermission.FILE_MANAGER, ToolPermission.DEVELOPER],
        'AUTONOMOUS': [ToolPermission.READ_ONLY, ToolPermission.SAFE, ToolPermission.PRODUCTIVITY, ToolPermission.FILE_MANAGER, ToolPermission.DEVELOPER, ToolPermission.AUTONOMOUS],
        'CUSTOM': []
    }
    
    def __init__(self):
        self.profile_permissions: Dict[str, List[ToolPermission]] = {}
    
    def check_permission(self, profile: str, tool: ToolDefinition) -> bool:
        """Check if a profile has permission to use a tool."""
        permissions = self.PERMISSION_PROFILES.get(profile, [])
        return tool.permission_required in permissions
    
    def get_allowed_tools(self, profile: str, registry: ToolRegistry) -> List[str]:
        """Get list of tools allowed for a profile."""
        permissions = self.PERMISSION_PROFILES.get(profile, [])
        allowed = []
        for name, tool in registry._tools.items():
            if tool.permission_required in permissions:
                allowed.append(name)
        return allowed
