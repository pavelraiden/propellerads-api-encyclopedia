# Common Errors and Recovery Procedures

## API Authentication Errors

### Error: 401 Unauthorized
**Symptoms:**
- HTTP status code: 401
- Message: "Invalid API key" or "Authentication failed"

**Causes:**
- Expired or invalid API key
- API key not properly set in environment
- Incorrect API key format

**Recovery Steps:**
1. Verify API key in environment variables
2. Check API key format and validity
3. Regenerate API key if necessary
4. Update environment configuration

```python
# Verification code
import os
api_key = os.getenv('MainAPI')
if not api_key:
    raise ValueError("MainAPI environment variable not set")
if len(api_key) < 32:
    raise ValueError("API key appears to be invalid (too short)")
```

## Rate Limiting Errors

### Error: 429 Too Many Requests
**Symptoms:**
- HTTP status code: 429
- Headers: X-RateLimit-Remaining: 0

**Rate Limits:**
- GET requests: 30 per minute
- POST requests: 150 per minute
- PUT/DELETE requests: 60 per minute

**Recovery Strategy:**
```python
import time
import random

def exponential_backoff_retry(func, max_retries=5):
    for attempt in range(max_retries):
        try:
            return func()
        except RateLimitError as e:
            if attempt == max_retries - 1:
                raise e
            
            # Exponential backoff with jitter
            wait_time = (2 ** attempt) + random.uniform(0, 1)
            print(f"Rate limited. Waiting {wait_time:.2f}s before retry {attempt + 1}")
            time.sleep(wait_time)
    
    raise Exception("Max retries exceeded")
```

## Data Validation Errors

### Error: 400 Bad Request
**Common Causes:**
- Invalid targeting parameters
- Missing required fields
- Incorrect data types
- Out-of-range values

**Validation Procedures:**
```python
def validate_campaign_data(campaign_data):
    """Validate campaign data before API call"""
    
    errors = []
    
    # Required fields
    required_fields = ['name', 'budget', 'countries']
    for field in required_fields:
        if field not in campaign_data:
            errors.append(f"Missing required field: {field}")
    
    # Budget validation
    if 'budget' in campaign_data:
        budget = campaign_data['budget']
        if not isinstance(budget, (int, float)) or budget < 10:
            errors.append("Budget must be numeric and >= 10")
    
    # Country validation
    if 'countries' in campaign_data:
        valid_countries = get_valid_countries()  # From API
        invalid_countries = set(campaign_data['countries']) - set(valid_countries)
        if invalid_countries:
            errors.append(f"Invalid countries: {invalid_countries}")
    
    return errors

def get_valid_countries():
    """Get list of valid country codes from API"""
    # Implementation to fetch from targeting options
    pass
```

## Network and Connectivity Errors

### Error: Connection Timeout
**Symptoms:**
- requests.exceptions.Timeout
- requests.exceptions.ConnectionError

**Recovery Steps:**
1. Check network connectivity
2. Verify API endpoint availability
3. Implement retry with timeout adjustment
4. Use circuit breaker pattern

```python
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def create_resilient_session():
    """Create HTTP session with retry strategy"""
    
    session = requests.Session()
    
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["HEAD", "GET", "OPTIONS", "POST", "PUT", "DELETE"]
    )
    
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    return session
```

## Business Logic Errors

### Error: Insufficient Balance
**Symptoms:**
- API returns success=false
- Message contains "insufficient" or "balance"

**Recovery Options:**
1. Reduce campaign budget
2. Pause low-performing campaigns
3. Alert for manual fund addition
4. Implement budget reallocation

```python
def handle_insufficient_balance(client, campaign_data):
    """Handle insufficient balance error"""
    
    # Get current balance
    balance = client.get_balance()
    current_balance = float(balance['data'])
    
    # Calculate required budget
    required_budget = campaign_data['budget']
    
    if current_balance < required_budget:
        # Option 1: Reduce budget to available balance
        adjusted_budget = min(required_budget, current_balance * 0.8)
        
        if adjusted_budget >= 10:  # Minimum budget
            campaign_data['budget'] = adjusted_budget
            return campaign_data
        else:
            # Option 2: Pause other campaigns to free budget
            return pause_low_performing_campaigns(client, required_budget)
    
    return campaign_data
```

## Error Logging and Monitoring

### Structured Error Logging
```python
import logging
import json
from datetime import datetime

def log_api_error(error, context):
    """Log API errors with structured format"""
    
    error_data = {
        'timestamp': datetime.now().isoformat(),
        'error_type': type(error).__name__,
        'error_message': str(error),
        'context': context,
        'recovery_attempted': False
    }
    
    logging.error(json.dumps(error_data))
    
    return error_data

# Usage
try:
    result = client.create_campaign(**params)
except Exception as e:
    error_data = log_api_error(e, {
        'operation': 'create_campaign',
        'params': params,
        'user_id': 'ai_agent'
    })
    
    # Attempt recovery
    recovery_result = attempt_error_recovery(e, params)
    error_data['recovery_attempted'] = True
    error_data['recovery_success'] = recovery_result['success']
```
