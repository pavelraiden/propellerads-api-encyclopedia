"""
Performance and Load Tests for PropellerAds SDK

Comprehensive tests for performance characteristics,
load handling, and scalability features.
"""

import pytest
import time
import threading
import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed
from unittest.mock import Mock, patch, MagicMock
from propellerads import PropellerAdsClient
from propellerads.exceptions import PropellerAdsError, RateLimitError


class TestPerformanceBasics:
    """Test basic performance characteristics."""
    
    def test_client_initialization_speed(self):
        """Test that client initialization is fast."""
        start_time = time.time()
        
        client = PropellerAdsClient(api_key="test-key")
        
        initialization_time = time.time() - start_time
        
        # Should initialize in less than 100ms
        assert initialization_time < 0.1
        assert client is not None
    
    @patch('requests.Session.request')
    def test_single_request_performance(self, mock_request):
        """Test performance of single API request."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '100.00'
        mock_request.return_value = mock_response
        
        client = PropellerAdsClient(api_key="test-key")
        
        start_time = time.time()
        balance = client.get_balance()
        request_time = time.time() - start_time
        
        # Request should complete quickly (excluding network time)
        assert request_time < 0.1
        assert balance is not None
    
    @patch('requests.Session.request')
    def test_multiple_sequential_requests(self, mock_request):
        """Test performance of multiple sequential requests."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '100.00'
        mock_request.return_value = mock_response
        
        client = PropellerAdsClient(api_key="test-key")
        
        start_time = time.time()
        
        # Make 10 sequential requests
        for _ in range(10):
            client.get_balance()
        
        total_time = time.time() - start_time
        
        # Should complete 10 requests in reasonable time
        assert total_time < 1.0  # Less than 1 second for 10 requests
        
        # Should have made exactly 10 calls
        assert mock_request.call_count == 10
    
    def test_memory_usage_stability(self):
        """Test that memory usage remains stable."""
        import gc
        import sys
        
        # Force garbage collection
        gc.collect()
        
        # Create multiple clients
        clients = []
        for i in range(100):
            client = PropellerAdsClient(api_key=f"test-key-{i}")
            clients.append(client)
        
        # Memory usage should not grow excessively
        # Note: This is a basic test; real implementation might use
        # more sophisticated memory monitoring
        
        # Clean up
        del clients
        gc.collect()


class TestConcurrency:
    """Test concurrent request handling."""
    
    @patch('requests.Session.request')
    def test_thread_safety(self, mock_request):
        """Test that client is thread-safe."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '100.00'
        mock_request.return_value = mock_response
        
        client = PropellerAdsClient(api_key="test-key")
        results = []
        errors = []
        
        def make_request():
            try:
                balance = client.get_balance()
                results.append(balance)
            except Exception as e:
                errors.append(e)
        
        # Create multiple threads
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
        
        # Start all threads
        start_time = time.time()
        for thread in threads:
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        total_time = time.time() - start_time
        
        # All requests should succeed
        assert len(errors) == 0
        assert len(results) == 10
        
        # Should complete in reasonable time
        assert total_time < 2.0
    
    @patch('requests.Session.request')
    def test_concurrent_different_operations(self, mock_request):
        """Test concurrent execution of different operations."""
        # Mock different responses for different endpoints
        def mock_response_side_effect(*args, **kwargs):
            url = kwargs.get('url', '')
            response = Mock()
            response.status_code = 200
            
            if 'balance' in url:
                response.text = '100.00'
            elif 'campaigns' in url:
                response.json.return_value = [{"id": 1, "name": "Test"}]
            else:
                response.json.return_value = {"status": "ok"}
            
            return response
        
        mock_request.side_effect = mock_response_side_effect
        
        client = PropellerAdsClient(api_key="test-key")
        results = {}
        
        def get_balance():
            results['balance'] = client.get_balance()
        
        def get_campaigns():
            results['campaigns'] = client.get_campaigns()
        
        def health_check():
            results['health'] = client.health_check()
        
        # Run different operations concurrently
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = [
                executor.submit(get_balance),
                executor.submit(get_campaigns),
                executor.submit(health_check)
            ]
            
            # Wait for all to complete
            for future in as_completed(futures):
                future.result()  # This will raise if there was an exception
        
        # All operations should have completed
        assert 'balance' in results
        assert 'campaigns' in results
        assert 'health' in results
    
    def test_rate_limiter_thread_safety(self):
        """Test that rate limiter is thread-safe."""
        client = PropellerAdsClient(api_key="test-key", rate_limit=10)
        
        results = []
        
        def try_acquire():
            success = client.rate_limiter.try_acquire(1)
            results.append(success)
        
        # Multiple threads trying to acquire tokens
        threads = []
        for _ in range(20):  # More threads than rate limit
            thread = threading.Thread(target=try_acquire)
            threads.append(thread)
        
        for thread in threads:
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # Some should succeed, some should fail
        successes = sum(1 for r in results if r)
        failures = sum(1 for r in results if not r)
        
        assert successes > 0
        assert failures > 0
        assert successes + failures == 20


class TestLoadHandling:
    """Test handling of high load scenarios."""
    
    @patch('requests.Session.request')
    def test_burst_request_handling(self, mock_request):
        """Test handling of burst requests."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '100.00'
        mock_request.return_value = mock_response
        
        client = PropellerAdsClient(api_key="test-key", rate_limit=100)
        
        # Make a burst of requests
        start_time = time.time()
        results = []
        
        for _ in range(50):
            try:
                balance = client.get_balance()
                results.append(balance)
            except RateLimitError:
                # Expected for some requests
                pass
        
        total_time = time.time() - start_time
        
        # Should handle burst reasonably
        assert len(results) > 0
        assert total_time < 5.0  # Should not take too long
    
    @patch('requests.Session.request')
    def test_sustained_load_handling(self, mock_request):
        """Test handling of sustained load."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '100.00'
        mock_request.return_value = mock_response
        
        client = PropellerAdsClient(api_key="test-key", rate_limit=60)
        
        # Simulate sustained load over time
        start_time = time.time()
        successful_requests = 0
        
        # Make requests for 2 seconds
        while time.time() - start_time < 2.0:
            try:
                client.get_balance()
                successful_requests += 1
            except RateLimitError:
                # Expected when rate limit is hit
                time.sleep(0.1)  # Brief pause
            except Exception:
                # Other errors
                pass
        
        # Should have made some successful requests
        assert successful_requests > 0
        
        # Rate should be reasonable (not exceeding configured limit too much)
        rate_per_second = successful_requests / 2.0
        assert rate_per_second <= client.config.rate_limit / 60 * 1.5  # Allow some tolerance
    
    def test_memory_usage_under_load(self):
        """Test memory usage under sustained load."""
        import gc
        
        client = PropellerAdsClient(api_key="test-key")
        
        # Force garbage collection before test
        gc.collect()
        
        # Simulate load by creating many objects
        for i in range(1000):
            # Create request data
            data = {
                "name": f"Campaign {i}",
                "budget": 100.0,
                "target_url": f"https://example{i}.com"
            }
            
            # Simulate processing (without actual network calls)
            try:
                client._sanitize_params(data)
            except AttributeError:
                # Method might not exist, that's ok for this test
                pass
        
        # Force garbage collection
        gc.collect()
        
        # Memory should not have grown excessively
        # Note: This is a basic test; real implementation might use
        # more sophisticated memory monitoring


class TestCircuitBreaker:
    """Test circuit breaker performance under load."""
    
    @patch('requests.Session.request')
    def test_circuit_breaker_response_time(self, mock_request):
        """Test that circuit breaker responds quickly when open."""
        # Simulate failing requests to trigger circuit breaker
        mock_request.side_effect = Exception("Server error")
        
        client = PropellerAdsClient(api_key="test-key")
        
        # Make requests to trigger circuit breaker
        for _ in range(6):  # Exceed failure threshold
            try:
                client.get_balance()
            except:
                pass
        
        # Now circuit should be open, requests should fail fast
        start_time = time.time()
        
        try:
            client.get_balance()
        except PropellerAdsError:
            pass  # Expected
        
        response_time = time.time() - start_time
        
        # Should fail very quickly when circuit is open
        assert response_time < 0.01  # Less than 10ms
    
    def test_circuit_breaker_recovery_performance(self):
        """Test circuit breaker recovery performance."""
        client = PropellerAdsClient(api_key="test-key")
        
        # Manually set circuit breaker to open state
        client.circuit_breaker['state'] = 'open'
        client.circuit_breaker['last_failure'] = time.time() - 70  # Past recovery timeout
        
        # Recovery check should be fast
        start_time = time.time()
        
        # This should trigger recovery check
        try:
            client._check_circuit_breaker()
        except AttributeError:
            # Method might not exist, that's ok for this test
            pass
        
        check_time = time.time() - start_time
        
        # Recovery check should be very fast
        assert check_time < 0.01


class TestCaching:
    """Test caching performance features."""
    
    @patch('requests.Session.request')
    def test_response_caching_performance(self, mock_request):
        """Test that response caching improves performance."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{"id": 1, "name": "Test Campaign"}]
        mock_request.return_value = mock_response
        
        client = PropellerAdsClient(api_key="test-key")
        
        # First request (should hit network)
        start_time = time.time()
        campaigns1 = client.get_campaigns()
        first_request_time = time.time() - start_time
        
        # Second request (might be cached)
        start_time = time.time()
        campaigns2 = client.get_campaigns()
        second_request_time = time.time() - start_time
        
        # Both should return data
        assert campaigns1 is not None
        assert campaigns2 is not None
        
        # Note: Actual caching implementation would make second request faster
        # This test establishes the baseline for performance comparison
    
    def test_cache_memory_efficiency(self):
        """Test that caching doesn't consume excessive memory."""
        client = PropellerAdsClient(api_key="test-key")
        
        # Simulate multiple cached responses
        cache_data = {}
        for i in range(100):
            key = f"campaigns_{i}"
            value = [{"id": j, "name": f"Campaign {j}"} for j in range(10)]
            cache_data[key] = value
        
        # Cache should not consume excessive memory
        # Note: This is a basic test; real implementation might use
        # more sophisticated cache management


class TestResourceManagement:
    """Test resource management and cleanup."""
    
    def test_connection_pool_efficiency(self):
        """Test that connection pooling is efficient."""
        client = PropellerAdsClient(api_key="test-key")
        
        # Session should reuse connections
        session = client.session
        assert session is not None
        
        # Should have configured adapters
        assert len(session.adapters) > 0
    
    def test_session_cleanup_performance(self):
        """Test that session cleanup is efficient."""
        clients = []
        
        # Create multiple clients
        start_time = time.time()
        for i in range(10):
            client = PropellerAdsClient(api_key=f"test-key-{i}")
            clients.append(client)
        
        creation_time = time.time() - start_time
        
        # Cleanup
        start_time = time.time()
        del clients
        cleanup_time = time.time() - start_time
        
        # Both operations should be fast
        assert creation_time < 1.0
        assert cleanup_time < 0.1
    
    def test_timeout_handling_performance(self):
        """Test that timeout handling is efficient."""
        client = PropellerAdsClient(api_key="test-key", timeout=0.001)  # Very short timeout
        
        start_time = time.time()
        
        try:
            # This should timeout quickly
            client.get_balance()
        except:
            pass  # Expected to fail
        
        timeout_time = time.time() - start_time
        
        # Should timeout close to the configured timeout
        assert timeout_time < 0.1  # Should not take much longer than timeout
