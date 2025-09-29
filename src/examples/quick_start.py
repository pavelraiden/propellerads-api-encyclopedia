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
    client = PropellerAdsUltimateClient()
    
    # 1. Перевірка здоров'я API
    print("1️⃣ Перевірка здоров'я API...")
    health = client.health_check()
    print(f"   Статус: {health['overall_health']}")
    
    # 2. Баланс акаунта
    print("\n2️⃣ Баланс акаунта...")
    balance = client.get_balance()
    if balance["success"]:
        print(f"   💰 Баланс: ${balance['data']}")
    
    # 3. Список кампаній
    print("\n3️⃣ Список кампаній...")
    campaigns = client.get_campaigns(page_size=5)
    if campaigns["success"]:
        campaigns_list = campaigns["data"]["result"]
        print(f"   📊 Знайдено кампаній: {len(campaigns_list)}")
        
        for campaign in campaigns_list[:3]:  # Показуємо перші 3
            status_text = "Активна" if campaign["status"] == 1 else "На паузі"
            print(f"   - {campaign['name']} (ID: {campaign['id']}) - {status_text}")
    
    # 4. Доступні країни
    print("\n4️⃣ Доступні країни...")
    countries = client.get_countries()
    if countries["success"]:
        countries_list = countries["data"]["result"]
        print(f"   🌍 Доступно країн: {len(countries_list)}")
        print(f"   Приклади: {', '.join([c['text'] for c in countries_list[:5]])}")
    
    # 5. Операційні системи
    print("\n5️⃣ Операційні системи...")
    os_list = client.get_operating_systems()
    if os_list["success"]:
        os_data = os_list["data"]["result"]
        print(f"   💻 Доступно ОС: {len(os_data)}")
        print(f"   Приклади: {', '.join([os['text'] for os in os_data[:5]])}")
    
    # 6. Браузери
    print("\n6️⃣ Браузери...")
    browsers = client.get_browsers()
    if browsers["success"]:
        browsers_data = browsers["data"]["result"]
        print(f"   🌐 Доступно браузерів: {len(browsers_data)}")
        print(f"   Приклади: {', '.join([b['text'] for b in browsers_data[:5]])}")
    
    print("\n✅ Quick Start завершено!")
    print("\n💡 Наступні кроки:")
    print("   - Вивчіть docs/api-reference.md для повного списку методів")
    print("   - Запустіть workflows/campaign_monitoring.py для моніторингу")
    print("   - Запустіть workflows/financial_control.py для фінансового контролю")

if __name__ == "__main__":
    quick_start_demo()
