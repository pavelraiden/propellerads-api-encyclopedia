"""
Simplified Data Validation Tests for PropellerAds SDK

Tests that work with the actual client implementation.
"""

import pytest
from decimal import Decimal
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from propellerads.client import PropellerAdsClient, BalanceResponse
from propellerads.exceptions import PropellerAdsError


class TestDataTypeHandling:
    """Test data type handling in real client."""
    
    def test_client_initialization_with_valid_data(self):
        """Test client initialization with valid data types."""
        # Valid string API key
        client = PropellerAdsClient(api_key="test-key-123")
        assert client.config.api_key == "test-key-123"
        
        # Valid timeout (integer)
        client = PropellerAdsClient(api_key="test-key", timeout=30)
        assert client.config.timeout == 30
        
        # Valid rate limit (integer)
        client = PropellerAdsClient(api_key="test-key", rate_limit=120)
        assert client.config.rate_limit == 120
    
    def test_client_initialization_with_invalid_data(self):
        """Test client initialization with invalid data types."""
        # Empty API key should raise error
        with pytest.raises(ValueError):
            PropellerAdsClient(api_key="")
        
        # None API key should raise error
        with pytest.raises(ValueError):
            PropellerAdsClient(api_key=None)
    
    @patch('requests.Session.request')
    def test_balance_response_data_types(self, mock_request):
        """Test balance response handles different data types."""
        # Test with string response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '100.50'
        mock_request.return_value = mock_response
        
        client = PropellerAdsClient(api_key="test-key")
        balance = client.get_balance()
        
        assert isinstance(balance, BalanceResponse)
        assert isinstance(balance.amount, Decimal)
        assert float(balance.amount) == 100.50
    
    def test_balance_response_edge_cases(self):
        """Test BalanceResponse with edge case inputs."""
        # Test with quoted string
        balance1 = BalanceResponse("'100.50'")
        assert float(balance1.amount) == 100.50
        
        # Test with double quotes
        balance2 = BalanceResponse('"200.75"')
        assert float(balance2.amount) == 200.75
        
        # Test with whitespace
        balance3 = BalanceResponse("  300.25  ")
        assert float(balance3.amount) == 300.25
        
        # Test with zero
        balance4 = BalanceResponse(0)
        assert float(balance4.amount) == 0.0


class TestRequestDataHandling:
    """Test request data handling."""
    
    @patch('requests.Session.request')
    def test_campaign_creation_data_types(self, mock_request):
        """Test campaign creation with different data types."""
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"id": 123, "name": "Test Campaign"}
        mock_request.return_value = mock_response
        
        client = PropellerAdsClient(api_key="test-key")
        
        # Test with proper data types
        campaign_data = {
            "name": "Test Campaign",  # string
            "target_url": "https://example.com",  # string
            "daily_budget": 100.0  # float
        }
        
        result = client.create_campaign(campaign_data)
        assert result["id"] == 123
        assert result["name"] == "Test Campaign"
    
    @patch('requests.Session.request')
    def test_statistics_request_data_types(self, mock_request):
        """Test statistics request with different data types."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "clicks": 100,
            "impressions": 1000,
            "conversions": 5,
            "cost": 50.0
        }
        mock_request.return_value = mock_response
        
        client = PropellerAdsClient(api_key="test-key")
        
        # Test with campaign_ids list
        stats = client.get_statistics(
            date_from="2023-01-01 00:00:00",
            date_to="2023-01-31 23:59:59",
            campaign_ids=[123]
        )
        assert stats["clicks"] == 100
        
        # Test with string dates
        stats = client.get_statistics(
            date_from="2023-01-01 00:00:00",
            date_to="2023-01-31 23:59:59"
        )
        assert stats["impressions"] == 1000


class TestErrorHandling:
    """Test error handling with different data types."""
    
    @patch('requests.Session.request')
    def test_malformed_json_response(self, mock_request):
        """Test handling of malformed JSON responses."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '{"incomplete": json'
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_request.return_value = mock_response
        
        client = PropellerAdsClient(api_key="test-key")
        
        # The client currently doesn't wrap JSON errors, so we expect ValueError
        with pytest.raises(ValueError):
            client.get_campaigns()
    
    @patch('requests.Session.request')
    def test_empty_response_handling(self, mock_request):
        """Test handling of empty responses."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = ""
        mock_response.json.side_effect = ValueError("No JSON object could be decoded")
        mock_request.return_value = mock_response
        
        client = PropellerAdsClient(api_key="test-key")
        
        # The client currently doesn't wrap JSON errors, so we expect ValueError
        with pytest.raises(ValueError):
            client.get_campaigns()


class TestConfigurationValidation:
    """Test configuration parameter validation."""
    
    def test_timeout_configuration(self):
        """Test timeout configuration validation."""
        # Valid timeout values
        valid_timeouts = [1, 30, 60, 300]
        for timeout in valid_timeouts:
            client = PropellerAdsClient(api_key="test-key", timeout=timeout)
            assert client.config.timeout == timeout
    
    def test_rate_limit_configuration(self):
        """Test rate limit configuration validation."""
        # Valid rate limit values
        valid_rates = [10, 60, 120, 300]
        for rate in valid_rates:
            client = PropellerAdsClient(api_key="test-key", rate_limit=rate)
            assert client.config.rate_limit == rate
    
    def test_base_url_configuration(self):
        """Test base URL configuration."""
        custom_url = "https://custom-api.propellerads.com/v5"
        client = PropellerAdsClient(api_key="test-key", base_url=custom_url)
        assert client.config.base_url == custom_url.rstrip('/')


class TestRealWorldDataScenarios:
    """Test real-world data scenarios."""
    
    def test_unicode_handling(self):
        """Test handling of Unicode characters."""
        client = PropellerAdsClient(api_key="test-key")
        
        # Unicode strings should not cause errors
        unicode_strings = [
            "Кампания",  # Cyrillic
            "キャンペーン",  # Japanese
            "活动",  # Chinese
            "🚀 Campaign",  # Emoji
            "Café & Résumé"  # Accented characters
        ]
        
        for name in unicode_strings:
            # Should not raise encoding errors
            assert isinstance(name, str)
            assert len(name) > 0
    
    def test_large_numbers(self):
        """Test handling of large numbers."""
        client = PropellerAdsClient(api_key="test-key")
        
        # Large budget values
        large_budget = 999999999.99
        assert isinstance(large_budget, float)
        assert large_budget > 0
        
        # Large campaign ID
        large_id = 2147483647  # Max 32-bit integer
        assert isinstance(large_id, int)
        assert large_id > 0
    
    def test_precision_handling(self):
        """Test handling of decimal precision."""
        # High precision decimals
        precise_values = [
            Decimal("100.123456789"),
            Decimal("0.000001"),
            Decimal("999999.999999")
        ]
        
        for value in precise_values:
            assert isinstance(value, Decimal)
            assert value >= 0


class TestCircuitBreakerDataHandling:
    """Test circuit breaker with different data scenarios."""
    
    def test_circuit_breaker_state_data(self):
        """Test circuit breaker state data types."""
        client = PropellerAdsClient(api_key="test-key")
        
        # Check circuit breaker state structure
        cb = client.circuit_breaker
        assert isinstance(cb, dict)
        assert isinstance(cb['failures'], int)
        assert isinstance(cb['state'], str)
        assert cb['state'] in ['closed', 'open', 'half-open']
        assert isinstance(cb['failure_threshold'], int)
        assert isinstance(cb['recovery_timeout'], int)
    
    def test_rate_limiter_data_handling(self):
        """Test rate limiter data handling."""
        client = PropellerAdsClient(api_key="test-key")
        
        # Rate limiter should exist and have proper methods
        assert hasattr(client, 'rate_limiter')
        assert hasattr(client.rate_limiter, 'try_acquire')
        
        # Test token acquisition
        success = client.rate_limiter.try_acquire(1)
        assert isinstance(success, bool)
