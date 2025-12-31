#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Configuration management for HackerTarget CLI.
Supports YAML config files, environment variables, and defaults.
"""

import os
import yaml
from pathlib import Path
from typing import Any, Dict, Optional

from .exceptions import ConfigError
from .logger import get_logger


class Config:
    """Configuration manager for HackerTarget CLI."""
    
    # Default configuration
    DEFAULTS = {
        'api': {
            'timeout': 30,
            'max_retries': 3,
            'backoff_factor': 0.5,
            'verify_ssl': True,
            'api_key': None,
        },
        'logging': {
            'level': 'INFO',
            'file': None,
            'colored': True,
        },
        'cache': {
            'enabled': False,
            'directory': '~/.hackertarget/cache',
            'ttl': 3600,  # 1 hour
        },
        'output': {
            'format': 'console',
            'colored': True,
            'verbose': False,
        },
        'batch': {
            'delay': 1.0,
            'continue_on_error': True,
        }
    }
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize configuration.
        
        Args:
            config_file: Path to configuration file (optional)
        """
        self.logger = get_logger()
        self.config = self._load_defaults()
        
        # Try to load from file
        if config_file:
            self._load_from_file(config_file)
        else:
            # Try default locations
            self._try_default_locations()
        
        # Override with environment variables
        self._load_from_env()
    
    def _load_defaults(self) -> Dict[str, Any]:
        """Load default configuration."""
        return dict(self.DEFAULTS)
    
    def _try_default_locations(self):
        """Try to load config from default locations."""
        default_paths = [
            Path.home() / '.hackertarget.yaml',
            Path.home() / '.hackertarget.yml',
            Path.home() / '.config' / 'hackertarget' / 'config.yaml',
            Path.cwd() / '.hackertarget.yaml',
        ]
        
        for path in default_paths:
            if path.exists():
                self.logger.debug(f"Found config file at: {path}")
                self._load_from_file(str(path))
                break
    
    def _load_from_file(self, filepath: str):
        """
        Load configuration from YAML file.
        
        Args:
            filepath: Path to config file
            
        Raises:
            ConfigError: If file cannot be loaded
        """
        try:
            path = Path(filepath).expanduser()
            
            if not path.exists():
                raise ConfigError(f"Config file not found: {filepath}", config_file=filepath)
            
            with open(path, 'r') as f:
                file_config = yaml.safe_load(f)
            
            if file_config:
                self._merge_config(file_config)
                self.logger.info(f"Loaded configuration from: {filepath}")
        
        except yaml.YAMLError as e:
            raise ConfigError(f"Invalid YAML in config file: {str(e)}", config_file=filepath)
        except Exception as e:
            raise ConfigError(f"Error loading config file: {str(e)}", config_file=filepath)
    
    def _load_from_env(self):
        """Load configuration from environment variables."""
        env_mappings = {
            'HACKERTARGET_API_KEY': ('api', 'api_key'),
            'HACKERTARGET_TIMEOUT': ('api', 'timeout'),
            'HACKERTARGET_LOG_LEVEL': ('logging', 'level'),
            'HACKERTARGET_LOG_FILE': ('logging', 'file'),
            'HACKERTARGET_CACHE_DIR': ('cache', 'directory'),
            'HACKERTARGET_CACHE_ENABLED': ('cache', 'enabled'),
        }
        
        for env_var, (section, key) in env_mappings.items():
            value = os.environ.get(env_var)
            if value is not None:
                # Convert boolean strings
                if value.lower() in ('true', 'yes', '1'):
                    value = True
                elif value.lower() in ('false', 'no', '0'):
                    value = False
                # Convert numeric strings
                elif value.isdigit():
                    value = int(value)
                
                if section not in self.config:
                    self.config[section] = {}
                self.config[section][key] = value
                self.logger.debug(f"Loaded from env: {env_var} = {value}")
    
    def _merge_config(self, new_config: Dict[str, Any]):
        """
        Merge new configuration with existing.
        
        Args:
            new_config: Configuration dictionary to merge
        """
        for section, values in new_config.items():
            if section in self.config:
                if isinstance(values, dict):
                    self.config[section].update(values)
                else:
                    self.config[section] = values
            else:
                self.config[section] = values
    
    def get(self, section: str, key: str, default: Any = None) -> Any:
        """
        Get configuration value.
        
        Args:
            section: Configuration section
            key: Configuration key
            default: Default value if not found
            
        Returns:
            Configuration value
        """
        try:
            return self.config.get(section, {}).get(key, default)
        except (KeyError, AttributeError):
            return default
    
    def set(self, section: str, key: str, value: Any):
        """
        Set configuration value.
        
        Args:
            section: Configuration section
            key: Configuration key
            value: Value to set
        """
        if section not in self.config:
            self.config[section] = {}
        self.config[section][key] = value
    
    def get_section(self, section: str) -> Dict[str, Any]:
        """
        Get entire configuration section.
        
        Args:
            section: Section name
            
        Returns:
            Section dictionary
        """
        return self.config.get(section, {})
    
    def save(self, filepath: str):
        """
        Save configuration to file.
        
        Args:
            filepath: Path to save config
            
        Raises:
            ConfigError: If file cannot be saved
        """
        try:
            path = Path(filepath).expanduser()
            path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(path, 'w') as f:
                yaml.dump(self.config, f, default_flow_style=False, sort_keys=False)
            
            self.logger.info(f"Configuration saved to: {filepath}")
        
        except Exception as e:
            raise ConfigError(f"Error saving config file: {str(e)}", config_file=filepath)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Get configuration as dictionary.
        
        Returns:
            Configuration dictionary
        """
        return dict(self.config)
    
    @classmethod
    def create_default_config(cls, filepath: str):
        """
        Create a default configuration file.
        
        Args:
            filepath: Path to create config file
        """
        config = cls()
        config.save(filepath)


# Global configuration instance
_config_instance: Optional[Config] = None


def get_config(config_file: Optional[str] = None) -> Config:
    """
    Get or create global configuration instance.
    
    Args:
        config_file: Optional path to config file
        
    Returns:
        Config instance
    """
    global _config_instance
    
    if _config_instance is None or config_file:
        _config_instance = Config(config_file)
    
    return _config_instance
