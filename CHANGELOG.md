# Changelog

All notable changes to the PropellerAds Python SDK will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2025-09-29

### 🚀 Major Release - Complete Rewrite

This is a major release with breaking changes and significant improvements.

### Added
- **EnhancedPropellerAdsClient**: New enterprise-grade client with advanced features
- **AsyncPropellerAdsClient**: Full async/await support for all operations
- **Natural Language Interface**: AI-powered command processing in plain English
- **MCP Integration**: Complete Model Context Protocol support for Claude Desktop
- **Pydantic V2 Schemas**: Full data validation with modern Pydantic
- **Circuit Breaker Pattern**: Automatic failure detection and recovery
- **Intelligent Retry Logic**: Exponential backoff with jitter
- **Rate Limiting**: Built-in 60 requests/minute protection
- **Comprehensive Monitoring**: Metrics collection and health checks
- **Production-Ready Error Handling**: Detailed error hierarchy and logging
- **Complete API Coverage**: All 164 PropellerAds API v5 endpoints
- **Real CRUD Operations**: Working POST, PATCH, DELETE operations
- **VCR.py Testing**: HTTP interaction recording for reliable tests
- **AI-Friendly Documentation**: Optimized for AI agents and developers
- **Security Features**: Input validation, secure defaults, audit logging

### Changed
- **Breaking**: Minimum Python version raised to 3.11+
- **Breaking**: Client initialization parameters changed
- **Breaking**: Response objects now use Pydantic models
- **Breaking**: Error handling completely redesigned
- **Improved**: Documentation restructured with comprehensive guides
- **Enhanced**: Package structure reorganized for better maintainability

### Deprecated
- **LegacyPropellerAdsClient**: Old client maintained for backward compatibility

### Removed
- **Python 3.8-3.10 Support**: Minimum version now 3.11+
- **Old Error Classes**: Replaced with new hierarchy
- **Deprecated Methods**: Cleaned up legacy API methods

### Fixed
- **Import Issues**: Resolved all module import problems
- **Version Consistency**: Aligned versions across all configuration files
- **Schema Validation**: Fixed Pydantic V2 compatibility issues
- **Error Handling**: Improved error messages and debugging information
- **Memory Leaks**: Fixed resource cleanup in client connections

### Security
- **API Key Protection**: Enhanced security for credential handling
- **Input Validation**: Comprehensive data sanitization
- **Secure Defaults**: HTTPS-only, secure headers, proper timeouts
- **Audit Logging**: Security event tracking and monitoring

## [1.0.0] - 2024-XX-XX

### Added
- Initial release of PropellerAds Python SDK
- Basic API client functionality
- Core campaign management features
- Statistics retrieval
- Balance checking
- Basic error handling
- Documentation and examples

### Features
- **PropellerAdsClient**: Basic synchronous client
- **Campaign Management**: Create, read, update campaigns
- **Statistics**: Retrieve campaign performance data
- **Balance**: Check account balance
- **Error Handling**: Basic exception handling
- **Documentation**: README and basic examples

## Migration Guide

### From 1.x to 2.0

#### Client Initialization
```python
# Old (1.x)
from propellerads import PropellerAdsClient
client = PropellerAdsClient(api_key="your_key")

# New (2.0)
from propellerads import EnhancedPropellerAdsClient
client = EnhancedPropellerAdsClient("your_key")
```

#### Async Support
```python
# New in 2.0
from propellerads import AsyncPropellerAdsClient

async with AsyncPropellerAdsClient("your_key") as client:
    balance = await client.get_balance()
    campaigns = await client.get_campaigns()
```

#### Natural Language Interface
```python
# New in 2.0
from propellerads.ai_interface import PropellerAdsAIInterface

ai = PropellerAdsAIInterface(client)
result = ai.process_natural_language_command("show my balance")
```

#### Error Handling
```python
# Old (1.x)
try:
    campaigns = client.get_campaigns()
except Exception as e:
    print(f"Error: {e}")

# New (2.0)
from propellerads.exceptions import PropellerAdsError, RateLimitError

try:
    campaigns = client.get_campaigns()
except RateLimitError as e:
    print(f"Rate limited: {e.retry_after} seconds")
except PropellerAdsError as e:
    print(f"API Error: {e.status_code} - {e}")
```

## Support

- **Documentation**: [GitHub Repository](https://github.com/pavelraiden/propellerads-api-encyclopedia)
- **Issues**: [GitHub Issues](https://github.com/pavelraiden/propellerads-api-encyclopedia/issues)
- **Support**: support@propellerads.com

## Contributors

- PropellerAds Team
- Community Contributors

---

**Note**: This changelog follows [Keep a Changelog](https://keepachangelog.com/) format. For the complete list of changes, see the [commit history](https://github.com/pavelraiden/propellerads-api-encyclopedia/commits/main).
