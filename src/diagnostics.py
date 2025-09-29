#!/usr/bin/env python3
"""
Детальна діагностика PropellerAds API токена
Базується на рекомендаціях Claude
"""

import requests
import os
import json
from datetime import datetime

API_KEY = os.getenv('MainAPI')
BASE_URL = "https://ssp-api.propellerads.com/v5"

def diagnose_token():
    """Детальна діагностика токена"""
    print("🔍 ДЕТАЛЬНА ДІАГНОСТИКА PropellerAds API ТОКЕНА")
    print("=" * 60)
    
    if not API_KEY:
        print("❌ API ключ не знайдено!")
        return
    
    print(f"🔑 API ключ: ...{API_KEY[-8:]}")
    print(f"🌐 Base URL: {BASE_URL}")
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "PropellerAds-API-Diagnostic/1.0"
    }
    
    print(f"📋 Заголовки: {json.dumps(headers, indent=2)}")
    
    # 1. Спроба отримати інформацію про токен
    print("\n1️⃣ ПЕРЕВІРКА ІНФОРМАЦІЇ ПРО ТОКЕН")
    print("-" * 40)
    
    token_endpoints = [
        "/adv/token/info",
        "/token/info", 
        "/auth/token/info",
        "/user/token/info"
    ]
    
    for endpoint in token_endpoints:
        url = f"{BASE_URL}{endpoint}"
        print(f"Спроба: {endpoint}")
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            print(f"  Статус: {response.status_code}")
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"  ✅ Відповідь: {json.dumps(data, indent=4)}")
                    break
                except:
                    print(f"  ✅ Відповідь (текст): {response.text}")
                    break
            else:
                print(f"  ❌ Помилка: {response.text[:100]}")
        except Exception as e:
            print(f"  ❌ Виключення: {e}")
    
    # 2. Детальна перевірка GET запиту (працює)
    print("\n2️⃣ ДЕТАЛЬНА ПЕРЕВІРКА GET ЗАПИТУ")
    print("-" * 40)
    
    try:
        response = requests.get(f"{BASE_URL}/adv/balance", headers=headers, timeout=10)
        print(f"GET /adv/balance:")
        print(f"  Статус: {response.status_code}")
        print(f"  Заголовки відповіді: {dict(response.headers)}")
        print(f"  Відповідь: {response.text}")
        
        # Перевіряємо специфічні заголовки
        if 'X-RateLimit-Limit' in response.headers:
            print(f"  Rate Limit: {response.headers['X-RateLimit-Limit']}")
        if 'X-RateLimit-Remaining' in response.headers:
            print(f"  Залишилось запитів: {response.headers['X-RateLimit-Remaining']}")
            
    except Exception as e:
        print(f"❌ Помилка GET запиту: {e}")
    
    # 3. Детальна перевірка POST запиту (не працює)
    print("\n3️⃣ ДЕТАЛЬНА ПЕРЕВІРКА POST ЗАПИТУ")
    print("-" * 40)
    
    # Мінімальний POST запит для статистики
    stats_data = {
        "day_from": "2025-09-01 00:00:00",
        "day_to": "2025-09-28 23:59:59",
        "tz": "+0000"
    }
    
    print(f"POST /adv/statistics:")
    print(f"  Дані: {json.dumps(stats_data, indent=2)}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/adv/statistics",
            headers=headers,
            json=stats_data,
            timeout=10
        )
        print(f"  Статус: {response.status_code}")
        print(f"  Заголовки відповіді: {dict(response.headers)}")
        print(f"  Відповідь: {response.text}")
        
        if response.status_code == 400:
            try:
                error_data = response.json()
                print(f"  📋 Деталі помилки: {json.dumps(error_data, indent=4)}")
            except:
                pass
                
    except Exception as e:
        print(f"❌ Помилка POST запиту: {e}")
    
    # 4. Спроба найпростішого POST запиту
    print("\n4️⃣ НАЙПРОСТІШИЙ POST ЗАПИТ")
    print("-" * 40)
    
    simple_campaign = {
        "name": f"Diagnostic Test {int(datetime.now().timestamp())}",
        "direction": "onclick",
        "rate_model": "cpm",
        "target_url": "https://example.com",
        "status": 0  # Пауза
    }
    
    print(f"POST /adv/campaigns (мінімальні дані):")
    print(f"  Дані: {json.dumps(simple_campaign, indent=2)}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/adv/campaigns",
            headers=headers,
            json=simple_campaign,
            timeout=10
        )
        print(f"  Статус: {response.status_code}")
        print(f"  Заголовки відповіді: {dict(response.headers)}")
        print(f"  Відповідь: {response.text}")
        
        if response.status_code == 403:
            print("  🔍 403 Access Denied - підтверджено проблему з правами")
        elif response.status_code == 400:
            try:
                error_data = response.json()
                print(f"  📋 Деталі 400 помилки: {json.dumps(error_data, indent=4)}")
            except:
                pass
                
    except Exception as e:
        print(f"❌ Помилка створення кампанії: {e}")
    
    # 5. Перевірка різних методів авторизації
    print("\n5️⃣ ПЕРЕВІРКА РІЗНИХ МЕТОДІВ АВТОРИЗАЦІЇ")
    print("-" * 40)
    
    auth_variants = [
        {"Authorization": f"Bearer {API_KEY}"},
        {"Authorization": f"Token {API_KEY}"},
        {"X-API-Key": API_KEY},
        {"api-key": API_KEY}
    ]
    
    for i, auth_header in enumerate(auth_variants, 1):
        print(f"Варіант {i}: {auth_header}")
        test_headers = {**headers, **auth_header}
        
        try:
            response = requests.get(f"{BASE_URL}/adv/balance", headers=test_headers, timeout=5)
            print(f"  Статус: {response.status_code}")
            if response.status_code == 200:
                print(f"  ✅ Працює!")
            else:
                print(f"  ❌ Не працює: {response.text[:50]}")
        except Exception as e:
            print(f"  ❌ Помилка: {e}")
    
    # 6. Рекомендації
    print("\n6️⃣ РЕКОМЕНДАЦІЇ")
    print("-" * 40)
    print("Базуючись на діагностиці:")
    print("1. Якщо GET працює, а POST/PUT повертають 403 - проблема в правах токена")
    print("2. Зверніться до менеджера PropellerAds з результатами цієї діагностики")
    print("3. Попросіть перевірити права токена в системі")
    print("4. Можливо потрібен токен з розширеними правами")
    print("5. Перевірте чи є додаткові налаштування в профілі SSP")
    
    print(f"\n📅 Діагностика завершена: {datetime.now().isoformat()}")

if __name__ == "__main__":
    diagnose_token()
