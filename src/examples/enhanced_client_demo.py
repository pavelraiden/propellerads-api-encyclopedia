#!/usr/bin/env python3
"""
Enhanced Client Demo - Simplified Version
Упрощенная демонстрация расширенного клиента
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from propellerads_client import PropellerAdsUltimateClient

def enhanced_demo():
    """Демонстрация расширенных возможностей"""
    
    print("🚀 ENHANCED PROPELLERADS CLIENT DEMO")
    print("=" * 45)
    
    # Инициализация клиента
    api_key = os.getenv('MainAPI')
    if not api_key:
        print("❌ Помилка: Встановіть змінну середовища MainAPI")
        return
    
    client = PropellerAdsUltimateClient(api_key=api_key)
    
    # Демонстрация enterprise features
    print("🔧 Enterprise Features:")
    print("   - Intelligent retry з exponential backoff")
    print("   - Rate limiting з token bucket algorithm") 
    print("   - Circuit breaker pattern")
    print("   - Professional logging з Request IDs")
    print("   - Metrics collection")
    print("   - Connection pooling")
    
    # Тестирование основных функций
    print("\n📊 Тестирование API...")
    
    try:
        # Баланс
        balance = client.get_balance()
        if balance["success"]:
            print(f"   💰 Баланс: ${balance['data']}")
        
        # Кампании
        campaigns = client.get_campaigns(page_size=3)
        if campaigns["success"]:
            count = len(campaigns.get('data', {}).get('result', []))
            print(f"   🎯 Кампаній: {count}")
        
        # Статистика
        stats = client.get_statistics(
            day_from="2025-09-01 00:00:00",
            day_to="2025-09-30 23:59:59",
            tz="+0000"
        )
        status = "✅" if stats.get('success') else "❌"
        print(f"   📈 Статистика: {status}")
        
    except Exception as e:
        print(f"   ❌ Помилка: {e}")
    
    print("\n✅ Enhanced Demo завершено!")

if __name__ == "__main__":
    enhanced_demo()
