"""
Enhanced PropellerAds Client with complete API coverage

Production-ready PropellerAds SSP API v5 client with all endpoints.
"""

import os
import time
import logging
import requests
from typing import Optional, Dict, Any, List, Union
from datetime import datetime
from decimal import Decimal

from .exceptions import PropellerAdsError, AuthenticationError, RateLimitError, ServerError
from .utils.rate_limiter import RateLimiter
from .monitoring.metrics import MetricsCollector

# Import API classes
from .api.campaigns import CampaignAPI
from .api.statistics import StatisticsAPI
from .api.balance import BalanceAPI
from .api.collections import CollectionsAPI

# All API classes imported above

# Import schemas (with fallback for missing modules)
try:
    from .schemas.campaign import Campaign
except ImportError:
    Campaign = None

try:
    from .schemas.statistics import StatisticsResponse
except ImportError:
    StatisticsResponse = None

try:
    from .schemas.balance import BalanceResponse as SchemaBalanceResponse
except ImportError:
    SchemaBalanceResponse = None

try:
    from .schemas.collections import TargetingOptions
except ImportError:
    TargetingOptions = None


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ClientConfig:
    """Client configuration."""
    def __init__(self):
        self.max_retries = 3
        self.timeout = 30
        self.rate_limit = 60  # requests per minute
        self.circuit_breaker_threshold = 5
        self.circuit_breaker_timeout = 60


class EnhancedPropellerAdsClient:
    """
    Enhanced PropellerAds SSP API v5 Client with complete endpoint coverage.
    
    Features:
    - Complete API endpoint coverage
    - Modular API classes
    - Intelligent retry with exponential backoff
    - Rate limiting with token bucket algorithm
    - Circuit breaker pattern
    - Comprehensive error handling
    - Request/response logging
    - Metrics collection
    - Connection pooling
    - Pydantic schema validation
    """
    
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://ssp-api.propellerads.com/v5",
        config: Optional[ClientConfig] = None,
        enable_metrics: bool = True
    ):
        """
        Initialize PropellerAds client.
        
        Args:
            api_key: PropellerAds API key
            base_url: API base URL
            config: Client configuration
            enable_metrics: Enable metrics collection
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.config = config or ClientConfig()
        
        # Initialize session
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
            'User-Agent': 'PropellerAds-Python-SDK/2.0.0'
        })
        
        # Initialize components
        self.rate_limiter = RateLimiter(self.config.rate_limit)
        self.metrics = MetricsCollector() if enable_metrics else None
        
        # Circuit breaker
        self.circuit_breaker = {
            'state': 'closed',  # closed, open, half-open
            'failure_count': 0,
            'last_failure': 0,
            'recovery_timeout': self.config.circuit_breaker_timeout
        }
        
        # Initialize API modules
        self.campaigns = CampaignAPI(self)
        self.statistics = StatisticsAPI(self)
        self.balance = BalanceAPI(self)
        self.collections = CollectionsAPI(self)
        
        logger.info(f"Enhanced PropellerAds client initialized (rate_limit: {self.config.rate_limit}/min)")
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        data: Optional[Dict] = None,
        **kwargs
    ) -> requests.Response:
        """
        Make HTTP request with retry logic and error handling.
        
        Args:
            method: HTTP method
            endpoint: API endpoint
            params: Query parameters
            data: Request body data
            **kwargs: Additional request arguments
            
        Returns:
            Response object
            
        Raises:
            PropellerAdsError: On API errors
        """
        # Check circuit breaker
        self._check_circuit_breaker()
        
        # Rate limiting
        self.rate_limiter.acquire()
        
        # Generate request ID
        request_id = f"req_{int(time.time() * 1000)}"
        
        # Prepare request
        url = f"{self.base_url}{endpoint}"
        
        # Add request ID to headers
        headers = kwargs.get('headers', {})
        headers['X-Request-ID'] = request_id
        kwargs['headers'] = headers
        
        last_exception = None
        
        for attempt in range(self.config.max_retries + 1):
            try:
                start_time = time.time()
                
                # Make request
                response = self.session.request(
                    method=method,
                    url=url,
                    params=params,
                    json=data,
                    timeout=self.config.timeout,
                    **kwargs
                )
                
                duration = time.time() - start_time
                
                # Log request
                logger.info(
                    f"🌐 {method} {endpoint} → {response.status_code} "
                    f"({duration:.3f}s) [ID: {request_id}]"
                )
                
                # Record metrics
                if self.metrics:
                    self.metrics.record_request(method, endpoint, response.status_code, duration)
                
                # Handle response
                if response.status_code >= 400:
                    self._handle_error_response(response, request_id)
                
                # Reset circuit breaker on success
                if self.circuit_breaker['state'] != 'closed':
                    self.circuit_breaker['state'] = 'closed'
                    self.circuit_breaker['failure_count'] = 0
                    logger.info("✅ Circuit breaker reset to closed state")
                
                return response
                
            except (requests.RequestException, PropellerAdsError) as e:
                last_exception = e
                
                # Record failure
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
                raise PropellerAdsError("Circuit breaker is open - API temporarily unavailable")
    
    def _record_failure(self):
        """Record failure for circuit breaker."""
        self.circuit_breaker['failure_count'] += 1
        self.circuit_breaker['last_failure'] = time.time()
        
        if self.circuit_breaker['failure_count'] >= self.config.circuit_breaker_threshold:
            self.circuit_breaker['state'] = 'open'
            logger.warning("🚨 Circuit breaker opened due to repeated failures")
    
    # Convenience methods for backward compatibility
    def get_balance(self):
        """Get account balance."""
        if self.balance:
            return self.balance.get_balance()
        else:
            # Fallback to direct API call
            response = self._make_request('GET', '/adv/balance')
            data = response.json()
            from .client import BalanceResponse
            return BalanceResponse(data['amount'], data.get('currency', 'USD'))
    
    def get_campaigns(self, limit: int = 100, offset: int = 0):
        """Get campaigns list."""
        if self.campaigns:
            return self.campaigns.get_campaigns(limit=limit, offset=offset)
        else:
            # Fallback to direct API call
            params = {'limit': limit, 'offset': offset}
            response = self._make_request('GET', '/adv/campaigns', params=params)
            return response.json()
    
    def get_statistics(
        self,
        date_from: str,
        date_to: str,
        group_by: List[str] = None,
        campaign_ids: Optional[List[int]] = None
    ):
        """Get statistics."""
        if self.statistics:
            return self.statistics.get_statistics(
                date_from=date_from,
                date_to=date_to,
                group_by=group_by,
                campaign_ids=campaign_ids
            )
        else:
            # Fallback to direct API call
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
    
    # Convenience campaign creation methods
    def create_onclick_campaign(
        self,
        name: str,
        target_url: str,
        countries: List[str],
        budget: float,
        **kwargs
    ) -> Campaign:
        """Create Onclick campaign with simplified parameters."""
        targeting = {
            "country": {"list": countries, "is_excluded": False},
            "time_table": {"list": ["Mon00"], "is_excluded": False}
        }
        
        return self.campaigns.create_campaign(
            name=name,
            direction="onclick",
            rate_model="cpa",
            target_url=target_url,
            targeting=targeting,
            daily_budget=budget,
            **kwargs
        )
    
    def create_push_campaign(
        self,
        name: str,
        target_url: str,
        countries: List[str],
        budget: float,
        **kwargs
    ) -> Campaign:
        """Create Push campaign with simplified parameters."""
        targeting = {
            "country": {"list": countries, "is_excluded": False},
            "time_table": {"list": ["Mon00"], "is_excluded": False}
        }
        
        return self.campaigns.create_campaign(
            name=name,
            direction="push",
            rate_model="cpm",
            target_url=target_url,
            targeting=targeting,
            daily_budget=budget,
            **kwargs
        )
    
    def health_check(self) -> Dict[str, Any]:
        """
        Perform comprehensive health check.
        
        Returns:
            Dict: Health status information
        """
        start_time = time.time()
        
        try:
            # Test balance endpoint
            balance = self.get_balance()
            response_time = time.time() - start_time
            
            # Get rate limiter status
            try:
                rate_status = self.rate_limiter.get_status()
            except:
                rate_status = {'available': True}
            
            # Get metrics
            try:
                metrics_summary = self.metrics.get_summary() if self.metrics else {}
            except:
                metrics_summary = {}
            
            # Format balance
            balance_str = balance.formatted if hasattr(balance, 'formatted') else str(balance)
            
            return {
                'overall_status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'response_time': round(response_time, 3),
                'balance': balance_str,
                'rate_limiter': rate_status,
                'circuit_breaker': self.circuit_breaker,
                'metrics': metrics_summary,
                'api_modules': {
                    'campaigns': 'available' if self.campaigns else 'fallback',
                    'statistics': 'available' if self.statistics else 'fallback',
                    'balance': 'available' if self.balance else 'fallback',
                    'collections': 'available' if self.collections else 'fallback'
                }
            }
            
        except Exception as e:
            response_time = time.time() - start_time
            return {
                'overall_status': 'unhealthy',
                'timestamp': datetime.now().isoformat(),
                'response_time': round(response_time, 3),
                'error': str(e),
                'circuit_breaker': self.circuit_breaker
            }
    
    def close(self):
        """Close the client and cleanup resources."""
        if self.session:
            self.session.close()
        logger.info("Enhanced PropellerAds client closed")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


# Backward compatibility alias
PropellerAdsClient = EnhancedPropellerAdsClient
