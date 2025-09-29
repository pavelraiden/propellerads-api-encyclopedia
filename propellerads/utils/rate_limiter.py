"""
Rate Limiter Utility

Token bucket algorithm implementation for API rate limiting.
"""

import time
import threading
from typing import Optional, Dict, Any
from dataclasses import dataclass


@dataclass
class RateLimitConfig:
    """Rate limiter configuration."""
    max_requests: int = 60
    time_window: int = 60  # seconds
    burst_allowance: float = 1.5  # Allow 50% burst


class RateLimiter:
    """
    Token bucket rate limiter.
    
    Implements token bucket algorithm for smooth rate limiting with burst support.
    Thread-safe implementation suitable for concurrent usage.
    
    Features:
    - Token bucket algorithm
    - Burst allowance
    - Thread-safe operations
    - Configurable limits
    - Status monitoring
    
    Example:
        >>> limiter = RateLimiter(max_requests=60, time_window=60)
        >>> limiter.acquire()  # Blocks if rate limit exceeded
        >>> status = limiter.get_status()
    """
    
    def __init__(
        self,
        max_requests: int = 60,
        time_window: int = 60,
        burst_allowance: float = 1.5
    ):
        """
        Initialize rate limiter.
        
        Args:
            max_requests: Maximum requests per time window
            time_window: Time window in seconds
            burst_allowance: Burst multiplier (1.0 = no burst, 2.0 = 100% burst)
        """
        self.config = RateLimitConfig(
            max_requests=max_requests,
            time_window=time_window,
            burst_allowance=burst_allowance
        )
        
        # Token bucket parameters
        self.bucket_size = int(max_requests * burst_allowance)
        self.refill_rate = max_requests / time_window  # tokens per second
        
        # State
        self.tokens = float(self.bucket_size)  # Start with full bucket
        self.last_refill = time.time()
        
        # Thread safety
        self._lock = threading.Lock()
        
        # Statistics
        self.total_requests = 0
        self.blocked_requests = 0
        self.total_wait_time = 0.0
    
    def acquire(self, tokens: int = 1, timeout: Optional[float] = None) -> bool:
        """
        Acquire tokens from the bucket.
        
        Args:
            tokens: Number of tokens to acquire
            timeout: Maximum time to wait (None = wait indefinitely)
            
        Returns:
            bool: True if tokens acquired, False if timeout
            
        Raises:
            ValueError: If tokens <= 0
        """
        if tokens <= 0:
            raise ValueError("Tokens must be positive")
        
        if tokens > self.bucket_size:
            raise ValueError(f"Cannot acquire {tokens} tokens (bucket size: {self.bucket_size})")
        
        start_time = time.time()
        
        with self._lock:
            self.total_requests += 1
            
            while True:
                # Refill bucket
                self._refill_bucket()
                
                # Check if we have enough tokens
                if self.tokens >= tokens:
                    self.tokens -= tokens
                    wait_time = time.time() - start_time
                    self.total_wait_time += wait_time
                    return True
                
                # Calculate wait time
                tokens_needed = tokens - self.tokens
                wait_time = tokens_needed / self.refill_rate
                
                # Check timeout
                if timeout is not None:
                    elapsed = time.time() - start_time
                    if elapsed + wait_time > timeout:
                        self.blocked_requests += 1
                        return False
                
                # Wait and retry
                time.sleep(min(wait_time, 0.1))  # Sleep in small increments
    
    def try_acquire(self, tokens: int = 1) -> bool:
        """
        Try to acquire tokens without blocking.
        
        Args:
            tokens: Number of tokens to acquire
            
        Returns:
            bool: True if tokens acquired, False otherwise
        """
        return self.acquire(tokens, timeout=0)
    
    def _refill_bucket(self):
        """Refill the token bucket based on elapsed time."""
        now = time.time()
        elapsed = now - self.last_refill
        
        if elapsed > 0:
            # Add tokens based on elapsed time
            tokens_to_add = elapsed * self.refill_rate
            self.tokens = min(self.bucket_size, self.tokens + tokens_to_add)
            self.last_refill = now
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get current rate limiter status.
        
        Returns:
            Dict: Status information including tokens, statistics, and configuration
        """
        with self._lock:
            self._refill_bucket()
            
            return {
                'tokens_available': round(self.tokens, 2),
                'bucket_size': self.bucket_size,
                'refill_rate': round(self.refill_rate, 4),
                'utilization': round((self.bucket_size - self.tokens) / self.bucket_size * 100, 1),
                'statistics': {
                    'total_requests': self.total_requests,
                    'blocked_requests': self.blocked_requests,
                    'success_rate': round(
                        (self.total_requests - self.blocked_requests) / max(self.total_requests, 1) * 100, 1
                    ),
                    'average_wait_time': round(
                        self.total_wait_time / max(self.total_requests, 1), 4
                    )
                },
                'configuration': {
                    'max_requests': self.config.max_requests,
                    'time_window': self.config.time_window,
                    'burst_allowance': self.config.burst_allowance
                }
            }
    
    def reset(self):
        """Reset the rate limiter state."""
        with self._lock:
            self.tokens = float(self.bucket_size)
            self.last_refill = time.time()
            self.total_requests = 0
            self.blocked_requests = 0
            self.total_wait_time = 0.0
    
    def set_rate(self, max_requests: int, time_window: int):
        """
        Update rate limiting parameters.
        
        Args:
            max_requests: New maximum requests per time window
            time_window: New time window in seconds
        """
        with self._lock:
            self.config.max_requests = max_requests
            self.config.time_window = time_window
            
            # Recalculate parameters
            self.bucket_size = int(max_requests * self.config.burst_allowance)
            self.refill_rate = max_requests / time_window
            
            # Adjust current tokens if bucket size changed
            self.tokens = min(self.tokens, self.bucket_size)
    
    def wait_for_capacity(self, required_tokens: int = 1) -> float:
        """
        Calculate wait time for required capacity.
        
        Args:
            required_tokens: Number of tokens needed
            
        Returns:
            float: Wait time in seconds (0 if capacity available)
        """
        with self._lock:
            self._refill_bucket()
            
            if self.tokens >= required_tokens:
                return 0.0
            
            tokens_needed = required_tokens - self.tokens
            return tokens_needed / self.refill_rate
    
    def __enter__(self):
        """Context manager entry."""
        self.acquire()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        pass  # Nothing to clean up


class AdaptiveRateLimiter(RateLimiter):
    """
    Adaptive rate limiter that adjusts based on API responses.
    
    Automatically adjusts rate limits based on:
    - 429 (Too Many Requests) responses
    - Response times
    - Error rates
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Adaptive parameters
        self.base_rate = self.config.max_requests
        self.adaptation_factor = 0.8  # Reduce rate by 20% on errors
        self.recovery_factor = 1.05   # Increase rate by 5% on success
        self.min_rate = max(1, self.base_rate // 10)  # Minimum 10% of base rate
        
        # Response tracking
        self.recent_errors = []
        self.recent_response_times = []
        self.window_size = 10  # Track last 10 responses
    
    def record_response(
        self,
        status_code: int,
        response_time: float,
        retry_after: Optional[int] = None
    ):
        """
        Record API response for adaptive adjustment.
        
        Args:
            status_code: HTTP status code
            response_time: Response time in seconds
            retry_after: Retry-After header value (for 429 responses)
        """
        with self._lock:
            # Record error
            is_error = status_code >= 400
            self.recent_errors.append(is_error)
            if len(self.recent_errors) > self.window_size:
                self.recent_errors.pop(0)
            
            # Record response time
            self.recent_response_times.append(response_time)
            if len(self.recent_response_times) > self.window_size:
                self.recent_response_times.pop(0)
            
            # Adapt rate based on response
            if status_code == 429:
                # Rate limit hit - reduce rate significantly
                if retry_after:
                    # Use server's suggestion
                    new_rate = max(self.min_rate, 60 // retry_after)
                else:
                    # Reduce by adaptation factor
                    new_rate = max(self.min_rate, int(self.config.max_requests * self.adaptation_factor))
                
                self._update_rate(new_rate)
            
            elif is_error:
                # Other error - slight reduction
                error_rate = sum(self.recent_errors) / len(self.recent_errors)
                if error_rate > 0.2:  # More than 20% errors
                    new_rate = max(self.min_rate, int(self.config.max_requests * 0.9))
                    self._update_rate(new_rate)
            
            else:
                # Success - gradually increase rate
                if len(self.recent_errors) >= self.window_size:
                    error_rate = sum(self.recent_errors) / len(self.recent_errors)
                    avg_response_time = sum(self.recent_response_times) / len(self.recent_response_times)
                    
                    if error_rate < 0.05 and avg_response_time < 1.0:  # Low error rate and fast responses
                        new_rate = min(self.base_rate, int(self.config.max_requests * self.recovery_factor))
                        self._update_rate(new_rate)
    
    def _update_rate(self, new_rate: int):
        """Update the rate limit."""
        if new_rate != self.config.max_requests:
            self.set_rate(new_rate, self.config.time_window)
    
    def get_adaptive_status(self) -> Dict[str, Any]:
        """Get adaptive rate limiter status."""
        status = self.get_status()
        
        with self._lock:
            error_rate = sum(self.recent_errors) / max(len(self.recent_errors), 1)
            avg_response_time = sum(self.recent_response_times) / max(len(self.recent_response_times), 1)
            
            status['adaptive'] = {
                'base_rate': self.base_rate,
                'current_rate': self.config.max_requests,
                'min_rate': self.min_rate,
                'recent_error_rate': round(error_rate * 100, 1),
                'average_response_time': round(avg_response_time, 3),
                'adaptation_active': self.config.max_requests != self.base_rate
            }
        
        return status
