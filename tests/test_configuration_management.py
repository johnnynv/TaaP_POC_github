"""Configuration management tests for cloud native testing platform."""

import pytest
import os
import tempfile
import yaml
from unittest.mock import Mock, patch, mock_open
from src.config import Config, DatabaseConfig, RedisConfig, APIConfig, ContainerConfig, MonitoringConfig


class TestConfigurationLoading:
    """Test configuration loading and validation (20 tests)."""
    
    @pytest.mark.unit
    def test_default_config_initialization(self):
        """Test default configuration initialization."""
        config = Config()
        
        assert config.database.host == "localhost"
        assert config.database.port == 5432
        assert config.redis.host == "localhost"
        assert config.redis.port == 6379
        assert config.api.base_url == "http://localhost:8080"

    @pytest.mark.unit
    def test_config_from_yaml_file(self):
        """Test configuration loading from YAML file."""
        yaml_content = """
database:
  host: db.example.com
  port: 5433
  name: prod_db
redis:
  host: redis.example.com
  port: 6380
api:
  base_url: https://api.example.com
  timeout: 60
"""
        
        with patch("builtins.open", mock_open(read_data=yaml_content)):
            config = Config(config_file="test_config.yaml")
            
            assert config.database.host == "db.example.com"
            assert config.database.port == 5433
            assert config.database.name == "prod_db"
            assert config.redis.host == "redis.example.com"
            assert config.api.base_url == "https://api.example.com"

    @pytest.mark.unit
    def test_config_from_environment_variables(self):
        """Test configuration loading from environment variables."""
        env_vars = {
            "DB_HOST": "env-db.example.com",
            "DB_PORT": "5434",
            "DB_NAME": "env_db",
            "REDIS_HOST": "env-redis.example.com",
            "API_BASE_URL": "https://env-api.example.com"
        }
        
        with patch.dict(os.environ, env_vars):
            config = Config()
            
            assert config.database.host == "env-db.example.com"
            assert config.database.port == 5434
            assert config.database.name == "env_db"
            assert config.redis.host == "env-redis.example.com"
            assert config.api.base_url == "https://env-api.example.com"

    @pytest.mark.unit
    def test_config_validation_success(self):
        """Test successful configuration validation."""
        config = Config()
        config.database.host = "valid-host.com"
        config.api.base_url = "https://valid-api.com"
        
        result = config.validate()
        assert result is True

    @pytest.mark.unit
    def test_config_validation_missing_db_host(self):
        """Test configuration validation with missing database host."""
        config = Config()
        config.database.host = ""
        
        with pytest.raises(ValueError, match="Database host is required"):
            config.validate()

    @pytest.mark.unit
    def test_config_validation_missing_api_url(self):
        """Test configuration validation with missing API URL."""
        config = Config()
        config.api.base_url = ""
        
        with pytest.raises(ValueError, match="API base URL is required"):
            config.validate()

    @pytest.mark.unit
    def test_config_validation_invalid_db_port(self):
        """Test configuration validation with invalid database port."""
        config = Config()
        config.database.port = 70000
        
        with pytest.raises(ValueError, match="Invalid database port"):
            config.validate()

    @pytest.mark.unit
    def test_config_validation_invalid_redis_port(self):
        """Test configuration validation with invalid Redis port."""
        config = Config()
        config.redis.port = -1
        
        with pytest.raises(ValueError, match="Invalid Redis port"):
            config.validate()

    @pytest.mark.unit
    def test_config_to_dict_conversion(self):
        """Test configuration to dictionary conversion."""
        config = Config()
        config_dict = config.to_dict()
        
        assert isinstance(config_dict, dict)
        assert "database" in config_dict
        assert "redis" in config_dict
        assert "api" in config_dict
        assert "container" in config_dict
        assert "monitoring" in config_dict

    @pytest.mark.unit
    def test_config_file_not_found(self):
        """Test handling of missing configuration file."""
        with patch("builtins.open", side_effect=FileNotFoundError):
            with patch("builtins.print") as mock_print:
                config = Config(config_file="nonexistent.yaml")
                mock_print.assert_called()
                # Should still have default values
                assert config.database.host == "localhost"

    @pytest.mark.unit
    def test_config_invalid_yaml(self):
        """Test handling of invalid YAML content."""
        invalid_yaml = "invalid: yaml: content: [unclosed"
        
        with patch("builtins.open", mock_open(read_data=invalid_yaml)):
            with patch("builtins.print") as mock_print:
                config = Config(config_file="invalid.yaml")
                mock_print.assert_called()
                # Should still have default values
                assert config.database.host == "localhost"

    @pytest.mark.unit
    def test_partial_config_override(self):
        """Test partial configuration override."""
        yaml_content = """
database:
  host: custom-db.com
# Other sections not specified should keep defaults
"""
        
        with patch("builtins.open", mock_open(read_data=yaml_content)):
            config = Config(config_file="partial.yaml")
            
            assert config.database.host == "custom-db.com"
            assert config.database.port == 5432  # Default value
            assert config.redis.host == "localhost"  # Default value

    @pytest.mark.unit
    def test_nested_config_override(self):
        """Test nested configuration parameter override."""
        yaml_content = """
container:
  resource_limits:
    cpu: "1000m"
    memory: "1Gi"
    storage: "10Gi"
"""
        
        with patch("builtins.open", mock_open(read_data=yaml_content)):
            config = Config(config_file="nested.yaml")
            
            assert config.container.resource_limits["cpu"] == "1000m"
            assert config.container.resource_limits["memory"] == "1Gi"
            assert config.container.resource_limits["storage"] == "10Gi"

    @pytest.mark.unit
    def test_environment_variable_type_conversion(self):
        """Test automatic type conversion for environment variables."""
        env_vars = {
            "DB_PORT": "3306",
            "REDIS_PORT": "6380"
        }
        
        with patch.dict(os.environ, env_vars):
            config = Config()
            
            assert isinstance(config.database.port, int)
            assert config.database.port == 3306
            assert isinstance(config.redis.port, int)
            assert config.redis.port == 6380

    @pytest.mark.unit
    def test_config_with_special_characters(self):
        """Test configuration with special characters in values."""
        yaml_content = """
database:
  password: "p@ssw0rd!#$%"
  user: "user-with-dashes"
api:
  base_url: "https://api.example.com:8443/v1"
"""
        
        with patch("builtins.open", mock_open(read_data=yaml_content)):
            config = Config(config_file="special.yaml")
            
            assert config.database.password == "p@ssw0rd!#$%"
            assert config.database.user == "user-with-dashes"
            assert config.api.base_url == "https://api.example.com:8443/v1"

    @pytest.mark.unit
    def test_config_boolean_values(self):
        """Test configuration with boolean values."""
        yaml_content = """
monitoring:
  metrics_enabled: false
  tracing_enabled: true
api:
  verify_ssl: false
"""
        
        with patch("builtins.open", mock_open(read_data=yaml_content)):
            config = Config(config_file="boolean.yaml")
            
            assert config.monitoring.metrics_enabled is False
            assert config.monitoring.tracing_enabled is True
            assert config.api.verify_ssl is False

    @pytest.mark.unit
    def test_config_list_values(self):
        """Test configuration with list/array values."""
        yaml_content = """
container:
  resource_limits:
    allowed_images:
      - "nginx:latest"
      - "redis:6.2"
      - "postgres:13"
"""
        
        with patch("builtins.open", mock_open(read_data=yaml_content)):
            config = Config(config_file="list.yaml")
            
            expected_images = ["nginx:latest", "redis:6.2", "postgres:13"]
            assert config.container.resource_limits.get("allowed_images") == expected_images

    @pytest.mark.unit
    def test_config_null_values(self):
        """Test configuration with null/None values."""
        yaml_content = """
redis:
  password: null
api:
  auth_token: null
container:
  k8s_config_path: null
"""
        
        with patch("builtins.open", mock_open(read_data=yaml_content)):
            config = Config(config_file="null.yaml")
            
            assert config.redis.password is None
            assert config.api.auth_token is None
            assert config.container.k8s_config_path is None

    @pytest.mark.unit
    def test_config_numeric_values(self):
        """Test configuration with various numeric values."""
        yaml_content = """
database:
  pool_size: 20
  max_overflow: 50
redis:
  socket_timeout: 10
  max_connections: 100
api:
  timeout: 45
  retries: 5
  rate_limit: 200
"""
        
        with patch("builtins.open", mock_open(read_data=yaml_content)):
            config = Config(config_file="numeric.yaml")
            
            assert config.database.pool_size == 20
            assert config.database.max_overflow == 50
            assert config.redis.socket_timeout == 10
            assert config.api.timeout == 45
            assert config.api.rate_limit == 200


class TestConfigurationDataClasses:
    """Test individual configuration dataclasses (20 tests)."""
    
    @pytest.mark.unit
    def test_database_config_defaults(self):
        """Test DatabaseConfig default values."""
        db_config = DatabaseConfig()
        
        assert db_config.host == "localhost"
        assert db_config.port == 5432
        assert db_config.name == "taap_db"
        assert db_config.user == "taap_user"
        assert db_config.password == ""
        assert db_config.ssl_mode == "prefer"
        assert db_config.pool_size == 10
        assert db_config.max_overflow == 20

    @pytest.mark.unit
    def test_database_config_custom_values(self):
        """Test DatabaseConfig with custom values."""
        db_config = DatabaseConfig(
            host="custom-db.com",
            port=5433,
            name="custom_db",
            user="custom_user",
            password="custom_pass",
            ssl_mode="require",
            pool_size=15,
            max_overflow=30
        )
        
        assert db_config.host == "custom-db.com"
        assert db_config.port == 5433
        assert db_config.name == "custom_db"
        assert db_config.user == "custom_user"
        assert db_config.password == "custom_pass"
        assert db_config.ssl_mode == "require"
        assert db_config.pool_size == 15
        assert db_config.max_overflow == 30

    @pytest.mark.unit
    def test_redis_config_defaults(self):
        """Test RedisConfig default values."""
        redis_config = RedisConfig()
        
        assert redis_config.host == "localhost"
        assert redis_config.port == 6379
        assert redis_config.db == 0
        assert redis_config.password is None
        assert redis_config.socket_timeout == 5
        assert redis_config.max_connections == 50

    @pytest.mark.unit
    def test_redis_config_with_password(self):
        """Test RedisConfig with password."""
        redis_config = RedisConfig(
            host="redis.example.com",
            port=6380,
            db=1,
            password="redis_password",
            socket_timeout=10,
            max_connections=100
        )
        
        assert redis_config.host == "redis.example.com"
        assert redis_config.port == 6380
        assert redis_config.db == 1
        assert redis_config.password == "redis_password"
        assert redis_config.socket_timeout == 10
        assert redis_config.max_connections == 100

    @pytest.mark.unit
    def test_api_config_defaults(self):
        """Test APIConfig default values."""
        api_config = APIConfig()
        
        assert api_config.base_url == "http://localhost:8080"
        assert api_config.timeout == 30
        assert api_config.retries == 3
        assert api_config.rate_limit == 100
        assert api_config.auth_token is None
        assert api_config.verify_ssl is True

    @pytest.mark.unit
    def test_api_config_with_auth(self):
        """Test APIConfig with authentication."""
        api_config = APIConfig(
            base_url="https://secure-api.com",
            timeout=60,
            retries=5,
            rate_limit=500,
            auth_token="bearer_token_123",
            verify_ssl=False
        )
        
        assert api_config.base_url == "https://secure-api.com"
        assert api_config.timeout == 60
        assert api_config.retries == 5
        assert api_config.rate_limit == 500
        assert api_config.auth_token == "bearer_token_123"
        assert api_config.verify_ssl is False

    @pytest.mark.unit
    def test_container_config_defaults(self):
        """Test ContainerConfig default values."""
        container_config = ContainerConfig()
        
        assert container_config.docker_host == "unix://var/run/docker.sock"
        assert container_config.k8s_config_path is None
        assert container_config.namespace == "default"
        assert container_config.registry_url == "docker.io"
        assert container_config.pull_policy == "IfNotPresent"
        assert container_config.resource_limits["cpu"] == "500m"
        assert container_config.resource_limits["memory"] == "512Mi"

    @pytest.mark.unit
    def test_container_config_custom_limits(self):
        """Test ContainerConfig with custom resource limits."""
        custom_limits = {
            "cpu": "2000m",
            "memory": "4Gi",
            "storage": "20Gi"
        }
        
        container_config = ContainerConfig(
            docker_host="tcp://docker.example.com:2376",
            k8s_config_path="/home/user/.kube/config",
            namespace="production",
            registry_url="registry.example.com",
            pull_policy="Always",
            resource_limits=custom_limits
        )
        
        assert container_config.docker_host == "tcp://docker.example.com:2376"
        assert container_config.k8s_config_path == "/home/user/.kube/config"
        assert container_config.namespace == "production"
        assert container_config.registry_url == "registry.example.com"
        assert container_config.pull_policy == "Always"
        assert container_config.resource_limits["cpu"] == "2000m"
        assert container_config.resource_limits["memory"] == "4Gi"
        assert container_config.resource_limits["storage"] == "20Gi"

    @pytest.mark.unit
    def test_monitoring_config_defaults(self):
        """Test MonitoringConfig default values."""
        monitoring_config = MonitoringConfig()
        
        assert monitoring_config.prometheus_url == "http://localhost:9090"
        assert monitoring_config.grafana_url == "http://localhost:3000"
        assert monitoring_config.jaeger_url == "http://localhost:14268"
        assert monitoring_config.log_level == "INFO"
        assert monitoring_config.metrics_enabled is True
        assert monitoring_config.tracing_enabled is True

    @pytest.mark.unit
    def test_monitoring_config_production_setup(self):
        """Test MonitoringConfig for production environment."""
        monitoring_config = MonitoringConfig(
            prometheus_url="https://prometheus.example.com",
            grafana_url="https://grafana.example.com",
            jaeger_url="https://jaeger.example.com",
            log_level="WARN",
            metrics_enabled=True,
            tracing_enabled=False
        )
        
        assert monitoring_config.prometheus_url == "https://prometheus.example.com"
        assert monitoring_config.grafana_url == "https://grafana.example.com"
        assert monitoring_config.jaeger_url == "https://jaeger.example.com"
        assert monitoring_config.log_level == "WARN"
        assert monitoring_config.metrics_enabled is True
        assert monitoring_config.tracing_enabled is False

    @pytest.mark.unit
    def test_config_dataclass_immutability(self):
        """Test that dataclass instances can be modified."""
        db_config = DatabaseConfig()
        original_host = db_config.host
        
        # Dataclasses are mutable by default
        db_config.host = "new-host.com"
        assert db_config.host == "new-host.com"
        assert db_config.host != original_host

    @pytest.mark.unit
    def test_config_dataclass_string_representation(self):
        """Test string representation of config dataclasses."""
        db_config = DatabaseConfig(host="test-db", port=5432)
        str_repr = str(db_config)
        
        assert "DatabaseConfig" in str_repr
        assert "test-db" in str_repr
        assert "5432" in str_repr

    @pytest.mark.unit
    def test_config_dataclass_equality(self):
        """Test equality comparison of config dataclasses."""
        db_config1 = DatabaseConfig(host="test-db", port=5432)
        db_config2 = DatabaseConfig(host="test-db", port=5432)
        db_config3 = DatabaseConfig(host="other-db", port=5432)
        
        assert db_config1 == db_config2
        assert db_config1 != db_config3

    @pytest.mark.unit
    def test_config_field_types(self):
        """Test that config fields have correct types."""
        db_config = DatabaseConfig()
        
        assert isinstance(db_config.host, str)
        assert isinstance(db_config.port, int)
        assert isinstance(db_config.pool_size, int)
        assert isinstance(db_config.max_overflow, int)

    @pytest.mark.unit
    def test_redis_config_optional_fields(self):
        """Test RedisConfig optional fields."""
        redis_config = RedisConfig()
        
        # Password should be None by default
        assert redis_config.password is None
        
        # Should be able to set password
        redis_config.password = "secret123"
        assert redis_config.password == "secret123"

    @pytest.mark.unit
    def test_api_config_url_validation(self):
        """Test API config URL format validation."""
        # Test valid URLs
        valid_urls = [
            "http://localhost:8080",
            "https://api.example.com",
            "https://api.example.com:8443/v1"
        ]
        
        for url in valid_urls:
            api_config = APIConfig(base_url=url)
            assert api_config.base_url == url

    @pytest.mark.unit
    def test_container_config_resource_limits_type(self):
        """Test ContainerConfig resource limits type."""
        container_config = ContainerConfig()
        
        assert isinstance(container_config.resource_limits, dict)
        assert "cpu" in container_config.resource_limits
        assert "memory" in container_config.resource_limits

    @pytest.mark.unit
    def test_monitoring_config_boolean_flags(self):
        """Test MonitoringConfig boolean flags."""
        monitoring_config = MonitoringConfig()
        
        assert isinstance(monitoring_config.metrics_enabled, bool)
        assert isinstance(monitoring_config.tracing_enabled, bool)
        assert monitoring_config.metrics_enabled is True
        assert monitoring_config.tracing_enabled is True

    @pytest.mark.unit
    def test_config_deep_copy_behavior(self):
        """Test deep copy behavior of config objects."""
        import copy
        
        original_config = ContainerConfig()
        original_config.resource_limits["cpu"] = "1000m"
        
        copied_config = copy.deepcopy(original_config)
        copied_config.resource_limits["cpu"] = "2000m"
        
        # Original should remain unchanged
        assert original_config.resource_limits["cpu"] == "1000m"
        assert copied_config.resource_limits["cpu"] == "2000m"

    @pytest.mark.unit
    def test_config_serialization_compatibility(self):
        """Test config serialization compatibility."""
        import json
        
        api_config = APIConfig(
            base_url="https://api.test.com",
            timeout=45,
            retries=3,
            verify_ssl=True
        )
        
        # Convert to dict for JSON serialization
        config_dict = {
            "base_url": api_config.base_url,
            "timeout": api_config.timeout,
            "retries": api_config.retries,
            "verify_ssl": api_config.verify_ssl
        }
        
        json_str = json.dumps(config_dict)
        deserialized = json.loads(json_str)
        
        assert deserialized["base_url"] == api_config.base_url
        assert deserialized["timeout"] == api_config.timeout 