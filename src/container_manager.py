"""Container management for cloud native testing platform."""

import docker
import asyncio
import logging
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
from datetime import datetime, timedelta
import yaml
import tempfile
import os

logger = logging.getLogger(__name__)


@dataclass
class ContainerStatus:
    """Container status information."""
    name: str
    image: str
    status: str
    ports: Dict[str, int]
    created_at: datetime
    running: bool
    exit_code: Optional[int] = None
    logs: Optional[str] = None


@dataclass
class PodStatus:
    """Kubernetes pod status information."""
    name: str
    namespace: str
    phase: str
    ready: bool
    restart_count: int
    node_name: Optional[str]
    created_at: datetime
    containers: List[Dict[str, Any]]


class DockerManager:
    """Docker container management."""
    
    def __init__(self, docker_host: str = "unix://var/run/docker.sock"):
        """Initialize Docker manager."""
        self.docker_host = docker_host
        self.client = None
        self._containers = {}
    
    def connect(self) -> None:
        """Connect to Docker daemon."""
        try:
            self.client = docker.DockerClient(base_url=self.docker_host)
            # Test connection
            self.client.ping()
            logger.info("Docker connection established")
        except Exception as e:
            logger.error(f"Failed to connect to Docker: {e}")
            raise
    
    def disconnect(self) -> None:
        """Disconnect from Docker daemon."""
        if self.client:
            self.client.close()
            logger.info("Docker connection closed")
    
    def pull_image(self, image: str, tag: str = "latest") -> bool:
        """Pull Docker image."""
        try:
            full_image = f"{image}:{tag}"
            self.client.images.pull(full_image)
            logger.info(f"Successfully pulled image: {full_image}")
            return True
        except Exception as e:
            logger.error(f"Failed to pull image {image}:{tag}: {e}")
            return False
    
    def create_container(
        self,
        image: str,
        name: str,
        ports: Optional[Dict[str, int]] = None,
        environment: Optional[Dict[str, str]] = None,
        volumes: Optional[Dict[str, Dict[str, str]]] = None,
        command: Optional[Union[str, List[str]]] = None,
        detach: bool = True
    ) -> Optional[str]:
        """Create and start a container."""
        try:
            container = self.client.containers.run(
                image=image,
                name=name,
                ports=ports or {},
                environment=environment or {},
                volumes=volumes or {},
                command=command,
                detach=detach,
                remove=False
            )
            
            self._containers[name] = container
            logger.info(f"Container {name} created and started")
            return container.id
            
        except Exception as e:
            logger.error(f"Failed to create container {name}: {e}")
            return None
    
    def stop_container(self, name: str, timeout: int = 10) -> bool:
        """Stop a container."""
        try:
            if name in self._containers:
                container = self._containers[name]
            else:
                container = self.client.containers.get(name)
            
            container.stop(timeout=timeout)
            logger.info(f"Container {name} stopped")
            return True
            
        except Exception as e:
            logger.error(f"Failed to stop container {name}: {e}")
            return False
    
    def remove_container(self, name: str, force: bool = False) -> bool:
        """Remove a container."""
        try:
            if name in self._containers:
                container = self._containers[name]
                del self._containers[name]
            else:
                container = self.client.containers.get(name)
            
            container.remove(force=force)
            logger.info(f"Container {name} removed")
            return True
            
        except Exception as e:
            logger.error(f"Failed to remove container {name}: {e}")
            return False
    
    def get_container_status(self, name: str) -> Optional[ContainerStatus]:
        """Get container status."""
        try:
            if name in self._containers:
                container = self._containers[name]
            else:
                container = self.client.containers.get(name)
            
            container.reload()
            
            return ContainerStatus(
                name=container.name,
                image=container.image.tags[0] if container.image.tags else "unknown",
                status=container.status,
                ports=container.ports,
                created_at=datetime.fromisoformat(container.attrs['Created'].replace('Z', '+00:00')),
                running=container.status == 'running',
                exit_code=container.attrs.get('State', {}).get('ExitCode')
            )
            
        except Exception as e:
            logger.error(f"Failed to get status for container {name}: {e}")
            return None
    
    def get_container_logs(self, name: str, tail: int = 100) -> Optional[str]:
        """Get container logs."""
        try:
            if name in self._containers:
                container = self._containers[name]
            else:
                container = self.client.containers.get(name)
            
            logs = container.logs(tail=tail, decode=True)
            return logs
            
        except Exception as e:
            logger.error(f"Failed to get logs for container {name}: {e}")
            return None
    
    def list_containers(self, all_containers: bool = True) -> List[ContainerStatus]:
        """List all containers."""
        try:
            containers = self.client.containers.list(all=all_containers)
            status_list = []
            
            for container in containers:
                status = ContainerStatus(
                    name=container.name,
                    image=container.image.tags[0] if container.image.tags else "unknown",
                    status=container.status,
                    ports=container.ports,
                    created_at=datetime.fromisoformat(container.attrs['Created'].replace('Z', '+00:00')),
                    running=container.status == 'running'
                )
                status_list.append(status)
            
            return status_list
            
        except Exception as e:
            logger.error(f"Failed to list containers: {e}")
            return []
    
    def cleanup_test_containers(self, prefix: str = "test-") -> int:
        """Clean up test containers with given prefix."""
        cleanup_count = 0
        try:
            containers = self.client.containers.list(all=True)
            for container in containers:
                if container.name.startswith(prefix):
                    try:
                        container.stop(timeout=5)
                        container.remove(force=True)
                        cleanup_count += 1
                        logger.info(f"Cleaned up container: {container.name}")
                    except Exception as e:
                        logger.warning(f"Failed to cleanup container {container.name}: {e}")
            
            return cleanup_count
            
        except Exception as e:
            logger.error(f"Failed to cleanup test containers: {e}")
            return 0


class KubernetesManager:
    """Kubernetes pod and service management."""
    
    def __init__(self, config_path: Optional[str] = None, namespace: str = "default"):
        """Initialize Kubernetes manager."""
        self.config_path = config_path or os.path.expanduser("~/.kube/config")
        self.namespace = namespace
        self.client = None
        self._pods = {}
    
    def connect(self) -> None:
        """Connect to Kubernetes cluster."""
        try:
            # Note: In a real implementation, you would use kubernetes client
            # For testing purposes, we'll simulate the connection
            logger.info("Kubernetes connection established (simulated)")
            self.client = "mock_k8s_client"  # Mock client for testing
        except Exception as e:
            logger.error(f"Failed to connect to Kubernetes: {e}")
            raise
    
    def create_pod(self, pod_spec: Dict[str, Any]) -> Optional[str]:
        """Create a Kubernetes pod."""
        try:
            pod_name = pod_spec.get("metadata", {}).get("name", "unknown")
            
            # Simulate pod creation
            self._pods[pod_name] = {
                "spec": pod_spec,
                "status": "Pending",
                "created_at": datetime.now()
            }
            
            logger.info(f"Pod {pod_name} created")
            return pod_name
            
        except Exception as e:
            logger.error(f"Failed to create pod: {e}")
            return None
    
    def delete_pod(self, name: str) -> bool:
        """Delete a Kubernetes pod."""
        try:
            if name in self._pods:
                del self._pods[name]
            
            logger.info(f"Pod {name} deleted")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete pod {name}: {e}")
            return False
    
    def get_pod_status(self, name: str) -> Optional[PodStatus]:
        """Get pod status."""
        try:
            if name not in self._pods:
                return None
            
            pod_data = self._pods[name]
            
            return PodStatus(
                name=name,
                namespace=self.namespace,
                phase=pod_data["status"],
                ready=pod_data["status"] == "Running",
                restart_count=0,
                node_name="test-node",
                created_at=pod_data["created_at"],
                containers=[]
            )
            
        except Exception as e:
            logger.error(f"Failed to get pod status {name}: {e}")
            return None
    
    def list_pods(self) -> List[PodStatus]:
        """List all pods in namespace."""
        pod_list = []
        for name, data in self._pods.items():
            status = PodStatus(
                name=name,
                namespace=self.namespace,
                phase=data["status"],
                ready=data["status"] == "Running",
                restart_count=0,
                node_name="test-node",
                created_at=data["created_at"],
                containers=[]
            )
            pod_list.append(status)
        
        return pod_list
    
    def apply_yaml(self, yaml_content: str) -> bool:
        """Apply Kubernetes YAML configuration."""
        try:
            resources = yaml.safe_load_all(yaml_content)
            for resource in resources:
                if resource and resource.get("kind") == "Pod":
                    self.create_pod(resource)
            
            logger.info("YAML configuration applied")
            return True
            
        except Exception as e:
            logger.error(f"Failed to apply YAML: {e}")
            return False


class ContainerManager:
    """Main container manager that handles Docker and Kubernetes."""
    
    def __init__(
        self,
        docker_host: str = "unix://var/run/docker.sock",
        k8s_config_path: Optional[str] = None,
        k8s_namespace: str = "default"
    ):
        """Initialize container manager."""
        self.docker = DockerManager(docker_host)
        self.kubernetes = KubernetesManager(k8s_config_path, k8s_namespace)
        self._connected = False
    
    def connect_all(self) -> None:
        """Connect to all container runtimes."""
        self.docker.connect()
        self.kubernetes.connect()
        self._connected = True
        logger.info("All container runtime connections established")
    
    def disconnect_all(self) -> None:
        """Disconnect from all container runtimes."""
        self.docker.disconnect()
        self._connected = False
        logger.info("All container runtime connections closed")
    
    def health_check(self) -> Dict[str, bool]:
        """Check health of container runtime connections."""
        return {
            "docker": self.docker.client is not None,
            "kubernetes": self.kubernetes.client is not None
        }
    
    def cleanup_all_test_resources(self) -> Dict[str, int]:
        """Clean up all test containers and pods."""
        result = {
            "docker_containers": 0,
            "k8s_pods": 0
        }
        
        if self._connected:
            result["docker_containers"] = self.docker.cleanup_test_containers()
            
            # Clean up test pods
            pods = self.kubernetes.list_pods()
            for pod in pods:
                if pod.name.startswith("test-"):
                    if self.kubernetes.delete_pod(pod.name):
                        result["k8s_pods"] += 1
        
        return result 