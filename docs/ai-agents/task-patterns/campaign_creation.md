# Task Pattern: Campaign Creation

## Context
- **Purpose**: Create a new advertising campaign in PropellerAds
- **Prerequisites**: Valid API key, sufficient account balance, targeting parameters
- **Expected Outcome**: Active campaign with unique campaign ID

## Execution Flow

### 1. Initial State
**Required:**
- API key authenticated
- Account balance > minimum campaign budget
- Valid targeting parameters (country, OS, browser, etc.)

**Optional:**
- Custom creative materials
- Advanced targeting settings
- Bid optimization preferences

### 2. Operation Steps

```python
# Step 1: Initialize client
client = PropellerAdsUltimateClient()

# Step 2: Validate inputs
required_params = {
    'name': 'Campaign Name',
    'budget': 100.0,  # Minimum budget
    'countries': ['US', 'CA'],  # Target countries
    'os': ['android', 'ios'],   # Target OS
    'browsers': ['chrome', 'safari']  # Target browsers
}

# Step 3: Create campaign
result = client.create_campaign(
    name=required_params['name'],
    budget=required_params['budget'],
    targeting={
        'countries': required_params['countries'],
        'os': required_params['os'],
        'browsers': required_params['browsers']
    }
)

# Step 4: Verify creation
if result['success']:
    campaign_id = result['data']['campaign_id']
    print(f"✅ Campaign created: {campaign_id}")
else:
    print(f"❌ Error: {result['error']}")
```

### 3. Validation
**Success Indicators:**
- HTTP status code: 200
- Response contains campaign_id
- Campaign status: 'pending' or 'active'

**Error Conditions:**
- Insufficient balance
- Invalid targeting parameters
- Rate limit exceeded
- API authentication failure

## Error Recovery

### Common Errors and Solutions

1. **Insufficient Balance**
   - Error: "Insufficient funds"
   - Solution: Check balance, add funds, or reduce budget
   - Code: `client.get_balance()`

2. **Invalid Targeting**
   - Error: "Invalid country code"
   - Solution: Validate targeting parameters
   - Code: `client.get_targeting_options()`

3. **Rate Limit**
   - Error: HTTP 429
   - Solution: Exponential backoff retry
   - Wait time: 5s, 10s, 20s, 40s

### Retry Strategy
```python
import time
import random

def create_campaign_with_retry(client, params, max_retries=3):
    for attempt in range(max_retries):
        try:
            result = client.create_campaign(**params)
            if result['success']:
                return result
        except RateLimitError:
            wait_time = (2 ** attempt) + random.uniform(0, 1)
            time.sleep(wait_time)
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
    return None
```

## Related Patterns
- [Campaign Monitoring](campaign_monitoring.md)
- [Budget Management](budget_management.md)
- [Targeting Optimization](targeting_optimization.md)

## Dependencies
- Valid PropellerAds account
- Sufficient API permissions
- Network connectivity
