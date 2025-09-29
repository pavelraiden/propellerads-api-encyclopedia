"""
Base API class with common functionality
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List, Union
from urllib.parse import urljoin
import aiohttp
from aiohttp import ClientTimeout, ClientSession

from ..exceptions import (
    PropellerAdsAPIError, 
    PropellerAdsAuthError,
    PropellerAdsRateLimitError,
    PropellerAdsValidationError
)


logger = logging.getLogger(__name__)


class BaseAPI:
    """Base API class with common functionality"""
    
    def __init__(self, client):
        """Initialize with client reference"""
        self.client = client
        self.api_key = client.api_key
        self.base_url = client.base_url
        
        # Request tracking
        self._request_count = 0
        self._error_count = 0
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self._ensure_session()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()
    
    async def _ensure_session(self):
        """Ensure HTTP session is created"""
        if self.session is None or self.session.closed:
            timeout = ClientTimeout(total=30, connect=10)
            self.session = ClientSession(
                timeout=timeout,
                headers={
                    'Authorization': f'Bearer {self.api_key}',
                    'Content-Type': 'application/json',
                    'User-Agent': 'PropellerAds-Python-SDK/2.0.0'
                }
            )
    
    async def close(self):
        """Close HTTP session"""
        if self.session and not self.session.closed:
            await self.session.close()
    
    def _build_url(self, endpoint: str) -> str:
        """Build full URL from endpoint"""
        return urljoin(f"{self.base_url}/", endpoint.lstrip('/'))
    
    async def _request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        retry_count: int = 3
    ) -> Dict[str, Any]:
        """Make HTTP request with error handling and retries"""
        
        await self._ensure_session()
        url = self._build_url(endpoint)
        
        # Clean params
        if params:
            params = {k: v for k, v in params.items() if v is not None}
        
        for attempt in range(retry_count + 1):
            try:
                self._request_count += 1
                
                logger.debug(f"Making {method} request to {url} (attempt {attempt + 1})")
                
                async with self.session.request(
                    method=method,
                    url=url,
                    json=data,
                    params=params
                ) as response:
                    
                    # Update rate limit info
                    self._update_rate_limit_info(response)
                    
                    # Handle response
                    response_data = await self._handle_response(response)
                    
                    logger.debug(f"Request successful: {method} {url}")
                    return response_data
                    
            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                self._error_count += 1
                
                if attempt == retry_count:
                    logger.error(f"Request failed after {retry_count + 1} attempts: {e}")
                    raise PropellerAdsAPIError(f"Request failed: {e}")
                
                # Exponential backoff
                wait_time = 2 ** attempt
                logger.warning(f"Request failed, retrying in {wait_time}s: {e}")
                await asyncio.sleep(wait_time)
    
    def _update_rate_limit_info(self, response):
        """Update rate limit information from response headers"""
        if 'X-RateLimit-Remaining' in response.headers:
            self._rate_limit_remaining = int(response.headers['X-RateLimit-Remaining'])
        
        if 'X-RateLimit-Reset' in response.headers:
            self._rate_limit_reset = int(response.headers['X-RateLimit-Reset'])
    
    async def _handle_response(self, response) -> Dict[str, Any]:
        """Handle HTTP response and errors"""
        
        # Check for rate limiting
        if response.status == 429:
            raise PropellerAdsRateLimitError(
                "Rate limit exceeded",
                retry_after=int(response.headers.get('Retry-After', 60))
            )
        
        # Check for authentication errors
        if response.status == 401:
            raise PropellerAdsAuthError("Invalid API key or authentication failed")
        
        # Check for validation errors
        if response.status == 422:
            error_data = await response.json()
            raise PropellerAdsValidationError(
                "Validation error",
                details=error_data.get('errors', {})
            )
        
        # Check for other client errors
        if 400 <= response.status < 500:
            try:
                error_data = await response.json()
                error_message = error_data.get('message', f'HTTP {response.status}')
            except:
                error_message = f'HTTP {response.status}'
            
            raise PropellerAdsAPIError(f"Client error: {error_message}")
        
        # Check for server errors
        if response.status >= 500:
            raise PropellerAdsAPIError(f"Server error: HTTP {response.status}")
        
        # Parse successful response
        try:
            return await response.json()
        except Exception as e:
            raise PropellerAdsAPIError(f"Failed to parse response: {e}")
    
    async def _get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make GET request"""
        return await self._request('GET', endpoint, params=params)
    
    async def _post(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make POST request"""
        return await self._request('POST', endpoint, data=data)
    
    async def _put(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make PUT request"""
        return await self._request('PUT', endpoint, data=data)
    
    async def _delete(self, endpoint: str) -> Dict[str, Any]:
        """Make DELETE request"""
        return await self._request('DELETE', endpoint)
    
    @property
    def rate_limit_remaining(self) -> int:
        """Get remaining rate limit"""
        return self._rate_limit_remaining
    
    @property
    def request_count(self) -> int:
        """Get total request count"""
        return self._request_count
    
    @property
    def error_count(self) -> int:
        """Get total error count"""
        return self._error_count
    
    def get_stats(self) -> Dict[str, Any]:
        """Get API usage statistics"""
        return {
            'total_requests': self._request_count,
            'total_errors': self._error_count,
            'error_rate': self._error_count / max(self._request_count, 1),
            'rate_limit_remaining': self._rate_limit_remaining,
            'rate_limit_reset': self._rate_limit_reset
        }
