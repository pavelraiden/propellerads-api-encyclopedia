#!/usr/bin/env python3
"""
Unit тести для PropellerAds API клієнтів
"""

import pytest
import asyncio
import os
import sys
from unittest.mock import Mock, patch, AsyncMock

# Додаємо src до path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from propellerads_client import PropellerAdsUltimateClient
# Імпорти з абсолютними шляхами
try:
    from src.client.async_client import PropellerAdsAsyncClient
    from src.models.campaign import CampaignCreate, Targeting, Rate
    from src.models.statistics import StatisticsRequest
    from src.exceptions import PropellerAdsError, AuthenticationError, ServerError
except ImportError:
    # Fallback для різних структур
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
    from client.async_client import PropellerAdsAsyncClient
    from models.campaign import CampaignCreate, Targeting, Rate
    from models.statistics import StatisticsRequest
    from exceptions import PropellerAdsError, AuthenticationError, ServerError


class TestPropellerAdsUltimateClient:
    """Тести для основного клієнта"""
    
    def setup_method(self):
        """Налаштування перед кожним тестом"""
        self.client = PropellerAdsUltimateClient()
    
    def test_client_initialization(self):
        """Тест ініціалізації клієнта"""
        assert self.client.api_token is not None
        assert self.client.base_url == "https://ssp-api.propellerads.com/v5"
        assert hasattr(self.client, 'session')
    
    @patch('requests.Session.get')
    def test_get_balance_success(self, mock_get):
        """Тест успішного отримання балансу"""
        # Mock відповідь
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '"1732.91"'
        mock_get.return_value = mock_response
        
        result = self.client.get_balance()
        
        assert result['success'] is True
        assert result['data'] == '1732.91'
        assert result['status_code'] == 200
    
    @patch('requests.Session.get')
    def test_get_campaigns_success(self, mock_get):
        """Тест успішного отримання кампаній"""
        # Mock відповідь
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'data': {
                'result': [
                    {'id': 123, 'name': 'Test Campaign'}
                ]
            }
        }
        mock_get.return_value = mock_response
        
        result = self.client.get_campaigns()
        
        assert result['success'] is True
        assert len(result['data']['result']) == 1
        assert result['data']['result'][0]['name'] == 'Test Campaign'
    
    @patch('requests.Session.get')
    def test_health_check(self, mock_get):
        """Тест health check"""
        # Mock відповідь для балансу
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '"1000.00"'
        mock_get.return_value = mock_response
        
        result = self.client.health_check()
        
        assert result['overall_health'] == 'healthy'
        assert 'balance' in result
        assert 'timestamp' in result
        assert 'api_version' in result
    
    def test_get_all_targeting_options(self):
        """Тест отримання всіх опцій таргетингу"""
        with patch.object(self.client, '_make_request') as mock_request:
            mock_request.return_value = {
                'success': True,
                'data': ['US', 'UK', 'DE']
            }
            
            result = self.client.get_all_targeting_options()
            
            assert 'countries' in result
            assert 'operating_systems' in result
            assert 'browsers' in result


class TestAsyncClient:
    """Тести для асинхронного клієнта"""
    
    @pytest.mark.asyncio
    async def test_async_client_initialization(self):
        """Тест ініціалізації async клієнта"""
        async with PropellerAdsAsyncClient() as client:
            assert client.api_token is not None
            assert client.base_url == "https://ssp-api.propellerads.com/v5"
    
    @pytest.mark.asyncio
    async def test_get_balance_async(self):
        """Тест async отримання балансу"""
        with patch('aiohttp.ClientSession.get') as mock_get:
            # Mock async response
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.text = AsyncMock(return_value='"1500.00"')
            mock_get.return_value.__aenter__.return_value = mock_response
            
            async with PropellerAdsAsyncClient() as client:
                result = await client.get_balance()
                
                assert result['success'] is True
                assert result['balance'] == '1500.00'
    
    @pytest.mark.asyncio
    async def test_retry_logic(self):
        """Тест retry логіки"""
        with patch('aiohttp.ClientSession.get') as mock_get:
            # Перший запит - помилка, другий - успіх
            mock_response_error = AsyncMock()
            mock_response_error.status = 500
            mock_response_error.text = AsyncMock(return_value='Server Error')
            
            mock_response_success = AsyncMock()
            mock_response_success.status = 200
            mock_response_success.text = AsyncMock(return_value='"1000.00"')
            
            mock_get.return_value.__aenter__.side_effect = [
                mock_response_error,
                mock_response_success
            ]
            
            async with PropellerAdsAsyncClient() as client:
                result = await client.get_balance()
                
                assert result['success'] is True
                assert mock_get.call_count == 2  # Retry спрацював


class TestModels:
    """Тести для Pydantic моделей"""
    
    def test_campaign_create_model(self):
        """Тест моделі створення кампанії"""
        campaign_data = {
            'name': 'Test Campaign',
            'direction': 'classic_push',
            'rate_model': 'cpc',
            'target_url': 'https://example.com',
            'targeting': {
                'country': {'list': ['US'], 'is_excluded': False}
            },
            'rates': [
                {'countries': ['US'], 'amount': 0.05}
            ]
        }
        
        campaign = CampaignCreate(**campaign_data)
        
        assert campaign.name == 'Test Campaign'
        assert campaign.direction == 'classic_push'
        assert campaign.rate_model == 'cpc'
        assert len(campaign.rates) == 1
    
    def test_statistics_request_model(self):
        """Тест моделі запиту статистики"""
        stats_data = {
            'day_from': '2025-09-01 00:00:00',
            'day_to': '2025-09-30 23:59:59',
            'group_by': ['campaign_id']
        }
        
        stats = StatisticsRequest(**stats_data)
        
        assert stats.day_from == '2025-09-01 00:00:00'
        assert stats.group_by == ['campaign_id']
        assert stats.tz == '+0000'  # Default value
    
    def test_invalid_campaign_data(self):
        """Тест валідації неправильних даних кампанії"""
        with pytest.raises(ValueError):
            CampaignCreate(
                name='',  # Порожнє ім'я
                direction='invalid_direction',
                rate_model='invalid_model',
                target_url='not_a_url',
                targeting={},
                rates=[]
            )


class TestExceptions:
    """Тести для кастомних винятків"""
    
    def test_propellerads_error(self):
        """Тест базового винятку"""
        error = PropellerAdsError("Test error", 400)
        
        assert str(error) == "Test error"
        assert error.status_code == 400
    
    def test_authentication_error(self):
        """Тест винятку аутентифікації"""
        error = AuthenticationError("Invalid token")
        
        assert str(error) == "Invalid token"
        assert error.status_code == 401
    
    def test_server_error(self):
        """Тест винятку сервера"""
        error = ServerError("Internal server error")
        
        assert str(error) == "Internal server error"
        assert error.status_code == 500


class TestIntegration:
    """Інтеграційні тести (потребують реального API токена)"""
    
    @pytest.mark.integration
    def test_real_api_balance(self):
        """Тест реального API балансу"""
        if not os.getenv('MainAPI'):
            pytest.skip("MainAPI token not available")
        
        client = PropellerAdsUltimateClient()
        result = client.get_balance()
        
        assert result['success'] is True
        assert 'data' in result
        assert isinstance(result['data'], str)
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_real_async_api_balance(self):
        """Тест реального async API балансу"""
        if not os.getenv('MainAPI'):
            pytest.skip("MainAPI token not available")
        
        async with PropellerAdsAsyncClient() as client:
            result = await client.get_balance()
            
            assert result['success'] is True
            assert 'balance' in result


if __name__ == '__main__':
    # Запуск тестів
    pytest.main([
        __file__,
        '-v',
        '--tb=short',
        '-m', 'not integration'  # Пропускаємо інтеграційні тести за замовчуванням
    ])
