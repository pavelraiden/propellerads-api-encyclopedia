#!/usr/bin/env python3
"""
PropellerAds API Quick Start Example
Working example with the actual PropellerAdsClient API
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from propellerads.client import PropellerAdsClient

def quick_start_demo():
    """Demonstration of core API functionality"""
    
    print("🚀 PROPELLERADS API QUICK START")
    print("=" * 40)
    
    # Initialize client
    api_key = os.getenv('MainAPI')
    if not api_key:
        print("❌ Error: Set MainAPI environment variable")
        return
    
    client = PropellerAdsClient(api_key=api_key)
    
    # 1. Health check
    print("1️⃣ API Health Check...")
    try:
        health = client.health_check()
        print(f"   Status: {'✅ Healthy' if health else '❌ Unhealthy'}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 2. Account balance
    print("\n2️⃣ Account Balance...")
    try:
        balance = client.get_balance()
        print(f"   💰 Balance: {balance.formatted}")
        print(f"   Currency: {balance.currency}")
        print(f"   Last Updated: {balance.last_updated.strftime('%Y-%m-%d %H:%M:%S')}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 3. Campaigns list
    print("\n3️⃣ Campaigns List...")
    try:
        campaigns = client.get_campaigns(limit=5)
        print(f"   📊 Found campaigns: {len(campaigns)}")
        
        for i, campaign in enumerate(list(campaigns)[:3], 1):  # Show first 3
            status_text = "Active" if hasattr(campaign, 'status') and campaign.status == "active" else "Paused"
            campaign_name = getattr(campaign, 'name', 'Unknown')
            campaign_id = getattr(campaign, 'id', 'Unknown')
            print(f"   {i}. {campaign_name} (ID: {campaign_id}) - {status_text}")
            if hasattr(campaign, 'budget'):
                print(f"      Budget: ${campaign.budget}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 4. Statistics (last 7 days)
    print("\n4️⃣ Recent Statistics...")
    try:
        from datetime import datetime, timedelta
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        
        stats = client.get_statistics(
            date_from=start_date.strftime('%Y-%m-%d'),
            date_to=end_date.strftime('%Y-%m-%d'),
            group_by=['day']
        )
        
        print(f"   📈 Statistics for last 7 days:")
        print(f"   Total Clicks: {stats.total_clicks:,}")
        print(f"   Total Impressions: {stats.total_impressions:,}")
        print(f"   Total Spend: ${stats.total_spend:.2f}")
        if stats.total_clicks > 0:
            ctr = (stats.total_clicks / stats.total_impressions) * 100
            print(f"   CTR: {ctr:.2f}%")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n✅ Quick Start Complete!")
    print("\n💡 Next Steps:")
    print("   - Check docs/MCP_INTEGRATION_GUIDE.md for Claude Desktop setup")
    print("   - Try src/enhanced_ai_interface.py for natural language commands")
    print("   - Run workflows/campaign_monitoring.py for monitoring")
    
    print("\n🔧 Enterprise Features Active:")
    print("   ✅ Intelligent retry with exponential backoff")
    print("   ✅ Rate limiting with token bucket algorithm")
    print("   ✅ Circuit breaker pattern")
    print("   ✅ Professional logging with Request IDs")
    print("   ✅ Metrics collection")
    print("   ✅ Connection pooling")
    
    # Close client properly
    client.close()

if __name__ == "__main__":
    quick_start_demo()
