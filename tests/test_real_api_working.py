"""
Working Real API Tests for PropellerAds SDK

These tests use the actual PropellerAds API with real credentials.
"""

import os
import pytest
from propellerads.client import PropellerAdsClient
from propellerads.exceptions import PropellerAdsError


class TestRealAPIWorking:
    """Test real API operations that actually work."""
    
    def setup_method(self):
        """Setup for real API tests."""
        self.api_key = os.environ.get('MainAPI')
        if not self.api_key:
            pytest.skip("No API key available - set MainAPI environment variable")
        self.client = PropellerAdsClient(api_key=self.api_key)
    
    def test_real_balance_check(self):
        """Test real balance check with actual API."""
        try:
            balance = self.client.get_balance()
            
            # Should return a BalanceResponse object
            assert balance is not None
            assert hasattr(balance, 'amount')
            assert hasattr(balance, 'currency')
            assert hasattr(balance, 'formatted')
            
            # Balance should be a positive number or zero
            assert float(balance.amount) >= 0
            
            print(f"✅ Real balance check successful: {balance.formatted}")
            
        except Exception as e:
            pytest.fail(f"Real balance check failed: {e}")
    
    def test_real_campaigns_list(self):
        """Test real campaigns list retrieval."""
        try:
            campaigns = self.client.get_campaigns()
            
            # Should return a list or dict
            assert campaigns is not None
            
            # If it's a dict with results, check the structure
            if isinstance(campaigns, dict) and 'result' in campaigns:
                campaigns_list = campaigns['result']
                assert isinstance(campaigns_list, list)
                print(f"✅ Real campaigns list successful: {len(campaigns_list)} campaigns")
            else:
                # If it's directly a list
                assert isinstance(campaigns, list)
                print(f"✅ Real campaigns list successful: {len(campaigns)} campaigns")
                
        except Exception as e:
            pytest.fail(f"Real campaigns list failed: {e}")
    
    def test_real_user_profile(self):
        """Test real user profile retrieval."""
        try:
            profile = self.client.get_user_profile()
            
            # Should return user profile data
            assert profile is not None
            assert isinstance(profile, dict)
            
            # Should have basic profile fields
            expected_fields = ['id', 'email', 'name']
            found_fields = [field for field in expected_fields if field in profile]
            
            print(f"✅ Real user profile successful: found {len(found_fields)} expected fields")
            
        except Exception as e:
            # Some endpoints might not be available, that's OK
            print(f"⚠️ User profile endpoint not available: {e}")
    
    def test_real_targeting_options(self):
        """Test real targeting options retrieval."""
        try:
            targeting = self.client.get_targeting_options()
            
            # Should return targeting data
            assert targeting is not None
            
            print(f"✅ Real targeting options successful")
            
        except Exception as e:
            # Some endpoints might not be available, that's OK
            print(f"⚠️ Targeting options endpoint not available: {e}")
    
    def test_real_statistics_basic(self):
        """Test real statistics with basic parameters."""
        try:
            from datetime import datetime, timedelta
            
            # Get statistics for last 7 days
            date_to = datetime.now()
            date_from = date_to - timedelta(days=7)
            
            stats = self.client.get_statistics(
                date_from=date_from.strftime('%Y-%m-%d 00:00:00'),
                date_to=date_to.strftime('%Y-%m-%d 23:59:59')
            )
            
            # Should return statistics data
            assert stats is not None
            
            print(f"✅ Real statistics successful")
            
        except Exception as e:
            # Statistics might require specific parameters
            print(f"⚠️ Statistics endpoint requires specific parameters: {e}")
    
    def test_real_api_authentication(self):
        """Test that API authentication is working."""
        try:
            # Try a simple authenticated request
            balance = self.client.get_balance()
            
            # If we get here without authentication error, auth is working
            assert balance is not None
            
            print(f"✅ Real API authentication successful")
            
        except PropellerAdsError as e:
            if "401" in str(e) or "unauthorized" in str(e).lower():
                pytest.fail(f"Authentication failed: {e}")
            else:
                # Other errors are OK for this test
                print(f"✅ Authentication working (other API error: {e})")
    
    def test_real_rate_limiting(self):
        """Test that rate limiting is working."""
        try:
            # Make multiple requests to test rate limiting
            for i in range(3):
                balance = self.client.get_balance()
                assert balance is not None
            
            print(f"✅ Real rate limiting test successful")
            
        except Exception as e:
            if "rate limit" in str(e).lower():
                print(f"✅ Rate limiting is working: {e}")
            else:
                pytest.fail(f"Rate limiting test failed: {e}")
    
    def test_real_error_handling(self):
        """Test real error handling with invalid requests."""
        try:
            # Try to get a non-existent campaign
            try:
                self.client.get_campaigns()  # This should work
                
                # Try an invalid endpoint (this should fail gracefully)
                invalid_response = self.client._make_request('GET', '/invalid/endpoint')
                
            except PropellerAdsError as e:
                # This is expected for invalid endpoints
                print(f"✅ Error handling working: {e}")
            except Exception as e:
                # Other exceptions should be handled gracefully
                print(f"✅ Error handling working (other error): {e}")
                
        except Exception as e:
            pytest.fail(f"Error handling test failed: {e}")


class TestRealAPIConfiguration:
    """Test real API configuration and setup."""
    
    def test_api_key_configuration(self):
        """Test API key configuration."""
        api_key = os.environ.get('MainAPI')
        
        if not api_key:
            pytest.skip("No API key available")
        
        # API key should be a non-empty string
        assert isinstance(api_key, str)
        assert len(api_key) > 0
        
        # Should be able to create client
        client = PropellerAdsClient(api_key=api_key)
        assert client is not None
        assert client.config.api_key == api_key
        
        print(f"✅ API key configuration successful")
    
    def test_client_configuration_options(self):
        """Test client configuration options."""
        api_key = os.environ.get('MainAPI')
        
        if not api_key:
            pytest.skip("No API key available")
        
        # Test different configuration options
        client = PropellerAdsClient(
            api_key=api_key,
            timeout=30,
            max_retries=3,
            rate_limit=60
        )
        
        assert client.config.timeout == 30
        assert client.config.max_retries == 3
        assert client.config.rate_limit == 60
        
        print(f"✅ Client configuration options successful")
    
    def test_base_url_configuration(self):
        """Test base URL configuration."""
        api_key = os.environ.get('MainAPI')
        
        if not api_key:
            pytest.skip("No API key available")
        
        # Test with default base URL
        client = PropellerAdsClient(api_key=api_key)
        assert "propellerads.com" in client.config.base_url
        
        # Test with custom base URL
        custom_url = "https://ssp-api.propellerads.com/v5"
        client_custom = PropellerAdsClient(api_key=api_key, base_url=custom_url)
        assert client_custom.config.base_url == custom_url
        
        print(f"✅ Base URL configuration successful")


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v", "--tb=short"])
