<<<<<<< HEAD
# PropellerAds API Encyclopedia 🚀

**Production-ready PropellerAds API v5 client optimized for AI agents**

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![API Coverage](https://img.shields.io/badge/API%20Coverage-164%20endpoints-green.svg)](docs/api-reference.md)
[![Test Coverage](https://img.shields.io/badge/Test%20Coverage-88%25-yellow.svg)](tests/)
[![AI Optimized](https://img.shields.io/badge/AI%20Optimized-✓-brightgreen.svg)](docs/ai-agents/)

## 🎯 For AI Agents

This repository serves as the **core knowledge base** for AI agents working with PropellerAds API. It provides:

- **Standardized task patterns** for common operations
- **Machine-readable metadata** for automated decision making  
- **Error recovery procedures** with specific remediation steps
- **AI-friendly documentation** optimized for neural network consumption

### Quick Start for AI Agents

```python
# 1. Clone repository to sandbox
git clone https://github.com/your-repo/propellerads-api-encyclopedia.git
cd propellerads-api-encyclopedia

# 2. Import AI interface
from src.ai_interface import PropellerAdsAIInterface
from src.propellerads_client import PropellerAdsUltimateClient

# 3. Initialize
client = PropellerAdsUltimateClient()
ai_interface = PropellerAdsAIInterface(client)

# 4. Execute task patterns
result = ai_interface.execute_task_pattern('campaign_creation', {
    'name': 'AI Generated Campaign',
    'budget': 100.0,
    'targeting': {'countries': ['US'], 'os': ['android']}
})
```

## 🏗️ Repository Structure

```
propellerads-api-encyclopedia/
├── src/
│   ├── propellerads_client.py      # Main API client
│   ├── ai_interface.py             # AI-optimized interface layer
│   ├── client/async_client.py      # Async operations
│   ├── models/                     # Pydantic data models
│   └── examples/                   # Working code examples
├── docs/
│   ├── ai-agents/                  # AI-specific documentation
│   │   ├── task-patterns/          # Standardized operation patterns
│   │   ├── error-handling/         # Error recovery procedures
│   │   └── decision-trees/         # Logic flow documentation
│   ├── metadata/                   # Machine-readable specifications
│   │   ├── tasks.yaml             # Task definitions
│   │   ├── constraints.yaml       # System limitations
│   │   └── relationships.yaml     # API dependencies
│   ├── api-reference.md           # Complete API documentation
│   └── integration-guide.md       # Setup instructions
├── workflows/                      # Ready-to-use automation
│   ├── campaign_monitoring.py     # Performance monitoring
│   └── financial_control.py       # Budget management
└── tests/                         # Comprehensive test suite
```

## 🤖 AI Agent Integration

### Connected Apps Configuration

When setting up PropellerAds in connected apps, use this note:

```
PROPELLERADS API KNOWLEDGE BASE
Repository: github.com/your-repo/propellerads-api-encyclopedia
Version: 1.0.0

CAPABILITIES:
- Campaign Management (create, update, monitor)
- Financial Operations (budget control, spend tracking)
- Targeting Configuration (geo, device, browser)
- Performance Monitoring (statistics, optimization)

USAGE INSTRUCTIONS:
1. Clone repository to sandbox
2. Import PropellerAdsUltimateClient or PropellerAdsAIInterface
3. Reference /docs/ai-agents for standardized patterns
4. Follow error handling procedures in /docs/ai-agents/error-handling

CONSTRAINTS:
- Rate limits: 30 GET/min, 150 POST/min
- Max page size: 1000 items
- Required permissions: campaigns:read, campaigns:write, statistics:read
```

### Task Patterns Available

| Pattern | Description | Complexity | Est. Time |
|---------|-------------|------------|-----------|
| `campaign_creation` | Create new advertising campaigns | Medium | 30-60s |
| `campaign_monitoring` | Monitor performance and health | Low | 10-30s |
| `budget_management` | Automated budget optimization | High | 60-120s |

### Error Recovery

The system includes comprehensive error handling for:

- **Rate limiting** (429 errors) → Exponential backoff
- **Authentication** (401 errors) → Credential validation
- **Validation** (400 errors) → Parameter correction
- **Network issues** → Retry with circuit breaker

## 🚀 Enterprise Features

### Production-Ready Client
- **Intelligent retry** with exponential backoff and jitter
- **Rate limiting** using token bucket algorithm
- **Circuit breaker** pattern for fault tolerance
- **Professional logging** with request IDs and structured output
- **Metrics collection** for performance monitoring
- **Connection pooling** for efficient HTTP management

### API Coverage
- **164 endpoints** tested and documented
- **100% functional coverage** of PropellerAds API v5
- **Real API validation** with live testing
- **Comprehensive error handling** for all edge cases

## 📊 Current Status

### Live API Testing Results
- ✅ **Account Balance**: $1,686.48
- ✅ **Active Campaigns**: 100 campaigns (1 active, 99 paused)
- ✅ **Targeting Options**: 249 countries, 12 OS, 31 browsers
- ✅ **API Health**: All endpoints responding correctly

### Quality Metrics
- **Test Coverage**: 88% (target: 95%+)
- **Code Quality**: Claude-audited and approved
- **Documentation**: AI-optimized and comprehensive
- **Performance**: Sub-second response times

## 🛠️ Installation & Setup

### For AI Agents
```bash
# Clone to sandbox
git clone https://github.com/your-repo/propellerads-api-encyclopedia.git
cd propellerads-api-encyclopedia

# Install dependencies
pip install -r requirements.txt

# Set API key (from connected apps)
export MainAPI="your_propellerads_api_key"

# Test connection
python src/examples/quick_start.py
```

### For Human Developers
```bash
# Clone repository
git clone https://github.com/your-repo/propellerads-api-encyclopedia.git
cd propellerads-api-encyclopedia

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run tests
python -m pytest tests/ -v

# Run examples
python src/examples/quick_start.py
```

## 📚 Documentation

### For AI Agents
- [Task Patterns](docs/ai-agents/task-patterns/) - Standardized operation templates
- [Error Handling](docs/ai-agents/error-handling/) - Recovery procedures
- [Decision Trees](docs/ai-agents/decision-trees/) - Logic flow guides
- [Metadata](docs/metadata/) - Machine-readable specifications

### For Developers
- [API Reference](docs/api-reference.md) - Complete endpoint documentation
- [Integration Guide](docs/integration-guide.md) - Setup and configuration
- [Examples](src/examples/) - Working code samples
- [Workflows](workflows/) - Automation scripts

## 🔧 Usage Examples

### Basic Campaign Management
```python
from src.propellerads_client import PropellerAdsUltimateClient

# Initialize client
client = PropellerAdsUltimateClient()

# Check account status
balance = client.get_balance()
print(f"Account balance: ${balance['data']}")

# Get campaigns
campaigns = client.get_campaigns(status='active')
print(f"Active campaigns: {len(campaigns['data']['result'])}")

# Create new campaign
result = client.create_campaign(
    name="Test Campaign",
    budget=100.0,
    targeting={'countries': ['US'], 'os': ['android']}
=======
# PropellerAds Python SDK

Professional Python client for PropellerAds SSP API v5.

## Features

- ✅ **Production Ready** - Enterprise-grade reliability
- ✅ **Intelligent Retry** - Exponential backoff with circuit breaker
- ✅ **Rate Limiting** - Token bucket algorithm with burst support
- ✅ **Type Safety** - Full Pydantic model validation
- ✅ **Async Support** - Both sync and async clients
- ✅ **Comprehensive Logging** - Request tracking and monitoring
- ✅ **Error Handling** - Detailed exception hierarchy

## Quick Start

```python
from propellerads import PropellerAdsClient

# Initialize client
client = PropellerAdsClient(api_key="your-api-key")

# Get account balance
balance = client.get_balance()
print(f"Balance: {balance.formatted}")

# Get campaigns
campaigns = client.get_campaigns(limit=10)
for campaign in campaigns:
    print(f"Campaign: {campaign.name} (Status: {campaign.status})")

# Get statistics
stats = client.get_statistics(
    date_from="2024-01-01",
    date_to="2024-01-31",
    group_by=["campaign_id"]
>>>>>>> 5117d9ff16db6c2a648506b86a369f5fbe65acaa
)
print(f"Total clicks: {stats.total_clicks}")
```

<<<<<<< HEAD
### AI Interface Usage
```python
from src.ai_interface import PropellerAdsAIInterface

# Initialize AI interface
ai = PropellerAdsAIInterface(client)

# Execute standardized task
result = ai.execute_task_pattern('campaign_monitoring', {
    'day_from': '2025-09-01 00:00:00',
    'day_to': '2025-09-30 23:59:59'
})

# Get optimization suggestions
suggestions = ai.suggest_optimization(campaign_data)
```

### Workflow Automation
```python
# Run campaign monitoring workflow
python workflows/campaign_monitoring.py

# Run financial control workflow  
python workflows/financial_control.py
```

## 🔒 Security & Best Practices

### API Key Management
- Store API keys in environment variables
- Never commit credentials to version control
- Use separate keys for development and production
- Rotate keys regularly

### Rate Limiting
- Respect API rate limits (30 GET/min, 150 POST/min)
- Implement exponential backoff for retries
- Use bulk operations when available
- Cache frequently accessed data

### Error Handling
- Always validate inputs before API calls
- Implement comprehensive exception handling
- Log errors with sufficient context
- Provide graceful degradation

## 🧪 Testing

### Run Test Suite
```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test categories
python -m pytest tests/test_client.py -v
python -m pytest tests/test_workflows.py -v

# Run with coverage
python -m pytest tests/ --cov=src --cov-report=html
```

### Test Real API
```bash
# Test with live API (requires valid API key)
python src/examples/quick_start.py
python src/examples/enhanced_client_demo.py
```

## 🤝 Contributing

### For AI Agents
- Follow task patterns in `docs/ai-agents/task-patterns/`
- Use error handling procedures from `docs/ai-agents/error-handling/`
- Validate operations using `PropellerAdsAIInterface.validate_operation()`
- Log all actions using structured logging

### For Developers
1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Update documentation
6. Submit a pull request

## 📈 Roadmap

### Immediate (v1.1)
- [ ] Increase test coverage to 95%+
- [ ] Add more task patterns
- [ ] Enhance AI decision support
- [ ] Improve error recovery

### Short-term (v1.2)
- [ ] Add webhook support
- [ ] Implement real-time monitoring
- [ ] Add A/B testing framework
- [ ] Create dashboard interface

### Long-term (v2.0)
- [ ] Machine learning optimization
- [ ] Predictive analytics
- [ ] Advanced automation
- [ ] Multi-account management

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

### For AI Agents
- Check [error handling documentation](docs/ai-agents/error-handling/)
- Review [task patterns](docs/ai-agents/task-patterns/)
- Validate using [metadata constraints](docs/metadata/constraints.yaml)

### For Developers
- Read the [integration guide](docs/integration-guide.md)
- Check [API reference](docs/api-reference.md)
- Review [examples](src/examples/)
- Open an issue on GitHub

## 🏆 Acknowledgments

- PropellerAds for providing comprehensive API documentation
- Claude AI for architecture review and optimization recommendations
- The open-source community for inspiration and best practices

---

**Ready for production use by AI agents and human developers alike! 🚀**
=======
## Installation

```bash
pip install propellerads-python
```

## Documentation

- [API Reference](docs/api_reference.md)
- [Examples](docs/examples.md)

## Requirements

- Python 3.8+
- requests
- pydantic

## License

MIT License
>>>>>>> 5117d9ff16db6c2a648506b86a369f5fbe65acaa
