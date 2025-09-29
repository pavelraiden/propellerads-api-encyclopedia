# PropellerAds MCP Integration Guide

## 🚀 Revolutionary Natural Language Interface for PropellerAds API

This guide covers the **Model Context Protocol (MCP)** integration that enables natural language interaction with PropellerAds API through Claude Desktop and other AI agents.

---

## 🎯 What is MCP Integration?

The MCP integration transforms our enterprise PropellerAds API client into a **natural language interface** that allows you to:

- **Talk to your campaigns** using plain English
- **Manage advertising** through conversational AI
- **Get insights** without writing code
- **Automate operations** through AI agents

### Example Interactions:

```
You: "Show me my account balance"
AI: "💰 Your account balance is $1,686.48"

You: "List my best performing campaigns"
AI: "📊 Found 5 top-performing campaigns with highest CTR"

You: "Pause campaign 123"
AI: "⚠️ This will pause campaign 123. Confirm? (y/n)"

You: "Create a push campaign for US with $100 budget"
AI: "✅ Campaign created successfully with ID 456"
```

---

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────────┐
│   Claude Desktop │    │   MCP Server     │    │  Enterprise Client  │
│   or AI Agent   │◄──►│  (Natural Lang)  │◄──►│  (PropellerAds API) │
└─────────────────┘    └──────────────────┘    └─────────────────────┘
        │                        │                        │
        │                        │                        │
        ▼                        ▼                        ▼
   Natural Language         Tool-based              REST API Calls
   Commands                 Architecture            with Enterprise
                                                   Features
```

### Components:

1. **MCP Server** (`src/mcp_server.py`)
   - Handles MCP protocol communication
   - Provides tool-based interface
   - Manages safety confirmations

2. **Enhanced AI Interface** (`src/enhanced_ai_interface.py`)
   - Natural language processing
   - Intent recognition and parsing
   - Intelligent operation validation

3. **Enterprise Client** (`src/propellerads_client.py`)
   - Production-ready API client
   - Rate limiting, retry logic, circuit breaker
   - Comprehensive error handling

---

## 🛠️ Installation & Setup

### 1. Install Dependencies

```bash
cd propellerads-api-encyclopedia
pip install mcp python-dotenv asyncio-mqtt
```

### 2. Configure Environment

Create `.env` file:
```bash
MainAPI=your_propellerads_api_token_here
```

### 3. Claude Desktop Integration

Copy the configuration to Claude Desktop:

**Location**: `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS)

```json
{
  "mcpServers": {
    "propellerads-enterprise": {
      "command": "python",
      "args": [
        "/path/to/propellerads-api-encyclopedia/src/mcp_server.py"
      ],
      "env": {
        "MainAPI": "your_propellerads_api_token_here"
      }
    }
  }
}
```

### 4. Test Installation

```bash
# Test MCP server
python src/mcp_server.py

# Test AI interface
python -c "
from src.enhanced_ai_interface import EnhancedPropellerAdsAI
from src.propellerads_client import PropellerAdsUltimateClient
ai = EnhancedPropellerAdsAI(PropellerAdsUltimateClient())
print(ai.process_natural_language_command('show my balance'))
"
```

---

## 🎮 Available Tools

### 📊 **Account & Balance Tools**

| Tool | Description | Example Command |
|------|-------------|-----------------|
| `get_account_balance` | Get current balance | "show my balance" |
| `health_check` | Check API connectivity | "check API status" |

### 🎯 **Campaign Management Tools**

| Tool | Description | Example Command |
|------|-------------|-----------------|
| `list_campaigns` | List campaigns with filters | "show active campaigns" |
| `get_campaign_details` | Get campaign details | "show details for campaign 123" |
| `create_campaign` | Create new campaign | "create push campaign for US" |
| `update_campaign` | Update campaign settings | "pause campaign 123" |

### 📈 **Analytics & Statistics Tools**

| Tool | Description | Example Command |
|------|-------------|-----------------|
| `get_campaign_statistics` | Get performance stats | "show stats for last 7 days" |
| `get_performance_summary` | Get performance overview | "show performance summary" |

### 🤖 **AI-Powered Tools**

| Tool | Description | Example Command |
|------|-------------|-----------------|
| `analyze_campaign_performance` | AI analysis with insights | "analyze campaign 123" |
| `get_optimization_recommendations` | AI optimization suggestions | "how can I optimize my campaigns?" |
| `execute_natural_language_command` | Process any natural language | "what should I do to improve ROI?" |

### 🎯 **Targeting & Configuration Tools**

| Tool | Description | Example Command |
|------|-------------|-----------------|
| `get_targeting_options` | Get available targeting | "show available countries" |

---

## 💬 Natural Language Commands

### 📊 **Account Information**
```
✅ "Show my balance"
✅ "How much money do I have?"
✅ "Check account status"
✅ "Is the API working?"
```

### 🎯 **Campaign Management**
```
✅ "List all campaigns"
✅ "Show active campaigns"
✅ "Show my best performing campaigns"
✅ "Get details for campaign 123"
✅ "Analyze campaign 456"
```

### ⚡ **Campaign Operations** (Write Operations)
```
⚠️ "Pause campaign 123" (requires confirmation)
⚠️ "Start campaign 456" (requires confirmation)
⚠️ "Update budget for campaign 123 to $200" (requires confirmation)
⚠️ "Create campaign named 'Test' for US with $100 budget" (requires confirmation)
```

### 📈 **Analytics & Insights**
```
✅ "Show performance statistics"
✅ "Get performance summary for last 30 days"
✅ "How are my campaigns performing?"
✅ "What optimization recommendations do you have?"
✅ "Show me targeting options"
```

### 🤖 **AI-Powered Queries**
```
✅ "What should I do to improve my ROI?"
✅ "Which campaigns need attention?"
✅ "How can I optimize my spending?"
✅ "What are the best performing countries?"
```

---

## 🔒 Safety Features

### Write Operation Confirmations

All **write operations** (create, update, delete) require explicit confirmation:

```
You: "Pause campaign 123"
AI: "⚠️ This will PAUSE campaign 123 'Summer Sale Campaign'. 
     Current status: Active, Daily budget: $150
     Confirm this action? (y/n)"

You: "y"
AI: "✅ Campaign 123 has been paused successfully"
```

### Operation Validation

The system validates operations before execution:

```
You: "Create campaign with $5000 budget"
AI: "⚠️ Warning: $5000 is a high daily budget. 
     Recommended starting budget: $50-$200
     Continue? (y/n)"
```

### Error Recovery

Intelligent error handling with suggestions:

```
You: "Show campaign 999"
AI: "❌ Campaign 999 not found
     💡 Suggestions:
     - List all campaigns to see available IDs
     - Check if campaign was recently deleted
     - Try: 'show all campaigns'"
```

---

## 🧪 Testing

### Run MCP Integration Tests

```bash
# Run all MCP tests
python -m pytest tests/test_mcp_integration.py -v

# Test specific functionality
python -m pytest tests/test_mcp_integration.py::TestEnhancedAIInterface::test_natural_language_processing_balance -v

# Test with coverage
python -m pytest tests/test_mcp_integration.py --cov=src --cov-report=html
```

### Manual Testing

```bash
# Test natural language processing
python -c "
from src.enhanced_ai_interface import EnhancedPropellerAdsAI
from src.propellerads_client import PropellerAdsUltimateClient

ai = EnhancedPropellerAdsAI(PropellerAdsUltimateClient())

# Test various commands
commands = [
    'show my balance',
    'list active campaigns', 
    'analyze campaign 123',
    'pause campaign 456'
]

for cmd in commands:
    result = ai.process_natural_language_command(cmd)
    print(f'Command: {cmd}')
    print(f'Result: {result}')
    print('-' * 50)
"
```

---

## 🚀 Advanced Features

### Context-Aware Conversations

The AI maintains context across conversations:

```
You: "Show my campaigns"
AI: "Found 5 campaigns. Here are the details..."

You: "Which one is performing best?"
AI: "Campaign 123 'Summer Sale' has the highest CTR at 2.3%"

You: "Analyze it"
AI: "Analyzing Campaign 123... [detailed analysis]"
```

### Intelligent Insights

Get proactive insights and recommendations:

```python
# Get intelligent insights
insights = ai_interface.get_intelligent_insights()

# Returns:
{
    "account_health": {"score": 85, "status": "healthy"},
    "performance_trends": {"trend": "improving", "change": "+12%"},
    "optimization_opportunities": [...],
    "risk_alerts": [...],
    "recommendations": [...]
}
```

### Batch Operations

Process multiple operations efficiently:

```
You: "Show me campaigns that need optimization"
AI: "Found 3 campaigns with optimization opportunities:
     - Campaign 123: Low CTR, suggest bid adjustment
     - Campaign 456: High CPA, suggest targeting refinement  
     - Campaign 789: Budget underutilized, suggest increase"

You: "Optimize all of them"
AI: "I'll create optimization plans for all 3 campaigns..."
```

---

## 🔧 Customization

### Adding Custom Commands

Extend the natural language patterns in `enhanced_ai_interface.py`:

```python
# Add new command patterns
self.command_patterns.update({
    r"(?:show|get).*(?:top|best).*(?:countries|geos)": {
        "action": "get", "entity": "top_countries", "write": False
    }
})
```

### Custom Tool Integration

Add new tools to the MCP server:

```python
# In mcp_server.py
Tool(
    name="custom_analysis",
    description="Custom analysis tool",
    inputSchema={...}
)
```

### AI Behavior Customization

Modify AI responses and behavior:

```python
# Customize response generation
def _generate_summary(self, intent, result):
    if intent.entity == "custom":
        return f"🎯 Custom operation completed: {result.message}"
    return super()._generate_summary(intent, result)
```

---

## 📚 API Reference

### EnhancedPropellerAdsAI Class

```python
class EnhancedPropellerAdsAI:
    def process_natural_language_command(
        self, 
        command: str, 
        confirm_write_operations: bool = True
    ) -> Dict[str, Any]
    
    def get_intelligent_insights(
        self, 
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]
    
    def _parse_command_intent(self, command: str) -> CommandIntent
    def _execute_intent(self, intent: CommandIntent) -> OperationResult
```

### PropellerAdsMCPServer Class

```python
class PropellerAdsMCPServer:
    def __init__(self)
    async def run(self)
    
    # Tool handlers
    async def _handle_get_balance(self) -> Dict[str, Any]
    async def _handle_list_campaigns(self, **kwargs) -> Dict[str, Any]
    async def _handle_natural_language(self, **kwargs) -> Dict[str, Any]
```

---

## 🐛 Troubleshooting

### Common Issues

**1. MCP Server Won't Start**
```bash
# Check dependencies
pip install mcp python-dotenv

# Check API token
echo $MainAPI

# Check Python path
which python
```

**2. Claude Desktop Integration Issues**
```bash
# Verify config file location
ls ~/Library/Application\ Support/Claude/claude_desktop_config.json

# Check config syntax
python -c "import json; print(json.load(open('claude_desktop_config.json')))"
```

**3. Natural Language Not Working**
```bash
# Test AI interface directly
python -c "
from src.enhanced_ai_interface import EnhancedPropellerAdsAI
from src.propellerads_client import PropellerAdsUltimateClient
ai = EnhancedPropellerAdsAI(PropellerAdsUltimateClient())
print(ai.process_natural_language_command('show my balance'))
"
```

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Performance Issues

Monitor performance:

```python
# Check response times
import time
start = time.time()
result = ai.process_natural_language_command("show campaigns")
print(f"Response time: {time.time() - start:.2f}s")
```

---

## 🎯 Best Practices

### 1. **Command Clarity**
- Use specific, clear commands
- Include relevant parameters
- Be explicit about intentions

### 2. **Safety First**
- Always confirm write operations
- Review changes before applying
- Use read operations for exploration

### 3. **Performance Optimization**
- Cache frequently accessed data
- Use batch operations when possible
- Monitor API rate limits

### 4. **Error Handling**
- Check operation results
- Handle API errors gracefully
- Provide fallback options

---

## 🚀 What's Next?

The MCP integration opens up exciting possibilities:

1. **Advanced AI Agents** - Build sophisticated automation workflows
2. **Voice Control** - Add speech-to-text for voice commands  
3. **Slack/Discord Bots** - Integrate with team communication tools
4. **Custom Dashboards** - Build conversational analytics interfaces
5. **Automated Optimization** - AI-driven campaign management

---

## 📞 Support

For issues or questions:

1. **Check Documentation** - Review this guide and API docs
2. **Run Tests** - Use the test suite to verify functionality
3. **Debug Mode** - Enable logging for detailed troubleshooting
4. **Community** - Share experiences and solutions

---

**🎉 Congratulations! You now have a revolutionary natural language interface for PropellerAds API management!**
