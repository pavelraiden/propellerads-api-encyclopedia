# 🚀 PropellerAds API Encyclopedia

**Production-ready PropellerAds API v5 client with AI-powered natural language interface**

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![API Coverage](https://img.shields.io/badge/API%20Coverage-100%25-green.svg)](docs/api-reference.md)
[![MCP Integration](https://img.shields.io/badge/MCP%20Integration-✓-brightgreen.svg)](docs/MCP_INTEGRATION_GUIDE.md)
[![AI Optimized](https://img.shields.io/badge/AI%20Optimized-✓-brightgreen.svg)](docs/ai-agents/)

## 📋 Table of Contents
1. [Introduction](#introduction)
2. [Features](#features)
3. [Quick Start](#quick-start)
4. [Repository Structure](#repository-structure)
5. [Basic Usage](#basic-usage)
6. [Natural Language Interface](#natural-language-interface)
7. [MCP Integration](#mcp-integration)
8. [Advanced Features](#advanced-features)
9. [AI Agent Documentation](#ai-agent-documentation)
10. [Testing & Examples](#testing--examples)
11. [API Reference](#api-reference)
12. [Troubleshooting](#troubleshooting)
13. [Contributing](#contributing)
14. [License](#license)
15. [Support](#support)

## 1. 🚪 Introduction
This repository contains a production-ready Python client for the PropellerAds API v5. It is designed to be used by both developers and AI agents, providing a robust and easy-to-use interface for interacting with the PropellerAds platform.

The client is built with a focus on reliability, performance, and ease of use. It includes a number of advanced features, such as intelligent retry, rate limiting, and a circuit breaker, to ensure that your application can handle any API issues that may arise.

In addition, the client includes an AI-powered natural language interface, which allows you to control the PropellerAds API using plain English commands. This makes it easy for AI agents to interact with the API, and it also makes it easier for developers to build applications that use the API.

## 2. 🎯 Features
- **Full API Coverage:** The client provides access to all 164 endpoints of the PropellerAds API v5.
- **Natural Language Interface:** Control the API using plain English commands.
- **MCP Integration:** Ready for Claude Desktop and other AI tools.
- **Enterprise-Grade Client:** Intelligent retry, rate limiting, circuit breaker, and more.
- **AI-Optimized:** Designed for seamless integration with AI agents.
- **Production-Ready:** Comprehensive error handling and testing.

## 3. 🚀 Quick Start
See the [QUICK_START.md](docs/QUICK_START.md) guide for a streamlined setup guide for new users.

## 4. 📁 Repository Structure
```
propellerads-api-encyclopedia/
├── propellerads/                   # Main client package
│   ├── client_enhanced.py          # Enhanced API client
│   ├── schemas/                    # Pydantic data models
│   └── api/                        # API endpoints
├── src/                            # Enhanced features
│   ├── enhanced_ai_interface.py    # Natural language interface
│   ├── mcp_server.py               # MCP server for Claude Desktop
│   └── examples/                   # Working code examples
├── docs/                           # Comprehensive documentation
│   ├── QUICK_START.md              # Quick start guide
│   ├── ADVANCED_USAGE.md           # Advanced usage guide
│   ├── MCP_INTEGRATION_GUIDE.md    # MCP setup guide
│   ├── api-reference.md            # API documentation
│   └── ai-agents/                  # AI-specific docs
└── tests/                          # Test suite
```

## 5. 📖 Basic Usage
```python
from propellerads.client_enhanced import EnhancedPropellerAdsClient

# Initialize client
client = EnhancedPropellerAdsClient(api_key="your_api_key")

# Check balance
balance = client.balance.get_balance()
print(f"Balance: ${balance.amount}")

# Get campaigns
campaigns = client.campaigns.get_campaigns()
print(f"Total campaigns: {len(campaigns)}")
```

## 6. 🤖 Natural Language Interface
```python
from src.ai_interface import AIInterface

# Initialize AI interface
ai = AIInterface(client)

# Use natural language
result = ai.process_natural_language_command("show my balance")
print(result["natural_language_summary"])  # "💰 Your account balance is $1635.22"
```

## 7. 🔌 MCP Integration
See the [MCP_INTEGRATION_GUIDE.md](docs/MCP_INTEGRATION_GUIDE.md) for step-by-step instructions for Claude Desktop integration.

## 8. 🔧 Advanced Features
See the [ADVANCED_USAGE.md](docs/ADVANCED_USAGE.md) for an in-depth look at intelligent insights, automation, and error handling.

## 9. 🧠 AI Agent Documentation
See the [ai-agents/](docs/ai-agents/) directory for a comprehensive guide for AI agents, including best practices and examples.

## 10. 🧪 Testing & Examples
See the [tests/](tests/) directory for detailed instructions for running tests and example scripts.

## 11. 📚 API Reference
See the [api-reference.md](docs/api-reference.md) for complete documentation for all 164 API endpoints.

## 12. 🩺 Troubleshooting
See the [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) for common issues and solutions, plus error code explanations.

## 13. 🤝 Contributing
See the [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines for contributing to the project.

## 14. 📄 License
MIT License - see [LICENSE](LICENSE) file for details.

## 15. 🆘 Support
- **Issues**: Open a GitHub issue
- **Documentation**: Check [docs/](docs/) directory
- **Examples**: See [src/examples/](src/examples/)
- **MCP Integration**: See [docs/MCP_INTEGRATION_GUIDE.md](docs/MCP_INTEGRATION_GUIDE.md)

