#!/usr/bin/env python3
"""
Simple Interface for Claude-PropellerAds Integration

This provides a simple command-line interface to interact with Claude
through the PropellerAds API integration.
"""

import os
import asyncio
import json
from claude_propellerads_integration import ClaudePropellerAdsIntegration, handle_mcp_request

class ClaudeInterface:
    """Simple interface for Claude interaction"""
    
    def __init__(self):
        self.integration = ClaudePropellerAdsIntegration()
        print("🤖 Claude-PropellerAds Interface Ready!")
        print("=" * 50)
        print(f"💰 Account Balance: {self.get_balance_sync()}")
        print("=" * 50)
    
    def get_balance_sync(self):
        """Get balance synchronously for display"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self.integration.get_balance())
            loop.close()
            if result["success"]:
                return result["balance"]["formatted"]
            return "Error getting balance"
        except:
            return "Unknown"
    
    async def process_command(self, command: str):
        """Process a command and return response"""
        command = command.lower().strip()
        
        if command in ["balance", "get balance", "check balance"]:
            return await self.integration.get_balance()
        
        elif command in ["campaigns", "get campaigns", "list campaigns"]:
            return await self.integration.get_campaigns()
        
        elif command in ["overview", "account overview", "status"]:
            return await self.integration.get_account_overview()
        
        elif command in ["stats", "statistics", "get stats"]:
            return await self.integration.get_statistics()
        
        elif command in ["targeting", "targeting options"]:
            return await self.integration.get_targeting_options()
        
        elif command in ["profile", "user profile"]:
            return await self.integration.get_user_profile()
        
        elif command.startswith("campaign "):
            # Extract campaign ID
            try:
                campaign_id = int(command.split()[-1])
                return await self.integration.get_campaign_details(campaign_id)
            except:
                return {"success": False, "error": "Invalid campaign ID"}
        
        elif command.startswith("analyze "):
            # Extract campaign ID for analysis
            try:
                campaign_id = int(command.split()[-1])
                return await self.integration.analyze_campaign_performance(campaign_id)
            except:
                return {"success": False, "error": "Invalid campaign ID for analysis"}
        
        else:
            return {
                "success": False,
                "error": "Unknown command",
                "available_commands": [
                    "balance - Check account balance",
                    "campaigns - List all campaigns", 
                    "overview - Get account overview",
                    "stats - Get statistics",
                    "targeting - Get targeting options",
                    "profile - Get user profile",
                    "campaign <id> - Get campaign details",
                    "analyze <id> - Analyze campaign performance",
                    "help - Show this help",
                    "quit - Exit interface"
                ]
            }
    
    def format_response(self, response):
        """Format response for display"""
        if response["success"]:
            if "balance" in response:
                return f"💰 Balance: {response['balance']['formatted']}"
            elif "campaigns" in response:
                campaigns = response["campaigns"]
                result = f"📋 Found {len(campaigns)} campaigns:\n"
                for i, campaign in enumerate(campaigns[:5], 1):
                    name = campaign.get("name", "Unknown")
                    status = campaign.get("status", "Unknown")
                    result += f"  {i}. {name} (Status: {status})\n"
                if len(campaigns) > 5:
                    result += f"  ... and {len(campaigns) - 5} more"
                return result
            elif "overview" in response:
                overview = response["overview"]
                balance = overview.get("balance", {})
                campaigns = overview.get("campaigns", {})
                return f"""📊 Account Overview:
💰 Balance: ${balance.get('amount', 'Unknown')} {balance.get('currency', '')}
📋 Campaigns: {campaigns.get('total', 0)} total, {campaigns.get('active', 0)} active
📈 Status: {overview.get('status', 'Unknown')}"""
            else:
                return f"✅ {response.get('message', 'Success')}"
        else:
            return f"❌ Error: {response.get('error', 'Unknown error')}"
    
    async def run_interactive(self):
        """Run interactive command loop"""
        print("\n🤖 Claude Interface - Type commands or 'help' for options")
        print("Type 'quit' to exit\n")
        
        while True:
            try:
                command = input("Claude> ").strip()
                
                if command.lower() in ["quit", "exit", "q"]:
                    print("👋 Goodbye!")
                    break
                
                if command.lower() in ["help", "?"]:
                    help_response = await self.process_command("help")
                    print("\n📚 Available Commands:")
                    for cmd in help_response["available_commands"]:
                        print(f"  • {cmd}")
                    print()
                    continue
                
                if not command:
                    continue
                
                print("🔄 Processing...")
                response = await self.process_command(command)
                print(self.format_response(response))
                print()
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

async def main():
    """Main function"""
    interface = ClaudeInterface()
    await interface.run_interactive()

if __name__ == "__main__":
    asyncio.run(main())
