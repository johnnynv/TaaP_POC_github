"""Configuration management for the cloud native testing platform."""

import os
import yaml
from typing import Dict, Any, Optional
from dataclasses import dataclass, field


@dataclass
class DatabaseConfig:
    """Database configuration settings."""
    host: str = "localhost"
    port: int = 5432
    name: str = "taap_db"
    user: str = "taap_user"
    password: str = ""
    ssl_mode: str = "prefer"
    pool_size: int = 10
    max_overflow: int = 20


@dataclass
class RedisConfig:
    """Redis configuration settings."""
    host: str = "localhost"
    port: int = 6379
    db: int = 0
    password: Optional[str] = None
    socket_timeout: int = 5
    max_connections: int = 50


@dataclass
class APIConfig:
    """API configuration settings."""
    base_url: str = "http://localhost:8080"
    timeout: int = 30
    retries: int = 3
    rate_limit: int = 100
    auth_token: Optional[str] = None
    verify_ssl: bool = True


@dataclass
class ContainerConfig:
    """Container orchestration configuration."""
    docker_host: str = "unix://var/run/docker.sock"
    k8s_config_path: Optional[str] = None
    namespace: str = "default"
    registry_url: str = "docker.io"
    pull_policy: str = "IfNotPresent"
    resource_limits: Dict[str, str] = field(default_factory=lambda: {
        "cpu": "500m",
        "memory": "512Mi"
    })


@dataclass
class MonitoringConfig:
    """Monitoring and observability configuration."""
    prometheus_url: str = "http://localhost:9090"
    grafana_url: str = "http://localhost:3000"
    jaeger_url: str = "http://localhost:14268"
    log_level: str = "INFO"
    metrics_enabled: bool = True
    tracing_enabled: bool = True


class Config:
    """Main configuration class for the testing platform."""
    
    def __init__(self, config_file: Optional[str] = None):
        """Initialize configuration from file or environment variables."""
        self.database = DatabaseConfig()
        self.redis = RedisConfig()
        self.api = APIConfig()
        self.container = ContainerConfig()
        self.monitoring = MonitoringConfig()
        
        if config_file:
            self.load_from_file(config_file)
        
        self.load_from_env()
    
    def load_from_file(self, config_file: str) -> None:
        """Load configuration from YAML file."""
        try:
            with open(config_file, 'r') as f:
                config_data = yaml.safe_load(f)
            
            if 'database' in config_data:
                self._update_dataclass(self.database, config_data['database'])
            if 'redis' in config_data:
                self._update_dataclass(self.redis, config_data['redis'])
            if 'api' in config_data:
                self._update_dataclass(self.api, config_data['api'])
            if 'container' in config_data:
                self._update_dataclass(self.container, config_data['container'])
            if 'monitoring' in config_data:
                self._update_dataclass(self.monitoring, config_data['monitoring'])
                
        except FileNotFoundError:
            print(f"Configuration file {config_file} not found, using defaults")
        except yaml.YAMLError as e:
            print(f"Error parsing configuration file: {e}")
    
    def load_from_env(self) -> None:
        """Load configuration from environment variables."""
        # Database configuration
        self.database.host = os.getenv('DB_HOST', self.database.host)
        self.database.port = int(os.getenv('DB_PORT', self.database.port))
        self.database.name = os.getenv('DB_NAME', self.database.name)
        self.database.user = os.getenv('DB_USER', self.database.user)
        self.database.password = os.getenv('DB_PASSWORD', self.database.password)
        
        # Redis configuration
        self.redis.host = os.getenv('REDIS_HOST', self.redis.host)
        self.redis.port = int(os.getenv('REDIS_PORT', self.redis.port))
        self.redis.password = os.getenv('REDIS_PASSWORD', self.redis.password)
        
        # API configuration
        self.api.base_url = os.getenv('API_BASE_URL', self.api.base_url)
        self.api.auth_token = os.getenv('API_AUTH_TOKEN', self.api.auth_token)
        
        # Container configuration
        self.container.k8s_config_path = os.getenv('KUBECONFIG', self.container.k8s_config_path)
        self.container.namespace = os.getenv('K8S_NAMESPACE', self.container.namespace)
    
    def _update_dataclass(self, obj: Any, data: Dict[str, Any]) -> None:
        """Update dataclass fields from dictionary."""
        for key, value in data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            'database': self.database.__dict__,
            'redis': self.redis.__dict__,
            'api': self.api.__dict__,
            'container': self.container.__dict__,
            'monitoring': self.monitoring.__dict__
        }
    
    def validate(self) -> bool:
        """Validate configuration settings."""
        if not self.database.host:
            raise ValueError("Database host is required")
        if not self.api.base_url:
            raise ValueError("API base URL is required")
        if self.database.port <= 0 or self.database.port > 65535:
            raise ValueError("Invalid database port")
        if self.redis.port <= 0 or self.redis.port > 65535:
            raise ValueError("Invalid Redis port")
        return True 