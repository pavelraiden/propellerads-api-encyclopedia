#!/usr/bin/env python3
"""
PropellerAds API Quick Start Example
Швидкий приклад використання API клієнта
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from propellerads_client import PropellerAdsUltimateClient

def quick_start_demo():
    """Демонстрація основних можливостей API"""
    
    print("🚀 PROPELLERADS API QUICK START")
    print("=" * 40)
    
    # Ініціалізація клієнта
    api_key = os.getenv('MainAPI')
    if not api_key:
        print("❌ Помилка: Встановіть змінну середовища MainAPI")
        return
    
    client = PropellerAdsUltimateClient(api_key=api_key)
    
    # 1. Перевірка здоров'я API
    print("1️⃣ Перевірка здоров'я API...")
    try:
        health = client.health_check()
        print(f"   Статус: {'✅ Healthy' if health['success'] else '❌ Unhealthy'}")
        if health['success']:
            print(f"   Баланс: ${health.get('balance', 'N/A')}")
            print(f"   Кампаній: {health.get('campaigns_count', 'N/A')}")
    except Exception as e:
        print(f"   ❌ Помилка: {e}")
    
    # 2. Баланс акаунта
    print("\n2️⃣ Баланс акаунта...")
    try:
        balance = client.get_balance()
        if balance["success"]:
            print(f"   💰 Баланс: ${balance['data']}")
        else:
            print(f"   ❌ Помилка: {balance.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"   ❌ Помилка: {e}")
    
    # 3. Список кампаній
    print("\n3️⃣ Список кампаній...")
    try:
        campaigns = client.get_campaigns(page_size=5)
        if campaigns["success"] and campaigns.get('data', {}).get('result'):
            campaigns_list = campaigns["data"]["result"]
            print(f"   📊 Знайдено кампаній: {len(campaigns_list)}")
            
            for campaign in campaigns_list[:3]:  # Показуємо перші 3
                status_text = "Активна" if campaign.get("status") == 1 else "На паузі"
                print(f"   - {campaign.get('name', 'N/A')} (ID: {campaign.get('id', 'N/A')}) - {status_text}")
        else:
            print(f"   ❌ Помилка: {campaigns.get('error', 'No campaigns found')}")
    except Exception as e:
        print(f"   ❌ Помилка: {e}")
    
    # 4. Доступні країни
    print("\n4️⃣ Доступні країни...")
    try:
        countries = client.get_countries()
        if countries["success"] and countries.get('data', {}).get('result'):
            countries_list = countries["data"]["result"]
            print(f"   🌍 Доступно країн: {len(countries_list)}")
            print(f"   Приклади: {', '.join([c.get('text', 'N/A') for c in countries_list[:5]])}")
        else:
            print(f"   ❌ Помилка: {countries.get('error', 'No countries found')}")
    except Exception as e:
        print(f"   ❌ Помилка: {e}")
    
    # 5. Операційні системи
    print("\n5️⃣ Операційні системи...")
    try:
        os_list = client.get_operating_systems()
        if os_list["success"] and os_list.get('data', {}).get('result'):
            os_data = os_list["data"]["result"]
            print(f"   💻 Доступно ОС: {len(os_data)}")
            print(f"   Приклади: {', '.join([os.get('text', 'N/A') for os in os_data[:5]])}")
        else:
            print(f"   ❌ Помилка: {os_list.get('error', 'No OS found')}")
    except Exception as e:
        print(f"   ❌ Помилка: {e}")
    
    # 6. Браузери
    print("\n6️⃣ Браузери...")
    try:
        browsers = client.get_browsers()
        if browsers["success"] and browsers.get('data', {}).get('result'):
            browsers_data = browsers["data"]["result"]
            print(f"   🌐 Доступно браузерів: {len(browsers_data)}")
            print(f"   Приклади: {', '.join([b.get('text', 'N/A') for b in browsers_data[:5]])}")
        else:
            print(f"   ❌ Помилка: {browsers.get('error', 'No browsers found')}")
    except Exception as e:
        print(f"   ❌ Помилка: {e}")
    
    print("\n✅ Quick Start завершено!")
    print("\n💡 Наступні кроки:")
    print("   - Вивчіть docs/api-reference.md для повного списку методів")
    print("   - Запустіть workflows/campaign_monitoring.py для моніторингу")
    print("   - Запустіть workflows/financial_control.py для фінансового контролю")
    print("\n🔧 Enterprise Features:")
    print("   - Intelligent retry з exponential backoff")
    print("   - Rate limiting з token bucket algorithm")
    print("   - Circuit breaker pattern")
    print("   - Professional logging з Request IDs")
    print("   - Metrics collection")
    print("   - Connection pooling")

if __name__ == "__main__":
    quick_start_demo()
