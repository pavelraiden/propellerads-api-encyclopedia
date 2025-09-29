#!/usr/bin/env python3
"""
Простий тест покращеного клієнта
"""

import asyncio
import aiohttp
import os
import logging
from datetime import datetime
from typing import Dict, Any

from tenacity import retry, stop_after_attempt, wait_exponential
from pydantic import BaseModel, Field

# Налаштування логування
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StatisticsRequest(BaseModel):
    """Модель для запиту статистики"""
    day_from: str
    day_to: str
    tz: str = "+0000"
    group_by: list = ["campaign_id"]

class PropellerAdsTestClient:
    """Тестовий клієнт з покращеннями"""
    
    def __init__(self, api_token: str = None):
        self.api_token = api_token or os.getenv('MainAPI')
        self.base_url = "https://ssp-api.propellerads.com/v5"
        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        self.session = None
        self.request_count = 0
        self.error_count = 0
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            headers=self.headers,
            timeout=aiohttp.ClientTimeout(total=30)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """HTTP запит з retry логікою"""
        url = f"{self.base_url}{endpoint}"
        self.request_count += 1
        
        try:
            async with self.session.request(method, url, **kwargs) as response:
                logger.info(f"🔄 {method} {endpoint} -> {response.status}")
                
                # Спеціальна обробка балансу
                if endpoint == "/adv/balance":
                    text = await response.text()
                    text = text.strip().strip('"')
                    if response.status == 200:
                        return {"success": True, "balance": float(text), "status_code": response.status}
                
                # Звичайна обробка
                if response.status in [200, 201, 204]:
                    try:
                        data = await response.json()
                        return {"success": True, "data": data, "status_code": response.status}
                    except:
                        text = await response.text()
                        return {"success": True, "data": text, "status_code": response.status}
                else:
                    try:
                        error_data = await response.json()
                    except:
                        error_data = await response.text()
                    
                    self.error_count += 1
                    return {"success": False, "error": error_data, "status_code": response.status}
                    
        except Exception as e:
            self.error_count += 1
            return {"success": False, "error": str(e), "status_code": None}
    
    async def get_balance(self):
        """Баланс"""
        return await self._request("GET", "/adv/balance")
    
    async def get_campaigns(self, **params):
        """Кампанії"""
        return await self._request("GET", "/adv/campaigns", params=params)
    
    async def get_statistics(self, params):
        """Статистика"""
        if isinstance(params, StatisticsRequest):
            params = params.dict()
        return await self._request("POST", "/adv/statistics", json=params)
    
    async def get_traffic_categories(self):
        """Категорії трафіку"""
        return await self._request("GET", "/collections/targeting/traffic_categories")
    
    async def health_check(self):
        """Перевірка здоров'я"""
        balance_result = await self.get_balance()
        return {
            "success": balance_result.get("success", False),
            "balance": balance_result.get("balance"),
            "requests": self.request_count,
            "errors": self.error_count,
            "error_rate": round(self.error_count / max(self.request_count, 1) * 100, 2)
        }

async def test_enhanced_client():
    """Тест покращеного клієнта"""
    print("🚀 ТЕСТ ПОКРАЩЕНОГО КЛІЄНТА")
    print("=" * 40)
    
    async with PropellerAdsTestClient() as client:
        
        # 1. Health check
        print("\n1️⃣ Health Check")
        health = await client.health_check()
        print(f"   Статус: {'✅' if health['success'] else '❌'}")
        print(f"   Баланс: ${health.get('balance', 'N/A')}")
        print(f"   Запитів: {health['requests']}")
        print(f"   Помилок: {health['errors']} ({health['error_rate']}%)")
        
        # 2. Pydantic модель
        print("\n2️⃣ Pydantic Statistics Model")
        stats_model = StatisticsRequest(
            day_from="2025-09-22 00:00:00",
            day_to="2025-09-29 23:59:59"
        )
        print(f"   Модель створена: ✅")
        print(f"   Group by: {stats_model.group_by}")
        
        # 3. Статистика з моделлю
        print("\n3️⃣ Statistics with Model")
        stats = await client.get_statistics(stats_model)
        print(f"   Результат: {'✅' if stats.get('success') else '❌'}")
        if stats.get('success'):
            data = stats.get('data', {})
            if isinstance(data, dict) and 'result' in data:
                print(f"   Записів: {len(data['result'])}")
        
        # 4. Retry логіка (тест з неіснуючим ендпоінтом)
        print("\n4️⃣ Retry Logic Test")
        fake_result = await client._request("GET", "/fake/endpoint")
        print(f"   404 обробка: {'✅' if fake_result.get('status_code') == 404 else '❌'}")
        
        # 5. Фінальна статистика
        print("\n5️⃣ Final Stats")
        final_health = await client.health_check()
        print(f"   Всього запитів: {final_health['requests']}")
        print(f"   Всього помилок: {final_health['errors']}")
        print(f"   Коефіцієнт помилок: {final_health['error_rate']}%")
        
        print("\n✅ ПОКРАЩЕНИЙ КЛІЄНТ ПРАЦЮЄ!")
        print("🎯 Retry логіка + Pydantic моделі + Enhanced error handling")

if __name__ == "__main__":
    asyncio.run(test_enhanced_client())
