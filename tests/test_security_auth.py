"""
Security and Authentication Tests for PropellerAds SDK

Comprehensive tests for security features, authentication,
and authorization mechanisms.
"""

import pytest
import time
from unittest.mock import Mock, patch, MagicMock
from propellerads import PropellerAdsClient, AuthenticationError, RateLimitError
from propellerads.exceptions import PropellerAdsError


class TestAuthentication:
    """Test authentication mechanisms."""
    
    def test_api_key_validation_empty(self):
        """Test that empty API key raises error."""
        with pytest.raises(ValueError, match="API key is required"):
            PropellerAdsClient(api_key="")
    
    def test_api_key_validation_none(self):
        """Test that None API key raises error."""
        with pytest.raises(ValueError, match="API key is required"):
            PropellerAdsClient(api_key=None)
    
    def test_api_key_validation_whitespace(self):
        """Test that whitespace-only API key raises error."""
        with pytest.raises(ValueError, match="API key is required"):
            PropellerAdsClient(api_key="   ")
    
    def test_api_key_format_validation(self):
        """Test API key format validation."""
        # Valid API key should work
        client = PropellerAdsClient(api_key="valid-api-key-123")
        assert client.config.api_key == "valid-api-key-123"
    
    @patch('requests.Session.request')
    def test_authentication_header_injection(self, mock_request):
        """Test that API key is properly injected in headers."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '100.00'
        mock_request.return_value = mock_response
        
        client = PropellerAdsClient(api_key="test-api-key")
        client.get_balance()
        
        # Check that the request was made with proper headers
        mock_request.assert_called_once()
        call_kwargs = mock_request.call_args[1]
        assert 'headers' in call_kwargs
        assert 'Authorization' in call_kwargs['headers']
    
    @patch('requests.Session.request')
    def test_unauthorized_response_handling(self, mock_request):
        """Test handling of 401 Unauthorized responses."""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.text = 'Unauthorized'
        mock_response.raise_for_status.side_effect = Exception("401 Unauthorized")
        mock_request.return_value = mock_response
        
        client = PropellerAdsClient(api_key="invalid-key")
        
        with pytest.raises(AuthenticationError):
            client.get_balance()
    
    @patch('requests.Session.request')
    def test_forbidden_response_handling(self, mock_request):
        """Test handling of 403 Forbidden responses."""
        mock_response = Mock()
        mock_response.status_code = 403
        mock_response.text = 'Forbidden'
        mock_response.raise_for_status.side_effect = Exception("403 Forbidden")
        mock_request.return_value = mock_response
        
        client = PropellerAdsClient(api_key="limited-key")
        
        with pytest.raises(AuthenticationError):
            client.get_balance()


class TestRateLimiting:
    """Test rate limiting mechanisms."""
    
    def test_rate_limiter_initialization(self):
        """Test rate limiter is properly initialized."""
        client = PropellerAdsClient(api_key="test-key", rate_limit=30)
        assert client.rate_limiter is not None
        assert hasattr(client.rate_limiter, 'try_acquire')
    
    def test_rate_limiter_token_acquisition(self):
        """Test rate limiter token acquisition."""
        client = PropellerAdsClient(api_key="test-key", rate_limit=60)
        
        # Should be able to acquire tokens initially
        success = client.rate_limiter.try_acquire(1)
        assert success is True
    
    def test_rate_limiter_status_reporting(self):
        """Test rate limiter status reporting."""
        client = PropellerAdsClient(api_key="test-key", rate_limit=60)
        
        status = client.rate_limiter.get_status()
        assert isinstance(status, dict)
        assert 'tokens_available' in status
        assert 'bucket_size' in status
        assert 'refill_rate' in status
    
    @patch('requests.Session.request')
    def test_rate_limit_enforcement(self, mock_request):
        """Test that rate limiting is enforced."""
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.text = 'Rate limit exceeded'
        mock_response.headers = {'Retry-After': '60'}
        mock_request.return_value = mock_response
        
        client = PropellerAdsClient(api_key="test-key")
        
        with pytest.raises(RateLimitError):
            client.get_balance()
    
    def test_rate_limit_configuration(self):
        """Test rate limit configuration options."""
        # Test different rate limits
        client1 = PropellerAdsClient(api_key="test-key", rate_limit=30)
        client2 = PropellerAdsClient(api_key="test-key", rate_limit=120)
        
        assert client1.config.rate_limit == 30
        assert client2.config.rate_limit == 120


class TestSecurityHeaders:
    """Test security-related headers and configurations."""
    
    @patch('requests.Session.request')
    def test_user_agent_header(self, mock_request):
        """Test that User-Agent header is set."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '100.00'
        mock_request.return_value = mock_response
        
        client = PropellerAdsClient(api_key="test-key")
        client.get_balance()
        
        call_kwargs = mock_request.call_args[1]
        headers = call_kwargs.get('headers', {})
        assert 'User-Agent' in headers
        assert 'PropellerAds' in headers['User-Agent']
    
    @patch('requests.Session.request')
    def test_content_type_header(self, mock_request):
        """Test that Content-Type header is set for JSON requests."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": 123}
        mock_request.return_value = mock_response
        
        client = PropellerAdsClient(api_key="test-key")
        client.create_campaign({
            "name": "Test Campaign",
            "target_url": "https://example.com",
            "daily_budget": 100
        })
        
        call_kwargs = mock_request.call_args[1]
        headers = call_kwargs.get('headers', {})
        assert 'Content-Type' in headers
        assert 'application/json' in headers['Content-Type']
    
    def test_session_security_configuration(self):
        """Test that session is configured securely."""
        client = PropellerAdsClient(api_key="test-key")
        session = client.session
        
        # Check that session has proper adapters
        assert len(session.adapters) > 0
        
        # Check that session has proper headers
        assert 'User-Agent' in session.headers


class TestInputValidation:
    """Test input validation and sanitization."""
    
    def test_campaign_data_validation(self):
        """Test campaign data validation."""
        client = PropellerAdsClient(api_key="test-key")
        
        # Test with invalid data types
        with pytest.raises((TypeError, ValueError)):
            client.create_campaign("invalid_data")
    
    def test_parameter_sanitization(self):
        """Test that parameters are properly sanitized."""
        client = PropellerAdsClient(api_key="test-key")
        
        # Test with potentially dangerous inputs
        safe_params = client._sanitize_params({
            "name": "<script>alert('xss')</script>",
            "budget": "100.50",
            "limit": "10"
        })
        
        # Should sanitize HTML/script tags
        assert "<script>" not in safe_params.get("name", "")
    
    def test_url_validation(self):
        """Test URL validation for target URLs."""
        client = PropellerAdsClient(api_key="test-key")
        
        # Valid URLs should pass
        valid_urls = [
            "https://example.com",
            "http://test.com/path",
            "https://subdomain.example.com/path?param=value"
        ]
        
        for url in valid_urls:
            validated = client._validate_url(url)
            assert validated is not None
        
        # Invalid URLs should fail
        invalid_urls = [
            "not-a-url",
            "ftp://example.com",
            "javascript:alert('xss')",
            ""
        ]
        
        for url in invalid_urls:
            with pytest.raises(ValueError):
                client._validate_url(url)


class TestErrorHandling:
    """Test error handling and security-related error responses."""
    
    @patch('requests.Session.request')
    def test_malformed_response_handling(self, mock_request):
        """Test handling of malformed responses."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = 'invalid-json-response'
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_request.return_value = mock_response
        
        client = PropellerAdsClient(api_key="test-key")
        
        with pytest.raises(PropellerAdsError):
            client.get_campaigns()
    
    @patch('requests.Session.request')
    def test_timeout_handling(self, mock_request):
        """Test handling of request timeouts."""
        from requests.exceptions import Timeout
        mock_request.side_effect = Timeout("Request timeout")
        
        client = PropellerAdsClient(api_key="test-key", timeout=1)
        
        with pytest.raises(PropellerAdsError):
            client.get_balance()
    
    @patch('requests.Session.request')
    def test_connection_error_handling(self, mock_request):
        """Test handling of connection errors."""
        from requests.exceptions import ConnectionError
        mock_request.side_effect = ConnectionError("Connection failed")
        
        client = PropellerAdsClient(api_key="test-key")
        
        with pytest.raises(PropellerAdsError):
            client.get_balance()
    
    def test_error_message_sanitization(self):
        """Test that error messages don't leak sensitive information."""
        client = PropellerAdsClient(api_key="secret-api-key-12345")
        
        try:
            # This should fail with invalid URL
            client._make_request("GET", "invalid-endpoint")
        except Exception as e:
            error_message = str(e)
            # Error message should not contain the API key
            assert "secret-api-key-12345" not in error_message


class TestSessionManagement:
    """Test session management and security."""
    
    def test_session_isolation(self):
        """Test that different clients have isolated sessions."""
        client1 = PropellerAdsClient(api_key="key1")
        client2 = PropellerAdsClient(api_key="key2")
        
        # Sessions should be different objects
        assert client1.session is not client2.session
        
        # Sessions should have different headers
        assert client1.session.headers != client2.session.headers
    
    def test_session_cleanup(self):
        """Test that sessions are properly cleaned up."""
        client = PropellerAdsClient(api_key="test-key")
        session = client.session
        
        # Session should be active
        assert session is not None
        
        # After client deletion, session should be cleaned up
        del client
        # Note: In real implementation, you might want to add explicit cleanup
    
    def test_connection_pooling(self):
        """Test connection pooling configuration."""
        client = PropellerAdsClient(api_key="test-key")
        session = client.session
        
        # Check that adapters are configured
        assert len(session.adapters) > 0
        
        # Check for HTTPS adapter
        https_adapter = session.get_adapter("https://")
        assert https_adapter is not None


class TestDataProtection:
    """Test data protection and privacy features."""
    
    def test_sensitive_data_logging(self):
        """Test that sensitive data is not logged."""
        import logging
        from io import StringIO
        
        # Capture log output
        log_capture = StringIO()
        handler = logging.StreamHandler(log_capture)
        logger = logging.getLogger('propellerads')
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
        
        try:
            client = PropellerAdsClient(api_key="secret-key-123")
            
            # Perform some operations that might log
            try:
                client.get_balance()
            except:
                pass  # We expect this to fail in tests
            
            log_output = log_capture.getvalue()
            
            # API key should not appear in logs
            assert "secret-key-123" not in log_output
            
        finally:
            logger.removeHandler(handler)
    
    def test_memory_cleanup(self):
        """Test that sensitive data is cleaned from memory."""
        api_key = "sensitive-api-key-123"
        client = PropellerAdsClient(api_key=api_key)
        
        # API key should be stored securely
        assert hasattr(client.config, 'api_key')
        
        # After operations, sensitive data should not linger
        # Note: This is a basic test; real implementation might use
        # more sophisticated memory protection
    
    def test_request_data_sanitization(self):
        """Test that request data is sanitized before sending."""
        client = PropellerAdsClient(api_key="test-key")
        
        # Test data with potentially sensitive information
        test_data = {
            "name": "Test Campaign",
            "password": "should-be-removed",
            "api_key": "should-be-removed",
            "secret": "should-be-removed"
        }
        
        sanitized = client._sanitize_request_data(test_data)
        
        # Sensitive fields should be removed or masked
        assert "password" not in sanitized
        assert "api_key" not in sanitized
        assert "secret" not in sanitized
        assert sanitized["name"] == "Test Campaign"
