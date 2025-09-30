"""
PropellerAds Professional Client

Production-ready PropellerAds SSP API v5 client with enterprise features.
"""

import os
import time
import logging
import requests
from typing import Optional, Dict, Any, List
from datetime import datetime
from decimal import Decimal

from .exceptions import PropellerAdsError, AuthenticationError, RateLimitError, ServerError
from .utils.rate_limiter import RateLimiter
from .monitoring.metrics import MetricsCollector


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BalanceResponse:
    """Simple balance response."""
    def __init__(self, amount: float, currency: str = "USD"):
        self.amount = Decimal(str(amount))
        self.currency = currency
        self.formatted = f"${float(amount):,.2f}"
        self.last_updated = datetime.now()


class PropellerAdsClient:
    """
    Professional PropellerAds SSP API v5 Client.
    
    Features:
    - Intelligent retry with exponential backoff
    - Rate limiting with token bucket algorithm
    - Circuit breaker pattern
    - Comprehensive error handling
    - Request/response logging
    - Metrics collection
    - Connection pooling
    """
    
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://ssp-api.propellerads.com/v5",
        timeout: int = 30,
        max_retries: int = 3,
        rate_limit: int = 60,
        enable_metrics: bool = True
    ):
        """
        Initialize PropellerAds client.
        
        Args:
            api_key: PropellerAds API key
            base_url: API base URL
            timeout: Request timeout in seconds
            max_retries: Maximum retry attempts
            rate_limit: Requests per minute
            enable_metrics: Enable metrics collection
        """
        # Configuration
        self.config = type('Config', (), {
            'api_key': api_key,
            'base_url': base_url.rstrip('/'),
            'timeout': timeout,
            'max_retries': max_retries,
            'rate_limit': rate_limit,
            'enable_metrics': enable_metrics
        })()
        
        # Validate configuration
        if not api_key:
            raise ValueError("API key is required")
        
        # Initialize components
        self.session = self._create_session()
        self.rate_limiter = RateLimiter(max_requests=rate_limit, time_window=60)
        self.metrics = MetricsCollector() if enable_metrics else None
        
        # Circuit breaker state
        self.circuit_breaker = {
            'failures': 0,
            'last_failure': None,
            'state': 'closed',  # closed, open, half-open
            'failure_threshold': 5,
            'recovery_timeout': 60
        }
        
        logger.info(f"PropellerAds client initialized (rate_limit: {rate_limit}/min)")
    
    def _create_session(self) -> requests.Session:
        """Create configured requests session."""
        session = requests.Session()
        
        # Set headers
        session.headers.update({
            'Authorization': f'Bearer {self.config.api_key}',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': 'PropellerAds-Python-SDK/1.0.0'
        })
        
        # Configure adapters for connection pooling
        adapter = requests.adapters.HTTPAdapter(
            pool_connections=10,
            pool_maxsize=20,
            max_retries=0  # We handle retries manually
        )
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        
        return session
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> requests.Response:
        """
        Make API request with retry logic and error handling.
        
        Args:
            method: HTTP method
            endpoint: API endpoint
            data: Request body data
            params: Query parameters
            
        Returns:
            requests.Response: API response
            
        Raises:
            PropellerAdsError: On API errors
        """
        # Check circuit breaker
        self._check_circuit_breaker()
        
        # Rate limiting
        self.rate_limiter.acquire()
        
        # Prepare request
        url = f"{self.config.base_url}{endpoint}"
        request_id = f"req_{int(time.time() * 1000)}"
        
        # Metrics
        if self.metrics:
            self.metrics.record_request_start(method, endpoint)
        
        # Retry logic
        last_exception = None
        for attempt in range(self.config.max_retries + 1):
            try:
                start_time = time.time()
                
                # Make request
                response = self.session.request(
                    method=method,
                    url=url,
                    json=data,
                    params=params,
                    timeout=self.config.timeout
                )
                
                response_time = time.time() - start_time
                
                # Log request
                logger.info(
                    f"🌐 {method} {endpoint} → {response.status_code} "
                    f"({response_time:.3f}s) [ID: {request_id}]"
                )
                
                # Handle response
                if response.status_code >= 400:
                    self._handle_error_response(response, request_id)
                
                # Success - reset circuit breaker
                self._record_success()
                
                # Record metrics
                if self.metrics:
                    self.metrics.record_request_success(response_time)
                
                return response
                
            except requests.exceptions.RequestException as e:
                last_exception = e
                self._record_failure()
                
                if self.metrics:
                    self.metrics.record_request_error(type(e).__name__)
                
                if attempt < self.config.max_retries:
                    wait_time = (2 ** attempt) * 0.5  # Exponential backoff
                    logger.warning(
                        f"⚠️ Request failed (attempt {attempt + 1}/{self.config.max_retries + 1}), "
                        f"retrying in {wait_time:.1f}s: {str(e)}"
                    )
                    time.sleep(wait_time)
                else:
                    logger.error(f"❌ Request failed after {self.config.max_retries + 1} attempts: {str(e)}")
        
        # All retries failed
        raise PropellerAdsError(f"Request failed after {self.config.max_retries + 1} attempts: {str(last_exception)}")
    
    def _handle_error_response(self, response: requests.Response, request_id: str):
        """Handle error response."""
        try:
            error_data = response.json()
            message = error_data.get('message', 'Unknown API error')
            
            if 'errors' in error_data:
                if isinstance(error_data['errors'], list):
                    message = '; '.join(error_data['errors'])
        except:
            message = response.text or f"HTTP {response.status_code} error"
            error_data = None
        
        # Create appropriate exception
        if response.status_code == 401:
            raise AuthenticationError(message, response_data=error_data, request_id=request_id)
        elif response.status_code == 429:
            raise RateLimitError(message, response_data=error_data, request_id=request_id)
        elif response.status_code >= 500:
            self._record_failure()
            raise ServerError(message, status_code=response.status_code, response_data=error_data, request_id=request_id)
        else:
            raise PropellerAdsError(
                message, 
                status_code=response.status_code, 
                response_data=error_data, 
                request_id=request_id
            )
    
    def _check_circuit_breaker(self):
        """Check circuit breaker state."""
        if self.circuit_breaker['state'] == 'open':
            if time.time() - self.circuit_breaker['last_failure'] > self.circuit_breaker['recovery_timeout']:
                self.circuit_breaker['state'] = 'half-open'
                logger.info("🔄 Circuit breaker entering half-open state")
            else:
                raise PropellerAdsError("Circuit breaker is open - too many failures")
    
    def _record_success(self):
        """Record successful request."""
        if self.circuit_breaker['state'] == 'half-open':
            self.circuit_breaker['state'] = 'closed'
            self.circuit_breaker['failures'] = 0
            logger.info("✅ Circuit breaker closed - service recovered")
    
    def _record_failure(self):
        """Record failed request."""
        self.circuit_breaker['failures'] += 1
        self.circuit_breaker['last_failure'] = time.time()
        
        if self.circuit_breaker['failures'] >= self.circuit_breaker['failure_threshold']:
            self.circuit_breaker['state'] = 'open'
            logger.error("🚨 Circuit breaker opened - too many failures")
            
            if self.metrics:
                self.metrics.record_circuit_breaker_trip()
    
    def get_balance(self) -> BalanceResponse:
        """
        Get account balance.
        
        Returns:
            BalanceResponse: Account balance information
        """
        response = self._make_request('GET', '/adv/balance')
        
        # Handle plain text response
        balance_text = response.text.strip()
        if balance_text.startswith('"') and balance_text.endswith('"'):
            balance_text = balance_text[1:-1]
        
        try:
            amount = float(balance_text)
        except ValueError:
            raise PropellerAdsError(f"Invalid balance format: {balance_text}")
        
        return BalanceResponse(amount=amount)
    
    def get_campaigns(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Get campaigns list.
        
        Args:
            limit: Number of campaigns to return
            offset: Offset for pagination
            
        Returns:
            List[Dict]: List of campaigns
        """
        params = {
            'limit': limit,
            'offset': offset
        }
        
        response = self._make_request('GET', '/adv/campaigns', params=params)
        return response.json()
    
    def get_statistics(
        self,
        date_from: str,
        date_to: str,
        group_by: List[str] = None,
        campaign_ids: Optional[List[int]] = None
    ) -> Dict[str, Any]:
        """
        Get statistics.
        
        Args:
            date_from: Start date (YYYY-MM-DD HH:MM:SS)
            date_to: End date (YYYY-MM-DD HH:MM:SS)
            group_by: Grouping fields
            campaign_ids: Filter by campaign IDs
            
        Returns:
            Dict: Statistics data
        """
        data = {
            'day_from': date_from,
            'day_to': date_to,
            'tz': '+0000',
            'group_by': group_by or ['campaign_id']
        }
        
        if campaign_ids:
            data['campaign_ids'] = campaign_ids
        
        response = self._make_request('POST', '/adv/statistics', data=data)
        return response.json()
    
    def health_check(self) -> Dict[str, Any]:
        """
        Perform health check.
        
        Returns:
            Dict: Health status information
        """
        start_time = time.time()
        
        try:
            # Test balance endpoint
            balance = self.get_balance()
            response_time = time.time() - start_time
            
            # Get rate limiter status
            rate_status = self.rate_limiter.get_status()
            
            # Get metrics
            metrics_summary = self.metrics.get_summary() if self.metrics else {}
            
            return {
                'overall_status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'response_time': round(response_time, 3),
                'balance': balance.formatted,
                'rate_limiter': rate_status,
                'circuit_breaker': self.circuit_breaker,
                'metrics': metrics_summary
            }
            
        except Exception as e:
            return {
                'overall_status': 'unhealthy',
                'timestamp': datetime.now().isoformat(),
                'error': str(e),
                'circuit_breaker': self.circuit_breaker
            }
    
    def close(self):
        """Close the client and cleanup resources."""
        if self.session:
            self.session.close()
        logger.info("PropellerAds client closed")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
