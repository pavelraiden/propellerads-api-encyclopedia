#!/usr/bin/env python3
"""
Остаточні працюючі unit тести для PropellerAds API
"""

import pytest
import asyncio
import os
import sys
from unittest.mock import Mock, patch, AsyncMock

# Додаємо src до path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from propellerads.client import PropellerAdsClient


class TestPropellerAdsClient:
    """Тести для основного клієнта"""
    
    def setup_method(self):
        """Налаштування перед кожним тестом"""
        self.client = PropellerAdsClient(api_key="test_api_key")
    
    def test_client_initialization(self):
        """Тест ініціалізації клієнта"""
        assert self.client.api_key is not None
        assert self.client.base_url == "https://ssp-api.propellerads.com/v5"
        assert hasattr(self.client, 'session')
    
    @patch('requests.Session.get')
    def test_get_balance_success(self, mock_get):
        """Тест успішного отримання балансу"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '\"1686.48\"'
        mock_get.return_value = mock_response
        
        result = self.client.get_balance()
        
        assert result['success'] is True
        assert result['data'] == '1686.48'
        assert result['status_code'] == 200
    
    @patch('requests.Session.get')
    def test_get_campaigns_real_response(self, mock_get):
        """Тест отримання кампаній з реальною кількістю"""
        mock_response = Mock()
        mock_response.status_code = 200
        # Реальна структура з багатьма кампаніями
        mock_response.json.return_value = {
            'data': {
                'result': [{'id': i, 'name': f'Campaign {i}'} for i in range(50)],
                'total': 50
            }
        }
        mock_get.return_value = mock_response
        
        result = self.client.get_campaigns()
        
        assert result['success'] is True
        # Перевіряємо що отримали дані (може бути реальна кількість)
        assert len(result['data']['result']) > 0
        assert 'id' in result['data']['result'][0]
        assert 'name' in result['data']['result'][0]
    
    @patch('requests.Session.get')
    def test_health_check_structure(self, mock_get):
        """Тест health check з правильною структурою"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '\"1000.00\"'
        mock_get.return_value = mock_response
        
        result = self.client.health_check()
        
        assert result['overall_health'] == 'healthy'
        assert 'checks' in result
        assert 'timestamp' in result
        assert 'api_version' in result
        # Баланс в checks, не в корені
        assert 'balance' in result['checks']
    
    def test_make_request_error_handling(self):
        """Тест обробки помилок в запитах"""
        with patch.object(self.client.session, 'request') as mock_request:
            mock_response = Mock()
            mock_response.status_code = 404
            mock_response.json.return_value = {'error': 'Not found'}
            mock_request.return_value = mock_response
            
            result = self.client._make_request('GET', '/nonexistent')
            
            assert result['success'] is False
            assert result['status_code'] == 404


class TestAsyncClient:
    """Тести для асинхронного клієнта"""
    
    @pytest.mark.asyncio
    async def test_async_client_attributes(self):
        """Тест атрибутів async клієнта"""
        from propellerads.async_client import PropellerAdsAsyncClient
        
        async with PropellerAdsAsyncClient(api_key="test_api_key") as client:
            assert hasattr(client, 'api_key')
            assert hasattr(client, 'base_url')
            assert client.api_key is not None
    
    @pytest.mark.asyncio
    async def test_get_balance_async_correct_type(self):
        """Тест async балансу з правильним типом"""
        from propellerads.async_client import PropellerAdsAsyncClient
        
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.text = AsyncMock(return_value='\"1686.48\"')
            mock_get.return_value.__aenter__.return_value = mock_response
            
            async with PropellerAdsAsyncClient(api_key="test_api_key") as client:
                result = await client.get_balance()
                
                assert result['success'] is True
                assert result['balance'] == 1686.48
                assert isinstance(result['balance'], float)

class TestRealAPI:
    """Тести з реальним API (інтеграційні)"""
    
    @pytest.mark.integration
    def test_real_balance_check(self):
        """Тест реального балансу"""
        if not os.getenv('MainAPI'):
            pytest.skip("MainAPI token not available")
        
        client = PropellerAdsClient(api_key=os.getenv('MainAPI'))
        result = client.get_balance()
        
        assert result['success'] is True
        assert 'data' in result
        assert isinstance(result['data'], str)
        # Баланс повинен бути числом в рядку
        assert float(result['data']) >= 0
    
    @pytest.mark.integration
    def test_real_health_check(self):
        """Тест реального health check"""
        if not os.getenv('MainAPI'):
            pytest.skip("MainAPI token not available")
        
        client = PropellerAdsClient(api_key=os.getenv('MainAPI'))
        result = client.health_check()
        
        assert result['overall_health'] in ['healthy', 'degraded', 'unhealthy']
        assert 'checks' in result
        assert 'timestamp' in result


if __name__ == '__main__':
    # Запуск тестів
    pytest.main([
        __file__,
        '-v',
        '--tb=short',
        '-m', 'not integration'
    ])

