#!/usr/bin/env python3
"""
Basic Usage Examples for PropellerAds Python SDK

This file demonstrates common usage patterns and best practices.
"""

import os
import asyncio
from propellerads.client import PropellerAdsClient
from claude_propellerads_integration import ClaudePropellerAdsIntegration

def basic_client_usage():
    """Basic client usage example"""
    print("🚀 Basic PropellerAds Client Usage")
    print("=" * 40)
    
    # Initialize client
    client = PropellerAdsClient(
        api_key=os.environ.get('MainAPI'),
        timeout=30,
        max_retries=3,
        rate_limit=60
    )
    
    try:
        # Check balance
        balance = client.get_balance()
        print(f"💰 Account Balance: {balance.formatted}")
        
        # Get campaigns
        campaigns = client.get_campaigns(limit=5)
        print(f"📋 Found {len(campaigns)} campaigns")
        
        for i, campaign in enumerate(campaigns[:3], 1):
            name = campaign.get('name', 'Unknown')
            status = campaign.get('status', 'Unknown')
            print(f"  {i}. {name} (Status: {status})")
        
        # Get user profile
        profile = client.get_user_profile()
        print(f"👤 User: {profile.get('name', 'Unknown')}")
        
        # Get targeting options
        targeting = client.get_targeting_options()
        countries = targeting.get('countries', [])
        print(f"🌍 Available countries: {len(countries)}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

async def claude_integration_example():
    """Claude AI integration example"""
    print("\n🤖 Claude AI Integration Example")
    print("=" * 40)
    
    try:
        # Initialize Claude integration
        claude = ClaudePropellerAdsIntegration()
        
        # Get account overview
        overview = await claude.get_account_overview()
        if overview["success"]:
            balance = overview["overview"]["balance"]
            campaigns = overview["overview"]["campaigns"]
            print(f"💰 Balance: ${balance['amount']} {balance['currency']}")
            print(f"📋 Campaigns: {campaigns['total']} total, {campaigns['active']} active")
        
        # Get recent statistics
        stats = await claude.get_statistics(days_back=7)
        if stats["success"]:
            print(f"📊 Statistics for last 7 days retrieved")
        
        # Analyze performance (if campaigns exist)
        campaigns_result = await claude.get_campaigns(limit=1)
        if campaigns_result["success"] and campaigns_result["campaigns"]:
            campaign_id = campaigns_result["campaigns"][0].get("id")
            if campaign_id:
                analysis = await claude.analyze_campaign_performance(campaign_id)
                if analysis["success"]:
                    print(f"🔍 Campaign {campaign_id} analysis completed")
        
    except Exception as e:
        print(f"❌ Claude Error: {e}")

def advanced_client_features():
    """Advanced client features example"""
    print("\n⚡ Advanced Client Features")
    print("=" * 40)
    
    # Client with advanced configuration
    client = PropellerAdsClient(
        api_key=os.environ.get('MainAPI'),
        timeout=60,
        max_retries=5,
        rate_limit=30,  # Lower rate for careful usage
        enable_metrics=True
    )
    
    try:
        # Get statistics with date range
        stats = client.get_statistics(
            date_from="2023-01-01 00:00:00",
            date_to="2023-01-31 23:59:59",
            group_by=["date", "campaign_id"]
        )
        print(f"📈 Statistics retrieved: {len(stats) if isinstance(stats, list) else 'N/A'} records")
        
        # Get campaign details (if campaigns exist)
        campaigns = client.get_campaigns(limit=1)
        if campaigns and len(campaigns) > 0:
            campaign_id = campaigns[0].get("id")
            if campaign_id:
                details = client.get_campaign(campaign_id)
                print(f"📋 Campaign details: {details.get('name', 'Unknown')}")
        
    except Exception as e:
        print(f"❌ Advanced Error: {e}")

def error_handling_example():
    """Error handling best practices"""
    print("\n🛡️ Error Handling Example")
    print("=" * 40)
    
    client = PropellerAdsClient(
        api_key="invalid-key",  # Intentionally invalid
        timeout=10,
        max_retries=1
    )
    
    try:
        balance = client.get_balance()
        print(f"Balance: {balance.formatted}")
    except Exception as e:
        print(f"✅ Expected error caught: {type(e).__name__}")
        print(f"   Message: {str(e)[:50]}...")

async def main():
    """Main example function"""
    print("🎯 PropellerAds Python SDK - Usage Examples")
    print("=" * 50)
    
    # Check if API key is available
    if not os.environ.get('MainAPI'):
        print("⚠️ Warning: MainAPI environment variable not set")
        print("   Some examples may not work without a valid API key")
        print()
    
    # Run examples
    basic_client_usage()
    await claude_integration_example()
    advanced_client_features()
    error_handling_example()
    
    print("\n✅ All examples completed!")
    print("\n📚 For more information:")
    print("   - Check the README.md file")
    print("   - Run: python claude_interface.py")
    print("   - Review the test files in tests/")

if __name__ == "__main__":
    asyncio.run(main())
