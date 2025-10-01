# PropellerAds Python SDK

A comprehensive Python SDK for the PropellerAds advertising platform with AI-powered campaign management.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://img.shields.io/badge/tests-185%20passing-green.svg)](./tests/)

## Features

- **Complete API Coverage**: Full access to PropellerAds advertising platform
- **AI Integration**: Natural language campaign management with Claude AI
- **Web Interface**: Modern dashboard for campaign monitoring and management
- **Automatic Pagination**: Handles large datasets seamlessly
- **Rate Limiting**: Built-in protection against API limits
- **Type Safety**: Full type hints and validation
- **Async Support**: Asynchronous operations for high-performance applications

## Quick Start

### Installation

```bash
pip install propellerads-python
```

### Basic Usage

```python
from propellerads import PropellerAdsClient

# Initialize client
client = PropellerAdsClient(api_key="your-api-key")

# Get account balance
balance = client.get_balance()
print(f"Balance: ${balance.amount}")

# Get all campaigns (with automatic pagination)
campaigns = client.get_campaigns()
print(f"Total campaigns: {len(campaigns)}")

# Get campaign statistics
stats = client.get_statistics(
    campaign_id=123456,
    day_from="2024-01-01",
    day_to="2024-01-31"
)
```

### AI-Powered Management

```python
from claude_natural_interface_v2 import EnhancedClaudeInterface

# Initialize AI interface
ai = EnhancedClaudeInterface()

# Natural language campaign management
response = ai.process_request("Show me campaigns with low performance")
print(response)
```

### Web Interface

```bash
cd web_interface
export MainAPI="your-api-key"
python app.py
```

Access the dashboard at `http://localhost:5000`

## Documentation

- [API Reference](./docs/api-reference.md)
- [Advanced Usage](./docs/ADVANCED_USAGE.md)
- [Web Interface Guide](./WEB_INTERFACE_DOCUMENTATION.md)
- [Troubleshooting](./docs/TROUBLESHOOTING.md)

## API Coverage

### Account Management
- Balance retrieval
- User profile and settings
- Notifications

### Campaign Operations
- Create, read, update, delete campaigns
- Campaign targeting and optimization
- Budget and bid management

### Analytics & Reporting
- Comprehensive statistics
- Performance metrics
- Custom date ranges

### Creative Management
- Upload and manage creatives
- Creative performance tracking

## Requirements

- Python 3.8+
- PropellerAds API key
- Optional: Anthropic API key for AI features

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.

## Support

- [Documentation](./docs/)
- [Issue Tracker](https://github.com/pavelraiden/propellerads-api-encyclopedia/issues)
- [Security Policy](./SECURITY.md)
