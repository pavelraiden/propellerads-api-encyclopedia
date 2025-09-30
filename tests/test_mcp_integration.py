#!/usr/bin/env python3
"""
Comprehensive MCP Integration Tests
Tests for the PropellerAds MCP server and enhanced AI interface
"""

import os
import sys
import pytest
import asyncio
import json
from unittest.mock import Mock, patch, AsyncMock
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from mcp_server import PropellerAdsMCPServer
from enhanced_ai_interface import EnhancedPropellerAdsAI, CommandIntent, OperationResult


class TestMCPServer:
    """Test MCP server functionality"""
    
    @pytest.fixture
    def mock_client(self):
        """Mock PropellerAds client"""
        client = Mock()
        client.get_balance.return_value = 1500.00
        client.health_check.return_value = True
        client.get_campaigns.return_value = [
            {"id": 1, "name": "Test Campaign 1", "status": 6, "clicks": 1000},
            {"id": 2, "name": "Test Campaign 2", "status": 7, "clicks": 500}
        ]
        client.get_campaign_details.return_value = {
            "id": 1, "name": "Test Campaign", "status": 6, "budget": 100
        }
        client.get_targeting_options.return_value = {
            "countries": ["US", "CA", "UK"],
            "devices": ["desktop", "mobile"],
            "browsers": ["chrome", "firefox"]
        }
        return client
    
    @pytest.fixture
    def mcp_server(self, mock_client):
        """MCP server with mocked client"""
        real_api_key = os.environ.get("MainAPI", "test_token")
        with patch.dict(os.environ, {"MainAPI": real_api_key}):
            with patch("mcp_server.PropellerAdsUltimateClient", return_value=mock_client):
                server = PropellerAdsMCPServer()
                server.client = mock_client
                return server
    
    @pytest.mark.asyncio
    async def test_get_balance_tool(self, mcp_server):
        """Test balance retrieval tool"""
        result = await mcp_server._handle_get_balance()
        
        assert result["status"] == "success"
        assert result["balance"] == 1500.00
        assert result["currency"] == "USD"
    
    @pytest.mark.asyncio
    async def test_health_check_tool(self, mcp_server):
        """Test health check tool"""
        result = await mcp_server._handle_health_check()
        
        assert result["status"] == "healthy"
        assert result["api_accessible"] is True
    
    @pytest.mark.asyncio
    async def test_list_campaigns_tool(self, mcp_server):
        """Test campaign listing tool"""
        # Test all campaigns
        result = await mcp_server._handle_list_campaigns()
        
        assert "campaigns" in result
        assert result["total_count"] == 2
        assert result["status_filter"] == "all"
        
        # Test active campaigns only
        result = await mcp_server._handle_list_campaigns(status="active")
        
        assert len(result["campaigns"]) == 1
        assert result["campaigns"][0]["status"] == 6
    
    @pytest.mark.asyncio
    async def test_campaign_details_tool(self, mcp_server):
        """Test campaign details tool"""
        result = await mcp_server._handle_get_campaign_details(campaign_id=1)
        
        assert "campaign" in result
        assert result["campaign"]["id"] == 1
        assert result["campaign_id"] == 1
    
    @pytest.mark.asyncio
    async def test_targeting_options_tool(self, mcp_server):
        """Test targeting options tool"""
        # Test all options
        result = await mcp_server._handle_targeting_options()
        
        assert "countries" in result
        assert "devices" in result
        assert "browsers" in result
        
        # Test specific option type
        result = await mcp_server._handle_targeting_options(option_type="countries")
        
        assert "countries" in result
        assert "devices" not in result
    
    @pytest.mark.asyncio
    async def test_write_operations_safety(self, mcp_server):
        """Test that write operations return safe responses"""
        # Test campaign creation
        result = await mcp_server._handle_create_campaign(
            name="Test Campaign",
            target_url="https://example.com",
            daily_budget=100,
            countries=["US"],
            bid_amount=0.50
        )
        
        assert result["operation"] == "create_campaign"
        assert result["status"] == "would_create"
        assert "note" in result
        
        # Test campaign update
        result = await mcp_server._handle_update_campaign(
            campaign_id=1,
            status="paused"
        )
        
        assert result["operation"] == "update_campaign"
        assert result["status"] == "would_update"


class TestEnhancedAIInterface:
    """Test enhanced AI interface functionality"""
    
    @pytest.fixture
    def mock_client(self):
        """Mock PropellerAds client"""
        client = Mock()
        client.get_balance.return_value = 1500.00
        client.health_check.return_value = True
        client.get_campaigns.return_value = [
            {"id": 1, "name": "Test Campaign 1", "status": 6, "clicks": 1000},
            {"id": 2, "name": "Test Campaign 2", "status": 7, "clicks": 500}
        ]
        client.get_campaign_details.return_value = {
            "id": 1, "name": "Test Campaign", "status": 6, "budget": 100
        }
        client.get_targeting_options.return_value = {
            "countries": ["US", "CA", "UK"],
            "devices": ["desktop", "mobile"]
        }
        return client
    
    @pytest.fixture
    def ai_interface(self, mock_client):
        """Enhanced AI interface with mocked client"""
        return EnhancedPropellerAdsAI(mock_client)
    
    def test_command_intent_parsing_balance(self, ai_interface):
        """Test parsing balance-related commands"""
        commands = [
            "show my balance",
            "get account balance",
            "check my funds",
            "how much money do I have"
        ]
        
        for command in commands:
            intent = ai_interface._parse_command_intent(command)
            assert intent.action == "get"
            assert intent.entity == "balance"
            assert not intent.is_write_operation
            assert intent.confidence > 0.5
    
    def test_command_intent_parsing_campaigns(self, ai_interface):
        """Test parsing campaign-related commands"""
        # List campaigns
        commands = [
            "show all campaigns",
            "list my campaigns",
            "get campaigns"
        ]
        
        for command in commands:
            intent = ai_interface._parse_command_intent(command)
            assert intent.action == "list"
            assert intent.entity == "campaigns"
            assert not intent.is_write_operation
    
    def test_command_intent_parsing_campaign_details(self, ai_interface):
        """Test parsing campaign details commands"""
        command = "show details for campaign 123"
        intent = ai_interface._parse_command_intent(command)
        
        assert intent.action == "get"
        assert intent.entity == "campaign_details"
        assert intent.parameters["campaign_id"] == 123
        assert not intent.is_write_operation
    
    def test_command_intent_parsing_write_operations(self, ai_interface):
        """Test parsing write operation commands"""
        # Pause campaign
        command = "pause campaign 123"
        intent = ai_interface._parse_command_intent(command)
        
        assert intent.action == "update"
        assert intent.entity == "campaign"
        assert intent.parameters["campaign_id"] == 123
        assert intent.parameters["status"] == "paused"
        assert intent.is_write_operation
        
        # Create campaign
        command = "create new campaign"
        intent = ai_interface._parse_command_intent(command)
        
        assert intent.action == "create"
        assert intent.entity == "campaign"
        assert intent.is_write_operation
    
    def test_parameter_extraction(self, ai_interface):
        """Test parameter extraction from commands"""
        command = "create campaign with $100 budget for US,CA targeting https://example.com"
        params = ai_interface._extract_parameters(command)
        
        assert params["budget"] == 100.0
        assert params["countries"] == ["US", "CA"]
        assert params["url"] == "https://example.com"
    
    def test_natural_language_processing_balance(self, ai_interface):
        """Test natural language processing for balance"""
        result = ai_interface.process_natural_language_command("show my balance")
        
        assert "result" in result
        assert result["result"]["success"] is True
        assert "balance" in result["result"]["data"]
        assert result["result"]["data"]["balance"] == 1500.00
    
    def test_natural_language_processing_campaigns(self, ai_interface):
        """Test natural language processing for campaigns"""
        result = ai_interface.process_natural_language_command("list all campaigns")
        
        assert "result" in result
        assert result["result"]["success"] is True
        assert "campaigns" in result["result"]["data"]
        assert result["result"]["data"]["count"] == 2
    
    def test_natural_language_processing_write_confirmation(self, ai_interface):
        """Test that write operations require confirmation"""
        result = ai_interface.process_natural_language_command("pause campaign 123")
        
        assert result["operation"] == "confirmation_required"
        assert "intent" in result
        assert result["intent"]["is_write_operation"] is True
    
    def test_natural_language_processing_unclear_command(self, ai_interface):
        """Test handling of unclear commands"""
        result = ai_interface.process_natural_language_command("do something weird")
        
        assert "error" in result or result.get("intent", {}).get("confidence", 1.0) < 0.5
        assert "suggestions" in result
    
    def test_intelligent_insights(self, ai_interface):
        """Test intelligent insights generation"""
        insights = ai_interface.get_intelligent_insights()
        
        assert "account_health" in insights
        assert "performance_trends" in insights
        assert "optimization_opportunities" in insights
        assert "risk_alerts" in insights
        assert "recommendations" in insights
    
    def test_account_health_assessment(self, ai_interface):
        """Test account health assessment"""
        health = ai_interface._assess_account_health()
        
        assert "score" in health
        assert "status" in health
        assert "balance" in health
        assert "active_campaigns" in health
        assert health["balance"] == 1500.00
        assert health["active_campaigns"] == 1  # One active campaign from mock


class TestMCPIntegration:
    """Test full MCP integration scenarios"""
    
    @pytest.fixture
    def mock_environment(self):
        """Mock environment setup"""
        real_api_key = os.environ.get("MainAPI", "test_token")
        with patch.dict(os.environ, {"MainAPI": real_api_key}):
            yield
    
    def test_mcp_server_initialization(self, mock_environment):
        """Test MCP server can be initialized"""
        with patch("mcp_server.PropellerAdsUltimateClient"):
            server = PropellerAdsMCPServer()
            assert server.api_token == "test_token"
            assert server.server is not None
    
    def test_mcp_server_missing_token(self):
        """Test MCP server fails without API token"""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="MainAPI environment variable is required"):
                PropellerAdsMCPServer()
    
    @pytest.mark.asyncio
    async def test_tool_execution_flow(self, mock_environment):
        """Test complete tool execution flow"""
        with patch("mcp_server.PropellerAdsUltimateClient") as mock_client_class:
            mock_client = Mock()
            mock_client.get_balance.return_value = 1500.00
            mock_client_class.return_value = mock_client
            
            server = PropellerAdsMCPServer()
            
            # Test tool execution
            result = await server._handle_get_balance()
            assert result["status"] == "success"
            assert result["balance"] == 1500.00


class TestMCPDocumentation:
    """Test MCP documentation and configuration"""
    
    def test_claude_desktop_config_exists(self):
        """Test Claude Desktop configuration file exists"""
        config_path = Path(__file__).parent.parent / "claude_desktop_config.json"
        assert config_path.exists()
        
        with open(config_path) as f:
            config = json.load(f)
        
        assert "mcpServers" in config
        assert "propellerads-enterprise" in config["mcpServers"]
        assert "command" in config["mcpServers"]["propellerads-enterprise"]
        assert "args" in config["mcpServers"]["propellerads-enterprise"]
    
    def test_mcp_server_file_exists(self):
        """Test MCP server file exists and is executable"""
        server_path = Path(__file__).parent.parent / "src" / "mcp_server.py"
        assert server_path.exists()
        
        # Check if file has proper shebang
        with open(server_path) as f:
            first_line = f.readline().strip()
        assert first_line.startswith("#!")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
