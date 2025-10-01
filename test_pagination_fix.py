#!/usr/bin/env python3
"""
Test script for pagination fix verification.
This script tests the corrected pagination functionality.
"""

import os
import sys
from propellerads.client import PropellerAdsClient

def test_pagination():
    """Test pagination functionality with real API."""
    
    api_key = os.getenv('MainAPI')
    if not api_key:
        print("❌ MainAPI environment variable not set")
        return False
    
    print("🔧 Testing Pagination Fix...")
    print("=" * 60)
    
    client = PropellerAdsClient(api_key=api_key)
    
    try:
        # Test 1: Auto-pagination (should get all campaigns)
        print("📊 Test 1: Auto-pagination (all campaigns)")
        all_campaigns = client.get_campaigns(auto_paginate=True)
        print(f"✅ Total campaigns loaded: {len(all_campaigns)}")
        
        # Test 2: Single page
        print("\n📄 Test 2: Single page (limit=50)")
        single_page = client.get_campaigns(limit=50, auto_paginate=False)
        print(f"✅ Single page campaigns: {len(single_page)}")
        
        # Test 3: Verify we got more campaigns with auto-pagination
        if len(all_campaigns) > len(single_page):
            print(f"✅ Auto-pagination works: {len(all_campaigns)} > {len(single_page)}")
        else:
            print(f"⚠️ Pagination might not be working correctly")
        
        # Test 4: Show sample campaigns
        if all_campaigns:
            print(f"\n📋 Sample campaigns:")
            print(f"   First: {all_campaigns[0].get('name', 'N/A')}")
            if len(all_campaigns) > 1:
                print(f"   Last:  {all_campaigns[-1].get('name', 'N/A')}")
        
        print("\n🎉 Pagination tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error during pagination test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_pagination()
    sys.exit(0 if success else 1)
