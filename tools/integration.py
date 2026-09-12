"""
Tool Integration Module

Provides integration capabilities for AI tools with external systems,
APIs, databases, and other services.

Author: Abdulraheem Nohari
"""

import asyncio
import json
import logging
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple, Type, Union
from enum import Enum
from contextlib import contextmanager, asynccontextmanager

from .registry import ToolRegistry, ToolInfo
from .sandbox import ToolSandbox, ExecutionResult
from .validator import ToolValidator, ValidationResult

logger = logging.getLogger(__name__)


class IntegrationError(Exception):
    """Base exception for integration errors"""
    pass


class ConnectionError(IntegrationError):
    """Raised when connection fails"""
    pass


class AuthenticationError(IntegrationError):
    """Raised when authentication fails"""
    pass


class ConfigurationError(IntegrationError):
    """Raised when configuration is invalid"""
    pass


class IntegrationType(Enum):
    """Types of integrations"""
    API = "api"
    DATABASE = "database"
    FILE_SYSTEM = "file_system"
    CLOUD = "cloud"
    WEBHOOK = "webhook"
    SOCKET = "socket"
    CUSTOM = "custom"


class IntegrationStatus(Enum):
    """Status of an integration"""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"
    AUTHENTICATING = "authenticating"


@dataclass
class IntegrationConfig:
    """Configuration for an integration"""
    name: str
    integration_type: IntegrationType
    base_url: Optional[str] = None
    api_key: Optional[str] = None
    auth_token: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    timeout: float = 30.0
    retry_count: int = 3
    retry_delay: float = 1.0
    ssl_verify: bool = True
    headers: Dict[str, str] = field(default_factory=dict)
    parameters: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary (excluding sensitive data)"""
        return {
            'name': self.name,
            'integration_type': self.integration_type.value,
            'base_url': self.base_url,
            'timeout': self.timeout,
            'retry_count': self.retry_count,
            'retry_delay': self.retry_delay,
            'ssl_verify': self.ssl_verify,
            'headers': self.headers,
            'parameters': self.parameters,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'IntegrationConfig':
        """Create from dictionary"""
        return cls(
            name=data.get('name', ''),
            integration_type=IntegrationType(data.get('integration_type', 'api')),
            base_url=data.get('base_url'),
            timeout=data.get('timeout', 30.0),
            retry_count=data.get('retry_count', 3),
            retry_delay=data.get('retry_delay', 1.0),
            ssl_verify=data.get('ssl_verify', True),
            headers=data.get('headers', {}),
            parameters=data.get('parameters', {}),
        )


@dataclass
class IntegrationResult:
    """Result of an integration operation"""
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    status_code: Optional[int] = None
    headers: Optional[Dict[str, str]] = None
    execution_time: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'success': self.success,
            'data': self.data,
            'error': self.error,
            'status_code': self.status_code,
            'headers': self.headers,
            'execution_time': self.execution_time,
        }


@dataclass
class Integration:
    """Represents an integration with an external system"""
    name: str
    config: IntegrationConfig
    status: IntegrationStatus = IntegrationStatus.DISCONNECTED
    is_connected: bool = False
    last_error: Optional[str] = None
    last_connection_time: Optional[float] = None
    connection_count: int = 0
    
    def connect(self) -> IntegrationResult:
        """
        Connect to the external system.
        
        Returns:
            IntegrationResult
        """
        raise NotImplementedError("Subclasses must implement connect()")
    
    def disconnect(self) -> IntegrationResult:
        """
        Disconnect from the external system.
        
        Returns:
            IntegrationResult
        """
        raise NotImplementedError("Subclasses must implement disconnect()")
    
    def test_connection(self) -> IntegrationResult:
        """
        Test the connection to the external system.
        
        Returns:
            IntegrationResult
        """
        raise NotImplementedError("Subclasses must implement test_connection()")
    
    def get_status(self) -> IntegrationStatus:
        """
        Get the current status of the integration.
        
        Returns:
            IntegrationStatus
        """
        return self.status
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'name': self.name,
            'config': self.config.to_dict(),
            'status': self.status.value,
            'is_connected': self.is_connected,
            'last_error': self.last_error,
            'last_connection_time': self.last_connection_time,
            'connection_count': self.connection_count,
        }


class APIIntegration(Integration):
    """Integration with REST APIs"""
    
    def __init__(self, config: IntegrationConfig):
        """
        Initialize API integration.
        
        Args:
            config: Integration configuration
        """
        super().__init__(
            name=config.name,
            config=config,
        )
        self._session = None
    
    def connect(self) -> IntegrationResult:
        """Connect to the API"""
        import requests
        
        try:
            self.status = IntegrationStatus.CONNECTING
            
            # Create session
            self._session = requests.Session()
            
            # Set default headers
            self._session.headers.update(self.config.headers)
            
            # Test connection
            test_result = self.test_connection()
            
            if test_result.success:
                self.status = IntegrationStatus.CONNECTED
                self.is_connected = True
                self.last_connection_time = asyncio.get_event_loop().time()
                self.connection_count += 1
                self.last_error = None
                
                return IntegrationResult(
                    success=True,
                    data={"message": f"Connected to {self.name}"},
                )
            else:
                self.status = IntegrationStatus.ERROR
                self.last_error = test_result.error
                return test_result
                
        except Exception as e:
            self.status = IntegrationStatus.ERROR
            self.last_error = str(e)
            return IntegrationResult(
                success=False,
                error=str(e),
            )
    
    def disconnect(self) -> IntegrationResult:
        """Disconnect from the API"""
        if self._session:
            self._session.close()
            self._session = None
        
        self.status = IntegrationStatus.DISCONNECTED
        self.is_connected = False
        
        return IntegrationResult(
            success=True,
            data={"message": f"Disconnected from {self.name}"},
        )
    
    def test_connection(self) -> IntegrationResult:
        """Test the API connection"""
        import requests
        import time
        
        start_time = time.time()
        
        try:
            if not self.config.base_url:
                return IntegrationResult(
                    success=False,
                    error="No base URL configured",
                )
            
            # Make a test request
            response = requests.get(
                self.config.base_url,
                timeout=self.config.timeout,
                verify=self.config.ssl_verify,
                headers=self.config.headers,
            )
            
            execution_time = time.time() - start_time
            
            if response.status_code < 400:
                return IntegrationResult(
                    success=True,
                    data={"status": "OK"},
                    status_code=response.status_code,
                    execution_time=execution_time,
                )
            else:
                return IntegrationResult(
                    success=False,
                    error=f"HTTP {response.status_code}: {response.text}",
                    status_code=response.status_code,
                    execution_time=execution_time,
                )
                
        except requests.exceptions.SSLError as e:
            return IntegrationResult(
                success=False,
                error=f"SSL error: {str(e)}",
                execution_time=time.time() - start_time,
            )
        except requests.exceptions.ConnectionError as e:
            return IntegrationResult(
                success=False,
                error=f"Connection error: {str(e)}",
                execution_time=time.time() - start_time,
            )
        except requests.exceptions.Timeout as e:
            return IntegrationResult(
                success=False,
                error=f"Timeout: {str(e)}",
                execution_time=time.time() - start_time,
            )
        except Exception as e:
            return IntegrationResult(
                success=False,
                error=str(e),
                execution_time=time.time() - start_time,
            )
    
    def request(self, 
                method: str, 
                endpoint: str, 
                data: Optional[Any] = None,
                params: Optional[Dict] = None,
                headers: Optional[Dict] = None) -> IntegrationResult:
        """
        Make an API request.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE, etc.)
            endpoint: API endpoint (appended to base URL)
            data: Request body data
            params: Query parameters
            headers: Additional headers
            
        Returns:
            IntegrationResult
        """
        import requests
        import time
        
        if not self.is_connected:
            connect_result = self.connect()
            if not connect_result.success:
                return connect_result
        
        start_time = time.time()
        
        try:
            url = f"{self.config.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
            
            # Merge headers
            request_headers = {**self.config.headers}
            if headers:
                request_headers.update(headers)
            
            # Add authentication if configured
            if self.config.api_key:
                request_headers['Authorization'] = f"Bearer {self.config.api_key}"
            elif self.config.auth_token:
                request_headers['Authorization'] = f"Token {self.config.auth_token}"
            
            # Make request
            method = method.upper()
            
            if method == 'GET':
                response = requests.get(
                    url,
                    params=params,
                    headers=request_headers,
                    timeout=self.config.timeout,
                    verify=self.config.ssl_verify,
                )
            elif method == 'POST':
                response = requests.post(
                    url,
                    json=data if data else None,
                    params=params,
                    headers=request_headers,
                    timeout=self.config.timeout,
                    verify=self.config.ssl_verify,
                )
            elif method == 'PUT':
                response = requests.put(
                    url,
                    json=data if data else None,
                    params=params,
                    headers=request_headers,
                    timeout=self.config.timeout,
                    verify=self.config.ssl_verify,
                )
            elif method == 'DELETE':
                response = requests.delete(
                    url,
                    params=params,
                    headers=request_headers,
                    timeout=self.config.timeout,
                    verify=self.config.ssl_verify,
                )
            elif method == 'PATCH':
                response = requests.patch(
                    url,
                    json=data if data else None,
                    params=params,
                    headers=request_headers,
                    timeout=self.config.timeout,
                    verify=self.config.ssl_verify,
                )
            else:
                return IntegrationResult(
                    success=False,
                    error=f"Unsupported HTTP method: {method}",
                    execution_time=time.time() - start_time,
                )
            
            execution_time = time.time() - start_time
            
            # Parse response
            try:
                response_data = response.json()
            except (json.JSONDecodeError, ValueError):
                response_data = response.text
            
            if response.status_code < 400:
                return IntegrationResult(
                    success=True,
                    data=response_data,
                    status_code=response.status_code,
                    headers=dict(response.headers),
                    execution_time=execution_time,
                )
            else:
                return IntegrationResult(
                    success=False,
                    error=f"HTTP {response.status_code}: {response.text}",
                    status_code=response.status_code,
                    execution_time=execution_time,
                )
                
        except requests.exceptions.SSLError as e:
            return IntegrationResult(
                success=False,
                error=f"SSL error: {str(e)}",
                execution_time=time.time() - start_time,
            )
        except requests.exceptions.ConnectionError as e:
            self.status = IntegrationStatus.ERROR
            self.is_connected = False
            return IntegrationResult(
                success=False,
                error=f"Connection error: {str(e)}",
                execution_time=time.time() - start_time,
            )
        except requests.exceptions.Timeout as e:
            return IntegrationResult(
                success=False,
                error=f"Timeout: {str(e)}",
                execution_time=time.time() - start_time,
            )
        except Exception as e:
            return IntegrationResult(
                success=False,
                error=str(e),
                execution_time=time.time() - start_time,
            )


class DatabaseIntegration(Integration):
    """Integration with databases"""
    
    def __init__(self, config: IntegrationConfig):
        """
        Initialize database integration.
        
        Args:
            config: Integration configuration
        """
        super().__init__(
            name=config.name,
            config=config,
        )
        self._connection = None
    
    def connect(self) -> IntegrationResult:
        """Connect to the database"""
        try:
            self.status = IntegrationStatus.CONNECTING
            
            # Implementation depends on database type
            # This is a generic implementation
            
            self.status = IntegrationStatus.CONNECTED
            self.is_connected = True
            self.last_connection_time = asyncio.get_event_loop().time()
            self.connection_count += 1
            self.last_error = None
            
            return IntegrationResult(
                success=True,
                data={"message": f"Connected to database {self.name}"},
            )
            
        except Exception as e:
            self.status = IntegrationStatus.ERROR
            self.last_error = str(e)
            return IntegrationResult(
                success=False,
                error=str(e),
            )
    
    def disconnect(self) -> IntegrationResult:
        """Disconnect from the database"""
        if self._connection:
            # Close connection
            self._connection = None
        
        self.status = IntegrationStatus.DISCONNECTED
        self.is_connected = False
        
        return IntegrationResult(
            success=True,
            data={"message": f"Disconnected from database {self.name}"},
        )
    
    def test_connection(self) -> IntegrationResult:
        """Test the database connection"""
        if not self.is_connected:
            return IntegrationResult(
                success=False,
                error="Not connected to database",
            )
        
        return IntegrationResult(
            success=True,
            data={"status": "OK"},
        )


class ToolIntegration:
    """
    Manages integrations for AI tools.
    
    This class provides a centralized way to manage external integrations
    for AI tools, including APIs, databases, and other services.
    """
    
    def __init__(self, 
                 registry: Optional[ToolRegistry] = None,
                 sandbox: Optional[ToolSandbox] = None):
        """
        Initialize the tool integration manager.
        
        Args:
            registry: Tool registry instance
            sandbox: Tool sandbox instance
        """
        self.registry = registry or ToolRegistry()
        self.sandbox = sandbox or ToolSandbox()
        self._integrations: Dict[str, Integration] = {}
        self._configs: Dict[str, IntegrationConfig] = {}
    
    def register_integration(self, 
                            name: str, 
                            config: IntegrationConfig,
                            integration_type: Optional[Type[Integration]] = None) -> Integration:
        """
        Register a new integration.
        
        Args:
            name: Name of the integration
            config: Integration configuration
            integration_type: Optional integration class
            
        Returns:
            Integration object
        """
        # Create integration based on type
        if integration_type:
            integration = integration_type(config)
        elif config.integration_type == IntegrationType.API:
            integration = APIIntegration(config)
        elif config.integration_type == IntegrationType.DATABASE:
            integration = DatabaseIntegration(config)
        else:
            # Create a generic integration
            integration = Integration(name=name, config=config)
        
        self._integrations[name] = integration
        self._configs[name] = config
        
        logger.info(f"Registered integration: {name} (type: {config.integration_type.value})")
        
        return integration
    
    def get_integration(self, name: str) -> Optional[Integration]:
        """
        Get a registered integration.
        
        Args:
            name: Name of the integration
            
        Returns:
            Integration object or None
        """
        return self._integrations.get(name)
    
    def get_config(self, name: str) -> Optional[IntegrationConfig]:
        """
        Get integration configuration.
        
        Args:
            name: Name of the integration
            
        Returns:
            IntegrationConfig or None
        """
        return self._configs.get(name)
    
    def connect(self, name: str) -> IntegrationResult:
        """
        Connect to an integration.
        
        Args:
            name: Name of the integration
            
        Returns:
            IntegrationResult
        """
        integration = self._integrations.get(name)
        if integration:
            return integration.connect()
        return IntegrationResult(
            success=False,
            error=f"Integration '{name}' not found",
        )
    
    def disconnect(self, name: str) -> IntegrationResult:
        """
        Disconnect from an integration.
        
        Args:
            name: Name of the integration
            
        Returns:
            IntegrationResult
        """
        integration = self._integrations.get(name)
        if integration:
            return integration.disconnect()
        return IntegrationResult(
            success=False,
            error=f"Integration '{name}' not found",
        )
    
    def test_connection(self, name: str) -> IntegrationResult:
        """
        Test connection to an integration.
        
        Args:
            name: Name of the integration
            
        Returns:
            IntegrationResult
        """
        integration = self._integrations.get(name)
        if integration:
            return integration.test_connection()
        return IntegrationResult(
            success=False,
            error=f"Integration '{name}' not found",
        )
    
    def connect_all(self) -> Dict[str, IntegrationResult]:
        """
        Connect to all registered integrations.
        
        Returns:
            Dictionary of integration names to results
        """
        results = {}
        for name, integration in self._integrations.items():
            results[name] = integration.connect()
        return results
    
    def disconnect_all(self) -> Dict[str, IntegrationResult]:
        """
        Disconnect from all registered integrations.
        
        Returns:
            Dictionary of integration names to results
        """
        results = {}
        for name, integration in self._integrations.items():
            results[name] = integration.disconnect()
        return results
    
    def unregister_integration(self, name: str) -> bool:
        """
        Unregister an integration.
        
        Args:
            name: Name of the integration
            
        Returns:
            True if integration was unregistered
        """
        if name in self._integrations:
            # Disconnect first
            self._integrations[name].disconnect()
            del self._integrations[name]
            del self._configs[name]
            logger.info(f"Unregistered integration: {name}")
            return True
        return False
    
    def get_all_integrations(self) -> List[Integration]:
        """
        Get all registered integrations.
        
        Returns:
            List of all Integration objects
        """
        return list(self._integrations.values())
    
    def get_integration_status(self, name: str) -> Optional[IntegrationStatus]:
        """
        Get the status of an integration.
        
        Args:
            name: Name of the integration
            
        Returns:
            IntegrationStatus or None
        """
        integration = self._integrations.get(name)
        if integration:
            return integration.get_status()
        return None
    
    def get_status_report(self) -> Dict[str, Any]:
        """
        Get a report of all integration statuses.
        
        Returns:
            Dictionary with integration status report
        """
        report = {
            'integrations': {},
            'total': len(self._integrations),
            'connected': 0,
            'disconnected': 0,
            'error': 0,
        }
        
        for name, integration in self._integrations.items():
            status = integration.get_status()
            report['integrations'][name] = {
                'status': status.value,
                'is_connected': integration.is_connected,
                'last_error': integration.last_error,
            }
            
            if status == IntegrationStatus.CONNECTED:
                report['connected'] += 1
            elif status == IntegrationStatus.DISCONNECTED:
                report['disconnected'] += 1
            else:
                report['error'] += 1
        
        return report
    
    def clear_all(self):
        """Clear all integrations"""
        self.disconnect_all()
        self._integrations.clear()
        self._configs.clear()
        logger.info("Cleared all integrations")


# Global integration manager instance
integration = ToolIntegration()


def get_integration() -> ToolIntegration:
    """Get the global tool integration instance"""
    return integration
