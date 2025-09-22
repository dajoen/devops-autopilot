"""Tests for Settings class and configuration management."""

import os
import pytest
from unittest.mock import patch, MagicMock

from backend.core.settings import Settings
from backend.core.config import ConfigManager, get_config
from backend.models.config import ConfigModel, DatabaseConfig, InfluxDBConfig, LLMConfig, BambooConfig


class TestSettings:
    """Test Settings facade."""

    def test_settings_init_with_default_config(self):
        """Test Settings initializes with default config."""
        settings = Settings()
        assert settings._config is not None

    def test_settings_init_with_custom_config(self):
        """Test Settings initializes with custom config."""
        mock_config = MagicMock(spec=ConfigModel)
        settings = Settings(config=mock_config)
        assert settings._config == mock_config

    def test_postgres_dsn_success(self):
        """Test postgres_dsn returns valid DSN."""
        mock_config = MagicMock(spec=ConfigModel)
        mock_db = MagicMock(spec=DatabaseConfig)
        mock_db.url = "postgresql+asyncpg://user:pass@localhost:5432/test"
        mock_config.database = mock_db
        
        settings = Settings(config=mock_config)
        dsn = settings.postgres_dsn()
        
        assert dsn == "postgresql+asyncpg://user:pass@localhost:5432/test"

    def test_influx_config_success(self):
        """Test influx_config returns tuple of settings."""
        mock_config = MagicMock(spec=ConfigModel)
        mock_influx = MagicMock()  # Remove spec to allow dynamic attributes
        mock_influx.url = "http://localhost:8086"
        mock_influx.org = "test-org"
        mock_influx.bucket = "test-bucket"
        mock_influx.token.get_secret_value.return_value = "test-token"
        mock_config.influxdb = mock_influx
        
        settings = Settings(config=mock_config)
        url, org, bucket, token = settings.influx_config()
        
        assert url == "http://localhost:8086"
        assert org == "test-org"
        assert bucket == "test-bucket"
        assert token == "test-token"

    def test_provider_success(self):
        """Test provider returns LLM provider name."""
        mock_config = MagicMock(spec=ConfigModel)
        mock_external = MagicMock()
        mock_llm = MagicMock(spec=LLMConfig)
        mock_llm.provider = "dummy"
        mock_external.llm = mock_llm
        mock_config.external_apis = mock_external
        
        settings = Settings(config=mock_config)
        provider = settings.provider()
        
        assert provider == "dummy"

    def test_provider_missing_external_apis(self):
        """Test provider raises when external_apis is None."""
        mock_config = MagicMock(spec=ConfigModel)
        mock_config.external_apis = None
        
        settings = Settings(config=mock_config)
        
        with pytest.raises(ValueError, match="LLM provider is not configured"):
            settings.provider()

    def test_provider_missing_llm_config(self):
        """Test provider raises when LLM config is None."""
        mock_config = MagicMock(spec=ConfigModel)
        mock_external = MagicMock()
        mock_external.llm = None
        mock_config.external_apis = mock_external
        
        settings = Settings(config=mock_config)
        
        with pytest.raises(ValueError, match="LLM provider is not configured"):
            settings.provider()

    def test_provider_empty_provider(self):
        """Test provider raises when provider is empty."""
        mock_config = MagicMock(spec=ConfigModel)
        mock_external = MagicMock()
        mock_llm = MagicMock(spec=LLMConfig)
        mock_llm.provider = ""
        mock_external.llm = mock_llm
        mock_config.external_apis = mock_external
        
        settings = Settings(config=mock_config)
        
        with pytest.raises(ValueError, match="LLM provider is not configured"):
            settings.provider()

    def test_bamboo_auth_success(self):
        """Test bamboo_auth returns tuple of credentials."""
        mock_config = MagicMock(spec=ConfigModel)
        mock_external = MagicMock()
        mock_bamboo = MagicMock()  # Remove spec to allow dynamic attributes
        mock_bamboo.base_url = "https://bamboo.example.com"
        mock_bamboo.username = "testuser"
        mock_bamboo.token.get_secret_value.return_value = "secret-token"
        mock_external.bamboo = mock_bamboo
        mock_config.external_apis = mock_external
        
        settings = Settings(config=mock_config)
        base_url, username, token = settings.bamboo_auth()
        
        assert base_url == "https://bamboo.example.com"
        assert username == "testuser"
        assert token == "secret-token"

    def test_bamboo_auth_missing_config(self):
        """Test bamboo_auth raises when bamboo config is missing."""
        mock_config = MagicMock(spec=ConfigModel)
        mock_config.external_apis = None
        
        settings = Settings(config=mock_config)
        
        with pytest.raises(ValueError, match="Bamboo configuration missing"):
            settings.bamboo_auth()

    def test_bamboo_auth_incomplete_config(self):
        """Test bamboo_auth raises when bamboo config is incomplete."""
        mock_config = MagicMock(spec=ConfigModel)
        mock_external = MagicMock()
        mock_bamboo = MagicMock()  # Remove spec to allow dynamic attributes
        mock_bamboo.base_url = "https://bamboo.example.com"
        mock_bamboo.username = ""  # Empty username
        mock_bamboo.token.get_secret_value.return_value = "secret-token"
        mock_external.bamboo = mock_bamboo
        mock_config.external_apis = mock_external
        
        settings = Settings(config=mock_config)
        
        with pytest.raises(ValueError, match="Incomplete Bamboo config"):
            settings.bamboo_auth()


class TestConfigManager:
    """Test ConfigManager singleton and configuration loading."""

    def test_singleton_instance(self):
        """Test ConfigManager is a singleton."""
        manager1 = ConfigManager()
        manager2 = ConfigManager()
        assert manager1 is manager2

    @patch.dict(os.environ, {
        "APP_NAME": "Test App",
        "APP_PORT": "9000",
        "DB_HOST": "testhost",
        "LLM_PROVIDER": "test-provider"
    })
    def test_env_overrides(self):
        """Test environment variables override config."""
        # Reset singleton for clean test
        ConfigManager._instance = None
        ConfigManager._config = None
        
        manager = ConfigManager()
        config = manager.config
        
        assert config.app.name == "Test App"
        assert config.app.port == 9000
        assert config.database.host == "testhost"
        
        # Clean up
        ConfigManager._instance = None
        ConfigManager._config = None

    def test_get_config_convenience_function(self):
        """Test get_config returns ConfigManager instance."""
        config = get_config()
        assert isinstance(config, ConfigModel)


class TestConfigValidation:
    """Test configuration model validation."""

    def test_database_config_valid(self):
        """Test DatabaseConfig with valid data."""
        db_config = DatabaseConfig(
            host="localhost",
            port=5432,
            database="test_db",
            username="user",
            password="secret"
        )
        
        assert db_config.host == "localhost"
        assert db_config.port == 5432
        assert db_config.database == "test_db"
        assert db_config.username == "user"
        assert db_config.password.get_secret_value() == "secret"
        assert "postgresql+asyncpg://user:secret@localhost:5432/test_db" in db_config.url

    def test_database_config_empty_database(self):
        """Test DatabaseConfig validation fails with empty database name."""
        with pytest.raises(ValueError, match="must not be empty"):
            DatabaseConfig(
                host="localhost",
                port=5432,
                database="",  # Empty
                username="user",
                password="secret"
            )

    def test_database_config_invalid_port(self):
        """Test DatabaseConfig validation fails with invalid port."""
        with pytest.raises(ValueError):
            DatabaseConfig(
                host="localhost",
                port=70000,  # Too high
                database="test",
                username="user",
                password="secret"
            )

    def test_influxdb_config_valid(self):
        """Test InfluxDBConfig with valid data."""
        influx_config = InfluxDBConfig(
            url="http://localhost:8086",
            token="test-token",
            org="test-org",
            bucket="test-bucket"
        )
        
        assert str(influx_config.url) == "http://localhost:8086/"  # AnyHttpUrl adds trailing slash
        assert influx_config.token.get_secret_value() == "test-token"
        assert influx_config.org == "test-org"
        assert influx_config.bucket == "test-bucket"

    def test_influxdb_config_invalid_url(self):
        """Test InfluxDBConfig validation fails with invalid URL."""
        with pytest.raises(ValueError):
            InfluxDBConfig(
                url="not-a-valid-url",
                token="test-token",
                org="test-org",
                bucket="test-bucket"
            )

    def test_llm_config_valid(self):
        """Test LLMConfig with valid data."""
        llm_config = LLMConfig(
            provider="openai",
            api_key="sk-test-key",
            model="gpt-3.5-turbo",
            base_url="https://api.openai.com/v1"
        )
        
        assert llm_config.provider == "openai"
        assert llm_config.api_key.get_secret_value() == "sk-test-key"
        assert llm_config.model == "gpt-3.5-turbo"
        assert str(llm_config.base_url) == "https://api.openai.com/v1"

    def test_llm_config_empty_provider(self):
        """Test LLMConfig validation fails with empty provider."""
        with pytest.raises(ValueError, match="LLM provider must be set"):
            LLMConfig(
                provider="",  # Empty
                api_key="sk-test-key"
            )

    def test_bamboo_config_valid(self):
        """Test Bamboo configuration with valid data."""
        bamboo_config = BambooConfig(
            base_url="https://bamboo.example.com",
            username="bamboo_user",
            token="bamboo-api-token"
        )
        
        assert str(bamboo_config.base_url).rstrip('/') == "https://bamboo.example.com"
        assert bamboo_config.username == "bamboo_user"
        assert bamboo_config.token.get_secret_value() == "bamboo-api-token"

    def test_bamboo_config_empty_username(self):
        """Test BambooConfig validation fails with empty username."""
        with pytest.raises(ValueError, match="Bamboo username must not be empty"):
            BambooConfig(
                base_url="https://bamboo.example.com",
                username="",  # Empty
                token="secret-token"
            )