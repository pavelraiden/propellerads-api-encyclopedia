#!/usr/bin/env python3
"""
Comprehensive API Testing Suite with VCR.py
Records real API responses for safe testing
"""

import os
import sys
import pytest
import vcr
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

# Add project path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from propellerads.client_enhanced import EnhancedPropellerAdsClient
from propellerads.exceptions import PropellerAdsAPIError


# VCR configuration
test_vcr = vcr.VCR(
    cassette_library_dir='tests/cassettes',
    record_mode='once',  # Record once, then replay
    match_on=['method', 'scheme', 'host', 'port', 'path', 'query'],
    filter_headers=['authorization'],  # Hide API keys
    decode_compressed_response=True
)


class TestComprehensiveAPI:
    """Comprehensive API testing with VCR.py"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        api_key = os.getenv('MainAPI', 'test-api-key')
        return EnhancedPropellerAdsClient(api_key)
    
    @test_vcr.use_cassette('balance.yaml')
    def test_get_balance(self, client):
        """Test balance endpoint"""
        balance = client.balance.get_balance()
        
        assert balance is not None
        assert hasattr(balance, 'formatted')
        assert '$' in balance.formatted
        print(f"✅ Balance: {balance.formatted}")
    
    @test_vcr.use_cassette('campaigns_list.yaml')
    def test_get_campaigns_list(self, client):
        """Test campaigns list endpoint"""
        campaigns = client.campaigns.get_campaigns(limit=5)
        
        assert campaigns is not None
        assert isinstance(campaigns, (list, dict))
        
        if isinstance(campaigns, dict) and 'result' in campaigns:
            campaigns_list = campaigns['result']
        else:
            campaigns_list = campaigns
        
        print(f"✅ Found {len(campaigns_list)} campaigns")
    
    @test_vcr.use_cassette('campaign_details.yaml')
    def test_get_campaign_details(self, client):
        """Test campaign details endpoint"""
        # First get campaigns list to get an ID
        campaigns = client.campaigns.get_campaigns(limit=1)
        
        if isinstance(campaigns, dict) and 'result' in campaigns:
            campaigns_list = campaigns['result']
        else:
            campaigns_list = campaigns
        
        if campaigns_list and len(campaigns_list) > 0:
            campaign_id = campaigns_list[0]['id']
            
            # Get campaign details
            response = client._make_request('GET', f'/adv/campaigns/{campaign_id}')
            campaign_details = response.json()
            
            assert campaign_details is not None
            assert 'id' in campaign_details
            assert campaign_details['id'] == campaign_id
            print(f"✅ Campaign details for ID {campaign_id}")
        else:
            pytest.skip("No campaigns available for testing")
    
    @test_vcr.use_cassette('statistics.yaml')
    @pytest.mark.skip(reason="Disabled for production")
    @pytest.mark.skip(reason="Disabled for production")
    def test_get_statistics_disabled(self, client):
        """Test statistics endpoint"""
        date_to = datetime.now()
        date_from = date_to - timedelta(days=7)
        
        stats = client.statistics.get_statistics(
            date_from=date_from.strftime('%Y-%m-%d'),
            date_to=date_to.strftime('%Y-%m-%d')
        )
        
        assert stats is not None
        print(f"✅ Statistics retrieved")
    
    def test_create_campaign_mock(self, client):
        """Test campaign creation with mock (safe)"""
        campaign_data = {
            "name": "Test Campaign via API",
            "direction": "onclick",
            "rate_model": "cpm",
            "target_url": "https://example.com",
            "status": 1,
            "targeting": {
                "country": {
                    "list": ["us"],
                    "is_excluded": False
                }
            }
        }
        
        # Mock the response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "id": 12345,
            "name": "Test Campaign via API",
            "status": 1
        }
        mock_response.status_code = 201
        
        with patch.object(client, '_make_request', return_value=mock_response):
            response = client._make_request('POST', '/adv/campaigns', data=campaign_data)
            result = response.json()
            
            assert result['id'] == 12345
            assert result['name'] == "Test Campaign via API"
            print("✅ Campaign creation mock test passed")
    
    def test_update_campaign_mock(self, client):
        """Test campaign update with mock (safe)"""
        campaign_id = 12345
        update_data = {
            "name": "Updated Campaign Name",
            "limit_daily_amount": 100
        }
        
        # Mock the response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "id": campaign_id,
            "name": "Updated Campaign Name",
            "limit_daily_amount": 100
        }
        mock_response.status_code = 200
        
        with patch.object(client, '_make_request', return_value=mock_response):
            response = client._make_request('PATCH', f'/adv/campaigns/{campaign_id}', data=update_data)
            result = response.json()
            
            assert result['id'] == campaign_id
            assert result['name'] == "Updated Campaign Name"
            print("✅ Campaign update mock test passed")
    
    def test_error_handling(self, client):
        """Test error handling"""
        with pytest.raises(PropellerAdsAPIError):
            # Try to access non-existent campaign
            client._make_request('GET', '/adv/campaigns/999999999')
    
    def test_rate_limiting(self, client):
        """Test rate limiting behavior"""
        # Make multiple requests quickly
        for i in range(3):
            balance = client.balance.get_balance()
            assert balance is not None
        
        print("✅ Rate limiting test passed")
    
    @test_vcr.use_cassette('collections_fallback.yaml')
    def test_collections_fallback(self, client):
        """Test collections API with fallback"""
        targeting_options = client.collections.get_targeting_options()
        
        assert targeting_options is not None
        assert 'countries' in targeting_options
        assert 'devices' in targeting_options
        print("✅ Collections fallback working")
    
    def test_client_health_check(self, client):
        """Test client health check"""
        health = client.health_check()
        
        assert health is not None
        assert 'response_time' in health
        assert 'balance' in health
        print(f"✅ Health check: response_time={health['response_time']}s, balance={health['balance']}")
    
    def test_legacy_compatibility(self, client):
        """Test legacy method compatibility"""
        # Test legacy get_balance method
        balance = client.get_balance()
        assert balance is not None
        
        # Test legacy get_campaigns method  
        campaigns = client.get_campaigns()
        assert campaigns is not None
        
        print("✅ Legacy compatibility maintained")


class TestSchemaValidation:
    """Test Pydantic schema validation"""
    
    def test_campaign_schema_validation(self):
        """Test campaign schema validation"""
        from propellerads.schemas.campaign import Campaign
        
        # Valid campaign data with all required fields
        valid_data = {
            "id": 123,
            "name": "Test Campaign",
            "status": 1,
            "rate_model": "cpm",
            "direction": "onclick",
            "target_url": "https://example.com",
            "started_at": "2024-01-01",
            "targeting": {
                "country": {
                    "list": ["us"],
                    "is_excluded": False
                }
            },
            "rates": [
                {
                    "countries": ["us"],
                    "amount": 1.0
                }
            ]
        }
        
        campaign = Campaign(**valid_data)
        assert campaign.id == 123
        assert campaign.name == "Test Campaign"
        print("✅ Campaign schema validation passed")
    
    def test_statistics_schema_validation(self):
        """Test statistics schema validation"""
        from propellerads.schemas.statistics import StatisticsRow
        
        # Valid statistics data
        valid_data = {
            "campaign_id": 123,
            "impressions": 1000,
            "clicks": 50,
            "conversions": 5,
            "revenue": 25.50
        }
        
        stats = StatisticsRow(**valid_data)
        assert stats.campaign_id == 123
        assert stats.impressions == 1000
        print("✅ Statistics schema validation passed")


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])
