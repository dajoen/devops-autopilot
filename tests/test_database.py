"""Tests for database connection managers."""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime
from pydantic import AnyHttpUrl
from pydantic import SecretStr

from backend.models.config import DatabaseConfig, InfluxDBConfig
from backend.core.database import DatabaseManager
from backend.core.influxdb import InfluxDBManager


class TestDatabaseManager:
    """Test cases for DatabaseManager."""

    def test_database_manager_singleton(self):
        """Test that DatabaseManager implements singleton pattern."""
        manager1 = DatabaseManager()
        manager2 = DatabaseManager()
        db_manager = DatabaseManager()
        
        assert manager1 is manager2
        assert manager1 is db_manager

    def test_database_manager_initialization(self):
        """Test DatabaseManager initializes with correct configuration."""
        config = DatabaseConfig(
            host="localhost",
            port=5432,
            database="test_db",
            username="test_user",
            password=SecretStr("test_password")
        )
        
        with patch('backend.core.database.create_async_engine') as mock_create_engine, \
             patch('backend.core.database.async_sessionmaker') as mock_sessionmaker:
            
            mock_engine = AsyncMock()
            mock_session_factory = AsyncMock()
            mock_create_engine.return_value = mock_engine
            mock_sessionmaker.return_value = mock_session_factory
            
            manager = DatabaseManager()
            manager.initialize(config)
            
            # Verify engine creation was called with correct URL
            expected_url = "postgresql+asyncpg://test_user:test_password@localhost:5432/test_db"
            mock_create_engine.assert_called_once_with(
                expected_url,
                echo=False,
                pool_size=10,
                max_overflow=20,
                pool_pre_ping=True,
                pool_recycle=3600
            )

    @pytest.mark.asyncio
    async def test_database_manager_get_session(self):
        """Test getting database session context manager."""
        config = DatabaseConfig(
            database="test_db",
            username="test_user",
            password=SecretStr("test_password")
        )
        
        with patch('backend.core.database.create_async_engine') as mock_create_engine, \
             patch('backend.core.database.async_sessionmaker') as mock_sessionmaker:
            
            mock_engine = AsyncMock()
            mock_session_factory = Mock()  # Regular Mock for the factory
            mock_session = AsyncMock()
            
            # Set up the session factory to return an async context manager
            mock_session_context = AsyncMock()
            mock_session_context.__aenter__.return_value = mock_session
            mock_session_context.__aexit__.return_value = None
            
            mock_create_engine.return_value = mock_engine
            mock_sessionmaker.return_value = mock_session_factory
            mock_session_factory.return_value = mock_session_context
            
            manager = DatabaseManager()
            manager.initialize(config)
            
            async with manager.get_session() as session:
                assert session == mock_session
            
            # Verify that commit was called (from successful path)
            mock_session.commit.assert_called_once()
            mock_create_engine.assert_called_once()
            mock_sessionmaker.assert_called_once_with(bind=mock_engine, expire_on_commit=False)

    @pytest.mark.asyncio
    async def test_database_manager_session_rollback_on_error(self):
        """Test that database session rollback occurs on error."""
        config = DatabaseConfig(
            database="test_db",
            username="test_user",
            password=SecretStr("test_password")
        )
        
        with patch('backend.core.database.create_async_engine') as mock_create_engine, \
             patch('backend.core.database.async_sessionmaker') as mock_sessionmaker:
            
            mock_engine = AsyncMock()
            mock_session_factory = Mock()  # Regular Mock for the factory
            mock_session = AsyncMock()
            
            # Set up the session factory to return an async context manager
            mock_session_context = AsyncMock()
            mock_session_context.__aenter__.return_value = mock_session
            mock_session_context.__aexit__.return_value = None
            
            mock_create_engine.return_value = mock_engine
            mock_sessionmaker.return_value = mock_session_factory
            mock_session_factory.return_value = mock_session_context
            
            manager = DatabaseManager()
            manager.initialize(config)
            
            try:
                async with manager.get_session() as session:
                    raise ValueError("Test error")
            except ValueError:
                pass
            
            # Check that rollback was called on session
            mock_session.rollback.assert_called_once()

    @pytest.mark.asyncio
    async def test_database_manager_check_connection_success(self):
        """Test database connection check success."""
        config = DatabaseConfig(
            database="test_db",
            username="test_user",
            password=SecretStr("test_password")
        )
        
        with patch('backend.core.database.create_async_engine') as mock_create_engine:
            mock_engine = Mock()  # Regular Mock for the engine
            mock_connection = AsyncMock()
            
            # Set up the async context manager for engine.begin()
            mock_connection_context = AsyncMock()
            mock_connection_context.__aenter__.return_value = mock_connection
            mock_connection_context.__aexit__.return_value = None
            
            mock_create_engine.return_value = mock_engine
            mock_engine.begin.return_value = mock_connection_context
            
            manager = DatabaseManager()
            manager.initialize(config)
            
            result = await manager.check_connection()
            
            assert result is True
            mock_engine.begin.assert_called_once()

    @pytest.mark.asyncio
    async def test_database_manager_check_connection_failure(self):
        """Test database connection check failure."""
        config = DatabaseConfig(
            database="test_db",
            username="test_user",
            password=SecretStr("test_password")
        )
        
        with patch('backend.core.database.create_async_engine') as mock_create_engine:
            mock_engine = AsyncMock()
            mock_create_engine.return_value = mock_engine
            mock_engine.begin.side_effect = Exception("Connection failed")
            
            manager = DatabaseManager()
            manager.initialize(config)
            
            result = await manager.check_connection()
            
            assert result is False

    @pytest.mark.asyncio
    async def test_database_manager_create_tables(self):
        """Test database table creation."""
        config = DatabaseConfig(
            database="test_db",
            username="test_user",
            password=SecretStr("test_password")
        )
        
        with patch('backend.core.database.create_async_engine') as mock_create_engine, \
             patch('backend.models.base.SQLAlchemyBase.metadata') as mock_metadata:
            
            mock_engine = Mock()  # Regular Mock for the engine
            mock_connection = AsyncMock()
            
            # Set up the async context manager for engine.begin()
            mock_connection_context = AsyncMock()
            mock_connection_context.__aenter__.return_value = mock_connection
            mock_connection_context.__aexit__.return_value = None
            
            mock_create_engine.return_value = mock_engine
            mock_engine.begin.return_value = mock_connection_context
            
            manager = DatabaseManager()
            manager.initialize(config)
            
            await manager.create_tables()
            
            mock_engine.begin.assert_called_once()
            mock_connection.run_sync.assert_called_once_with(mock_metadata.create_all)

    @pytest.mark.asyncio
    async def test_database_manager_close(self):
        """Test database manager close."""
        config = DatabaseConfig(
            database="test_db",
            username="test_user",
            password=SecretStr("test_password")
        )
        
        with patch('backend.core.database.create_async_engine') as mock_create_engine, \
             patch('backend.core.database.async_sessionmaker') as mock_sessionmaker:
            mock_engine = Mock()  # Regular Mock for the engine
            mock_engine.dispose = AsyncMock()  # But dispose should be async
            mock_create_engine.return_value = mock_engine
            mock_sessionmaker.return_value = Mock()  # Mock session factory
            
            manager = DatabaseManager()
            manager.initialize(config)
            
            # Verify the engine was set
            assert manager._engine is mock_engine
            
            await manager.close()
            
            # Check that dispose was awaited
            mock_engine.dispose.assert_called_once()


class TestInfluxDBManager:
    """Test cases for InfluxDBManager."""

    def test_influxdb_manager_singleton(self):
        """Test that InfluxDBManager implements singleton pattern."""
        manager1 = InfluxDBManager()
        manager2 = InfluxDBManager()
        influx_manager = InfluxDBManager()
        
        assert manager1 is manager2
        assert manager1 is influx_manager

    def test_influxdb_manager_initialization_success(self):
        """Test InfluxDBManager initializes successfully with client."""
        config = InfluxDBConfig(
            url=AnyHttpUrl("http://localhost:8086"),
            token=SecretStr("test_token"),
            org="test_org",
            bucket="test_bucket"
        )
        
        with patch('influxdb_client.InfluxDBClient') as mock_client_class, \
             patch('influxdb_client.client.write_api.SYNCHRONOUS') as mock_synchronous:
            mock_client = Mock()
            mock_write_api = Mock()
            mock_query_api = Mock()
            mock_client_class.return_value = mock_client
            mock_client.write_api.return_value = mock_write_api
            mock_client.query_api.return_value = mock_query_api
            
            manager = InfluxDBManager()
            manager.initialize(config)
            
            # Check that client was created
            assert manager.client == mock_client
            mock_client_class.assert_called_once_with(
                url="http://localhost:8086/",
                token="test_token",
                org="test_org"
            )

    def test_influxdb_manager_initialization_no_client(self):
        """Test InfluxDBManager initialization when client creation fails."""
        config = InfluxDBConfig(
            url=AnyHttpUrl("http://localhost:8086"),
            token=SecretStr("test_token"),
            org="test_org",
            bucket="test_bucket"
        )
        
        with patch('influxdb_client.InfluxDBClient') as mock_client_class:
            mock_client_class.side_effect = ImportError("InfluxDB client not available")
            
            manager = InfluxDBManager()
            manager.initialize(config)
            
            # Check that client is None when import fails
            assert manager.client is None

    def test_influxdb_manager_write_point(self):
        """Test writing a point to InfluxDB."""
        config = InfluxDBConfig(
            url=AnyHttpUrl("http://localhost:8086"),
            token=SecretStr("test_token"),
            org="test_org",
            bucket="test_bucket"
        )
        
        with patch('influxdb_client.InfluxDBClient') as mock_client_class, \
             patch('influxdb_client.client.write_api.SYNCHRONOUS'):
            mock_client = Mock()
            mock_write_api = Mock()
            mock_client_class.return_value = mock_client
            mock_client.write_api.return_value = mock_write_api
            
            manager = InfluxDBManager()
            manager.initialize(config)
            
            # Test write_point method with correct signature
            result = manager.write_point(
                measurement="test_measurement",
                fields={"value": 1.0},
                tags={"tag1": "value1"}
            )
            
            assert result is True

    @pytest.mark.asyncio
    async def test_influxdb_manager_query(self):
        """Test querying InfluxDB."""
        config = InfluxDBConfig(
            url=AnyHttpUrl("http://localhost:8086"),
            token=SecretStr("test_token"),
            org="test_org",
            bucket="test_bucket"
        )
        
        with patch('influxdb_client.InfluxDBClient') as mock_client_class, \
             patch('influxdb_client.client.write_api.SYNCHRONOUS'):
            mock_client = Mock()
            mock_query_api = Mock()
            mock_client_class.return_value = mock_client
            mock_client.query_api.return_value = mock_query_api
            
            # Mock the actual result that would be returned
            expected_result = [{"test": "result"}]
            mock_query_api.query.return_value = expected_result
            
            manager = InfluxDBManager()
            manager.initialize(config)
            
            query = 'from(bucket:"test_bucket") |> range(start: -1h)'
            result = await manager.query(query)
            
            assert result == expected_result

    @pytest.mark.asyncio
    async def test_influxdb_manager_check_connection_available(self):
        """Test InfluxDB connection check when available."""
        config = InfluxDBConfig(
            url=AnyHttpUrl("http://localhost:8086"),
            token=SecretStr("test_token"),
            org="test_org",
            bucket="test_bucket"
        )
        
        with patch('influxdb_client.InfluxDBClient') as mock_client_class, \
             patch('influxdb_client.client.write_api.SYNCHRONOUS'):
            mock_client = Mock()
            mock_health = Mock()
            mock_health.status = "pass"
            mock_client_class.return_value = mock_client
            mock_client.health.return_value = mock_health
            
            manager = InfluxDBManager()
            manager.initialize(config)
            
            result = await manager.check_connection()
            
            assert result is True

    @pytest.mark.asyncio
    async def test_influxdb_manager_check_connection_unavailable(self):
        """Test InfluxDB connection check when unavailable."""
        manager = InfluxDBManager()
        # Ensure manager is in uninitialized state
        manager._client = None
        result = await manager.check_connection()
        
        assert result is False

    def test_influxdb_manager_close(self):
        """Test closing InfluxDB manager."""
        config = InfluxDBConfig(
            url=AnyHttpUrl("http://localhost:8086"),
            token=SecretStr("test_token"),
            org="test_org",
            bucket="test_bucket"
        )
        
        with patch('influxdb_client.InfluxDBClient') as mock_client_class, \
             patch('influxdb_client.client.write_api.SYNCHRONOUS'):
            mock_client = Mock()
            mock_client_class.return_value = mock_client
            
            manager = InfluxDBManager()
            manager.initialize(config)
            
            manager.close()
            
            mock_client.close.assert_called_once()
            assert manager.client is None


class TestDatabaseIntegration:
    """Integration tests for database managers."""

    def test_database_managers_can_coexist(self):
        """Test that both database managers can coexist."""
        db_config = DatabaseConfig(
            database="test_db",
            username="test_user",
            password=SecretStr("test_password")
        )
        
        influx_config = InfluxDBConfig(
            url=AnyHttpUrl("http://localhost:8086"),
            token=SecretStr("test_token"),
            org="test_org",
            bucket="test_bucket"
        )
        
        with patch('backend.core.database.create_async_engine'), \
             patch('influxdb_client.InfluxDBClient'), \
             patch.dict('sys.modules', {'influxdb_client': Mock()}):
            
            db_manager = DatabaseManager()
            influx_manager = InfluxDBManager()
            
            db_manager.initialize(db_config)
            influx_manager.initialize(influx_config)
            
            # Verify managers are different instances
            assert db_manager is not influx_manager
            # Verify they are singletons
            assert db_manager is DatabaseManager()
            assert influx_manager is InfluxDBManager()

    def test_database_config_url_property(self):
        """Test DatabaseConfig URL property generation."""
        config = DatabaseConfig(
            host="localhost",
            port=5432,
            database="test_db",
            username="test_user",
            password=SecretStr("test_password")
        )
        
        expected_url = "postgresql+asyncpg://test_user:test_password@localhost:5432/test_db"
        assert config.url == expected_url

    def test_database_config_validation(self):
        """Test DatabaseConfig field validation."""
        # Test valid configuration
        config = DatabaseConfig(
            database="test_db",
            username="test_user",
            password=SecretStr("test_password")
        )
        assert config.database == "test_db"
        assert config.username == "test_user"
        
        # Test empty database name validation
        with pytest.raises(ValueError, match="must not be empty"):
            DatabaseConfig(
                database="",
                username="test_user",
                password=SecretStr("test_password")
            )
        
        # Test empty username validation
        with pytest.raises(ValueError, match="must not be empty"):
            DatabaseConfig(
                database="test_db",
                username="",
                password=SecretStr("test_password")
            )

    def test_influxdb_config_validation(self):
        """Test InfluxDBConfig field validation."""
        # Test valid configuration
        config = InfluxDBConfig(
            url=AnyHttpUrl("http://localhost:8086"),
            token=SecretStr("test_token"),
            org="test_org",
            bucket="test_bucket"
        )
        assert str(config.url) == "http://localhost:8086/"
        assert config.token.get_secret_value() == "test_token"
        
        # Test empty org validation
        with pytest.raises(ValueError, match="must not be empty"):
            InfluxDBConfig(
                url=AnyHttpUrl("http://localhost:8086"),
                token=SecretStr("test_token"),
                org="",
                bucket="test_bucket"
            )
        
        # Test empty bucket validation
        with pytest.raises(ValueError, match="must not be empty"):
            InfluxDBConfig(
                url=AnyHttpUrl("http://localhost:8086"),
                token=SecretStr("test_token"),
                org="test_org",
                bucket=""
            )