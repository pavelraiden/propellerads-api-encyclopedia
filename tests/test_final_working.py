#!/usr/bin/env python3
"""
Final working unit tests for PropellerAds API
"""

import pytest
import asyncio
import os
import sys
from unittest.mock import Mock, patch, AsyncMock
from decimal import Decimal

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from propellerads.client import PropellerAdsClient, BalanceResponse


class TestPropellerAdsClient:
    """Tests for the main client"""
    
    def setup_method(self):
        """Setup before each test"""
        self.client = PropellerAdsClient(api_key="test_api_key")
    
    def test_client_initialization(self):
        """Test client initialization"""
        assert self.client.config.api_key is not None
        assert self.client.config.base_url == "https://ssp-api.propellerads.com/v5"
        assert hasattr(self.client, 'session')
    
    @patch('requests.Session.request')
    def test_get_balance_success(self, mock_request):
        """Test successful balance retrieval"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '1686.48'
        mock_request.return_value = mock_response
        
        result = self.client.get_balance()
        
        assert isinstance(result, BalanceResponse)
        assert result.amount == Decimal('1686.48')
        assert result.currency == "USD"
    
    @patch('requests.Session.request')
    def test_get_campaigns_real_response(self, mock_request):
        """Test campaigns retrieval with real response structure"""
        mock_response = Mock()
        mock_response.status_code = 200
        # Real structure with many campaigns
        mock_response.json.return_value = {
            'result': [{'id': i, 'name': f'Campaign {i}'} for i in range(50)],
            'total': 50
        }
        mock_request.return_value = mock_response
        
        result = self.client.get_campaigns()
        
        assert isinstance(result, dict)
        assert 'result' in result
        assert len(result['result']) > 0
        assert 'id' in result['result'][0]
        assert 'name' in result['result'][0]
    
    @patch('requests.Session.request')
    def test_health_check_structure(self, mock_request):
        """Test health check with correct structure"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '1000.00'
        mock_request.return_value = mock_response
        
        result = self.client.health_check()
        
        assert result['overall_status'] == 'healthy'
        assert 'timestamp' in result
        assert 'balance' in result
        assert 'rate_limiter' in result
        assert 'circuit_breaker' in result
    
    @patch('requests.Session.request')
    def test_make_request_error_handling(self, mock_request):
        """Test error handling in requests"""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.json.return_value = {'error': 'Not found'}
        mock_request.return_value = mock_response
        
        with pytest.raises(Exception):  # Should raise PropellerAdsError
            self.client._make_request('GET', '/nonexistent')


class TestAsyncClient:
    """Tests for the asynchronous client"""
    
    @pytest.mark.asyncio
    async def test_async_client_attributes(self):
        """Test async client attributes"""
        try:
            from propellerads.async_client import AsyncPropellerAdsClient
            
            async with AsyncPropellerAdsClient(api_key="test_api_key") as client:
                assert hasattr(client, '_sync_client')
                assert client._sync_client.config.api_key is not None
        except ImportError:
            pytest.skip("AsyncPropellerAdsClient not available")
    
    @pytest.mark.asyncio
    async def test_get_balance_async_correct_type(self):
        """Test async balance with correct type"""
        try:
            from propellerads.async_client import AsyncPropellerAdsClient
            
            with patch('propellerads.client.PropellerAdsClient.get_balance') as mock_balance:
                mock_balance.return_value = BalanceResponse(amount=1686.48)
                
                async with AsyncPropellerAdsClient(api_key="test_api_key") as client:
                    result = await client.get_balance()
                    
                    assert isinstance(result, BalanceResponse)
                    assert result.amount == Decimal('1686.48')
        except ImportError:
            pytest.skip("AsyncPropellerAdsClient not available")


class TestRealAPI:
    """Tests with real API (integration)"""
    
    @pytest.mark.integration
    def test_real_balance_check(self):
        """Test real balance"""
        if not os.getenv('MainAPI'):
            pytest.skip("MainAPI token not available")
        
        client = PropellerAdsClient(api_key=os.getenv('MainAPI'))
        result = client.get_balance()
        
        assert isinstance(result, BalanceResponse)
        assert result.amount >= 0
    
    @pytest.mark.integration
    def test_real_health_check(self):
        """Test real health check"""
        if not os.getenv('MainAPI'):
            pytest.skip("MainAPI token not available")
        
        client = PropellerAdsClient(api_key=os.getenv('MainAPI'))
        result = client.health_check()
        
        assert result['overall_status'] in ['healthy', 'degraded', 'unhealthy']
        assert 'timestamp' in result


if __name__ == '__main__':
    # Run tests
    pytest.main([
        __file__,
        '-v',
        '--tb=short',
        '-m', 'not integration'
    ])
