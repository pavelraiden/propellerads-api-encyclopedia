# 🚀 Production Deployment Guide

## 📋 Pre-Deployment Checklist

### ✅ Security Requirements
- [ ] API keys stored in secure environment variables
- [ ] Rate limiting configured and tested
- [ ] Input validation implemented
- [ ] Error handling masks sensitive information
- [ ] HTTPS-only communication enforced
- [ ] Security scan passed (bandit)
- [ ] Dependency vulnerabilities checked (safety)

### ✅ Performance Requirements
- [ ] Load testing completed
- [ ] Memory usage profiled
- [ ] Response times benchmarked
- [ ] Circuit breaker tested
- [ ] Connection pooling configured
- [ ] Caching strategy implemented

### ✅ Testing Requirements
- [ ] All unit tests passing (161+ tests)
- [ ] Integration tests completed
- [ ] Performance tests passed
- [ ] Security tests validated
- [ ] Real API tests successful
- [ ] Code coverage > 80%

### ✅ Documentation Requirements
- [ ] API documentation complete
- [ ] User guide for non-developers
- [ ] Installation instructions tested
- [ ] Troubleshooting guide available
- [ ] Performance tuning guide
- [ ] Security best practices documented

## 🏗️ Infrastructure Setup

### 1. Server Requirements

**Minimum Requirements:**
- Python 3.8+
- 2GB RAM
- 1 CPU core
- 10GB disk space

**Recommended for Production:**
- Python 3.11+
- 4GB RAM
- 2+ CPU cores
- 50GB disk space
- Load balancer
- Monitoring system

### 2. Environment Configuration

```bash
# Production environment variables
export ENVIRONMENT=production
export MainAPI=your_propellerads_api_key
export ANTHROPIC_API_KEY=your_claude_api_key
export LOG_LEVEL=INFO
export RATE_LIMIT=60
export ENABLE_CIRCUIT_BREAKER=true
export MAX_RETRIES=3
export TIMEOUT=30
```

### 3. Installation Steps

```bash
# 1. Clone repository
git clone https://github.com/pavelraiden/propellerads-api-encyclopedia.git
cd propellerads-api-encyclopedia

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env with your API keys

# 5. Run tests
pytest tests/ -v

# 6. Start application
python claude_natural_interface_v2.py
```

## 🔒 Security Configuration

### 1. API Key Management

```bash
# Use environment variables (recommended)
export MainAPI="your_api_key_here"

# Or use .env file (development only)
echo "MainAPI=your_api_key_here" > .env
```

### 2. Rate Limiting Setup

```python
# Configure rate limiting
client = PropellerAdsClient(
    api_key=os.getenv('MainAPI'),
    rate_limit=60,  # requests per minute
    enable_circuit_breaker=True
)
```

### 3. Security Headers

```python
# Implement security headers
SECURITY_HEADERS = {
    'X-Content-Type-Options': 'nosniff',
    'X-Frame-Options': 'DENY',
    'X-XSS-Protection': '1; mode=block',
    'Strict-Transport-Security': 'max-age=31536000'
}
```

## ⚡ Performance Optimization

### 1. Connection Pooling

```python
# Configure connection pooling
import requests.adapters

session = requests.Session()
adapter = requests.adapters.HTTPAdapter(
    pool_connections=10,
    pool_maxsize=20,
    max_retries=3
)
session.mount('https://', adapter)
```

### 2. Caching Strategy

```python
# Implement response caching
from functools import lru_cache

@lru_cache(maxsize=128)
def get_cached_data(endpoint, params):
    return client.make_request(endpoint, params)
```

### 3. Async Operations

```python
# Use async client for high-throughput
from propellerads.async_client import AsyncPropellerAdsClient

async def process_campaigns():
    async with AsyncPropellerAdsClient() as client:
        campaigns = await client.get_campaigns()
        return campaigns
```

## 📊 Monitoring & Logging

### 1. Logging Configuration

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('propellerads.log'),
        logging.StreamHandler()
    ]
)
```

### 2. Health Checks

```python
# Implement health check endpoint
def health_check():
    try:
        balance = client.get_balance()
        return {"status": "healthy", "balance": balance.amount}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}
```

### 3. Performance Metrics

```python
# Monitor key metrics
import time
import psutil

def monitor_performance():
    start_time = time.time()
    memory_usage = psutil.Process().memory_info().rss / 1024 / 1024
    
    # Your API call here
    response = client.get_campaigns()
    
    response_time = time.time() - start_time
    
    return {
        "response_time": response_time,
        "memory_usage_mb": memory_usage,
        "status": "success"
    }
```

## 🔄 CI/CD Pipeline

### 1. GitHub Actions Setup

The repository includes a complete CI/CD pipeline:

- **Testing:** Runs on Python 3.8-3.11
- **Security:** Bandit and Safety scans
- **Performance:** Benchmark testing
- **Build:** Package creation and validation

### 2. Deployment Automation

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    tags:
      - 'v*'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to server
        run: |
          ssh user@server 'cd /app && git pull && systemctl restart propellerads'
```

## 🚨 Troubleshooting

### Common Issues

**1. API Key Errors**
```bash
# Check environment variables
echo $MainAPI
echo $ANTHROPIC_API_KEY

# Verify API key validity
python -c "from propellerads import PropellerAdsClient; print(PropellerAdsClient().get_balance())"
```

**2. Rate Limiting**
```python
# Adjust rate limits
client = PropellerAdsClient(rate_limit=30)  # Reduce from 60 to 30
```

**3. Memory Issues**
```bash
# Monitor memory usage
python -c "import psutil; print(f'Memory: {psutil.virtual_memory().percent}%')"
```

**4. Connection Timeouts**
```python
# Increase timeout
client = PropellerAdsClient(timeout=60)  # Increase from 30 to 60
```

## 📈 Performance Benchmarks

### Expected Performance Metrics

| Metric | Target | Acceptable |
|--------|--------|------------|
| API Response Time | < 500ms | < 1000ms |
| Memory Usage | < 50MB | < 100MB |
| CPU Usage | < 10% | < 25% |
| Error Rate | < 0.1% | < 1% |
| Uptime | > 99.9% | > 99% |

### Load Testing

```bash
# Run load tests
pytest tests/test_performance_simple.py -v --benchmark-only
```

## 🔐 Security Best Practices

### 1. API Key Rotation

```bash
# Rotate API keys monthly
# 1. Generate new key in PropellerAds dashboard
# 2. Update environment variable
# 3. Test with new key
# 4. Deactivate old key
```

### 2. Access Control

```python
# Implement IP whitelisting
ALLOWED_IPS = ['192.168.1.0/24', '10.0.0.0/8']

def check_ip_access(request_ip):
    return request_ip in ALLOWED_IPS
```

### 3. Audit Logging

```python
# Log all API calls
def audit_log(action, user, result):
    logger.info(f"AUDIT: {user} performed {action} with result {result}")
```

## 📞 Support & Maintenance

### Regular Maintenance Tasks

**Daily:**
- [ ] Check error logs
- [ ] Monitor performance metrics
- [ ] Verify API connectivity

**Weekly:**
- [ ] Review security logs
- [ ] Update dependencies
- [ ] Run full test suite

**Monthly:**
- [ ] Rotate API keys
- [ ] Performance optimization review
- [ ] Security audit

### Emergency Procedures

**API Outage:**
1. Check PropellerAds status page
2. Verify network connectivity
3. Check API key validity
4. Enable circuit breaker
5. Contact support if needed

**Performance Issues:**
1. Check system resources
2. Review recent changes
3. Analyze performance logs
4. Scale resources if needed
5. Optimize queries

---

**🚀 Ready for Production Deployment!**

This guide ensures your PropellerAds SDK deployment is secure, performant, and maintainable.
