"""Configuration management with YAML loading and environment override."""

import os
import yaml
from typing import Optional
from pathlib import Path
from ..models.config import ConfigModel


class ConfigManager:
    """Singleton configuration manager."""
    
    _instance: Optional["ConfigManager"] = None
    _config: Optional[ConfigModel] = None
    
    def __new__(cls) -> "ConfigManager":
        """Ensure singleton instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize configuration manager."""
        if self._config is None:
            self._config = self._load_config()
    
    def _load_config(self) -> ConfigModel:
        """Load configuration from YAML file and environment variables."""
        # Get config file path
        config_path = os.getenv("CONFIG_PATH", "config/config.yaml")
        config_file = Path(config_path)
        
        # Load from YAML file if it exists
        config_data = {}
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f) or {}
        
        # Override with environment variables
        env_overrides = self._get_env_overrides()
        config_data = self._merge_config(config_data, env_overrides)
        
        # Create and return configuration model
        return ConfigModel(**config_data)
    
    def _get_env_overrides(self) -> dict:
        """Extract configuration overrides from environment variables."""
        env_config = {}
        
        # App configuration
        if os.getenv("APP_NAME"):
            env_config.setdefault("app", {})["name"] = os.getenv("APP_NAME")
        if os.getenv("APP_VERSION"):
            env_config.setdefault("app", {})["version"] = os.getenv("APP_VERSION")
        if os.getenv("APP_HOST"):
            env_config.setdefault("app", {})["host"] = os.getenv("APP_HOST")
        if os.getenv("APP_PORT"):
            env_config.setdefault("app", {})["port"] = int(os.getenv("APP_PORT", "8000"))
        if os.getenv("APP_DEBUG"):
            env_config.setdefault("app", {})["debug"] = os.getenv("APP_DEBUG", "false").lower() == "true"
        
        # Database configuration
        if os.getenv("DB_HOST"):
            env_config.setdefault("database", {})["host"] = os.getenv("DB_HOST")
        if os.getenv("DB_PORT"):
            env_config.setdefault("database", {})["port"] = int(os.getenv("DB_PORT", "5432"))
        if os.getenv("DB_DATABASE"):
            env_config.setdefault("database", {})["database"] = os.getenv("DB_DATABASE")
        if os.getenv("DB_USERNAME"):
            env_config.setdefault("database", {})["username"] = os.getenv("DB_USERNAME")
        if os.getenv("DB_PASSWORD"):
            env_config.setdefault("database", {})["password"] = os.getenv("DB_PASSWORD")
        
        # InfluxDB configuration
        if os.getenv("INFLUXDB_URL"):
            env_config.setdefault("influxdb", {})["url"] = os.getenv("INFLUXDB_URL")
        if os.getenv("INFLUXDB_TOKEN"):
            env_config.setdefault("influxdb", {})["token"] = os.getenv("INFLUXDB_TOKEN")
        if os.getenv("INFLUXDB_ORG"):
            env_config.setdefault("influxdb", {})["org"] = os.getenv("INFLUXDB_ORG")
        if os.getenv("INFLUXDB_BUCKET"):
            env_config.setdefault("influxdb", {})["bucket"] = os.getenv("INFLUXDB_BUCKET")
        
        # CORS configuration
        if os.getenv("CORS_ORIGINS"):
            origins_str = os.getenv("CORS_ORIGINS", "")
            origins = [origin.strip() for origin in origins_str.split(",")]
            env_config.setdefault("cors", {})["origins"] = origins

        # External APIs: LLM
        if os.getenv("LLM_PROVIDER"):
            env_config.setdefault("external_apis", {}).setdefault("llm", {})["provider"] = os.getenv("LLM_PROVIDER")
        if os.getenv("LLM_API_KEY"):
            env_config.setdefault("external_apis", {}).setdefault("llm", {})["api_key"] = os.getenv("LLM_API_KEY")
        if os.getenv("LLM_MODEL"):
            env_config.setdefault("external_apis", {}).setdefault("llm", {})["model"] = os.getenv("LLM_MODEL")
        if os.getenv("LLM_BASE_URL"):
            env_config.setdefault("external_apis", {}).setdefault("llm", {})["base_url"] = os.getenv("LLM_BASE_URL")

        # External APIs: Bamboo
        if os.getenv("BAMBOO_BASE_URL"):
            env_config.setdefault("external_apis", {}).setdefault("bamboo", {})["base_url"] = os.getenv("BAMBOO_BASE_URL")
        if os.getenv("BAMBOO_USERNAME"):
            env_config.setdefault("external_apis", {}).setdefault("bamboo", {})["username"] = os.getenv("BAMBOO_USERNAME")
        if os.getenv("BAMBOO_TOKEN"):
            env_config.setdefault("external_apis", {}).setdefault("bamboo", {})["token"] = os.getenv("BAMBOO_TOKEN")
        
        return env_config
    
    def _merge_config(self, base: dict, override: dict) -> dict:
        """Recursively merge configuration dictionaries."""
        result = base.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_config(result[key], value)
            else:
                result[key] = value
        
        return result
    
    @property
    def config(self) -> ConfigModel:
        """Get configuration instance."""
        if self._config is None:
            self._config = self._load_config()
        return self._config
    
    def reload(self) -> ConfigModel:
        """Reload configuration from file and environment."""
        self._config = self._load_config()
        return self._config


def get_config() -> ConfigModel:
    """Get configuration instance (convenience function)."""
    manager = ConfigManager()
    return manager.config