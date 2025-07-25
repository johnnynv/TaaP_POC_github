"""API client for cloud native testing platform."""

import asyncio
import aiohttp
import requests
import json
import time
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


@dataclass
class APIResponse:
    """API response container."""
    status_code: int
    data: Any
    headers: Dict[str, str]
    response_time: float
    success: bool
    error: Optional[str] = None


class RateLimiter:
    """Simple rate limiter implementation."""
    
    def __init__(self, max_requests: int, time_window: int):
        """Initialize rate limiter."""
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = []
    
    def can_proceed(self) -> bool:
        """Check if request can proceed."""
        now = time.time()
        # Remove old requests outside time window
        self.requests = [req_time for req_time in self.requests if now - req_time < self.time_window]
        
        if len(self.requests) < self.max_requests:
            self.requests.append(now)
            return True
        return False
    
    def wait_time(self) -> float:
        """Calculate wait time until next request is allowed."""
        if not self.requests:
            return 0
        oldest_request = min(self.requests)
        return max(0, self.time_window - (time.time() - oldest_request))


class APIClient:
    """HTTP API client with retry logic and rate limiting."""
    
    def __init__(
        self,
        base_url: str,
        timeout: int = 30,
        retries: int = 3,
        rate_limit: int = 100,
        auth_token: Optional[str] = None
    ):
        """Initialize API client."""
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.retries = retries
        self.auth_token = auth_token
        self.rate_limiter = RateLimiter(rate_limit, 60)  # rate_limit per minute
        self.session = None
        
        # Default headers
        self.default_headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "TaaP-Test-Client/1.0"
        }
        
        if auth_token:
            self.default_headers["Authorization"] = f"Bearer {auth_token}"
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.timeout),
            headers=self.default_headers
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    def _apply_rate_limit(self) -> None:
        """Apply rate limiting."""
        if not self.rate_limiter.can_proceed():
            wait_time = self.rate_limiter.wait_time()
            if wait_time > 0:
                time.sleep(wait_time)
    
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> APIResponse:
        """Make HTTP request with retry logic."""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        merged_headers = {**self.default_headers, **(headers or {})}
        
        start_time = time.time()
        last_error = None
        
        for attempt in range(self.retries + 1):
            try:
                self._apply_rate_limit()
                
                if self.session:
                    # Async request
                    async with self.session.request(
                        method=method,
                        url=url,
                        json=data,
                        headers=merged_headers,
                        params=params
                    ) as response:
                        response_data = await self._parse_response(response)
                        response_time = time.time() - start_time
                        
                        return APIResponse(
                            status_code=response.status,
                            data=response_data,
                            headers=dict(response.headers),
                            response_time=response_time,
                            success=response.status < 400
                        )
                else:
                    # Sync request
                    response = requests.request(
                        method=method,
                        url=url,
                        json=data,
                        headers=merged_headers,
                        params=params,
                        timeout=self.timeout
                    )
                    response_time = time.time() - start_time
                    
                    return APIResponse(
                        status_code=response.status_code,
                        data=self._parse_sync_response(response),
                        headers=dict(response.headers),
                        response_time=response_time,
                        success=response.status_code < 400
                    )
                    
            except Exception as e:
                last_error = str(e)
                logger.warning(f"Request attempt {attempt + 1} failed: {e}")
                if attempt < self.retries:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
        
        response_time = time.time() - start_time
        return APIResponse(
            status_code=0,
            data=None,
            headers={},
            response_time=response_time,
            success=False,
            error=last_error
        )
    
    async def _parse_response(self, response: aiohttp.ClientResponse) -> Any:
        """Parse aiohttp response."""
        content_type = response.headers.get('Content-Type', '')
        if 'application/json' in content_type:
            return await response.json()
        else:
            return await response.text()
    
    def _parse_sync_response(self, response: requests.Response) -> Any:
        """Parse requests response."""
        content_type = response.headers.get('Content-Type', '')
        if 'application/json' in content_type:
            try:
                return response.json()
            except json.JSONDecodeError:
                return response.text
        else:
            return response.text
    
    async def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None) -> APIResponse:
        """Make GET request."""
        return await self._make_request("GET", endpoint, params=params, headers=headers)
    
    async def post(self, endpoint: str, data: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None) -> APIResponse:
        """Make POST request."""
        return await self._make_request("POST", endpoint, data=data, headers=headers)
    
    async def put(self, endpoint: str, data: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None) -> APIResponse:
        """Make PUT request."""
        return await self._make_request("PUT", endpoint, data=data, headers=headers)
    
    async def patch(self, endpoint: str, data: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None) -> APIResponse:
        """Make PATCH request."""
        return await self._make_request("PATCH", endpoint, data=data, headers=headers)
    
    async def delete(self, endpoint: str, headers: Optional[Dict[str, str]] = None) -> APIResponse:
        """Make DELETE request."""
        return await self._make_request("DELETE", endpoint, headers=headers)
    
    # Synchronous methods for compatibility
    def sync_get(self, endpoint: str, params: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None) -> APIResponse:
        """Make synchronous GET request."""
        return asyncio.run(self._make_request("GET", endpoint, params=params, headers=headers))
    
    def sync_post(self, endpoint: str, data: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None) -> APIResponse:
        """Make synchronous POST request."""
        return asyncio.run(self._make_request("POST", endpoint, data=data, headers=headers))


class MockAPIServer:
    """Mock API server for testing purposes."""
    
    def __init__(self, responses: Dict[str, Dict[str, Any]]):
        """Initialize mock server with predefined responses."""
        self.responses = responses
        self.request_log = []
    
    def get_response(self, method: str, endpoint: str) -> Dict[str, Any]:
        """Get mock response for method and endpoint."""
        key = f"{method.upper()}:{endpoint}"
        self.request_log.append({
            "method": method,
            "endpoint": endpoint,
            "timestamp": datetime.now()
        })
        
        if key in self.responses:
            return self.responses[key]
        else:
            return {
                "status_code": 404,
                "data": {"error": "Not found"},
                "headers": {"Content-Type": "application/json"}
            }
    
    def add_response(self, method: str, endpoint: str, response: Dict[str, Any]) -> None:
        """Add a mock response."""
        key = f"{method.upper()}:{endpoint}"
        self.responses[key] = response
    
    def get_request_count(self, method: str = None, endpoint: str = None) -> int:
        """Get count of requests matching criteria."""
        if not method and not endpoint:
            return len(self.request_log)
        
        count = 0
        for request in self.request_log:
            if method and request["method"].upper() != method.upper():
                continue
            if endpoint and request["endpoint"] != endpoint:
                continue
            count += 1
        return count
    
    def clear_log(self) -> None:
        """Clear request log."""
        self.request_log.clear() 