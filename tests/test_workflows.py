#!/usr/bin/env python3
"""
Unit тести для воркфлоу
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch

# Додаємо src до path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from workflows.campaign_monitoring import CampaignMonitor
from workflows.financial_control import FinancialController


class TestCampaignMonitor:
    """Тести для моніторингу кампаній"""
    
    def setup_method(self):
        """Налаштування перед кожним тестом"""
        with patch('workflows.campaign_monitoring.PropellerAdsUltimateClient') as mock_client_class:
            self.mock_client = Mock()
            mock_client_class.return_value = self.mock_client
            self.monitor = CampaignMonitor()
    
    def test_monitor_initialization(self):
        """Тест ініціалізації монітора"""
        assert hasattr(self.monitor, 'client')
        assert hasattr(self.monitor, 'alerts')
    
    def test_check_campaign_performance(self):
        """Тест перевірки продуктивності кампаній"""
        # Mock дані кампаній
        self.mock_client.get_campaigns.return_value = {
            'success': True,
            'data': {
                'result': [
                    {'id': 123, 'name': 'Test Campaign', 'status': 'active'}
                ]
            }
        }
        
        self.mock_client.get_campaign_details.return_value = {
            'success': True,
            'data': {'spent': 100.0, 'conversions': 5}
        }
        
        result = self.monitor.check_campaign_performance()
        
        assert result['total_campaigns'] == 1
        assert result['active_campaigns'] == 1
        assert len(result['campaign_details']) == 1
    
    def test_generate_daily_report(self):
        """Тест генерації щоденного звіту"""
        # Mock health check
        self.mock_client.health_check.return_value = {
            'overall_health': 'healthy',
            'balance': '1000.00'
        }
        
        # Mock campaigns
        self.mock_client.get_campaigns.return_value = {
            'success': True,
            'data': {'result': []}
        }
        
        report = self.monitor.generate_daily_report()
        
        assert 'health_status' in report
        assert 'campaign_summary' in report
        assert 'timestamp' in report
        assert report['health_status'] == 'healthy'


class TestFinancialController:
    """Тести для фінансового контролю"""
    
    def setup_method(self):
        """Налаштування перед кожним тестом"""
        with patch('workflows.financial_control.PropellerAdsUltimateClient') as mock_client_class:
            self.mock_client = Mock()
            mock_client_class.return_value = self.mock_client
            self.controller = FinancialController()
    
    def test_controller_initialization(self):
        """Тест ініціалізації контролера"""
        assert hasattr(self.controller, 'client')
        assert hasattr(self.controller, 'thresholds')
        assert self.controller.thresholds['low_balance'] == 100.0
    
    def test_check_balance_normal(self):
        """Тест перевірки нормального балансу"""
        self.mock_client.get_balance.return_value = {
            'success': True,
            'data': '500.00'
        }
        
        result = self.controller.check_balance()
        
        assert result['status'] == 'normal'
        assert result['balance'] == 500.0
        assert result['alert_level'] == 'none'
    
    def test_check_balance_low(self):
        """Тест перевірки низького балансу"""
        self.mock_client.get_balance.return_value = {
            'success': True,
            'data': '50.00'
        }
        
        result = self.controller.check_balance()
        
        assert result['status'] == 'low'
        assert result['balance'] == 50.0
        assert result['alert_level'] == 'warning'
    
    def test_check_balance_critical(self):
        """Тест перевірки критично низького балансу"""
        self.mock_client.get_balance.return_value = {
            'success': True,
            'data': '5.00'
        }
        
        result = self.controller.check_balance()
        
        assert result['status'] == 'critical'
        assert result['balance'] == 5.0
        assert result['alert_level'] == 'critical'
    
    def test_generate_financial_report(self):
        """Тест генерації фінансового звіту"""
        # Mock balance
        self.mock_client.get_balance.return_value = {
            'success': True,
            'data': '1000.00'
        }
        
        # Mock campaigns
        self.mock_client.get_campaigns.return_value = {
            'success': True,
            'data': {
                'result': [
                    {'id': 123, 'name': 'Campaign 1'},
                    {'id': 456, 'name': 'Campaign 2'}
                ]
            }
        }
        
        report = self.controller.generate_financial_report()
        
        assert 'balance_status' in report
        assert 'total_campaigns' in report
        assert 'recommendations' in report
        assert report['balance_status']['balance'] == 1000.0
        assert report['total_campaigns'] == 2
    
    def test_budget_alerts(self):
        """Тест бюджетних алертів"""
        # Mock низький баланс
        self.mock_client.get_balance.return_value = {
            'success': True,
            'data': '25.00'
        }
        
        alerts = self.controller.check_budget_alerts()
        
        assert len(alerts) > 0
        assert any('low balance' in alert.lower() for alert in alerts)


if __name__ == '__main__':
    # Запуск тестів
    pytest.main([
        __file__,
        '-v',
        '--tb=short'
    ])
