#!/usr/bin/env python3
"""
Enhanced AI Interface for PropellerAds API
Advanced natural language processing and intelligent operation handling

This module provides sophisticated AI-powered features including:
- Natural language command processing
- Intelligent operation validation
- Context-aware recommendations
- Advanced error handling with recovery suggestions
"""

import re
import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
from datetime import datetime, timedelta
from dataclasses import dataclass

sys.path.append(str(Path(__file__).parent.parent))
from propellerads.client import PropellerAdsClient as PropellerAdsUltimateClient
from src.ai_interface import PropellerAdsAIInterface

logger = logging.getLogger(__name__)


@dataclass
class CommandIntent:
    """Represents a parsed natural language command intent"""
    action: str  # create, update, list, get, analyze, etc.
    entity: str  # campaign, statistics, balance, etc.
    parameters: Dict[str, Any]
    confidence: float
    is_write_operation: bool
    requires_confirmation: bool


@dataclass
class OperationResult:
    """Represents the result of an operation"""
    success: bool
    data: Any
    message: str
    suggestions: List[str]
    warnings: List[str]


class EnhancedPropellerAdsAI(PropellerAdsAIInterface):
    """Enhanced AI interface with advanced natural language processing"""
    
    def __init__(self, client):
        """Initialize enhanced AI interface"""
        super().__init__(client)
        
        # Natural language patterns
        self.command_patterns = {
            # Balance and account
            r"(?:show|get|check).*(?:balance|money|funds)": {
                "action": "get", "entity": "balance", "write": False
            },
            r"(?:health|status|check).*(?:api|connection)": {
                "action": "check", "entity": "health", "write": False
            },
            
            # Campaign listing
            r"(?:show|list|get).*campaigns?": {
                "action": "list", "entity": "campaigns", "write": False
            },
            r"(?:show|get).*(?:best|top|performing).*campaigns?": {
                "action": "list", "entity": "campaigns", "write": False,
                "params": {"filter": "top_performing"}
            },
            r"(?:show|get).*(?:active|running).*campaigns?": {
                "action": "list", "entity": "campaigns", "write": False,
                "params": {"status": "active"}
            },
            r"(?:show|get).*(?:paused|stopped).*campaigns?": {
                "action": "list", "entity": "campaigns", "write": False,
                "params": {"status": "paused"}
            },
            
            # Campaign details
            r"(?:show|get).*(?:details|info).*campaign.*?(\d+)": {
                "action": "get", "entity": "campaign_details", "write": False,
                "extract": ["campaign_id"]
            },
            r"(?:analyze|check).*campaign.*?(\d+)": {
                "action": "analyze", "entity": "campaign", "write": False,
                "extract": ["campaign_id"]
            },
            
            # Campaign creation
            r"create.*campaign": {
                "action": "create", "entity": "campaign", "write": True
            },
            r"(?:make|build|setup).*campaign": {
                "action": "create", "entity": "campaign", "write": True
            },
            
            # Campaign updates
            r"(?:pause|stop).*campaign.*?(\d+)": {
                "action": "update", "entity": "campaign", "write": True,
                "extract": ["campaign_id"], "params": {"status": "paused"}
            },
            r"(?:start|resume|activate).*campaign.*?(\d+)": {
                "action": "update", "entity": "campaign", "write": True,
                "extract": ["campaign_id"], "params": {"status": "active"}
            },
            r"(?:update|change).*budget.*campaign.*?(\d+).*?(\d+(?:\.\d+)?)": {
                "action": "update", "entity": "campaign", "write": True,
                "extract": ["campaign_id", "budget"]
            },
            
            # Statistics
            r"(?:show|get).*(?:stats|statistics|performance)": {
                "action": "get", "entity": "statistics", "write": False
            },
            r"(?:show|get).*(?:summary|overview)": {
                "action": "get", "entity": "summary", "write": False
            },
            
            # Optimization
            r"(?:optimize|improve).*campaigns?": {
                "action": "optimize", "entity": "campaigns", "write": False
            },
            r"(?:recommend|suggest).*(?:optimization|improvements)": {
                "action": "recommend", "entity": "optimization", "write": False
            },
            
            # Targeting
            r"(?:show|get).*(?:targeting|countries|devices)": {
                "action": "get", "entity": "targeting", "write": False
            }
        }
        
        # Parameter extraction patterns
        self.param_patterns = {
            "budget": r"\$?(\d+(?:\.\d+)?)",
            "countries": r"(?:country|countries).*?([A-Z]{2}(?:,\s*[A-Z]{2})*)",
            "bid": r"bid.*?\$?(\d+(?:\.\d+)?)",
            "url": r"(?:url|link|website).*?(https?://[^\s]+)",
            "name": r"(?:name|title).*?['\"]([^'\"]+)['\"]",
            "format": r"(?:format|type).*?(push|popunder|onclick|interstitial)"
        }
    
    def process_natural_language_command(self, command: str, confirm_write_operations: bool = True) -> Dict[str, Any]:
        """Process natural language command with enhanced intelligence"""
        try:
            # Parse command intent
            intent = self._parse_command_intent(command)
            
            if intent.confidence < 0.5:
                return {
                    "error": "Could not understand the command",
                    "suggestions": self._get_command_suggestions(command),
                    "confidence": intent.confidence
                }
            
            # Check if write operation needs confirmation
            if intent.is_write_operation and confirm_write_operations:
                return {
                    "operation": "confirmation_required",
                    "intent": intent.__dict__,
                    "message": f"This will perform a WRITE operation: {intent.action} {intent.entity}",
                    "parameters": intent.parameters,
                    "confirm_command": f"confirm_{intent.action}_{intent.entity}"
                }
            
            # Execute the operation
            result = self._execute_intent(intent)
            
            return {
                "intent": intent.__dict__,
                "result": result.__dict__,
                "natural_language_summary": self._generate_summary(intent, result)
            }
            
        except Exception as e:
            logger.error(f"Natural language processing error: {e}")
            return {
                "error": str(e),
                "suggestions": ["Try rephrasing your command", "Use more specific terms"]
            }
    
    def _parse_command_intent(self, command: str) -> CommandIntent:
        """Parse natural language command into structured intent"""
        command_lower = command.lower().strip()
        
        best_match = None
        best_confidence = 0.0
        
        # Try to match against known patterns
        for pattern, config in self.command_patterns.items():
            match = re.search(pattern, command_lower)
            if match:
                confidence = len(match.group(0)) / len(command_lower)
                if confidence > best_confidence:
                    best_confidence = confidence
                    best_match = (match, config)
        
        if best_match:
            match, config = best_match
            
            # Extract parameters
            parameters = config.get("params", {}).copy()
            
            # Extract dynamic parameters
            if "extract" in config:
                for i, param_name in enumerate(config["extract"]):
                    if i + 1 <= len(match.groups()):
                        value = match.group(i + 1)
                        if param_name == "campaign_id":
                            parameters[param_name] = int(value)
                        elif param_name == "budget":
                            parameters["daily_budget"] = float(value)
                        else:
                            parameters[param_name] = value
            
            # Extract additional parameters from command
            additional_params = self._extract_parameters(command_lower)
            parameters.update(additional_params)
            
            return CommandIntent(
                action=config["action"],
                entity=config["entity"],
                parameters=parameters,
                confidence=min(best_confidence * 1.5, 1.0),  # Boost confidence for good matches
                is_write_operation=config.get("write", False),
                requires_confirmation=config.get("write", False)
            )
        
        # Fallback: try to extract basic intent
        return self._fallback_intent_extraction(command_lower)
    
    def _extract_parameters(self, command: str) -> Dict[str, Any]:
        """Extract parameters from command text"""
        params = {}
        
        for param_name, pattern in self.param_patterns.items():
            match = re.search(pattern, command)
            if match:
                value = match.group(1)
                if param_name in ["budget", "bid"]:
                    params[param_name] = float(value)
                elif param_name == "countries":
                    params[param_name] = [c.strip() for c in value.split(",")]
                else:
                    params[param_name] = value
        
        return params
    
    def _fallback_intent_extraction(self, command: str) -> CommandIntent:
        """Fallback intent extraction for unmatched commands"""
        # Simple keyword-based fallback
        if any(word in command for word in ["create", "make", "new"]):
            action = "create"
            is_write = True
        elif any(word in command for word in ["update", "change", "modify"]):
            action = "update"
            is_write = True
        elif any(word in command for word in ["delete", "remove", "stop"]):
            action = "delete"
            is_write = True
        elif any(word in command for word in ["show", "get", "list", "display"]):
            action = "get"
            is_write = False
        else:
            action = "unknown"
            is_write = False
        
        # Determine entity
        if "campaign" in command:
            entity = "campaign"
        elif "balance" in command:
            entity = "balance"
        elif "stat" in command:
            entity = "statistics"
        else:
            entity = "unknown"
        
        return CommandIntent(
            action=action,
            entity=entity,
            parameters={},
            confidence=0.3,  # Low confidence for fallback
            is_write_operation=is_write,
            requires_confirmation=is_write
        )
    
    def _execute_intent(self, intent: CommandIntent) -> OperationResult:
        """Execute the parsed intent"""
        try:
            if intent.action == "get" and intent.entity == "balance":
                balance_response = self.client.get_balance()
                # Handle BalanceResponse object
                if hasattr(balance_response, 'amount'):
                    balance_amount = float(balance_response.amount)
                    currency = getattr(balance_response, 'currency', 'USD')
                else:
                    balance_amount = float(balance_response)
                    currency = "USD"
                
                return OperationResult(
                    success=True,
                    data={"balance": balance_amount, "currency": currency},
                    message=f"Current account balance: ${balance_amount:.2f}",
                    suggestions=["Check campaign performance", "Review spending trends"],
                    warnings=[]
                )
            
            elif intent.action == "check" and intent.entity == "health":
                health = self.client.health_check()
                return OperationResult(
                    success=health,
                    data={"healthy": health},
                    message="API is healthy" if health else "API connection issues",
                    suggestions=["Test API endpoints"] if health else ["Check API credentials"],
                    warnings=[] if health else ["API may be experiencing issues"]
                )
            
            elif intent.action == "list" and intent.entity == "campaigns":
                campaigns = self.client.get_campaigns()
                
                # Apply filters
                if intent.parameters.get("filter") == "top_performing":
                    # Sort by performance (mock implementation)
                    campaigns = sorted(campaigns, key=lambda x: x.get("clicks", 0), reverse=True)[:10]
                elif intent.parameters.get("status"):
                    status_map = {"active": [6], "paused": [7], "stopped": [8]}
                    target_statuses = status_map.get(intent.parameters["status"], [])
                    campaigns = [c for c in campaigns if c.get("status") in target_statuses]
                
                return OperationResult(
                    success=True,
                    data={"campaigns": campaigns, "count": len(campaigns)},
                    message=f"Found {len(campaigns)} campaigns",
                    suggestions=["Analyze campaign performance", "Check campaign details"],
                    warnings=[]
                )
            
            elif intent.action == "get" and intent.entity == "campaign_details":
                campaign_id = intent.parameters.get("campaign_id")
                if not campaign_id:
                    raise ValueError("Campaign ID is required")
                
                campaign = self.client.get_campaign_details(campaign_id)
                return OperationResult(
                    success=True,
                    data={"campaign": campaign},
                    message=f"Campaign {campaign_id} details retrieved",
                    suggestions=["Analyze performance", "Update settings"],
                    warnings=[]
                )
            
            elif intent.action == "analyze" and intent.entity == "campaign":
                campaign_id = intent.parameters.get("campaign_id")
                if not campaign_id:
                    raise ValueError("Campaign ID is required")
                
                analysis = self.analyze_campaign_performance(campaign_id)
                return OperationResult(
                    success=True,
                    data={"analysis": analysis},
                    message=f"Campaign {campaign_id} analysis completed",
                    suggestions=analysis.get("recommendations", []),
                    warnings=analysis.get("warnings", [])
                )
            
            elif intent.action == "get" and intent.entity == "statistics":
                stats = self.get_performance_analytics()
                return OperationResult(
                    success=True,
                    data={"statistics": stats},
                    message="Performance statistics retrieved",
                    suggestions=["Review trends", "Optimize campaigns"],
                    warnings=[]
                )
            
            elif intent.action == "get" and intent.entity == "summary":
                days = intent.parameters.get("days", 7)
                summary = self._get_performance_summary(days=days)
                return OperationResult(
                    success=True,
                    data={"summary": summary},
                    message=f"Performance summary for last {days} days",
                    suggestions=["Check individual campaigns", "Review optimization opportunities"],
                    warnings=[]
                )
            
            elif intent.action == "optimize" and intent.entity == "campaigns":
                recommendations = self.get_optimization_recommendations()
                return OperationResult(
                    success=True,
                    data={"recommendations": recommendations},
                    message="Optimization recommendations generated",
                    suggestions=recommendations.get("actions", []),
                    warnings=recommendations.get("warnings", [])
                )
            
            elif intent.action == "get" and intent.entity == "targeting":
                # Get targeting options from available endpoints
                try:
                    # Use available API methods
                    options = {}
                    
                    # Try to get countries
                    if hasattr(self.client, 'get_countries'):
                        options["countries"] = self.client.get_countries()
                    else:
                        # Fallback: provide common countries
                        options["countries"] = ["US", "CA", "UK", "DE", "FR", "AU", "JP"]
                    
                    # Try to get other targeting options
                    if hasattr(self.client, 'get_devices'):
                        options["devices"] = self.client.get_devices()
                    else:
                        options["devices"] = ["desktop", "mobile", "tablet"]
                    
                    if hasattr(self.client, 'get_browsers'):
                        options["browsers"] = self.client.get_browsers()
                    else:
                        options["browsers"] = ["chrome", "firefox", "safari", "edge"]
                    
                    # Add OS options
                    options["operating_systems"] = ["windows", "macos", "linux", "android", "ios"]
                    
                    # Add ad formats
                    options["ad_formats"] = ["push", "popunder", "onclick", "interstitial"]
                    
                    total_options = len(options["countries"]) + len(options["devices"]) + len(options["browsers"])
                    
                    return OperationResult(
                        success=True,
                        data={"targeting_options": options},
                        message=f"Targeting options available: {len(options['countries'])} countries, {len(options['devices'])} devices, {len(options['browsers'])} browsers",
                        suggestions=["Review available countries", "Check device options", "Explore ad formats"],
                        warnings=[]
                    )
                except Exception as e:
                    return OperationResult(
                        success=False,
                        data={},
                        message=f"Could not retrieve targeting options: {str(e)}",
                        suggestions=["Check API connectivity"],
                        warnings=[str(e)]
                    )
            
            # Write operations (would require confirmation in real implementation)
            elif intent.action == "create" and intent.entity == "campaign":
                return OperationResult(
                    success=False,
                    data={"operation": "create_campaign", "parameters": intent.parameters},
                    message="Campaign creation requires confirmation and additional parameters",
                    suggestions=[
                        "Specify campaign name, target URL, budget, and countries",
                        "Use format: 'create campaign named \"My Campaign\" for US with $100 budget targeting https://example.com'"
                    ],
                    warnings=["This is a write operation that will create a real campaign"]
                )
            
            elif intent.action == "update" and intent.entity == "campaign":
                return OperationResult(
                    success=False,
                    data={"operation": "update_campaign", "parameters": intent.parameters},
                    message="Campaign update requires confirmation",
                    suggestions=["Confirm the changes you want to make"],
                    warnings=["This is a write operation that will modify a real campaign"]
                )
            
            else:
                return OperationResult(
                    success=False,
                    data={},
                    message=f"Unknown operation: {intent.action} {intent.entity}",
                    suggestions=self._get_command_suggestions(f"{intent.action} {intent.entity}"),
                    warnings=[]
                )
                
        except Exception as e:
            return OperationResult(
                success=False,
                data={},
                message=f"Operation failed: {str(e)}",
                suggestions=["Check your parameters", "Try a simpler command"],
                warnings=[str(e)]
            )
    
    def _generate_summary(self, intent: CommandIntent, result: OperationResult) -> str:
        """Generate natural language summary of the operation"""
        if not result.success:
            return f"❌ {result.message}"
        
        if intent.action == "get" and intent.entity == "balance":
            balance = result.data.get("balance", 0)
            return f"💰 Your account balance is ${balance:.2f}"
        
        elif intent.action == "list" and intent.entity == "campaigns":
            count = result.data.get("count", 0)
            return f"📊 Found {count} campaigns matching your criteria"
        
        elif intent.action == "analyze" and intent.entity == "campaign":
            campaign_id = intent.parameters.get("campaign_id")
            return f"🔍 Analysis completed for campaign {campaign_id}"
        
        elif intent.action == "get" and intent.entity == "statistics":
            return "📈 Performance statistics retrieved successfully"
        
        else:
            return f"✅ {result.message}"
    
    def _get_command_suggestions(self, command: str) -> List[str]:
        """Get command suggestions for unclear input"""
        suggestions = [
            "show my balance",
            "list all campaigns",
            "show active campaigns",
            "get campaign details for 123",
            "analyze campaign 123",
            "show performance statistics",
            "get optimization recommendations",
            "show targeting options"
        ]
        
        # Add context-specific suggestions based on command
        if "campaign" in command.lower():
            suggestions.extend([
                "create campaign named \"Test\" for US with $50 budget",
                "pause campaign 123",
                "update budget for campaign 123 to $100"
            ])
        
        return suggestions[:5]  # Return top 5 suggestions
    
    def get_intelligent_insights(self, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get intelligent insights based on current context"""
        try:
            insights = {
                "account_health": self._assess_account_health(),
                "performance_trends": self._analyze_performance_trends(),
                "optimization_opportunities": self._identify_optimization_opportunities(),
                "risk_alerts": self._check_risk_alerts(),
                "recommendations": self._generate_smart_recommendations()
            }
            
            return insights
            
        except Exception as e:
            logger.error(f"Error generating insights: {e}")
            return {"error": str(e)}
    
    def _assess_account_health(self) -> Dict[str, Any]:
        """Assess overall account health"""
        try:
            balance = self.client.get_balance()
            campaigns = self.client.get_campaigns()
            
            active_campaigns = [c for c in campaigns if c.get("status") == 6]
            
            health_score = 100
            issues = []
            
            # Check balance
            if balance < 50:
                health_score -= 30
                issues.append("Low account balance")
            
            # Check active campaigns
            if len(active_campaigns) == 0:
                health_score -= 40
                issues.append("No active campaigns")
            elif len(active_campaigns) < 3:
                health_score -= 20
                issues.append("Few active campaigns")
            
            return {
                "score": max(health_score, 0),
                "status": "healthy" if health_score >= 80 else "needs_attention" if health_score >= 50 else "critical",
                "balance": float(balance),
                "active_campaigns": len(active_campaigns),
                "total_campaigns": len(campaigns),
                "issues": issues
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def _analyze_performance_trends(self) -> Dict[str, Any]:
        """Analyze performance trends"""
        # Mock implementation - in real scenario, would analyze historical data
        return {
            "trend": "stable",
            "change_percentage": 5.2,
            "period": "7_days",
            "key_metrics": {
                "clicks": {"trend": "up", "change": 12.3},
                "conversions": {"trend": "stable", "change": 2.1},
                "cost": {"trend": "down", "change": -5.8}
            }
        }
    
    def _identify_optimization_opportunities(self) -> List[Dict[str, Any]]:
        """Identify optimization opportunities"""
        return [
            {
                "type": "budget_reallocation",
                "priority": "high",
                "description": "Reallocate budget from low-performing to high-performing campaigns",
                "potential_impact": "15-25% ROI improvement"
            },
            {
                "type": "targeting_optimization",
                "priority": "medium",
                "description": "Refine geo-targeting based on performance data",
                "potential_impact": "10-15% cost reduction"
            }
        ]
    
    def _check_risk_alerts(self) -> List[Dict[str, Any]]:
        """Check for risk alerts"""
        alerts = []
        
        try:
            balance = self.client.get_balance()
            if balance < 100:
                alerts.append({
                    "type": "low_balance",
                    "severity": "high" if balance < 50 else "medium",
                    "message": f"Account balance is low: ${balance}",
                    "action": "Add funds to prevent campaign interruption"
                })
        except:
            pass
        
        return alerts
    
    def _generate_smart_recommendations(self) -> List[str]:
        """Generate smart recommendations"""
        return [
            "Consider testing new ad formats for better performance",
            "Review and optimize underperforming campaigns",
            "Expand successful campaigns to similar markets",
            "Implement automated bidding strategies",
            "Set up performance monitoring alerts"
        ]
    
    def _get_performance_summary(self, days: int = 7) -> Dict[str, Any]:
        """Get performance summary for specified days"""
        try:
            # Get basic account info
            balance_response = self.client.get_balance()
            balance = float(balance_response.amount) if hasattr(balance_response, 'amount') else float(balance_response)
            
            campaigns = self.client.get_campaigns()
            active_campaigns = [c for c in campaigns if c.get("status") == 6]
            
            # Calculate basic metrics
            total_campaigns = len(campaigns)
            active_count = len(active_campaigns)
            
            # Mock performance data (in real implementation, would fetch from statistics API)
            summary = {
                "period": f"last_{days}_days",
                "account_balance": balance,
                "campaigns": {
                    "total": total_campaigns,
                    "active": active_count,
                    "paused": total_campaigns - active_count
                },
                "performance": {
                    "estimated_spend": min(balance * 0.1, 100),  # Mock data
                    "estimated_clicks": active_count * 1000,    # Mock data
                    "estimated_impressions": active_count * 50000  # Mock data
                },
                "health_score": self._calculate_health_score(balance, active_count),
                "recommendations": self._get_summary_recommendations(balance, active_count)
            }
            
            return summary
            
        except Exception as e:
            return {
                "error": str(e),
                "period": f"last_{days}_days",
                "message": "Could not generate performance summary"
            }
    
    def _calculate_health_score(self, balance: float, active_campaigns: int) -> int:
        """Calculate account health score"""
        score = 100
        
        if balance < 50:
            score -= 40
        elif balance < 100:
            score -= 20
        
        if active_campaigns == 0:
            score -= 50
        elif active_campaigns < 3:
            score -= 20
        
        return max(score, 0)
    
    def _get_summary_recommendations(self, balance: float, active_campaigns: int) -> List[str]:
        """Get recommendations based on account state"""
        recommendations = []
        
        if balance < 100:
            recommendations.append("Consider adding funds to maintain campaign performance")
        
        if active_campaigns == 0:
            recommendations.append("Start some campaigns to begin generating traffic")
        elif active_campaigns < 3:
            recommendations.append("Consider launching additional campaigns for better diversification")
        
        if active_campaigns > 0:
            recommendations.append("Monitor campaign performance and optimize based on results")
        
        return recommendations
