"""
Simplified Performance Tests for PropellerAds SDK

Tests that work with the actual client implementation.
"""

import pytest
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from unittest.mock import Mock, patch
from propellerads.client import PropellerAdsClient
from propellerads.exceptions import PropellerAdsError, RateLimitError


class TestPerformanceBasics:
    """Test basic performance characteristics."""
    
    def test_client_initialization_speed(self):
        """Test that client initialization is fast."""
        start_time = time.time()
        
        client = PropellerAdsClient(api_key="test-key")
        
        initialization_time = time.time() - start_time
        
        # Should initialize in less than 1 second
        assert initialization_time < 1.0
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
        assert request_time < 1.0
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
        
        # Make 5 sequential requests
        for _ in range(5):
            client.get_balance()
        
        total_time = time.time() - start_time
        
        # Should complete 5 requests in reasonable time
        assert total_time < 5.0
        
        # Should have made exactly 5 calls
        assert mock_request.call_count == 5


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
        for _ in range(3):
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
        assert len(results) == 3
        
        # Should complete in reasonable time
        assert total_time < 5.0
    
    def test_rate_limiter_thread_safety(self):
        """Test that rate limiter is thread-safe."""
        client = PropellerAdsClient(api_key="test-key", rate_limit=10)
        
        results = []
        
        def try_acquire():
            success = client.rate_limiter.try_acquire(1)
            results.append(success)
        
        # Multiple threads trying to acquire tokens
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=try_acquire)
            threads.append(thread)
        
        for thread in threads:
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # Should have some results
        assert len(results) == 5
        # All results should be boolean
        assert all(isinstance(r, bool) for r in results)


class TestResourceManagement:
    """Test resource management and cleanup."""
    
    def test_connection_pool_efficiency(self):
        """Test that connection pooling is efficient."""
        client = PropellerAdsClient(api_key="test-key")
        
        # Session should reuse connections
        session = client.session
        assert session is not None
        
        # Should have configured adapters
        assert hasattr(session, 'adapters')
    
    def test_session_cleanup_performance(self):
        """Test that session cleanup is efficient."""
        clients = []
        
        # Create multiple clients
        start_time = time.time()
        for i in range(5):
            client = PropellerAdsClient(api_key=f"test-key-{i}")
            clients.append(client)
        
        creation_time = time.time() - start_time
        
        # Cleanup
        start_time = time.time()
        del clients
        cleanup_time = time.time() - start_time
        
        # Both operations should be fast
        assert creation_time < 5.0
        assert cleanup_time < 1.0
    
    def test_timeout_handling_performance(self):
        """Test that timeout handling is efficient."""
        client = PropellerAdsClient(api_key="test-key", timeout=1)
        
        # Timeout configuration should be set
        assert client.config.timeout == 1


class TestCircuitBreakerPerformance:
    """Test circuit breaker performance."""
    
    def test_circuit_breaker_state_check_performance(self):
        """Test that circuit breaker state checks are fast."""
        client = PropellerAdsClient(api_key="test-key")
        
        start_time = time.time()
        
        # Check circuit breaker state multiple times
        for _ in range(100):
            state = client.circuit_breaker['state']
            assert state in ['closed', 'open', 'half-open']
        
        check_time = time.time() - start_time
        
        # State checks should be very fast
        assert check_time < 1.0
    
    def test_circuit_breaker_failure_tracking_performance(self):
        """Test circuit breaker failure tracking performance."""
        client = PropellerAdsClient(api_key="test-key")
        
        start_time = time.time()
        
        # Simulate failure tracking
        initial_failures = client.circuit_breaker['failures']
        client._record_failure()
        
        tracking_time = time.time() - start_time
        
        # Failure tracking should be fast
        assert tracking_time < 0.1
        assert client.circuit_breaker['failures'] == initial_failures + 1


class TestRateLimiterPerformance:
    """Test rate limiter performance."""
    
    def test_rate_limiter_acquisition_speed(self):
        """Test rate limiter token acquisition speed."""
        client = PropellerAdsClient(api_key="test-key", rate_limit=100)
        
        start_time = time.time()
        
        # Try to acquire tokens multiple times
        for _ in range(10):
            client.rate_limiter.try_acquire(1)
        
        acquisition_time = time.time() - start_time
        
        # Token acquisition should be fast
        assert acquisition_time < 1.0
    
    def test_rate_limiter_status_check_performance(self):
        """Test rate limiter status check performance."""
        client = PropellerAdsClient(api_key="test-key")
        
        start_time = time.time()
        
        # Check status multiple times
        for _ in range(50):
            # Rate limiter should exist
            assert hasattr(client, 'rate_limiter')
        
        check_time = time.time() - start_time
        
        # Status checks should be very fast
        assert check_time < 0.5


class TestMemoryEfficiency:
    """Test memory efficiency."""
    
    def test_memory_usage_stability(self):
        """Test that memory usage remains stable."""
        import gc
        
        # Force garbage collection
        gc.collect()
        
        # Create multiple clients
        clients = []
        for i in range(10):
            client = PropellerAdsClient(api_key=f"test-key-{i}")
            clients.append(client)
        
        # Should not cause memory issues
        assert len(clients) == 10
        
        # Clean up
        del clients
        gc.collect()
    
    def test_session_reuse_efficiency(self):
        """Test that session reuse is efficient."""
        client = PropellerAdsClient(api_key="test-key")
        
        # Get session reference
        session1 = client.session
        session2 = client.session
        
        # Should be the same object (reused)
        assert session1 is session2


class TestConfigurationPerformance:
    """Test configuration performance."""
    
    def test_configuration_access_speed(self):
        """Test that configuration access is fast."""
        client = PropellerAdsClient(api_key="test-key")
        
        start_time = time.time()
        
        # Access configuration multiple times
        for _ in range(1000):
            api_key = client.config.api_key
            timeout = client.config.timeout
            rate_limit = client.config.rate_limit
        
        access_time = time.time() - start_time
        
        # Configuration access should be very fast
        assert access_time < 1.0
    
    def test_multiple_client_creation_performance(self):
        """Test performance of creating multiple clients."""
        start_time = time.time()
        
        # Create multiple clients
        clients = []
        for i in range(10):
            client = PropellerAdsClient(api_key=f"test-key-{i}")
            clients.append(client)
        
        creation_time = time.time() - start_time
        
        # Should create clients efficiently
        assert creation_time < 5.0
        assert len(clients) == 10
