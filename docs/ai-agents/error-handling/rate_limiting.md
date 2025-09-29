# Rate Limiting Strategies

## PropellerAds API Rate Limits

### Current Limits (as of 2025)
- **GET requests**: 30 per minute
- **POST requests**: 150 per minute  
- **PUT/DELETE requests**: 60 per minute
- **Burst allowance**: 10 requests per 10 seconds

### Rate Limit Headers
```
X-RateLimit-Limit: 30
X-RateLimit-Remaining: 25
X-RateLimit-Reset: 1640995200
```

## Implementation Strategies

### 1. Token Bucket Algorithm
```python
import time
import threading

class TokenBucket:
    """Token bucket rate limiter"""
    
    def __init__(self, capacity, refill_rate):
        self.capacity = capacity
        self.tokens = capacity
        self.refill_rate = refill_rate
        self.last_refill = time.time()
        self.lock = threading.Lock()
    
    def consume(self, tokens=1):
        """Consume tokens from bucket"""
        with self.lock:
            now = time.time()
            
            # Refill tokens
            elapsed = now - self.last_refill
            self.tokens = min(
                self.capacity,
                self.tokens + elapsed * self.refill_rate
            )
            self.last_refill = now
            
            # Check if enough tokens
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            
            return False
    
    def wait_for_tokens(self, tokens=1):
        """Wait until tokens are available"""
        while not self.consume(tokens):
            time.sleep(0.1)

# Usage
get_limiter = TokenBucket(capacity=30, refill_rate=0.5)  # 30 per minute
post_limiter = TokenBucket(capacity=150, refill_rate=2.5)  # 150 per minute

def rate_limited_get(client, endpoint, **kwargs):
    get_limiter.wait_for_tokens()
    return client._make_request('GET', endpoint, **kwargs)
```

### 2. Adaptive Rate Limiting
```python
class AdaptiveRateLimiter:
    """Adaptive rate limiter that adjusts based on API responses"""
    
    def __init__(self, initial_rate=1.0):
        self.current_rate = initial_rate  # requests per second
        self.last_request = 0
        self.consecutive_successes = 0
        self.consecutive_failures = 0
    
    def wait_and_execute(self, func, *args, **kwargs):
        """Execute function with adaptive rate limiting"""
        
        # Wait based on current rate
        now = time.time()
        time_since_last = now - self.last_request
        min_interval = 1.0 / self.current_rate
        
        if time_since_last < min_interval:
            time.sleep(min_interval - time_since_last)
        
        self.last_request = time.time()
        
        try:
            result = func(*args, **kwargs)
            self._handle_success()
            return result
        except RateLimitError:
            self._handle_rate_limit()
            raise
        except Exception as e:
            self._handle_error()
            raise
    
    def _handle_success(self):
        """Handle successful request"""
        self.consecutive_successes += 1
        self.consecutive_failures = 0
        
        # Gradually increase rate after sustained success
        if self.consecutive_successes >= 10:
            self.current_rate = min(self.current_rate * 1.1, 2.0)
            self.consecutive_successes = 0
    
    def _handle_rate_limit(self):
        """Handle rate limit error"""
        self.consecutive_failures += 1
        self.consecutive_successes = 0
        
        # Aggressively reduce rate
        self.current_rate *= 0.5
        
        # Wait longer before next attempt
        time.sleep(60 / self.current_rate)
    
    def _handle_error(self):
        """Handle other errors"""
        self.consecutive_failures += 1
        self.consecutive_successes = 0
        
        # Slightly reduce rate
        if self.consecutive_failures >= 3:
            self.current_rate *= 0.8
```

### 3. Queue-Based Rate Limiting
```python
import queue
import threading
import time

class RateLimitedQueue:
    """Queue-based rate limiter for batch operations"""
    
    def __init__(self, rate_limit, burst_size=10):
        self.rate_limit = rate_limit  # requests per second
        self.burst_size = burst_size
        self.queue = queue.Queue()
        self.running = False
        self.worker_thread = None
    
    def start(self):
        """Start the rate-limited worker"""
        self.running = True
        self.worker_thread = threading.Thread(target=self._worker)
        self.worker_thread.start()
    
    def stop(self):
        """Stop the worker"""
        self.running = False
        if self.worker_thread:
            self.worker_thread.join()
    
    def submit(self, func, *args, **kwargs):
        """Submit a function to be executed with rate limiting"""
        future = threading.Event()
        result_container = {'result': None, 'error': None}
        
        self.queue.put((func, args, kwargs, future, result_container))
        
        # Wait for completion
        future.wait()
        
        if result_container['error']:
            raise result_container['error']
        
        return result_container['result']
    
    def _worker(self):
        """Worker thread that processes queue with rate limiting"""
        tokens = self.burst_size
        last_refill = time.time()
        
        while self.running:
            try:
                # Refill tokens
                now = time.time()
                elapsed = now - last_refill
                tokens = min(
                    self.burst_size,
                    tokens + elapsed * self.rate_limit
                )
                last_refill = now
                
                # Get next item
                item = self.queue.get(timeout=1)
                func, args, kwargs, future, result_container = item
                
                # Wait for token
                if tokens < 1:
                    time.sleep((1 - tokens) / self.rate_limit)
                    tokens = 1
                
                tokens -= 1
                
                # Execute function
                try:
                    result = func(*args, **kwargs)
                    result_container['result'] = result
                except Exception as e:
                    result_container['error'] = e
                finally:
                    future.set()
                    self.queue.task_done()
                    
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Worker error: {e}")

# Usage
rate_limiter = RateLimitedQueue(rate_limit=0.5)  # 30 per minute
rate_limiter.start()

# Submit rate-limited requests
result = rate_limiter.submit(client.get_campaigns)
```

## Best Practices

### 1. Respect API Limits
- Always check rate limit headers
- Implement proper backoff strategies
- Use bulk operations when available
- Cache frequently accessed data

### 2. Monitor Rate Limit Usage
```python
def track_rate_limit_usage(response):
    """Track rate limit usage from API response"""
    
    headers = response.headers
    
    limit = int(headers.get('X-RateLimit-Limit', 0))
    remaining = int(headers.get('X-RateLimit-Remaining', 0))
    reset_time = int(headers.get('X-RateLimit-Reset', 0))
    
    usage_percentage = ((limit - remaining) / limit) * 100 if limit > 0 else 0
    
    if usage_percentage > 80:
        print(f"⚠️  Rate limit usage high: {usage_percentage:.1f}%")
    
    return {
        'limit': limit,
        'remaining': remaining,
        'reset_time': reset_time,
        'usage_percentage': usage_percentage
    }
```

### 3. Graceful Degradation
```python
def graceful_api_call(client, operation, **kwargs):
    """Make API call with graceful degradation"""
    
    try:
        # Primary attempt
        return operation(**kwargs)
    except RateLimitError:
        # Fallback to cached data if available
        cached_result = get_cached_result(operation.__name__, kwargs)
        if cached_result:
            print("⚠️  Using cached data due to rate limit")
            return cached_result
        
        # Wait and retry
        time.sleep(60)
        return operation(**kwargs)
    except Exception as e:
        # Log error and return safe default
        log_api_error(e, {'operation': operation.__name__, 'kwargs': kwargs})
        return get_safe_default(operation.__name__)
```
