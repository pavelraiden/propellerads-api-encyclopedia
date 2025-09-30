# 🚀 Quick Start Guide

This guide will help you get up and running with the PropellerAds API Encyclopedia in just a few minutes.

## 1. Installation

First, clone the repository and install the required dependencies:

```bash
# Clone repository
git clone https://github.com/pavelraiden/propellerads-api-encyclopedia.git
cd propellerads-api-encyclopedia

# Install dependencies
pip install -r requirements.txt
```

## 2. Set API Key

Next, you need to set your PropellerAds API key as an environment variable:

```bash
export MainAPI="your_propellerads_api_key"
```

## 3. Basic Usage

Now you can start using the client to interact with the PropellerAds API. Here's a simple example that shows how to get your account balance:

```python
from propellerads.client_enhanced import EnhancedPropellerAdsClient

# Initialize client
client = EnhancedPropellerAdsClient(api_key="your_api_key")

# Check balance
balance = client.balance.get_balance()
print(f"Balance: ${balance.amount}")
```

## 4. Natural Language Interface

You can also use the natural language interface to control the API using plain English commands:

```python
from src.ai_interface import AIInterface

# Initialize AI interface
ai = AIInterface(client)

# Use natural language
result = ai.process_natural_language_command("show my balance")
print(result["natural_language_summary"])  # "💰 Your account balance is $1635.22"
```

## 5. Next Steps

Now that you're up and running, you can explore the following resources to learn more:

- [ADVANCED_USAGE.md](ADVANCED_USAGE.md): Learn about the advanced features of the client.
- [api-reference.md](api-reference.md): Browse the complete API reference.
- [examples/](src/examples/): Check out the example scripts for more usage examples.

