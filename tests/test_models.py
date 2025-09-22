"""Tests for data models and validation."""

import pytest
from datetime import datetime
from pydantic import ValidationError

from backend.models.health import HealthResponse, HealthStatus, DatabaseStatus
from backend.models.runs import Run, RunStatus, RunType
from backend.models.logs import Log, LogLevel


"""Tests for data models and validation."""

import pytest
from datetime import datetime
from pydantic import ValidationError

from backend.models.health import HealthResponse, HealthStatus, DatabaseStatus
from backend.models.runs import Run, RunStatus, RunType, RunCreate
from backend.models.logs import Log, LogLevel, LogCreate


class TestHealthModels:
    """Test health check models."""

    def test_health_status_enum_values(self):
        """Test HealthStatus enum has expected values."""
        assert HealthStatus.HEALTHY == "healthy"
        assert HealthStatus.UNHEALTHY == "unhealthy"
        assert HealthStatus.DEGRADED == "degraded"

    def test_database_status_healthy(self):
        """Test DatabaseStatus with healthy status."""
        status = DatabaseStatus(
            name="postgres",
            status=HealthStatus.HEALTHY,
            response_time_ms=15.5
        )
        
        assert status.name == "postgres"
        assert status.status == HealthStatus.HEALTHY
        assert status.response_time_ms == 15.5
        assert status.error is None

    def test_database_status_unhealthy(self):
        """Test DatabaseStatus with unhealthy status."""
        status = DatabaseStatus(
            name="influxdb",
            status=HealthStatus.UNHEALTHY,
            error="Connection timeout"
        )
        
        assert status.name == "influxdb"
        assert status.status == HealthStatus.UNHEALTHY
        assert status.response_time_ms is None
        assert status.error == "Connection timeout"

    def test_health_response_valid(self):
        """Test HealthResponse with valid data."""
        health = HealthResponse(
            status=HealthStatus.HEALTHY,
            timestamp=datetime.now(),
            version="1.0.0",
            uptime_seconds=3600.5,
            databases=[
                DatabaseStatus(name="postgres", status=HealthStatus.HEALTHY, response_time_ms=10.0),
                DatabaseStatus(name="influxdb", status=HealthStatus.HEALTHY, response_time_ms=25.5)
            ]
        )
        
        assert health.status == HealthStatus.HEALTHY
        assert health.version == "1.0.0"
        assert health.uptime_seconds == 3600.5
        assert len(health.databases) == 2
        assert health.databases[0].name == "postgres"
        assert health.databases[1].name == "influxdb"

    def test_health_response_degraded(self):
        """Test HealthResponse with degraded status."""
        health = HealthResponse(
            status=HealthStatus.DEGRADED,
            timestamp=datetime.now(),
            version="1.0.0",
            uptime_seconds=1800.0,
            databases=[
                DatabaseStatus(name="postgres", status=HealthStatus.HEALTHY, response_time_ms=10.0),
                DatabaseStatus(name="influxdb", status=HealthStatus.UNHEALTHY, error="Connection failed")
            ]
        )
        
        assert health.status == HealthStatus.DEGRADED
        assert health.databases[0].status == HealthStatus.HEALTHY
        assert health.databases[1].status == HealthStatus.UNHEALTHY
        assert health.databases[1].error == "Connection failed"


class TestRunModels:
    """Test DevOps run models."""

    def test_run_status_enum_values(self):
        """Test RunStatus enum has expected values."""
        assert RunStatus.PENDING == "pending"
        assert RunStatus.RUNNING == "running"
        assert RunStatus.COMPLETED == "completed"
        assert RunStatus.FAILED == "failed"
        assert RunStatus.CANCELLED == "cancelled"

    def test_run_type_enum_values(self):
        """Test RunType enum has expected values."""
        assert RunType.DEPLOYMENT == "deployment"
        assert RunType.PIPELINE == "pipeline"
        assert RunType.BACKUP == "backup"
        assert RunType.MAINTENANCE == "maintenance"
        assert RunType.TEST == "test"
        assert RunType.OTHER == "other"

    def test_run_create_valid(self):
        """Test RunCreate model with valid data."""
        run_create = RunCreate(
            name="deploy-api",
            type=RunType.DEPLOYMENT,
            description="Deploy API to production",
            parameters={"branch": "main", "environment": "prod"},
            tags={"team": "backend", "priority": "high"}
        )
        
        assert run_create.name == "deploy-api"
        assert run_create.type == RunType.DEPLOYMENT
        assert run_create.description == "Deploy API to production"
        assert run_create.parameters is not None
        assert run_create.parameters["branch"] == "main"
        assert run_create.tags is not None
        assert run_create.tags["team"] == "backend"

    def test_run_valid_creation(self):
        """Test Run model with valid data."""
        now = datetime.now()
        run = Run(
            id=1,
            name="test-deployment",
            type=RunType.DEPLOYMENT,
            status=RunStatus.RUNNING,
            created_at=now,
            updated_at=now,
            started_at=now,
            duration_seconds=300.5,
            parameters={"branch": "main", "commit": "abc123"}
        )
        
        assert run.id == 1
        assert run.name == "test-deployment"
        assert run.type == RunType.DEPLOYMENT
        assert run.status == RunStatus.RUNNING
        assert run.duration_seconds == 300.5
        assert run.parameters is not None
        assert run.parameters["branch"] == "main"

    def test_run_with_minimal_data(self):
        """Test Run model with only required fields."""
        now = datetime.now()
        run = Run(
            id=2,
            name="minimal-run",
            type=RunType.OTHER,
            created_at=now,
            updated_at=now
        )
        
        assert run.id == 2
        assert run.name == "minimal-run"
        assert run.type == RunType.OTHER
        assert run.status == RunStatus.PENDING  # Default value
        assert run.duration_seconds is None
        assert run.parameters is None

    def test_run_invalid_status(self):
        """Test Run validation fails with invalid status."""
        with pytest.raises(ValidationError):
            # Use dict approach to bypass type checking
            invalid_data = {
                "id": 1,
                "name": "test-run",
                "type": RunType.TEST,
                "status": "invalid-status",  # Not a valid RunStatus
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
            Run(**invalid_data)

    def test_log_entry_invalid_level(self):
        """Test Log validation fails with invalid log level."""
        with pytest.raises(ValidationError):
            # Use dict approach to bypass type checking
            invalid_data = {
                "id": 1,
                "level": "invalid-level",  # Not a valid LogLevel
                "message": "Test message",
                "source": "test-service",
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
            Log(**invalid_data)


class TestLogModels:
    """Test logging models."""

    def test_log_level_enum_values(self):
        """Test LogLevel enum has expected values."""
        assert LogLevel.DEBUG == "debug"
        assert LogLevel.INFO == "info"
        assert LogLevel.WARNING == "warning"
        assert LogLevel.ERROR == "error"
        assert LogLevel.CRITICAL == "critical"

    def test_log_create_valid(self):
        """Test LogCreate model with valid data."""
        log_create = LogCreate(
            level=LogLevel.INFO,
            message="Application started successfully",
            source="api-server",
            run_id=123,
            metadata={"version": "1.0.0", "environment": "production"}
        )
        
        assert log_create.level == LogLevel.INFO
        assert log_create.message == "Application started successfully"
        assert log_create.source == "api-server"
        assert log_create.run_id == 123
        assert log_create.metadata is not None
        assert log_create.metadata["version"] == "1.0.0"

    def test_log_entry_valid_creation(self):
        """Test Log model with valid data."""
        now = datetime.now()
        log = Log(
            id=1,
            level=LogLevel.INFO,
            message="User logged in",
            source="auth-service",
            run_id=456,
            created_at=now,
            updated_at=now,
            metadata={"user_id": "123", "ip": "192.168.1.1"}
        )
        
        assert log.id == 1
        assert log.level == LogLevel.INFO
        assert log.message == "User logged in"
        assert log.source == "auth-service"
        assert log.run_id == 456
        assert log.metadata is not None
        assert log.metadata["user_id"] == "123"

    def test_log_entry_minimal_data(self):
        """Test Log with only required fields."""
        now = datetime.now()
        log = Log(
            id=2,
            level=LogLevel.ERROR,
            message="Database connection failed",
            source="db-service",
            created_at=now,
            updated_at=now
        )
        
        assert log.id == 2
        assert log.level == LogLevel.ERROR
        assert log.message == "Database connection failed"
        assert log.source == "db-service"
        assert log.run_id is None
        assert log.metadata is None

    def test_log_entry_invalid_level(self):
        """Test Log validation fails with invalid log level."""
        with pytest.raises(ValidationError):
            # Use dict approach to bypass type checking
            invalid_data = {
                "id": 1,
                "level": "invalid-level",  # Not a valid LogLevel
                "message": "Test message",
                "source": "test-service",
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
            Log(**invalid_data)


class TestModelSerialization:
    """Test model serialization and deserialization."""

    def test_database_status_json_serialization(self):
        """Test DatabaseStatus can be serialized to JSON."""
        status = DatabaseStatus(
            name="postgres",
            status=HealthStatus.HEALTHY,
            response_time_ms=15.5
        )
        
        json_data = status.model_dump()
        
        assert json_data["name"] == "postgres"
        assert json_data["status"] == "healthy"
        assert json_data["response_time_ms"] == 15.5
        assert json_data["error"] is None

    def test_run_json_serialization(self):
        """Test Run model can be serialized to JSON."""
        run = Run(
            id=1,
            name="test-run",
            type=RunType.DEPLOYMENT,
            status=RunStatus.COMPLETED,
            created_at=datetime(2023, 1, 1, 12, 0, 0),
            updated_at=datetime(2023, 1, 1, 12, 5, 0),
            duration_seconds=300.5,
            parameters={"key": "value"}
        )
        
        json_data = run.model_dump()
        
        assert json_data["id"] == 1
        assert json_data["name"] == "test-run"
        assert json_data["type"] == "deployment"
        assert json_data["status"] == "completed"
        assert json_data["duration_seconds"] == 300.5
        assert json_data["parameters"]["key"] == "value"

    def test_log_json_serialization(self):
        """Test Log can be serialized to JSON."""
        log = Log(
            id=1,
            level=LogLevel.WARNING,
            message="High CPU usage detected",
            source="monitor",
            run_id=456,
            created_at=datetime(2023, 1, 1, 12, 0, 0),
            updated_at=datetime(2023, 1, 1, 12, 0, 0)
        )
        
        json_data = log.model_dump()
        
        assert json_data["id"] == 1
        assert json_data["level"] == "warning"
        assert json_data["message"] == "High CPU usage detected"
        assert json_data["source"] == "monitor"
        assert json_data["run_id"] == 456

    def test_model_deserialization_from_dict(self):
        """Test models can be created from dictionary data."""
        status_data = {
            "name": "api",
            "status": "healthy",
            "response_time_ms": 12.5
        }
        
        status = DatabaseStatus(**status_data)
        
        assert status.name == "api"
        assert status.status == HealthStatus.HEALTHY
        assert status.response_time_ms == 12.5

    def test_model_validation_on_deserialization(self):
        """Test validation works when deserializing from dict."""
        invalid_data = {
            "name": "test-service",
            "status": "invalid-status",  # Invalid
            "response_time_ms": 10.0
        }
        
        with pytest.raises(ValidationError):
            DatabaseStatus(**invalid_data)