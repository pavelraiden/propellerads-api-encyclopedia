#!/usr/bin/env python3
"""
PropellerAds Async API Client
На основі знахідок з MCP репозиторію JanNafta/propellerads-mcp
"""

import asyncio
import aiohttp
import os
import json
from datetime import datetime
from typing import Dict, Any, List, Optional

class PropellerAdsAsyncClient:
    """Асинхронний клієнт для PropellerAds API v5"""
    
    def __init__(self, api_token: str = None, base_url: str = None):
        self.api_token = api_token or os.getenv('MainAPI')
        self.base_url = base_url or "https://ssp-api.propellerads.com/v5"
        
        if not self.api_token:
            raise ValueError("API token is required")
        
        # Правильні заголовки згідно з MCP
        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        # Налаштування клієнта
        self.timeout = aiohttp.ClientTimeout(total=30)
        self.session = None
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            headers=self.headers,
            timeout=self.timeout,
            connector=aiohttp.TCPConnector(limit=10)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Базовий метод для HTTP запитів"""
        if not self.session:
            raise RuntimeError("Client not initialized. Use async with statement.")
        
        # Формуємо URL
        url = f"{self.base_url}{endpoint}"
        
        try:
            async with self.session.request(method, url, **kwargs) as response:
                
                # Логування запиту
                print(f"🔄 {method} {endpoint} -> {response.status}")
                
                # Спеціальна обробка для балансу (повертає plain text)
                if endpoint == "/adv/balance":
                    text = await response.text()
                    text = text.strip()
                    # Видаляємо лапки якщо є
                    if text.startswith('"') and text.endswith('"'):
                        text = text[1:-1]
                    return {"balance": text, "status_code": response.status}
                
                # Обробка успішних відповідей
                if response.status in [200, 201, 204]:
                    try:
                        data = await response.json()
                        return {"success": True, "data": data, "status_code": response.status}
                    except:
                        text = await response.text()
                        return {"success": True, "data": text, "status_code": response.status}
                
                # Обробка помилок
                try:
                    error_data = await response.json()
                    return {
                        "success": False, 
                        "error": error_data, 
                        "status_code": response.status
                    }
                except:
                    text = await response.text()
                    return {
                        "success": False, 
                        "error": text, 
                        "status_code": response.status
                    }
                    
        except asyncio.TimeoutError:
            return {"success": False, "error": "Request timeout", "status_code": 408}
        except Exception as e:
            return {"success": False, "error": str(e), "status_code": None}
    
    # === БАЗОВІ МЕТОДИ ===
    
    async def get_balance(self) -> Dict[str, Any]:
        """Отримання балансу акаунта"""
        return await self._request("GET", "/adv/balance")
    
    # === КАМПАНІЇ ===
    
    async def get_campaigns(self, **filters) -> Dict[str, Any]:
        """Отримання списку кампаній з фільтрами"""
        return await self._request("GET", "/adv/campaigns", params=filters)
    
    async def get_campaign(self, campaign_id: int) -> Dict[str, Any]:
        """Отримання інформації про конкретну кампанію"""
        return await self._request("GET", f"/adv/campaigns/{campaign_id}")
    
    async def create_campaign(self, campaign_data: Dict[str, Any]) -> Dict[str, Any]:
        """Створення нової кампанії"""
        return await self._request("POST", "/adv/campaigns", json=campaign_data)
    
    async def update_campaign(self, campaign_id: int, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Оновлення кампанії"""
        return await self._request("PATCH", f"/adv/campaigns/{campaign_id}", json=update_data)
    
    async def start_campaigns(self, campaign_ids: List[int]) -> Dict[str, Any]:
        """Запуск кампаній"""
        return await self._request("PUT", "/adv/campaigns/play", json={"campaign_ids": campaign_ids})
    
    async def stop_campaigns(self, campaign_ids: List[int]) -> Dict[str, Any]:
        """Зупинка кампаній"""
        return await self._request("PUT", "/adv/campaigns/stop", json={"campaign_ids": campaign_ids})
    
    # === СТАВКИ ===
    
    async def get_campaign_rates(self, campaign_id: int, only_active: int = 1) -> Dict[str, Any]:
        """Отримання ставок кампанії"""
        params = {"only_active": only_active}
        return await self._request("GET", f"/adv/campaigns/{campaign_id}/rates/", params=params)
    
    async def set_campaign_rates(self, campaign_id: int, rates: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Встановлення ставок кампанії"""
        return await self._request("PUT", f"/adv/campaigns/{campaign_id}/rates/", json={"rates": rates})
    
    async def get_zone_rates(self, campaign_id: int, only_active: int = 1) -> Dict[str, Any]:
        """Отримання зональних ставок"""
        params = {"only_active": only_active}
        return await self._request("GET", f"/adv/campaigns/{campaign_id}/zone-rates/", params=params)
    
    # === СТАТИСТИКА ===
    
    async def get_statistics(self, **params) -> Dict[str, Any]:
        """Отримання статистики"""
        return await self._request("POST", "/adv/statistics", json=params)
    
    # === КОЛЕКЦІЇ ===
    
    async def get_countries(self) -> Dict[str, Any]:
        """Отримання списку країн"""
        return await self._request("GET", "/collections/targeting/countries")
    
    async def get_operating_systems(self) -> Dict[str, Any]:
        """Отримання списку ОС"""
        return await self._request("GET", "/collections/targeting/operating_systems")
    
    async def get_browsers(self) -> Dict[str, Any]:
        """Отримання списку браузерів"""
        return await self._request("GET", "/collections/targeting/browsers")
    
    async def get_traffic_categories(self) -> Dict[str, Any]:
        """Отримання категорій трафіку"""
        return await self._request("GET", "/collections/targeting/traffic_categories")

# === ТЕСТУВАННЯ ===

async def test_async_client():
    """Тестування асинхронного клієнта"""
    print("🚀 ТЕСТУВАННЯ ASYNC PROPELLERADS CLIENT")
    print("=" * 50)
    
    async with PropellerAdsAsyncClient() as client:
        
        # 1. Тест балансу
        print("\n1️⃣ Тестування балансу...")
        balance = await client.get_balance()
        print(f"   Результат: {balance}")
        
        # 2. Тест кампаній
        print("\n2️⃣ Тестування списку кампаній...")
        campaigns = await client.get_campaigns(page_size=5)
        print(f"   Статус: {campaigns.get('status_code')}")
        print(f"   Успіх: {campaigns.get('success')}")
        
        if campaigns.get('success') and campaigns.get('data'):
            campaign_data = campaigns['data']
            if isinstance(campaign_data, dict) and 'data' in campaign_data:
                campaigns_list = campaign_data['data'].get('result', [])
                print(f"   Кампаній знайдено: {len(campaigns_list)}")
                
                # Тестуємо управління кампаніями якщо є
                if campaigns_list:
                    campaign_id = campaigns_list[0]['id']
                    print(f"\n3️⃣ Тестування управління кампанією ID: {campaign_id}")
                    
                    # Тест отримання ставок
                    rates = await client.get_campaign_rates(campaign_id)
                    print(f"   Ставки - Статус: {rates.get('status_code')}, Успіх: {rates.get('success')}")
                    
                    # Тест зональних ставок
                    zone_rates = await client.get_zone_rates(campaign_id)
                    print(f"   Зональні ставки - Статус: {zone_rates.get('status_code')}, Успіх: {zone_rates.get('success')}")
        
        # 3. Тест створення кампанії
        print("\n4️⃣ Тестування створення кампанії...")
        
        # Спочатку отримуємо категорії трафіку
        traffic_cats = await client.get_traffic_categories()
        available_cats = ["mainstream"]  # дефолт
        
        print(f"   Traffic cats result: {traffic_cats}")
        
        if traffic_cats.get('success') and traffic_cats.get('data'):
            cats_data = traffic_cats['data']
            print(f"   Cats data type: {type(cats_data)}")
            print(f"   Cats data: {cats_data}")
            
            if isinstance(cats_data, dict) and 'result' in cats_data:
                # Результат - це список рядків, а не об'єктів
                result_list = cats_data['result']
                if result_list and isinstance(result_list, list):
                    available_cats = [result_list[0]]  # Беремо перший елемент
            elif isinstance(cats_data, list):
                available_cats = [cat.get('value', 'mainstream') if isinstance(cat, dict) else str(cat) for cat in cats_data[:1]]
            else:
                print(f"   Unexpected data format, using default")
        
        campaign_data = {
            "name": f"Async Test {int(datetime.now().timestamp())}",
            "direction": "onclick",
            "rate_model": "cpm",
            "target_url": "https://example.com",
            "status": 0,  # Неактивна
            "targeting": {
                "traffic_categories": {
                    "list": available_cats,
                    "is_excluded": False
                }
            }
        }
        
        create_result = await client.create_campaign(campaign_data)
        print(f"   Створення - Статус: {create_result.get('status_code')}, Успіх: {create_result.get('success')}")
        if not create_result.get('success'):
            print(f"   Помилка: {create_result.get('error')}")
        
        # 4. Тест статистики
        print("\n5️⃣ Тестування статистики...")
        stats_params = {
            "day_from": "2025-09-22 00:00:00",
            "day_to": "2025-09-29 23:59:59",
            "tz": "+0000",
            "group_by": ["campaign_id"]
        }
        
        stats = await client.get_statistics(**stats_params)
        print(f"   Статистика - Статус: {stats.get('status_code')}, Успіх: {stats.get('success')}")
        
        # 5. Тест колекцій
        print("\n6️⃣ Тестування колекцій...")
        
        collections_tests = [
            ("Країни", client.get_countries()),
            ("ОС", client.get_operating_systems()),
            ("Браузери", client.get_browsers()),
            ("Категорії трафіку", client.get_traffic_categories())
        ]
        
        for name, coro in collections_tests:
            result = await coro
            print(f"   {name} - Статус: {result.get('status_code')}, Успіх: {result.get('success')}")
    
    print("\n✅ Тестування завершено!")

async def main():
    """Головна функція"""
    try:
        await test_async_client()
    except Exception as e:
        print(f"❌ Помилка тестування: {e}")

if __name__ == "__main__":
    asyncio.run(main())
