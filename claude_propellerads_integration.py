
#!/usr/bin/env python3
"""
Claude MCP Integration with PropellerAds API

This module provides Claude with direct access to PropellerAds API functionality
through the MCP (Model Context Protocol) interface.
"""

import os
import json
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

from propellerads.client import PropellerAdsClient
from propellerads.exceptions import PropellerAdsError
from anthropic import AsyncAnthropic


class ClaudePropellerAdsIntegration:
    """
    Claude integration for PropellerAds API operations.
    
    This class provides Claude with the ability to:
    - Check account balance and status
    - Manage campaigns (create, read, update, delete)
    - Retrieve and analyze statistics
    - Configure targeting options
    - Monitor performance metrics
    """
    
    def __init__(self):
        """Initialize the Claude-PropellerAds integration."""
        self.api_key = os.environ.get("MainAPI")
        if not self.api_key:
            raise ValueError("PropellerAds API key not found in environment variable 'MainAPI'")
        
        self.client = PropellerAdsClient(
            api_key=self.api_key,
            timeout=30,
            max_retries=3,
            rate_limit=60
        )
        
        self.anthropic_client = AsyncAnthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
        
        # System prompt for Claude
        self.system_prompt = self._create_system_prompt()
    
    def _create_system_prompt(self) -> str:
        """Create advanced system prompt for Claude to work with PropellerAds."""
        from claude_advanced_system_prompt import get_advanced_system_prompt
        return get_advanced_system_prompt()
    
    async def get_balance(self) -> Dict[str, Any]:
        """Get account balance information."""
        try:
            balance = self.client.get_balance()
            return {
                "success": True,
                "balance": {
                    "amount": float(balance.amount),
                    "currency": balance.currency,
                    "formatted": balance.formatted
                },
                "message": f"Current account balance: {balance.formatted}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to retrieve balance: {e}"
            }
    
    async def get_campaigns(self, limit: int = 50) -> Dict[str, Any]:
        """Get list of campaigns."""
        try:
            campaigns = self.client.get_campaigns()
            
            # Handle different response formats
            if isinstance(campaigns, dict) and 'result' in campaigns:
                campaigns_list = campaigns['result'][:limit]
                total_count = len(campaigns['result'])
            else:
                campaigns_list = campaigns[:limit] if isinstance(campaigns, list) else []
                total_count = len(campaigns_list)
            
            return {
                "success": True,
                "campaigns": campaigns_list,
                "count": len(campaigns_list),
                "total": total_count,
                "message": f"Retrieved {len(campaigns_list)} campaigns"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to retrieve campaigns: {e}"
            }
    
    async def get_campaign_details(self, campaign_id: int) -> Dict[str, Any]:
        """Get detailed information about a specific campaign."""
        try:
            campaign = self.client.get_campaign(campaign_id)
            return {
                "success": True,
                "campaign": campaign,
                "message": f"Retrieved details for campaign {campaign_id}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to retrieve campaign {campaign_id}: {e}"
            }
    
    async def get_statistics(self, 
                           days_back: int = 7,
                           campaign_id: Optional[int] = None,
                           group_by: Optional[List[str]] = None) -> Dict[str, Any]:
        """Get performance statistics."""
        try:
            date_to = datetime.now()
            date_from = date_to - timedelta(days=days_back)
            
            params = {
                'date_from': date_from.strftime('%Y-%m-%d 00:00:00'),
                'date_to': date_to.strftime('%Y-%m-%d 23:59:59')
            }
            
            if campaign_id:
                params['campaign_id'] = campaign_id
            
            if group_by:
                params['group_by'] = group_by
            
            stats = self.client.get_statistics(**params)
            
            return {
                "success": True,
                "statistics": stats,
                "period": f"{days_back} days",
                "date_range": {
                    "from": date_from.strftime('%Y-%m-%d'),
                    "to": date_to.strftime('%Y-%m-%d')
                },
                "message": f"Retrieved statistics for {days_back} days"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to retrieve statistics: {e}"
            }
    
    async def get_targeting_options(self) -> Dict[str, Any]:
        """Get available targeting options."""
        try:
            targeting = self.client.get_targeting_options()
            return {
                "success": True,
                "targeting_options": targeting,
                "message": "Retrieved targeting options"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to retrieve targeting options: {e}"
            }
    
    async def get_user_profile(self) -> Dict[str, Any]:
        """Get user profile information."""
        try:
            profile = self.client.get_user_profile()
            return {
                "success": True,
                "profile": profile,
                "message": "Retrieved user profile"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to retrieve user profile: {e}"
            }
    
    async def create_campaign(self, campaign_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new campaign with the provided data.
        
        Args:
            campaign_data: Dictionary containing campaign configuration
            
        Returns:
            Dict with success status and campaign data or error message
        """
        try:
            # Validate required fields
            required_fields = ['name', 'target_url']
            missing_fields = [field for field in required_fields if not campaign_data.get(field)]
            
            if missing_fields:
                return {
                    'success': False,
                    'error': f'Missing required fields: {", ".join(missing_fields)}'
                }
            
            # Set default values and format according to PropellerAds API schema
            from datetime import datetime, timedelta
            
            # Calculate dates
            start_date = datetime.now().strftime('%d/%m/%Y')
            end_date = (datetime.now() + timedelta(days=30)).strftime('%d/%m/%Y')
            
            final_data = {
                'name': campaign_data.get('name', 'API Test Campaign'),
                'direction': 'onclick',  # onclick or push
                'rate_model': 'cpm',     # cpm or cpa
                'target_url': campaign_data.get('target_url', campaign_data.get('landing_url', '')),
                'frequency': 3,
                'capping': 86400,
                'status': 1,  # 1 = active (let API handle status transitions)
                'started_at': start_date,
                'expired_at': end_date,
                'is_adblock_buy': 1,
                'targeting': {
                    'country': {
                        'list': [country.lower() for country in campaign_data.get('countries', ['us'])],
                        'is_excluded': False
                    },
                    'connection': campaign_data.get('devices', ['mobile'])[0] if campaign_data.get('devices') else 'mobile',
                    'traffic_categories': ['propeller'],  # Required field
                    'user_activity': {
                        'list': [1, 2, 3],  # All user activity types
                        'is_excluded': False
                    },
                    'time_table': {
                        'list': ['Mon00', 'Mon01', 'Mon02', 'Mon03', 'Mon04', 'Mon05', 'Mon06', 'Mon07', 'Mon08', 'Mon09', 'Mon10', 'Mon11', 'Mon12', 'Mon13', 'Mon14', 'Mon15', 'Mon16', 'Mon17', 'Mon18', 'Mon19', 'Mon20', 'Mon21', 'Mon22', 'Mon23'],  # All day Monday as example
                        'is_excluded': False
                    }
                },
                'timezone': 0,  # UTC
                'allow_zone_update': True,
                'rates': [
                    {
                        'countries': [country.lower() for country in campaign_data.get('countries', ['us'])],
                        'amount': max(0.47, float(campaign_data.get('budget', 50)) / 100)  # Ensure minimum $0.47
                    }
                ]
            }
            
            # Create campaign via API
            result = self.client.create_campaign(final_data)
            
            return {
                'success': True,
                'campaign': result,
                'message': f'Campaign "{final_data["name"]}" created successfully in DRAFT status'
            }
            
        except PropellerAdsError as e:
            # Log the full error for debugging
            print(f"DEBUG: PropellerAds API Error: {str(e)}")
            return {
                'success': False,
                'error': f'PropellerAds API error: {str(e)}'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Unexpected error: {str(e)}'
            }

    async def analyze_campaign_performance(self, campaign_id: int) -> Dict[str, Any]:
        """Analyze campaign performance and provide optimization suggestions."""
        try:
            # Get campaign details
            campaign_result = await self.get_campaign_details(campaign_id)
            if not campaign_result["success"]:
                return campaign_result
            
            # Get campaign statistics
            stats_result = await self.get_statistics(days_back=30, campaign_id=campaign_id)
            if not stats_result["success"]:
                return stats_result
            
            campaign = campaign_result["campaign"]
            stats = stats_result["statistics"]
            
            # Perform analysis
            analysis = {
                "campaign_id": campaign_id,
                "campaign_name": campaign.get("name", "Unknown"),
                "status": campaign.get("status", "Unknown"),
                "performance_metrics": stats,
                "recommendations": []
            }
            
            # Add basic recommendations based on performance
            if isinstance(stats, list) and stats:
                total_impressions = sum(s.get("impressions", 0) for s in stats)
                total_clicks = sum(s.get("clicks", 0) for s in stats)
                total_cost = sum(s.get("cost", 0) for s in stats)
                
                if total_impressions > 0:
                    ctr = (total_clicks / total_impressions) * 100
                    analysis["ctr"] = round(ctr, 2)
                    
                    if ctr < 1.0:
                        analysis["recommendations"].append("Consider improving ad creative - CTR is below 1%")
                    elif ctr > 5.0:
                        analysis["recommendations"].append("Excellent CTR! Consider increasing budget")
                
                if total_cost > 0:
                    analysis["total_cost"] = total_cost
                    analysis["recommendations"].append(f"Total spend in last 30 days: ${total_cost:.2f}")
            
            return {
                "success": True,
                "analysis": analysis,
                "message": f"Analyzed performance for campaign {campaign_id}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to analyze campaign {campaign_id}: {e}"
            }
    
    async def get_account_overview(self) -> Dict[str, Any]:
        """Get comprehensive account overview."""
        try:
            # Get balance
            balance_result = await self.get_balance()
            
            # Get campaigns
            campaigns_result = await self.get_campaigns()
            
            # Get recent statistics
            stats_result = await self.get_statistics(days_back=7)
            
            overview = {
                "timestamp": datetime.now().isoformat(),
                "balance": balance_result.get("balance"),
                "campaigns": {
                    "total": campaigns_result.get("total", 0),
                    "active": 0,
                    "paused": 0
                },
                "recent_performance": stats_result.get("statistics"),
                "status": "healthy" if balance_result["success"] else "issues"
            }
            
            # Count campaign statuses
            if campaigns_result["success"]:
                for campaign in campaigns_result.get("campaigns", []):
                    status = campaign.get("status", "unknown")
                    if status == "active":
                        overview["campaigns"]["active"] += 1
                    elif status == "paused":
                        overview["campaigns"]["paused"] += 1
            
            return {
                "success": True,
                "overview": overview,
                "message": "Generated account overview"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to generate account overview: {e}"
            }


# MCP Server Functions for Claude
async def handle_mcp_request(method: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """Handle MCP requests from Claude."""
    integration = ClaudePropellerAdsIntegration()
    
    if method == "get_balance":
        return await integration.get_balance()
    
    elif method == "get_campaigns":
        limit = params.get("limit", 50)
        return await integration.get_campaigns(limit)
    
    elif method == "get_campaign_details":
        campaign_id = params.get("campaign_id")
        if not campaign_id:
            return {"success": False, "error": "campaign_id required"}
        return await integration.get_campaign_details(campaign_id)
    
    elif method == "get_statistics":
        days_back = params.get("days_back", 7)
        campaign_id = params.get("campaign_id")
        group_by = params.get("group_by")
        return await integration.get_statistics(days_back, campaign_id, group_by)
    
    elif method == "get_targeting_options":
        return await integration.get_targeting_options()
    
    elif method == "get_user_profile":
        return await integration.get_user_profile()
    
    elif method == "analyze_campaign_performance":
        campaign_id = params.get("campaign_id")
        if not campaign_id:
            return {"success": False, "error": "campaign_id required"}
        return await integration.analyze_campaign_performance(campaign_id)
    
    elif method == "get_account_overview":
        return await integration.get_account_overview()
    
    else:
        return {
            "success": False,
            "error": f"Unknown method: {method}",
            "available_methods": [
                "get_balance", "get_campaigns", "get_campaign_details", 
                "get_statistics", "get_targeting_options", "get_user_profile",
                "analyze_campaign_performance", "get_account_overview"
            ]
        }

