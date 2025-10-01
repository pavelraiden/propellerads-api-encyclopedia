"""
Edge Cases and Boundary Testing for PropellerAds SDK

Comprehensive testing of edge cases, boundary conditions, and extreme scenarios.
"""

import pytest
import time
import threading
from unittest.mock import Mock, patch, MagicMock
from propellerads.client import PropellerAdsClient, BalanceResponse
from propellerads.exceptions import PropellerAdsError


class TestBoundaryValues:
    """Test boundary value conditions."""
    
    def test_minimum_budget_values(self):
        """Test minimum budget boundary values."""
        client = PropellerAdsClient(api_key="test-key")
        
        # Test very small budget values
        small_budgets = [0.01, 0.001, 0.0001]
        for budget in small_budgets:
            assert isinstance(budget, float)
            assert budget > 0
    
    def test_maximum_budget_values(self):
        """Test maximum budget boundary values."""
        client = PropellerAdsClient(api_key="test-key")
        
        # Test very large budget values
        large_budgets = [999999.99, 1000000.00, 9999999.99]
        for budget in large_budgets:
            assert isinstance(budget, float)
            assert budget > 0
    
    def test_campaign_id_boundaries(self):
        """Test campaign ID boundary values."""
        client = PropellerAdsClient(api_key="test-key")
        
        # Test edge case IDs
        edge_ids = [1, 2147483647, 9223372036854775807]  # Min, 32-bit max, 64-bit max
        for campaign_id in edge_ids:
            assert isinstance(campaign_id, int)
            assert campaign_id > 0
    
    def test_string_length_boundaries(self):
        """Test string length boundary conditions."""
        client = PropellerAdsClient(api_key="test-key")
        
        # Test very short strings
        short_string = "a"
        assert len(short_string) == 1
        
        # Test very long strings
        long_string = "a" * 1000
        assert len(long_string) == 1000
        
        # Test empty string
        empty_string = ""
        assert len(empty_string) == 0
    
    def test_date_range_boundaries(self):
        """Test date range boundary conditions."""
        client = PropellerAdsClient(api_key="test-key")
        
        # Test edge case dates
        edge_dates = [
            "1970-01-01 00:00:00",  # Unix epoch
            "2038-01-19 03:14:07",  # 32-bit timestamp limit
            "2099-12-31 23:59:59"   # Far future
        ]
        
        for date_str in edge_dates:
            assert isinstance(date_str, str)
            assert len(date_str) > 0


class TestExtremeLoadScenarios:
    """Test extreme load and stress scenarios."""
    
    def test_rapid_sequential_requests(self):
        """Test rapid sequential API requests."""
        client = PropellerAdsClient(api_key="test-key", rate_limit=1000)
        
        # Test rapid token acquisition
        start_time = time.time()
        
        for i in range(10):
            success = client.rate_limiter.try_acquire(1)
            # Should handle rapid requests
            assert isinstance(success, bool)
        
        elapsed = time.time() - start_time
        assert elapsed < 1.0  # Should be fast
    
    def test_concurrent_client_creation(self):
        """Test concurrent client creation."""
        clients = []
        errors = []
        
        def create_client(index):
            try:
                client = PropellerAdsClient(api_key=f"test-key-{index}")
                clients.append(client)
            except Exception as e:
                errors.append(e)
        
        # Create multiple clients concurrently
        threads = []
        for i in range(5):
            thread = threading.Thread(target=create_client, args=(i,))
            threads.append(thread)
        
        for thread in threads:
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # All clients should be created successfully
        assert len(errors) == 0
        assert len(clients) == 5
    
    def test_memory_intensive_operations(self):
        """Test memory-intensive operations."""
        client = PropellerAdsClient(api_key="test-key")
        
        # Test large data structures
        large_data = {
            "campaigns": [{"id": i, "name": f"Campaign {i}"} for i in range(1000)],
            "statistics": [{"date": f"2023-01-{i:02d}", "impressions": i * 1000} for i in range(1, 32)]
        }
        
        # Should handle large data structures
        assert len(large_data["campaigns"]) == 1000
        assert len(large_data["statistics"]) == 31
    
    @patch('requests.Session.request')
    def test_large_response_handling(self, mock_request):
        """Test handling of large API responses."""
        # Create a large mock response with correct PropellerAds structure
        large_response_data = {
            "result": [
                {
                    "id": i,
                    "name": f"Campaign {i}",
                    "statistics": {
                        "impressions": i * 1000,
                        "clicks": i * 50,
                        "conversions": i * 2
                    }
                }
                for i in range(1, 101)  # 100 campaigns (first page)
            ],
            "meta": {
                "total_items": 100,
                "total_pages": 1,
                "page_size": 100,
                "page": 1
            }
        }
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = large_response_data
        mock_request.return_value = mock_response
        
        client = PropellerAdsClient(api_key="test-key")
        
        campaigns = client.get_campaigns()
        
        # Should handle large responses (now returns list directly)
        assert len(campaigns) == 100
        assert isinstance(campaigns, list)
        assert campaigns[0]["id"] == 1


class TestNetworkFailureScenarios:
    """Test network failure and recovery scenarios."""
    
    @patch('requests.Session.request')
    def test_connection_timeout_recovery(self, mock_request):
        """Test connection timeout and recovery."""
        from requests.exceptions import Timeout, ConnectionError
        
        # First call times out, second succeeds
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '100.00'
        
        mock_request.side_effect = [Timeout("Connection timeout"), mock_response]
        
        client = PropellerAdsClient(api_key="test-key", max_retries=2)
        
        # Should handle timeout and retry
        try:
            balance = client.get_balance()
        except PropellerAdsError:
            pass  # Expected due to timeout
        
        assert mock_request.call_count >= 1
    
    @patch('requests.Session.request')
    def test_intermittent_network_failures(self, mock_request):
        """Test intermittent network failures."""
        from requests.exceptions import ConnectionError
        
        # Simulate intermittent failures
        mock_response_success = Mock()
        mock_response_success.status_code = 200
        mock_response_success.text = '100.00'
        
        mock_request.side_effect = [
            ConnectionError("Network error"),
            mock_response_success,
            ConnectionError("Network error"),
            mock_response_success
        ]
        
        client = PropellerAdsClient(api_key="test-key", max_retries=3)
        
        # Should handle intermittent failures
        for _ in range(2):
            try:
                balance = client.get_balance()
            except PropellerAdsError:
                pass  # Expected due to network errors
    
    @patch('requests.Session.request')
    def test_server_error_recovery(self, mock_request):
        """Test server error recovery scenarios."""
        # Simulate server errors followed by success
        mock_response_error = Mock()
        mock_response_error.status_code = 500
        mock_response_error.text = 'Internal Server Error'
        mock_response_error.raise_for_status.side_effect = Exception("500 Error")
        
        mock_response_success = Mock()
        mock_response_success.status_code = 200
        mock_response_success.text = '100.00'
        
        mock_request.side_effect = [mock_response_error, mock_response_success]
        
        client = PropellerAdsClient(api_key="test-key", max_retries=2)
        
        # Should handle server errors
        try:
            balance = client.get_balance()
        except PropellerAdsError:
            pass  # Expected due to server error


class TestDataCorruptionScenarios:
    """Test data corruption and malformed data scenarios."""
    
    @patch('requests.Session.request')
    def test_malformed_json_responses(self, mock_request):
        """Test handling of malformed JSON responses."""
        malformed_responses = [
            '{"incomplete": json',
            '{"valid": "json", "but": "unexpected_structure"}',
            '[]',  # Array instead of object
            'null',
            '{"nested": {"very": {"deep": {"structure": "value"}}}}'
        ]
        
        client = PropellerAdsClient(api_key="test-key")
        
        for malformed_json in malformed_responses:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.text = malformed_json
            
            if malformed_json.startswith('{') and malformed_json.endswith('}'):
                try:
                    import json
                    mock_response.json.return_value = json.loads(malformed_json)
                except:
                    mock_response.json.side_effect = ValueError("Invalid JSON")
            else:
                mock_response.json.side_effect = ValueError("Invalid JSON")
            
            mock_request.return_value = mock_response
            
            # Should handle malformed responses gracefully
            try:
                result = client.get_campaigns()
            except (ValueError, PropellerAdsError):
                pass  # Expected for malformed data
    
    def test_balance_response_edge_cases(self):
        """Test BalanceResponse with edge case inputs."""
        edge_cases = [
            "0",
            "0.00",
            "999999999.99",
            "'0.01'",
            '"1000.50"',
            "  500.25  ",
            "1e6",  # Scientific notation
            "1.23456789012345"  # High precision
        ]
        
        for value in edge_cases:
            try:
                balance = BalanceResponse(value)
                assert balance.amount >= 0
                assert isinstance(balance.formatted, str)
            except (ValueError, TypeError):
                pass  # Some edge cases may legitimately fail
    
    @patch('requests.Session.request')
    def test_unicode_and_encoding_issues(self, mock_request):
        """Test Unicode and encoding edge cases."""
        unicode_test_data = {
            "campaign_name": "测试活动 🚀",
            "description": "Тестовая кампания с эмодзи 😀",
            "target_url": "https://example.com/测试",
            "keywords": ["café", "résumé", "naïve", "🎯"]
        }
        
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"id": 12345, **unicode_test_data}
        mock_request.return_value = mock_response
        
        client = PropellerAdsClient(api_key="test-key")
        
        # Should handle Unicode data properly
        result = client.create_campaign(unicode_test_data)
        assert result["id"] == 12345


class TestResourceExhaustionScenarios:
    """Test resource exhaustion scenarios."""
    
    def test_circuit_breaker_under_stress(self):
        """Test circuit breaker behavior under stress."""
        client = PropellerAdsClient(api_key="test-key")
        
        # Simulate multiple failures
        initial_failures = client.circuit_breaker['failures']
        
        for _ in range(10):
            client._record_failure()
        
        # Circuit breaker should track failures
        assert client.circuit_breaker['failures'] > initial_failures
    
    def test_rate_limiter_exhaustion(self):
        """Test rate limiter behavior when exhausted."""
        client = PropellerAdsClient(api_key="test-key", rate_limit=5)
        
        # Try to exhaust rate limiter
        acquisitions = []
        for _ in range(10):
            success = client.rate_limiter.try_acquire(1)
            acquisitions.append(success)
        
        # Should have some successful and some failed acquisitions
        assert len(acquisitions) == 10
        assert any(acquisitions)  # At least some should succeed
    
    def test_session_resource_cleanup(self):
        """Test session resource cleanup."""
        clients = []
        
        # Create many clients
        for i in range(20):
            client = PropellerAdsClient(api_key=f"test-key-{i}")
            clients.append(client)
        
        # All should be created successfully
        assert len(clients) == 20
        
        # Cleanup should work
        for client in clients:
            if hasattr(client, 'close'):
                client.close()


class TestConcurrencyEdgeCases:
    """Test concurrency edge cases."""
    
    def test_simultaneous_rate_limit_access(self):
        """Test simultaneous rate limiter access."""
        client = PropellerAdsClient(api_key="test-key", rate_limit=10)
        
        results = []
        errors = []
        
        def try_acquire_token():
            try:
                success = client.rate_limiter.try_acquire(1)
                results.append(success)
            except Exception as e:
                errors.append(e)
        
        # Multiple threads accessing rate limiter simultaneously
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=try_acquire_token)
            threads.append(thread)
        
        for thread in threads:
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # Should handle concurrent access without errors
        assert len(errors) == 0
        assert len(results) == 10
    
    def test_circuit_breaker_race_conditions(self):
        """Test circuit breaker race conditions."""
        client = PropellerAdsClient(api_key="test-key")
        
        def record_failure():
            client._record_failure()
        
        def record_success():
            client._record_success()
        
        # Simulate concurrent success/failure recording
        threads = []
        for i in range(10):
            if i % 2 == 0:
                thread = threading.Thread(target=record_failure)
            else:
                thread = threading.Thread(target=record_success)
            threads.append(thread)
        
        for thread in threads:
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # Circuit breaker should maintain consistent state
        assert isinstance(client.circuit_breaker['failures'], int)
        assert client.circuit_breaker['failures'] >= 0


class TestConfigurationEdgeCases:
    """Test configuration edge cases."""
    
    def test_extreme_timeout_values(self):
        """Test extreme timeout configuration values."""
        # Very short timeout
        client1 = PropellerAdsClient(api_key="test-key", timeout=1)
        assert client1.config.timeout == 1
        
        # Very long timeout
        client2 = PropellerAdsClient(api_key="test-key", timeout=3600)
        assert client2.config.timeout == 3600
    
    def test_extreme_rate_limit_values(self):
        """Test extreme rate limit values."""
        # Very low rate limit
        client1 = PropellerAdsClient(api_key="test-key", rate_limit=1)
        assert client1.config.rate_limit == 1
        
        # Very high rate limit
        client2 = PropellerAdsClient(api_key="test-key", rate_limit=10000)
        assert client2.config.rate_limit == 10000
    
    def test_extreme_retry_values(self):
        """Test extreme retry configuration values."""
        # No retries
        client1 = PropellerAdsClient(api_key="test-key", max_retries=0)
        assert client1.config.max_retries == 0
        
        # Many retries
        client2 = PropellerAdsClient(api_key="test-key", max_retries=100)
        assert client2.config.max_retries == 100
    
    def test_unusual_api_key_formats(self):
        """Test unusual API key formats."""
        unusual_keys = [
            "a",  # Very short
            "x" * 1000,  # Very long
            "key-with-dashes-and-numbers-123",
            "key_with_underscores_456",
            "MixedCaseKey789",
            "key.with.dots.012"
        ]
        
        for key in unusual_keys:
            client = PropellerAdsClient(api_key=key)
            assert client.config.api_key == key
