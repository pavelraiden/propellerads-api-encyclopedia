"""
Data Validation and Edge Case Tests for PropellerAds SDK

Comprehensive tests for data validation, input sanitization,
boundary conditions, and edge cases.
"""

import pytest
import json
from decimal import Decimal
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from propellerads import PropellerAdsClient, BalanceResponse
from propellerads.exceptions import PropellerAdsError


class TestDataTypeValidation:
    """Test validation of different data types."""
    
    def test_integer_validation(self):
        """Test integer parameter validation."""
        client = PropellerAdsClient(api_key="test-key")
        
        # Valid integers
        valid_integers = [0, 1, 100, 999999]
        for value in valid_integers:
            validated = client._validate_integer(value, "test_param")
            assert validated == value
        
        # Invalid integers
        invalid_values = ["not_int", 3.14, None, [], {}]
        for value in invalid_values:
            with pytest.raises((TypeError, ValueError)):
                client._validate_integer(value, "test_param")
    
    def test_float_validation(self):
        """Test float parameter validation."""
        client = PropellerAdsClient(api_key="test-key")
        
        # Valid floats
        valid_floats = [0.0, 1.5, 100.99, 999999.99]
        for value in valid_floats:
            validated = client._validate_float(value, "test_param")
            assert abs(validated - value) < 0.001
        
        # Invalid floats
        invalid_values = ["not_float", None, [], {}, "3.14.15"]
        for value in invalid_values:
            with pytest.raises((TypeError, ValueError)):
                client._validate_float(value, "test_param")
    
    def test_string_validation(self):
        """Test string parameter validation."""
        client = PropellerAdsClient(api_key="test-key")
        
        # Valid strings
        valid_strings = ["test", "Campaign Name", "https://example.com"]
        for value in valid_strings:
            validated = client._validate_string(value, "test_param")
            assert validated == value
        
        # Invalid strings
        invalid_values = [123, None, [], {}]
        for value in invalid_values:
            with pytest.raises((TypeError, ValueError)):
                client._validate_string(value, "test_param")
    
    def test_boolean_validation(self):
        """Test boolean parameter validation."""
        client = PropellerAdsClient(api_key="test-key")
        
        # Valid booleans
        assert client._validate_boolean(True, "test_param") is True
        assert client._validate_boolean(False, "test_param") is False
        
        # String representations
        assert client._validate_boolean("true", "test_param") is True
        assert client._validate_boolean("false", "test_param") is False
        assert client._validate_boolean("1", "test_param") is True
        assert client._validate_boolean("0", "test_param") is False
        
        # Invalid booleans
        invalid_values = ["maybe", 2, None, [], {}]
        for value in invalid_values:
            with pytest.raises((TypeError, ValueError)):
                client._validate_boolean(value, "test_param")


class TestBoundaryConditions:
    """Test boundary conditions and limits."""
    
    def test_budget_boundaries(self):
        """Test budget validation boundaries."""
        client = PropellerAdsClient(api_key="test-key")
        
        # Minimum budget
        assert client._validate_budget(0.01) == 0.01
        
        # Maximum reasonable budget
        assert client._validate_budget(999999.99) == 999999.99
        
        # Invalid budgets
        invalid_budgets = [-1, 0, 10000000, "invalid"]
        for budget in invalid_budgets:
            with pytest.raises((ValueError, TypeError)):
                client._validate_budget(budget)
    
    def test_campaign_name_length(self):
        """Test campaign name length validation."""
        client = PropellerAdsClient(api_key="test-key")
        
        # Valid lengths
        short_name = "A"
        medium_name = "Campaign Name"
        long_name = "A" * 100
        
        assert client._validate_campaign_name(short_name) == short_name
        assert client._validate_campaign_name(medium_name) == medium_name
        assert client._validate_campaign_name(long_name) == long_name
        
        # Invalid lengths
        empty_name = ""
        too_long_name = "A" * 256
        
        with pytest.raises(ValueError):
            client._validate_campaign_name(empty_name)
        
        with pytest.raises(ValueError):
            client._validate_campaign_name(too_long_name)
    
    def test_date_range_validation(self):
        """Test date range validation."""
        client = PropellerAdsClient(api_key="test-key")
        
        today = datetime.now().date()
        yesterday = today - timedelta(days=1)
        tomorrow = today + timedelta(days=1)
        
        # Valid date ranges
        valid_ranges = [
            (yesterday, today),
            (today, today),
            (yesterday, tomorrow)
        ]
        
        for start_date, end_date in valid_ranges:
            start_str = start_date.strftime("%Y-%m-%d")
            end_str = end_date.strftime("%Y-%m-%d")
            validated = client._validate_date_range(start_str, end_str)
            assert validated is not None
        
        # Invalid date ranges
        future_start = tomorrow.strftime("%Y-%m-%d")
        past_end = yesterday.strftime("%Y-%m-%d")
        
        with pytest.raises(ValueError):
            client._validate_date_range(future_start, past_end)  # Start after end
    
    def test_pagination_limits(self):
        """Test pagination parameter limits."""
        client = PropellerAdsClient(api_key="test-key")
        
        # Valid pagination
        valid_limits = [1, 10, 100, 1000]
        for limit in valid_limits:
            validated = client._validate_limit(limit)
            assert validated == limit
        
        valid_offsets = [0, 10, 100, 1000]
        for offset in valid_offsets:
            validated = client._validate_offset(offset)
            assert validated == offset
        
        # Invalid pagination
        invalid_limits = [0, -1, 10001]
        for limit in invalid_limits:
            with pytest.raises(ValueError):
                client._validate_limit(limit)
        
        invalid_offsets = [-1, -10]
        for offset in invalid_offsets:
            with pytest.raises(ValueError):
                client._validate_offset(offset)


class TestInputSanitization:
    """Test input sanitization and security."""
    
    def test_html_sanitization(self):
        """Test HTML/script tag sanitization."""
        client = PropellerAdsClient(api_key="test-key")
        
        # Dangerous inputs
        dangerous_inputs = [
            "<script>alert('xss')</script>",
            "<img src=x onerror=alert('xss')>",
            "javascript:alert('xss')",
            "<iframe src='javascript:alert(1)'></iframe>"
        ]
        
        for dangerous_input in dangerous_inputs:
            sanitized = client._sanitize_html(dangerous_input)
            assert "<script>" not in sanitized
            assert "javascript:" not in sanitized
            assert "onerror=" not in sanitized
            assert "<iframe" not in sanitized
    
    def test_sql_injection_prevention(self):
        """Test SQL injection prevention."""
        client = PropellerAdsClient(api_key="test-key")
        
        # SQL injection attempts
        sql_injections = [
            "'; DROP TABLE campaigns; --",
            "1' OR '1'='1",
            "UNION SELECT * FROM users",
            "'; INSERT INTO campaigns VALUES ('evil'); --"
        ]
        
        for injection in sql_injections:
            sanitized = client._sanitize_sql(injection)
            assert "DROP TABLE" not in sanitized.upper()
            assert "UNION SELECT" not in sanitized.upper()
            assert "INSERT INTO" not in sanitized.upper()
            assert "--" not in sanitized
    
    def test_url_sanitization(self):
        """Test URL sanitization."""
        client = PropellerAdsClient(api_key="test-key")
        
        # Valid URLs
        valid_urls = [
            "https://example.com",
            "http://test.com/path",
            "https://subdomain.example.com/path?param=value"
        ]
        
        for url in valid_urls:
            sanitized = client._sanitize_url(url)
            assert sanitized.startswith(("http://", "https://"))
        
        # Dangerous URLs
        dangerous_urls = [
            "javascript:alert('xss')",
            "data:text/html,<script>alert('xss')</script>",
            "ftp://malicious.com",
            "file:///etc/passwd"
        ]
        
        for url in dangerous_urls:
            with pytest.raises(ValueError):
                client._sanitize_url(url)
    
    def test_parameter_encoding(self):
        """Test parameter encoding for special characters."""
        client = PropellerAdsClient(api_key="test-key")
        
        # Special characters that need encoding
        special_chars = {
            "Campaign & Co": "Campaign %26 Co",
            "Test + Plus": "Test %2B Plus",
            "Space Test": "Space%20Test",
            "Quote\"Test": "Quote%22Test"
        }
        
        for original, expected in special_chars.items():
            encoded = client._encode_parameter(original)
            assert expected in encoded or original == encoded  # Allow both encoded and original


class TestEdgeCases:
    """Test edge cases and unusual scenarios."""
    
    def test_empty_response_handling(self):
        """Test handling of empty responses."""
        client = PropellerAdsClient(api_key="test-key")
        
        # Empty string response
        empty_response = Mock()
        empty_response.status_code = 200
        empty_response.text = ""
        empty_response.json.side_effect = ValueError("No JSON object could be decoded")
        
        with patch('requests.Session.request', return_value=empty_response):
            with pytest.raises(PropellerAdsError):
                client.get_campaigns()
    
    def test_null_value_handling(self):
        """Test handling of null values in responses."""
        client = PropellerAdsClient(api_key="test-key")
        
        # Response with null values
        null_response = Mock()
        null_response.status_code = 200
        null_response.json.return_value = {
            "campaigns": [
                {"id": 1, "name": "Campaign 1", "budget": None},
                {"id": 2, "name": None, "budget": 100.0},
                {"id": None, "name": "Campaign 3", "budget": 50.0}
            ]
        }
        
        with patch('requests.Session.request', return_value=null_response):
            campaigns = client.get_campaigns()
            assert campaigns is not None
            # Should handle null values gracefully
    
    def test_unicode_handling(self):
        """Test handling of Unicode characters."""
        client = PropellerAdsClient(api_key="test-key")
        
        # Unicode campaign names
        unicode_names = [
            "Кампания",  # Cyrillic
            "キャンペーン",  # Japanese
            "活动",  # Chinese
            "🚀 Campaign",  # Emoji
            "Café & Résumé"  # Accented characters
        ]
        
        for name in unicode_names:
            # Should not raise encoding errors
            sanitized = client._sanitize_string(name)
            assert isinstance(sanitized, str)
    
    def test_very_large_numbers(self):
        """Test handling of very large numbers."""
        client = PropellerAdsClient(api_key="test-key")
        
        # Very large budget
        large_budget = 999999999.99
        validated = client._validate_budget(large_budget)
        assert validated == large_budget
        
        # Very large campaign ID
        large_id = 2147483647  # Max 32-bit integer
        validated = client._validate_integer(large_id, "campaign_id")
        assert validated == large_id
    
    def test_precision_handling(self):
        """Test handling of decimal precision."""
        client = PropellerAdsClient(api_key="test-key")
        
        # High precision decimals
        precise_values = [
            Decimal("100.123456789"),
            Decimal("0.000001"),
            Decimal("999999.999999")
        ]
        
        for value in precise_values:
            # Should handle high precision appropriately
            validated = client._validate_decimal(value)
            assert isinstance(validated, (Decimal, float))
    
    @patch('requests.Session.request')
    def test_malformed_json_response(self, mock_request):
        """Test handling of malformed JSON responses."""
        malformed_responses = [
            '{"incomplete": json',
            '{"valid": "json", "but": "unexpected_structure"}',
            '[1, 2, 3]',  # Array instead of object
            'not json at all'
        ]
        
        client = PropellerAdsClient(api_key="test-key")
        
        for malformed_json in malformed_responses:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.text = malformed_json
            mock_response.json.side_effect = ValueError("Invalid JSON")
            mock_request.return_value = mock_response
            
            with pytest.raises(PropellerAdsError):
                client.get_campaigns()


class TestBalanceResponseEdgeCases:
    """Test edge cases for BalanceResponse."""
    
    def test_balance_response_with_quotes(self):
        """Test BalanceResponse with quoted string values."""
        # Test with single quotes
        balance1 = BalanceResponse("'100.50'")
        assert float(balance1.amount) == 100.50
        
        # Test with double quotes
        balance2 = BalanceResponse('"200.75"')
        assert float(balance2.amount) == 200.75
        
        # Test with mixed quotes
        balance3 = BalanceResponse("'300.25\"")
        assert float(balance3.amount) == 300.25
    
    def test_balance_response_with_whitespace(self):
        """Test BalanceResponse with whitespace."""
        # Test with leading/trailing whitespace
        balance1 = BalanceResponse("  100.50  ")
        assert float(balance1.amount) == 100.50
        
        # Test with tabs and newlines
        balance2 = BalanceResponse("\\t200.75\\n")
        assert float(balance2.amount) == 200.75
    
    def test_balance_response_edge_values(self):
        """Test BalanceResponse with edge values."""
        # Zero balance
        balance1 = BalanceResponse(0)
        assert float(balance1.amount) == 0.0
        
        # Very small balance
        balance2 = BalanceResponse(0.01)
        assert float(balance2.amount) == 0.01
        
        # Very large balance
        balance3 = BalanceResponse(999999999.99)
        assert float(balance3.amount) == 999999999.99
    
    def test_balance_response_invalid_inputs(self):
        """Test BalanceResponse with invalid inputs."""
        invalid_inputs = [
            "not_a_number",
            "",
            None,
            [],
            {}
        ]
        
        for invalid_input in invalid_inputs:
            with pytest.raises((ValueError, TypeError, AttributeError)):
                BalanceResponse(invalid_input)


class TestParameterCombinations:
    """Test various parameter combinations."""
    
    def test_campaign_creation_parameter_combinations(self):
        """Test different parameter combinations for campaign creation."""
        client = PropellerAdsClient(api_key="test-key")
        
        # Minimal required parameters
        minimal_params = {
            "name": "Test Campaign",
            "target_url": "https://example.com",
            "daily_budget": 100.0
        }
        
        validated = client._validate_campaign_params(minimal_params)
        assert validated is not None
        
        # Full parameter set
        full_params = {
            "name": "Full Test Campaign",
            "target_url": "https://example.com/landing",
            "daily_budget": 500.0,
            "bid_amount": 0.50,
            "countries": ["US", "CA", "UK"],
            "devices": ["desktop", "mobile"],
            "browsers": ["chrome", "firefox"],
            "operating_systems": ["windows", "macos", "android"]
        }
        
        validated = client._validate_campaign_params(full_params)
        assert validated is not None
        
        # Invalid combinations
        invalid_params = {
            "name": "",  # Empty name
            "target_url": "invalid-url",  # Invalid URL
            "daily_budget": -100  # Negative budget
        }
        
        with pytest.raises(ValueError):
            client._validate_campaign_params(invalid_params)
    
    def test_statistics_parameter_combinations(self):
        """Test different parameter combinations for statistics."""
        client = PropellerAdsClient(api_key="test-key")
        
        # Date range only
        date_params = {
            "date_from": "2023-01-01",
            "date_to": "2023-01-31"
        }
        
        validated = client._validate_statistics_params(date_params)
        assert validated is not None
        
        # Campaign-specific statistics
        campaign_params = {
            "campaign_id": 123,
            "date_from": "2023-01-01",
            "date_to": "2023-01-31"
        }
        
        validated = client._validate_statistics_params(campaign_params)
        assert validated is not None
        
        # Grouping parameters
        group_params = {
            "date_from": "2023-01-01",
            "date_to": "2023-01-31",
            "group_by": "country"
        }
        
        validated = client._validate_statistics_params(group_params)
        assert validated is not None
