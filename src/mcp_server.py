#!/usr/bin/env python3
"""
PropellerAds MCP Server
Enterprise-grade MCP server with natural language interface for PropellerAds API

Integrates our enterprise PropellerAdsUltimateClient with MCP protocol
for seamless AI agent and Claude Desktop integration.
"""

import os
import sys
import asyncio
import logging
import json
from typing import Any, Dict, List, Optional, Sequence
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent))

from mcp.server import Server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    LoggingLevel
)
import mcp.server.stdio
from dotenv import load_dotenv

sys.path.append(str(Path(__file__).parent.parent))
from propellerads.client import PropellerAdsClient as PropellerAdsUltimateClient
from ai_interface import PropellerAdsAIInterface

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class PropellerAdsMCPServer:
    """Enterprise MCP Server for PropellerAds API integration"""
    
    def __init__(self):
        """Initialize the MCP server with enterprise client"""
        # Get API token from environment
        self.api_token = os.getenv("MainAPI")
        if not self.api_token:
            raise ValueError(
                "MainAPI environment variable is required. "
                "This should be your PropellerAds API token."
            )
        
        # Initialize server
        self.server = Server("propellerads-enterprise-mcp")
        
        # Initialize our enterprise client
        self.client = PropellerAdsUltimateClient()
        
        # Initialize AI interface
        self.ai_interface = PropellerAdsAIInterface(self.client)
        
        # Track operations for safety
        self.pending_operations = {}
        
        # Register handlers
        self._register_tools()
        self._register_resources()
    
    def _register_tools(self):
        """Register all available tools"""
        
        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            """List all available PropellerAds tools"""
            return [
                # Account & Balance Tools
                Tool(
                    name="get_account_balance",
                    description="Get current account balance and basic account info (READ operation)",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "additionalProperties": False
                    }
                ),
                Tool(
                    name="health_check",
                    description="Check API health and connectivity (READ operation)",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "additionalProperties": False
                    }
                ),
                
                # Campaign Management Tools
                Tool(
                    name="list_campaigns",
                    description="List all campaigns with optional filters (READ operation)",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "status": {
                                "type": "string",
                                "enum": ["all", "active", "paused", "stopped", "draft"],
                                "description": "Filter by campaign status",
                                "default": "all"
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of campaigns to return",
                                "default": 100,
                                "minimum": 1,
                                "maximum": 1000
                            }
                        },
                        "additionalProperties": False
                    }
                ),
                Tool(
                    name="get_campaign_details",
                    description="Get detailed information about a specific campaign (READ operation)",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "campaign_id": {
                                "type": "integer",
                                "description": "Campaign ID to get details for"
                            }
                        },
                        "required": ["campaign_id"],
                        "additionalProperties": False
                    }
                ),
                Tool(
                    name="create_campaign",
                    description="Create a new advertising campaign (WRITE - requires confirmation)",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "Campaign name"
                            },
                            "target_url": {
                                "type": "string",
                                "description": "Landing page URL"
                            },
                            "daily_budget": {
                                "type": "number",
                                "description": "Daily budget in USD",
                                "minimum": 1
                            },
                            "countries": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Target countries (ISO codes)"
                            },
                            "bid_amount": {
                                "type": "number",
                                "description": "Bid amount in USD",
                                "minimum": 0.01
                            },
                            "ad_format": {
                                "type": "string",
                                "enum": ["push", "popunder", "onclick", "interstitial"],
                                "description": "Advertisement format",
                                "default": "push"
                            }
                        },
                        "required": ["name", "target_url", "daily_budget", "countries", "bid_amount"],
                        "additionalProperties": False
                    }
                ),
                Tool(
                    name="update_campaign",
                    description="Update campaign settings (WRITE - requires confirmation)",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "campaign_id": {
                                "type": "integer",
                                "description": "Campaign ID to update"
                            },
                            "name": {
                                "type": "string",
                                "description": "New campaign name"
                            },
                            "daily_budget": {
                                "type": "number",
                                "description": "New daily budget in USD",
                                "minimum": 1
                            },
                            "status": {
                                "type": "string",
                                "enum": ["active", "paused", "stopped"],
                                "description": "New campaign status"
                            }
                        },
                        "required": ["campaign_id"],
                        "additionalProperties": False
                    }
                ),
                
                # Statistics & Analytics Tools
                Tool(
                    name="get_campaign_statistics",
                    description="Get performance statistics for campaigns (READ operation)",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "campaign_ids": {
                                "type": "array",
                                "items": {"type": "integer"},
                                "description": "Campaign IDs to get stats for (empty = all campaigns)"
                            },
                            "date_from": {
                                "type": "string",
                                "description": "Start date (YYYY-MM-DD format)",
                                "pattern": "^\\d{4}-\\d{2}-\\d{2}$"
                            },
                            "date_to": {
                                "type": "string",
                                "description": "End date (YYYY-MM-DD format)",
                                "pattern": "^\\d{4}-\\d{2}-\\d{2}$"
                            },
                            "group_by": {
                                "type": "string",
                                "enum": ["campaign", "country", "date", "zone"],
                                "description": "Group statistics by",
                                "default": "campaign"
                            }
                        },
                        "additionalProperties": False
                    }
                ),
                Tool(
                    name="get_performance_summary",
                    description="Get overall performance summary with insights (READ operation)",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "days": {
                                "type": "integer",
                                "description": "Number of days to analyze",
                                "default": 7,
                                "minimum": 1,
                                "maximum": 90
                            }
                        },
                        "additionalProperties": False
                    }
                ),
                
                # AI-Powered Tools
                Tool(
                    name="analyze_campaign_performance",
                    description="AI-powered analysis of campaign performance with recommendations (READ operation)",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "campaign_id": {
                                "type": "integer",
                                "description": "Campaign ID to analyze"
                            },
                            "analysis_type": {
                                "type": "string",
                                "enum": ["performance", "optimization", "scaling", "troubleshooting"],
                                "description": "Type of analysis to perform",
                                "default": "performance"
                            }
                        },
                        "required": ["campaign_id"],
                        "additionalProperties": False
                    }
                ),
                Tool(
                    name="get_optimization_recommendations",
                    description="Get AI-powered optimization recommendations (READ operation)",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "campaign_ids": {
                                "type": "array",
                                "items": {"type": "integer"},
                                "description": "Campaign IDs to optimize (empty = all campaigns)"
                            },
                            "optimization_goal": {
                                "type": "string",
                                "enum": ["roi", "volume", "cpa", "ctr"],
                                "description": "Primary optimization goal",
                                "default": "roi"
                            }
                        },
                        "additionalProperties": False
                    }
                ),
                
                # Targeting & Configuration Tools
                Tool(
                    name="get_targeting_options",
                    description="Get available targeting options (countries, devices, etc.) (READ operation)",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "option_type": {
                                "type": "string",
                                "enum": ["countries", "devices", "browsers", "os", "all"],
                                "description": "Type of targeting options to retrieve",
                                "default": "all"
                            }
                        },
                        "additionalProperties": False
                    }
                ),
                
                # Natural Language Interface
                Tool(
                    name="execute_natural_language_command",
                    description="Execute commands using natural language (SMART - auto-detects READ/WRITE)",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "command": {
                                "type": "string",
                                "description": "Natural language command (e.g., 'show me my best performing campaigns', 'pause campaign 123', 'create a push campaign for US with $100 budget')"
                            },
                            "confirm_write_operations": {
                                "type": "boolean",
                                "description": "Whether to ask for confirmation before write operations",
                                "default": True
                            }
                        },
                        "required": ["command"],
                        "additionalProperties": False
                    }
                )
            ]
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> Sequence[TextContent]:
            """Handle tool calls"""
            try:
                logger.info(f"Tool called: {name} with arguments: {arguments}")
                
                # Route to appropriate handler
                if name == "get_account_balance":
                    result = await self._handle_get_balance()
                elif name == "health_check":
                    result = await self._handle_health_check()
                elif name == "list_campaigns":
                    result = await self._handle_list_campaigns(**arguments)
                elif name == "get_campaign_details":
                    result = await self._handle_get_campaign_details(**arguments)
                elif name == "create_campaign":
                    result = await self._handle_create_campaign(**arguments)
                elif name == "update_campaign":
                    result = await self._handle_update_campaign(**arguments)
                elif name == "get_campaign_statistics":
                    result = await self._handle_get_statistics(**arguments)
                elif name == "get_performance_summary":
                    result = await self._handle_performance_summary(**arguments)
                elif name == "analyze_campaign_performance":
                    result = await self._handle_analyze_performance(**arguments)
                elif name == "get_optimization_recommendations":
                    result = await self._handle_optimization_recommendations(**arguments)
                elif name == "get_targeting_options":
                    result = await self._handle_targeting_options(**arguments)
                elif name == "execute_natural_language_command":
                    result = await self._handle_natural_language(**arguments)
                else:
                    result = {"error": f"Unknown tool: {name}"}
                
                # Format response
                if isinstance(result, dict) and "error" in result:
                    return [TextContent(type="text", text=f"❌ Error: {result['error']}")]
                else:
                    return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
                    
            except Exception as e:
                logger.error(f"Tool execution error: {e}")
                return [TextContent(type="text", text=f"❌ Tool execution failed: {str(e)}")]
    
    def _register_resources(self):
        """Register MCP resources"""
        
        @self.server.list_resources()
        async def list_resources() -> List[Resource]:
            """List available resources"""
            return [
                Resource(
                    uri="propellerads://documentation",
                    name="PropellerAds API Documentation",
                    description="Complete API documentation and usage examples",
                    mimeType="text/markdown"
                ),
                Resource(
                    uri="propellerads://ai-patterns",
                    name="AI Task Patterns",
                    description="Standardized patterns for AI operations",
                    mimeType="application/json"
                )
            ]
        
        @self.server.read_resource()
        async def read_resource(uri: str) -> str:
            """Read resource content"""
            if uri == "propellerads://documentation":
                # Return our comprehensive documentation
                docs_path = Path(__file__).parent.parent / "docs" / "ai-agents"
                if docs_path.exists():
                    content = "# PropellerAds Enterprise API Documentation\\n\\n"
                    for doc_file in docs_path.rglob("*.md"):
                        content += f"## {doc_file.name}\\n\\n"
                        content += doc_file.read_text() + "\\n\\n"
                    return content
                else:
                    return "Documentation not found"
            elif uri == "propellerads://ai-patterns":
                # Return AI task patterns
                patterns_path = Path(__file__).parent.parent / "docs" / "metadata" / "tasks.yaml"
                if patterns_path.exists():
                    return patterns_path.read_text()
                else:
                    return "{}"
            else:
                raise ValueError(f"Unknown resource: {uri}")
    
    # Tool handlers
    async def _handle_get_balance(self) -> Dict[str, Any]:
        """Handle balance request"""
        try:
            balance = self.client.get_balance()
            return {
                "balance": float(balance),
                "currency": "USD",
                "status": "success"
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def _handle_health_check(self) -> Dict[str, Any]:
        """Handle health check"""
        try:
            health = self.client.health_check()
            return {
                "status": "healthy" if health else "unhealthy",
                "api_accessible": health,
                "timestamp": str(asyncio.get_event_loop().time())
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def _handle_list_campaigns(self, status: str = "all", limit: int = 100) -> Dict[str, Any]:
        """Handle campaign listing"""
        try:
            campaigns = self.client.get_campaigns()
            
            # Filter by status if specified
            if status != "all":
                status_map = {
                    "active": [6],  # working
                    "paused": [7],  # paused
                    "stopped": [8], # stopped
                    "draft": [1]    # draft
                }
                if status in status_map:
                    campaigns = [c for c in campaigns if c.get("status") in status_map[status]]
            
            # Limit results
            campaigns = campaigns[:limit]
            
            return {
                "campaigns": campaigns,
                "total_count": len(campaigns),
                "status_filter": status,
                "limit": limit
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def _handle_get_campaign_details(self, campaign_id: int) -> Dict[str, Any]:
        """Handle campaign details request"""
        try:
            campaign = self.client.get_campaign_details(campaign_id)
            return {
                "campaign": campaign,
                "campaign_id": campaign_id
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def _handle_create_campaign(self, **kwargs) -> Dict[str, Any]:
        """Handle campaign creation (requires confirmation)"""
        try:
            # This is a write operation - in real MCP, this would trigger confirmation
            logger.warning(f"WRITE OPERATION: Creating campaign with params: {kwargs}")
            
            # For now, return what would be created (dry run)
            return {
                "operation": "create_campaign",
                "status": "would_create",
                "parameters": kwargs,
                "note": "This is a WRITE operation that would create a real campaign. In production, this requires user confirmation."
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def _handle_update_campaign(self, **kwargs) -> Dict[str, Any]:
        """Handle campaign update (requires confirmation)"""
        try:
            # This is a write operation - in real MCP, this would trigger confirmation
            logger.warning(f"WRITE OPERATION: Updating campaign with params: {kwargs}")
            
            return {
                "operation": "update_campaign",
                "status": "would_update",
                "parameters": kwargs,
                "note": "This is a WRITE operation that would update a real campaign. In production, this requires user confirmation."
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def _handle_get_statistics(self, **kwargs) -> Dict[str, Any]:
        """Handle statistics request"""
        try:
            # Use our AI interface for intelligent statistics
            stats = self.ai_interface.get_performance_analytics(**kwargs)
            return {
                "statistics": stats,
                "parameters": kwargs
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def _handle_performance_summary(self, days: int = 7) -> Dict[str, Any]:
        """Handle performance summary"""
        try:
            summary = self.ai_interface.get_performance_summary(days=days)
            return {
                "summary": summary,
                "period_days": days
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def _handle_analyze_performance(self, campaign_id: int, analysis_type: str = "performance") -> Dict[str, Any]:
        """Handle AI performance analysis"""
        try:
            analysis = self.ai_interface.analyze_campaign_performance(campaign_id, analysis_type)
            return {
                "analysis": analysis,
                "campaign_id": campaign_id,
                "analysis_type": analysis_type
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def _handle_optimization_recommendations(self, **kwargs) -> Dict[str, Any]:
        """Handle optimization recommendations"""
        try:
            recommendations = self.ai_interface.get_optimization_recommendations(**kwargs)
            return {
                "recommendations": recommendations,
                "parameters": kwargs
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def _handle_targeting_options(self, option_type: str = "all") -> Dict[str, Any]:
        """Handle targeting options request"""
        try:
            options = self.client.get_targeting_options()
            
            if option_type != "all" and option_type in options:
                return {option_type: options[option_type]}
            else:
                return options
        except Exception as e:
            return {"error": str(e)}
    
    async def _handle_natural_language(self, command: str, confirm_write_operations: bool = True) -> Dict[str, Any]:
        """Handle natural language commands"""
        try:
            # Use AI interface to process natural language
            result = self.ai_interface.process_natural_language_command(
                command, 
                confirm_write_operations=confirm_write_operations
            )
            return {
                "command": command,
                "result": result,
                "processed_by": "ai_interface"
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def run(self):
        """Run the MCP server"""
        logger.info("Starting PropellerAds Enterprise MCP Server...")
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )


async def main():
    """Main entry point"""
    try:
        server = PropellerAdsMCPServer()
        await server.run()
    except Exception as e:
        logger.error(f"Server startup failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
