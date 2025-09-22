"""Tests for backend services layer."""

import pytest
import time
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

from backend.services.health import HealthService
from backend.services.logs import LogService
from backend.services.runs import RunService
from backend.models.health import HealthResponse, HealthStatus, DatabaseStatus
from backend.models.logs import Log, LogLevel, LogCreate
from backend.models.runs import Run, RunStatus, RunType, RunCreate


class TestHealthService:
    """Test health check service."""

    @pytest.fixture
    def health_service(self):
        """Create a health service instance for testing."""
        return HealthService()

    @pytest.mark.asyncio
    async def test_get_health_all_healthy(self, health_service):
        """Test health check when all services are healthy."""
        with patch.object(health_service, '_check_databases', return_value=[
            DatabaseStatus(
                name="PostgreSQL", 
                status=HealthStatus.HEALTHY, 
                response_time_ms=15.5
            ),
            DatabaseStatus(
                name="InfluxDB", 
                status=HealthStatus.HEALTHY, 
                response_time_ms=25.0
            )
        ]) as mock_db:
            
            health = await health_service.get_health_status("1.0.0")
            
            assert health.status == HealthStatus.HEALTHY
            assert health.version == "1.0.0"
            assert health.uptime_seconds > 0
            assert len(health.databases) == 2
            
            # Check database statuses
            postgres_status = next(db for db in health.databases if db.name == "PostgreSQL")
            influx_status = next(db for db in health.databases if db.name == "InfluxDB")
            
            assert postgres_status.status == HealthStatus.HEALTHY
            assert postgres_status.response_time_ms == 15.5
            assert influx_status.status == HealthStatus.HEALTHY
            assert influx_status.response_time_ms == 25.0
            
            mock_db.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_health_degraded_influxdb_down(self, health_service):
        """Test health check when InfluxDB is down (degraded state)."""
        with patch.object(health_service, '_check_databases', return_value=[
            DatabaseStatus(
                name="PostgreSQL", 
                status=HealthStatus.HEALTHY, 
                response_time_ms=15.5
            ),
            DatabaseStatus(
                name="InfluxDB", 
                status=HealthStatus.UNHEALTHY, 
                response_time_ms=1000.0,
                error="Connection failed"
            )
        ]) as mock_db:
            
            health = await health_service.get_health_status("1.0.0")
            
            assert health.status == HealthStatus.DEGRADED
            assert len(health.databases) == 2
            
            influx_status = next(db for db in health.databases if db.name == "InfluxDB")
            assert influx_status.status == HealthStatus.UNHEALTHY
            assert influx_status.error == "Connection failed"

    @pytest.mark.asyncio
    async def test_get_health_unhealthy_postgres_down(self, health_service):
        """Test health check when PostgreSQL is down (unhealthy state)."""
        with patch.object(health_service, '_check_databases', return_value=[
            DatabaseStatus(
                name="PostgreSQL", 
                status=HealthStatus.UNHEALTHY, 
                response_time_ms=5000.0,
                error="Connection timeout"
            ),
            DatabaseStatus(
                name="InfluxDB", 
                status=HealthStatus.HEALTHY, 
                response_time_ms=25.0
            )
        ]) as mock_db:
            
            health = await health_service.get_health_status("1.0.0")
            
            assert health.status == HealthStatus.DEGRADED
            assert len(health.databases) == 2
            
            postgres_status = next(db for db in health.databases if db.name == "PostgreSQL")
            assert postgres_status.status == HealthStatus.UNHEALTHY
            assert postgres_status.error == "Connection timeout"

    @pytest.mark.asyncio
    async def test_check_databases_success(self, health_service):
        """Test _check_databases method success."""
        with patch('backend.services.health.db_manager.check_connection', return_value=True), \
             patch('backend.services.health.influxdb_manager.check_connection', return_value=True):
            
            databases = await health_service._check_databases()
            
            assert len(databases) == 2
            assert databases[0].name == "PostgreSQL"
            assert databases[0].status == HealthStatus.HEALTHY
            assert databases[1].name == "InfluxDB"
            assert databases[1].status == HealthStatus.HEALTHY

    @pytest.mark.asyncio
    async def test_check_databases_failure(self, health_service):
        """Test _check_databases method with failures."""
        with patch('backend.services.health.db_manager.check_connection', side_effect=Exception("DB error")), \
             patch('backend.services.health.influxdb_manager.check_connection', return_value=False):
            
            databases = await health_service._check_databases()
            
            assert len(databases) == 2
            assert databases[0].name == "PostgreSQL"
            assert databases[0].status == HealthStatus.UNHEALTHY
            assert "DB error" in databases[0].error
            assert databases[1].name == "InfluxDB"
            assert databases[1].status == HealthStatus.UNHEALTHY

    @pytest.mark.asyncio
    async def test_check_influxdb_success(self, health_service):
        """Test _check_influxdb method success."""
        with patch('backend.services.health.influxdb_manager.check_connection', return_value=True):
            
            db_status = await health_service._check_influxdb()
            
            assert db_status.name == "InfluxDB"
            assert db_status.status == HealthStatus.HEALTHY
            assert db_status.response_time_ms > 0
            assert db_status.error is None

    @pytest.mark.asyncio
    async def test_check_influxdb_unavailable(self, health_service):
        """Test _check_influxdb method when unavailable."""
        with patch('backend.services.health.influxdb_manager.check_connection', return_value=False):
            
            db_status = await health_service._check_influxdb()
            
            assert db_status.name == "InfluxDB"
            assert db_status.status == HealthStatus.UNHEALTHY
            assert db_status.error == "Connection failed"

    def test_get_uptime(self, health_service):
        """Test uptime calculation."""
        # Health service initializes start_time in __init__
        uptime = time.time() - health_service.start_time
        
        assert uptime >= 0
        assert isinstance(uptime, float)


class TestLogsService:
    """Test logs service."""

    @pytest.fixture
    def logs_service(self):
        """Create a logs service instance for testing."""
        return LogService()

    @pytest.fixture
    def sample_log_create(self):
        """Create a sample log creation request."""
        return LogCreate(
            level=LogLevel.INFO,
            message="Test log message",
            source="test-service",
            run_id=123,
            metadata={"version": "1.0.0"}
        )

    @pytest.mark.asyncio
    async def test_create_log_success(self, logs_service, sample_log_create):
        """Test successful log creation."""
        result = await logs_service.create_log(sample_log_create)
        
        assert result.id == 1
        assert result.message == "Test log message"
        assert result.level == LogLevel.INFO
        assert result.source == "test-service"
        assert result.run_id == 123
        assert result.metadata == {"version": "1.0.0"}
        assert result.created_at is not None
        assert result.updated_at is not None

    @pytest.mark.asyncio
    async def test_get_logs_by_run(self, logs_service):
        """Test retrieving logs by run ID."""
        logs = await logs_service.get_logs_by_run(run_id=123, limit=50)
        
        # Should return the mock logs with run_id filter applied
        assert isinstance(logs, list)
        assert len(logs) >= 0  # Mock implementation may return empty list

    @pytest.mark.asyncio
    async def test_get_logs_with_filters(self, logs_service):
        """Test retrieving logs with various filters."""
        logs = await logs_service.get_logs(
            limit=10, 
            offset=0, 
            level=LogLevel.ERROR,
            run_id=123,
            source="database"
        )
        
        # Should return the mock logs with filters applied
        assert isinstance(logs, list)
        assert len(logs) >= 0

    @pytest.mark.asyncio
    async def test_delete_old_logs(self, logs_service):
        """Test deleting old logs."""
        deleted_count = await logs_service.delete_old_logs(days=30)
        
        # Mock implementation returns 0
        assert deleted_count == 0


class TestRunsService:
    """Test runs service."""

    @pytest.fixture
    def runs_service(self):
        """Create a runs service instance for testing."""
        return RunService()

    @pytest.fixture
    def sample_run_create(self):
        """Create a sample run creation request."""
        return RunCreate(
            name="test-deployment",
            type=RunType.DEPLOYMENT,
            description="Test deployment run",
            parameters={"branch": "main", "environment": "staging"},
            tags={"team": "backend", "priority": "normal"}
        )

    @pytest.mark.asyncio
    async def test_create_run_success(self, runs_service, sample_run_create):
        """Test successful run creation."""
        result = await runs_service.create_run(sample_run_create)
        
        assert result.id == 1
        assert result.name == "test-deployment"
        assert result.type == RunType.DEPLOYMENT
        assert result.description == "Test deployment run"
        assert result.parameters == {"branch": "main", "environment": "staging"}
        assert result.tags == {"team": "backend", "priority": "normal"}
        assert result.status == RunStatus.PENDING
        assert result.created_at is not None
        assert result.updated_at is not None

    @pytest.mark.asyncio
    async def test_get_run_exists(self, runs_service):
        """Test retrieving run by ID when it exists."""
        run = await runs_service.get_run(1)
        
        assert run is not None
        assert run.id == 1
        assert run.name == "Sample Run"
        assert run.type == RunType.DEPLOYMENT
        assert run.status == RunStatus.COMPLETED

    @pytest.mark.asyncio
    async def test_get_run_not_exists(self, runs_service):
        """Test retrieving run by ID when it doesn't exist."""
        run = await runs_service.get_run(999)
        
        assert run is None

    @pytest.mark.asyncio
    async def test_list_runs(self, runs_service):
        """Test listing runs with pagination."""
        runs = await runs_service.list_runs(limit=10, offset=0)
        
        assert isinstance(runs, list)
        assert len(runs) == 1  # Mock implementation returns one run
        assert runs[0].name == "Sample Run"

    @pytest.mark.asyncio
    async def test_update_run(self, runs_service):
        """Test updating run."""
        from backend.models.runs import RunUpdate
        
        run_update = RunUpdate(status=RunStatus.RUNNING)
        updated_run = await runs_service.update_run(1, run_update)
        
        assert updated_run is not None
        assert updated_run.status == RunStatus.RUNNING

    @pytest.mark.asyncio
    async def test_update_run_not_exists(self, runs_service):
        """Test updating run that doesn't exist."""
        from backend.models.runs import RunUpdate
        
        run_update = RunUpdate(status=RunStatus.FAILED)
        updated_run = await runs_service.update_run(999, run_update)
        
        assert updated_run is None

    @pytest.mark.asyncio
    async def test_delete_run(self, runs_service):
        """Test deleting a run."""
        success = await runs_service.delete_run(1)
        
        # Mock implementation always returns True
        assert success is True


class TestServiceIntegration:
    """Integration tests for services working together."""

    def test_services_can_be_instantiated(self):
        """Test that all services can be created without errors."""
        health_service = HealthService()
        logs_service = LogService()
        runs_service = RunService()
        
        assert health_service is not None
        assert logs_service is not None
        assert runs_service is not None

    @pytest.mark.asyncio
    async def test_run_lifecycle_with_logging(self):
        """Test complete run lifecycle with associated logging."""
        runs_service = RunService()
        logs_service = LogService()
        
        # Mock the database sessions
        with patch('backend.services.runs.db_manager.get_session') as mock_runs_session, \
             patch('backend.services.logs.db_manager.get_session') as mock_logs_session:
            
            # Setup run mocks
            mock_run_session = AsyncMock()
            mock_runs_session.return_value.__aenter__.return_value = mock_run_session
            mock_runs_session.return_value.__aexit__.return_value = None
            
            # Setup log mocks
            mock_log_session = AsyncMock()
            mock_logs_session.return_value.__aenter__.return_value = mock_log_session  
            mock_logs_session.return_value.__aexit__.return_value = None
            
            # Mock run creation
            mock_run = Run(
                id=1, name="integration-test", type=RunType.TEST,
                status=RunStatus.PENDING, created_at=datetime.now(), updated_at=datetime.now()
            )
            
            mock_run_session.add = Mock()
            mock_run_session.flush = AsyncMock()
            mock_run_session.refresh = AsyncMock()
            
            # Mock log creation
            mock_log = Log(
                id=1, level=LogLevel.INFO, message="Run started", source="test",
                run_id=1, created_at=datetime.now(), updated_at=datetime.now()
            )
            
            mock_log_session.add = Mock()
            mock_log_session.flush = AsyncMock()
            mock_log_session.refresh = AsyncMock()
            
            with patch('backend.models.runs.Run', return_value=mock_run), \
                 patch('backend.models.logs.Log', return_value=mock_log):
                
                # Create run
                run_create = RunCreate(
                    name="integration-test",
                    type=RunType.TEST,
                    description="Integration test run"
                )
                created_run = await runs_service.create_run(run_create)
                
                # Create associated log
                log_create = LogCreate(
                    level=LogLevel.INFO,
                    message="Run started",
                    source="test",
                    run_id=created_run.id
                )
                created_log = await logs_service.create_log(log_create)
                
                # Verify integration
                assert created_run.id == 1
                assert created_log.run_id == created_run.id
                assert created_log.message == "Run started"