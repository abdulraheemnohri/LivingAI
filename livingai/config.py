# LivingAI Config: Configuration Management
# ========================================
# This module provides configuration management for LivingAI.

import os
import yaml
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path


class ConfigManager:
    """
    Manages LivingAI configuration from YAML files and environment variables.
    """
    
    # Default configuration
    DEFAULT_CONFIG: Dict[str, Any] = {
        "model": {
            "repository": "HuggingFaceTB/SmolLM3-3B",
            "revision": "main",
            "runtime": "auto",
            "quantization": "auto",
            "context": "auto",
            "threads": "auto",
            "batch_size": "auto",
        },
        "generation": {
            "temperature": 0.7,
            "top_p": 0.9,
            "max_tokens": 512,
            "streaming": True,
        },
        "memory": {
            "enabled": True,
            "consolidation_interval": 3600,  # 1 hour
        },
        "learning": {
            "enabled": True,
            "auto_consolidate": True,
        },
        "skills": {
            "enabled": True,
            "sandbox": True,
        },
        "actions": {
            "auto_allow_low_risk": True,
            "confirm_medium_risk": True,
            "block_high_risk": True,
        },
        "voice": {
            "enabled": False,
            "stt_engine": "termux",
            "tts_engine": "android",
        },
        "privacy": {
            "cloud_ai": False,
            "telemetry": False,
            "analytics": False,
        },
        "battery": {
            "min_percentage": 20,
            "charging_required": False,
        },
        "logging": {
            "level": "INFO",
            "file": "~/.livingai/logs/livingai.log",
        },
        "download": {
            "automatic_download": True,
            "automatic_update": False,
            "wifi_only": True,
            "mobile_data_confirmation": True,
            "resume_download": True,
            "verify_download": True,
            "background_download": True,
        },
        "security": {
            "audit_logging": True,
            "skill_sandbox": True,
        },
    }
    
    def __init__(self, config_path: str):
        """
        Initialize the ConfigManager.
        
        Args:
            config_path: Path to the YAML configuration file.
        """
        self.config_path = os.path.expanduser(config_path)
        self._config: Dict[str, Any] = {}
        self._load_config()
    
    def _load_config(self) -> None:
        """Load configuration from file and environment variables."""
        # Start with defaults
        self._config = self.DEFAULT_CONFIG.copy()
        
        # Load from YAML file if it exists
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    file_config = yaml.safe_load(f)
                    if file_config:
                        self._config = self._deep_merge(self._config, file_config)
            except Exception as e:
                logging.warning(f"Failed to load config from {self.config_path}: {e}")
        
        # Override with environment variables
        self._override_with_env()
        
        # Expand paths
        self._expand_paths()
    
    def _deep_merge(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """
        Deep merge two dictionaries.
        
        Args:
            base: Base dictionary.
            override: Dictionary with override values.
            
        Returns:
            Dict[str, Any]: Merged dictionary.
        """
        result = base.copy()
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        return result
    
    def _override_with_env(self) -> None:
        """Override configuration with environment variables."""
        # Map environment variables to config keys
        env_mapping = {
            "LIVINGAI_MODEL_REPOSITORY": "model.repository",
            "LIVINGAI_MODEL_REVISION": "model.revision",
            "LIVINGAI_MODEL_RUNTIME": "model.runtime",
            "LIVINGAI_MODEL_QUANTIZATION": "model.quantization",
            "LIVINGAI_MODEL_CONTEXT": "model.context",
            "LIVINGAI_MODEL_THREADS": "model.threads",
            "LIVINGAI_GENERATION_TEMPERATURE": "generation.temperature",
            "LIVINGAI_GENERATION_TOP_P": "generation.top_p",
            "LIVINGAI_GENERATION_MAX_TOKENS": "generation.max_tokens",
            "LIVINGAI_MEMORY_ENABLED": "memory.enabled",
            "LIVINGAI_LEARNING_ENABLED": "learning.enabled",
            "LIVINGAI_VOICE_ENABLED": "voice.enabled",
            "LIVINGAI_LOG_LEVEL": "logging.level",
            "LIVINGAI_HOME": "paths.home",
            "LIVINGAI_MODEL_DIR": "paths.models",
        }
        
        for env_var, config_key in env_mapping.items():
            env_value = os.getenv(env_var)
            if env_value is not None:
                self._set_nested(self._config, config_key, env_value)
    
    def _expand_paths(self) -> None:
        """Expand user paths in configuration."""
        path_keys = ["logging.file"]
        for key in path_keys:
            if self._get_nested(self._config, key):
                expanded = os.path.expanduser(self._get_nested(self._config, key))
                self._set_nested(self._config, key, expanded)
    
    def _get_nested(self, data: Dict[str, Any], path: str) -> Any:
        """
        Get a nested value from a dictionary using dot notation.
        
        Args:
            data: Dictionary to search.
            path: Dot-separated path to the value.
            
        Returns:
            Any: The value at the path, or None if not found.
        """
        keys = path.split('.')
        current = data
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return None
        return current
    
    def _set_nested(self, data: Dict[str, Any], path: str, value: Any) -> None:
        """
        Set a nested value in a dictionary using dot notation.
        
        Args:
            data: Dictionary to modify.
            path: Dot-separated path to the value.
            value: Value to set.
        """
        keys = path.split('.')
        current = data
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        current[keys[-1]] = self._convert_type(value)
    
    def _convert_type(self, value: str) -> Any:
        """
        Convert a string value to its appropriate Python type.
        
        Args:
            value: String value to convert.
            
        Returns:
            Any: Converted value.
        """
        if value.lower() == "true":
            return True
        elif value.lower() == "false":
            return False
        elif value.isdigit():
            return int(value)
        elif value.replace('.', '').replace('-', '').isdigit():
            return float(value)
        else:
            return value
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value by dot-separated key.
        
        Args:
            key: Dot-separated configuration key.
            default: Default value if key not found.
            
        Returns:
            Any: The configuration value.
        """
        value = self._get_nested(self._config, key)
        return value if value is not None else default
    
    def set(self, key: str, value: Any) -> None:
        """
        Set a configuration value by dot-separated key.
        
        Args:
            key: Dot-separated configuration key.
            value: Value to set.
        """
        self._set_nested(self._config, key, value)
        self._save_config()
    
    def _save_config(self) -> None:
        """Save the current configuration to the YAML file."""
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, 'w') as f:
                yaml.dump(self._config, f, default_flow_style=False, sort_keys=False)
        except Exception as e:
            logging.error(f"Failed to save config to {self.config_path}: {e}")
    
    def show(self) -> None:
        """Print the current configuration."""
        print(yaml.dump(self._config, default_flow_style=False, sort_keys=False))
    
    def get_all(self) -> Dict[str, Any]:
        """
        Get the entire configuration dictionary.
        
        Returns:
            Dict[str, Any]: The full configuration.
        """
        return self._config.copy()
    
    def reset(self) -> None:
        """Reset configuration to defaults."""
        self._config = self.DEFAULT_CONFIG.copy()
        self._save_config()
        logging.info("Configuration reset to defaults")
    
    def edit(self) -> None:
        """Edit configuration interactively."""
        # This would typically open an editor, but for now we'll just show instructions
        print(f"Edit the configuration file at: {self.config_path}")
        print("After editing, changes will be automatically loaded.")
    
    def menu(self) -> None:
        """Show interactive configuration menu."""
        from .ui.menus import ConfigMenu
        menu = ConfigMenu(self)
        menu.show()
    
    def get_model_config(self) -> Dict[str, Any]:
        """Get model-specific configuration."""
        return self.get("model", {})
    
    def get_generation_config(self) -> Dict[str, Any]:
        """Get generation-specific configuration."""
        return self.get("generation", {})
    
    def get_memory_config(self) -> Dict[str, Any]:
        """Get memory-specific configuration."""
        return self.get("memory", {})
    
    def get_learning_config(self) -> Dict[str, Any]:
        """Get learning-specific configuration."""
        return self.get("learning", {})
    
    def get_voice_config(self) -> Dict[str, Any]:
        """Get voice-specific configuration."""
        return self.get("voice", {})
    
    def get_actions_config(self) -> Dict[str, Any]:
        """Get actions-specific configuration."""
        return self.get("actions", {})
    
    def get_download_config(self) -> Dict[str, Any]:
        """Get download-specific configuration."""
        return self.get("download", {})
    
    def get_security_config(self) -> Dict[str, Any]:
        """Get security-specific configuration."""
        return self.get("security", {})
