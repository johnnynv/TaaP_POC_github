import pytest
import asyncio
import json
import yaml
from datetime import datetime
from faker import Faker
from unittest.mock import Mock, MagicMock
import redis
import requests
from src.config import Config
from src.database import DatabaseManager
from src.api_client import APIClient
from src.container_manager import ContainerManager

fake = Faker()

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
def config():
    """Global configuration fixture."""
    return Config()

@pytest.fixture
def mock_redis():
    """Mock Redis client."""
    mock_client = Mock()
    mock_client.get.return_value = None
    mock_client.set.return_value = True
    mock_client.delete.return_value = 1
    mock_client.exists.return_value = 1
    return mock_client

@pytest.fixture
def mock_database():
    """Mock database connection."""
    mock_db = Mock()
    mock_db.execute.return_value = Mock(fetchall=lambda: [])
    mock_db.commit.return_value = None
    return mock_db

@pytest.fixture
def api_client():
    """API client fixture."""
    return APIClient(base_url="http://localhost:8080")

@pytest.fixture
def container_manager():
    """Container manager fixture."""
    return ContainerManager()

@pytest.fixture
def sample_user_data():
    """Generate sample user data."""
    return {
        "id": fake.uuid4(),
        "name": fake.name(),
        "email": fake.email(),
        "age": fake.random_int(min=18, max=99),
        "created_at": fake.date_time().isoformat()
    }

@pytest.fixture
def sample_product_data():
    """Generate sample product data."""
    return {
        "id": fake.uuid4(),
        "name": fake.catch_phrase(),
        "price": fake.pydecimal(left_digits=3, right_digits=2, positive=True),
        "category": fake.word(),
        "description": fake.text(max_nb_chars=200),
        "stock": fake.random_int(min=0, max=1000)
    }

@pytest.fixture
def sample_order_data(sample_user_data, sample_product_data):
    """Generate sample order data."""
    return {
        "id": fake.uuid4(),
        "user_id": sample_user_data["id"],
        "product_id": sample_product_data["id"],
        "quantity": fake.random_int(min=1, max=10),
        "total_amount": fake.pydecimal(left_digits=4, right_digits=2, positive=True),
        "status": fake.random_element(elements=("pending", "confirmed", "shipped", "delivered")),
        "created_at": fake.date_time().isoformat()
    }

@pytest.fixture
def test_config():
    """Test configuration data."""
    return {
        "api": {
            "base_url": "http://test-api.example.com",
            "timeout": 30,
            "retries": 3
        },
        "database": {
            "host": "localhost",
            "port": 5432,
            "name": "test_db",
            "user": "test_user"
        },
        "redis": {
            "host": "localhost",
            "port": 6379,
            "db": 0
        }
    }

@pytest.fixture
def mock_kubernetes_client():
    """Mock Kubernetes client."""
    mock_client = Mock()
    mock_client.list_namespaced_pod.return_value = Mock(items=[])
    mock_client.create_namespaced_pod.return_value = Mock(metadata=Mock(name="test-pod"))
    return mock_client

@pytest.fixture
def docker_container_config():
    """Docker container configuration."""
    return {
        "image": "nginx:latest",
        "name": f"test-container-{fake.uuid4()[:8]}",
        "ports": {"80/tcp": 8080},
        "environment": {
            "ENV": "test",
            "DEBUG": "true"
        }
    } 