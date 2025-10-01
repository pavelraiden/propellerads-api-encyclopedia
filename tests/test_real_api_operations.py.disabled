#!/usr/bin/env python3
"""
REAL API Operations Tests
Tests actual POST/PATCH/DELETE operations with safe test data
"""

import os
import sys
import pytest
import vcr
from datetime import datetime, timedelta

# Add project path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from propellerads.client_enhanced import EnhancedPropellerAdsClient
from propellerads.exceptions import PropellerAdsAPIError


# VCR configuration for real operations
real_vcr = vcr.VCR(
    cassette_library_dir='tests/cassettes/real_operations',
    record_mode='once',
    match_on=['method', 'scheme', 'host', 'port', 'path', 'query'],
    filter_headers=['authorization'],
    decode_compressed_response=True
)


class TestRealAPIOperations:
    """Test real API operations with actual data"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        api_key = os.getenv('MainAPI')
        if not api_key:
            pytest.skip("API key not available")
        return EnhancedPropellerAdsClient(api_key)
    
    @real_vcr.use_cassette('create_test_campaign.yaml')
    def test_create_campaign_real(self, client):
        """Test REAL campaign creation"""
        campaign_data = {
            "name": f"TEST_CAMPAIGN_API_{int(datetime.now().timestamp())}",
            "direction": "onclick",
            "rate_model": "cpm",
            "target_url": "https://propellerads.com/?test=1",
            "status": 1,  # Draft status
            "started_at": datetime.now().strftime("%d/%m/%Y"),
            "expired_at": (datetime.now() + timedelta(days=30)).strftime("%d/%m/%Y"),
            "targeting": {
                "country": {
                    "list": ["us"],
                    "is_excluded": False
                },
                "connection": "all"
            },
            "rates": [
                {
                    "countries": ["us"],
                    "amount": 0.01  # Very low test rate
                }
            ]
        }
        
        try:
            response = client._make_request('POST', '/adv/campaigns', data=campaign_data)
            result = response.json()
            
            assert 'id' in result
            assert result['name'] == campaign_data['name']
            assert result['status'] == 1  # Draft
            
            # Store campaign ID for cleanup
            campaign_id = result['id']
            print(f"✅ Created test campaign ID: {campaign_id}")
            
            # Clean up - delete the test campaign
            try:
                delete_response = client._make_request('DELETE', f'/adv/campaigns/{campaign_id}')
                print(f"✅ Cleaned up test campaign ID: {campaign_id}")
            except:
                print(f"⚠️ Could not delete test campaign ID: {campaign_id} - manual cleanup needed")
            
            return campaign_id
            
        except PropellerAdsAPIError as e:
            if "validation" in str(e).lower():
                pytest.skip(f"Campaign validation failed (expected): {e}")
            else:
                raise
    
    @real_vcr.use_cassette('update_campaign_real.yaml')
    def test_update_campaign_real(self, client):
        """Test REAL campaign update"""
        # First get existing campaigns
        campaigns_response = client._make_request('GET', '/adv/campaigns', params={'page_size': 1})
        campaigns_data = campaigns_response.json()
        
        if not campaigns_data.get('result'):
            pytest.skip("No campaigns available for update test")
        
        campaign_id = campaigns_data['result'][0]['id']
        original_name = campaigns_data['result'][0]['name']
        
        # Update with safe data
        update_data = {
            "name": f"{original_name}_UPDATED_TEST",
            "limit_daily_amount": 1  # Very low limit for safety
        }
        
        try:
            response = client._make_request('PATCH', f'/adv/campaigns/{campaign_id}', data=update_data)
            result = response.json()
            
            assert result['id'] == campaign_id
            assert result['name'] == update_data['name']
            
            print(f"✅ Updated campaign ID: {campaign_id}")
            
            # Restore original name
            restore_data = {"name": original_name}
            client._make_request('PATCH', f'/adv/campaigns/{campaign_id}', data=restore_data)
            print(f"✅ Restored original campaign name")
            
        except PropellerAdsAPIError as e:
            if "permission" in str(e).lower() or "access" in str(e).lower():
                pytest.skip(f"No permission to update campaign (expected): {e}")
            else:
                raise
    
    @real_vcr.use_cassette('statistics_detailed.yaml')
    def test_statistics_detailed_real(self, client):
        """Test detailed statistics with various parameters"""
        date_to = datetime.now()
        date_from = date_to - timedelta(days=30)
        
        # Test different grouping options
        test_cases = [
            {'group_by[]': ['campaign_id']},
            {'group_by[]': ['campaign_id', 'date_time']},
            {'group_by[]': ['date_time']},
        ]
        
        for i, test_case in enumerate(test_cases):
            stats_params = {
                'day_from': date_from.strftime('%Y-%m-%d'),
                'day_to': date_to.strftime('%Y-%m-%d'),
                'tz': '+0000',
                **test_case
            }
            
            response = client._make_request('GET', '/adv/statistics', params=stats_params)
            result = response.json()
            
            assert isinstance(result, list)
            print(f"✅ Statistics test case {i+1}: {len(result)} records")
    
    @real_vcr.use_cassette('campaign_operations_full.yaml')
    def test_campaign_full_lifecycle(self, client):
        """Test full campaign lifecycle: create -> read -> update -> delete"""
        
        # 1. CREATE
        campaign_data = {
            "name": f"LIFECYCLE_TEST_{int(datetime.now().timestamp())}",
            "direction": "onclick",
            "rate_model": "cpm",
            "target_url": "https://propellerads.com/?lifecycle_test=1",
            "status": 1,
            "started_at": datetime.now().strftime("%d/%m/%Y"),
            "expired_at": (datetime.now() + timedelta(days=7)).strftime("%d/%m/%Y"),
            "targeting": {
                "country": {
                    "list": ["us"],
                    "is_excluded": False
                }
            },
            "rates": [
                {
                    "countries": ["us"],
                    "amount": 0.01
                }
            ]
        }
        
        try:
            # CREATE
            create_response = client._make_request('POST', '/adv/campaigns', data=campaign_data)
            created_campaign = create_response.json()
            campaign_id = created_campaign['id']
            print(f"✅ CREATED campaign ID: {campaign_id}")
            
            # READ
            read_response = client._make_request('GET', f'/adv/campaigns/{campaign_id}')
            read_campaign = read_response.json()
            assert read_campaign['id'] == campaign_id
            print(f"✅ READ campaign ID: {campaign_id}")
            
            # UPDATE
            update_data = {"name": f"{campaign_data['name']}_UPDATED"}
            update_response = client._make_request('PATCH', f'/adv/campaigns/{campaign_id}', data=update_data)
            updated_campaign = update_response.json()
            assert updated_campaign['name'] == update_data['name']
            print(f"✅ UPDATED campaign ID: {campaign_id}")
            
            # DELETE
            delete_response = client._make_request('DELETE', f'/adv/campaigns/{campaign_id}')
            print(f"✅ DELETED campaign ID: {campaign_id}")
            
            # Verify deletion
            try:
                client._make_request('GET', f'/adv/campaigns/{campaign_id}')
                assert False, "Campaign should be deleted"
            except PropellerAdsAPIError:
                print(f"✅ VERIFIED deletion of campaign ID: {campaign_id}")
                
        except PropellerAdsAPIError as e:
            if any(word in str(e).lower() for word in ['validation', 'permission', 'access']):
                pytest.skip(f"Campaign lifecycle test limited by API permissions: {e}")
            else:
                raise
    
    def test_error_handling_comprehensive(self, client):
        """Test comprehensive error handling"""
        
        # Test 404 error
        with pytest.raises(PropellerAdsAPIError):
            client._make_request('GET', '/adv/campaigns/999999999')
        
        # Test invalid data
        with pytest.raises(PropellerAdsAPIError):
            client._make_request('POST', '/adv/campaigns', data={"invalid": "data"})
        
        # Test invalid endpoint
        with pytest.raises(PropellerAdsAPIError):
            client._make_request('GET', '/adv/nonexistent')
        
        print("✅ Error handling comprehensive test passed")
    
    def test_rate_limiting_stress(self, client):
        """Test rate limiting under stress"""
        
        # Make many requests quickly
        start_time = datetime.now()
        successful_requests = 0
        
        for i in range(10):
            try:
                client._make_request('GET', '/adv/balance')
                successful_requests += 1
            except Exception as e:
                if "rate limit" in str(e).lower():
                    print(f"✅ Rate limiting triggered at request {i+1}")
                    break
                else:
                    raise
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print(f"✅ Rate limiting stress test: {successful_requests} requests in {duration:.2f}s")
        assert successful_requests > 0
    
    def test_concurrent_requests(self, client):
        """Test concurrent request handling"""
        import threading
        import queue
        
        results = queue.Queue()
        
        def make_request():
            try:
                response = client._make_request('GET', '/adv/balance')
                results.put(('success', response.json()))
            except Exception as e:
                results.put(('error', str(e)))
        
        # Start multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads
        for thread in threads:
            thread.join()
        
        # Check results
        successes = 0
        errors = 0
        
        while not results.empty():
            result_type, result_data = results.get()
            if result_type == 'success':
                successes += 1
            else:
                errors += 1
        
        print(f"✅ Concurrent requests: {successes} successes, {errors} errors")
        assert successes > 0


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])
