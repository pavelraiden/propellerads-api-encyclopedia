# 🔧 Advanced Usage Guide

This guide covers the advanced features of the PropellerAds API Encyclopedia, including intelligent insights, automation, and error handling.

## 1. Intelligent Insights

The client includes an AI-powered interface that can provide you with intelligent insights about your account and campaigns.

```python
from src.ai_interface import AIInterface

# Initialize AI interface
ai = AIInterface(client)

# Get AI-powered insights
insights = ai.get_intelligent_insights()
print(f"Account Health Score: {insights["account_health"]["score"]}")
print(f"Recommendations: {insights["recommendations"]}")
```

## 2. Workflow Automation

The repository includes a number of ready-to-use workflows for automating common tasks, such as campaign monitoring and financial control.

```python
# Campaign monitoring
from workflows.campaign_monitoring import monitor_campaigns
results = monitor_campaigns(days=7)

# Financial control
from workflows.financial_control import check_budget_alerts
alerts = check_budget_alerts()
```

## 3. Error Handling

The client includes comprehensive error handling to ensure that your application can handle any API issues that may arise.

- **Rate limiting** (429) → Exponential backoff
- **Authentication** (401) → Credential validation
- **Validation** (400) → Parameter correction
- **Network issues** → Retry with circuit breaker

## 4. Customization

You can customize the behavior of the client by passing a number of optional arguments to the `EnhancedPropellerAdsClient` constructor.

```python
from propellerads.client_enhanced import EnhancedPropellerAdsClient

# Initialize client with custom settings
client = EnhancedPropellerAdsClient(
    api_key="your_api_key",
    rate_limit=120,  # 120 requests per minute
    retry_attempts=5,
    backoff_factor=0.5
)
```

