# Знахідки з PropellerAds MCP репозиторію

**Джерело:** https://github.com/JanNafta/propellerads-mcp

## 🔍 Ключові відкриття:

### 1. Правильні ендпоінти для кампаній:
```python
# GET кампанії з фільтрами
async def get_campaigns(self, **filters) -> Dict[str, Any]:
    return await self._request("GET", "/adv/campaigns", params=filters)

# GET конкретна кампанія
async def get_campaign(self, campaign_id: int) -> Dict[str, Any]:
    return await self._request("GET", f"/adv/campaigns/{campaign_id}")

# POST створення кампанії
async def create_campaign(self, campaign_data: Dict[str, Any]) -> Dict[str, Any]:
    return await self._request("POST", "/adv/campaigns", json=campaign_data)

# PATCH оновлення кампанії
async def update_campaign(self, campaign_id: int, update_data: Dict[str, Any]) -> Dict[str, Any]:
    return await self._request("PATCH", f"/adv/campaigns/{campaign_id}", json=update_data)
```

### 2. Управління кампаніями:
```python
# Запуск кампаній
async def start_campaigns(self, campaign_ids: List[int]) -> Dict[str, Any]:
    return await self._request("PUT", "/adv/campaigns/play", json={"campaign_ids": campaign_ids})

# Зупинка кампаній  
async def stop_campaigns(self, campaign_ids: List[int]) -> Dict[str, Any]:
    return await self._request("PUT", "/adv/campaigns/stop", json={"campaign_ids": campaign_ids})
```

### 3. Управління ставками:
```python
# Отримання ставок кампанії
async def get_campaign_rates(self, campaign_id: int, only_active: int = 1) -> Dict[str, Any]:
    params = {"only_active": only_active}
    return await self._request("GET", f"/adv/campaigns/{campaign_id}/rates/", params=params)

# Встановлення ставок
async def set_campaign_rates(self, campaign_id: int, rates: List[Dict[str, Any]]) -> Dict[str, Any]:
    return await self._request("PUT", f"/adv/campaigns/{campaign_id}/rates/", json={"rates": rates})

# Зональні ставки
async def get_zone_rates(self, campaign_id: int, only_active: int = 1) -> Dict[str, Any]:
    return await self._request("GET", f"/adv/campaigns/{campaign_id}/zone-rates/", params=params)
```

### 4. Правильна авторизація:
```python
def __init__(self, api_token: str, base_url: str = None):
    self.api_token = api_token
    self.base_url = base_url or "https://ssp-api.propellerads.com/v5"
    
    # Правильні заголовки
    self.headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json", 
        "Accept": "application/json"
    }
```

### 5. Обробка помилок:
```python
# Спеціальна обробка для балансу (повертає plain string)
if endpoint == "/adv/balance":
    text = response.text.strip()
    if text.startswith('"') and text.endswith('"'):
        text = text[1:-1]  # Видаляємо лапки
    return text

# Стандартна обробка JSON
return response.json()
```

### 6. Статистика (можливі параметри):
- Використовує POST запити до `/adv/statistics`
- Підтримує різні group_by параметри
- Має спеціальну обробку дат та часових зон

## 🎯 Важливі інсайти:

### Чому POST запити не працюють у нас:
1. **Async/Await:** MCP використовує асинхронні запити
2. **Спеціальна обробка помилок:** Детальна обробка різних статус кодів
3. **Правильні параметри:** Точні назви полів та структура даних

### Можливі рішення:
1. **Перевірити async підхід** - можливо API краще працює з асинхронними запитами
2. **Додати спеціальну обробку балансу** - він повертає plain text
3. **Використати точні параметри** з MCP коду
4. **Додати retry логіку** для нестабільних ендпоінтів

## 📋 Для тестування:
- Спробувати async версію клієнта
- Перевірити точні параметри для створення кампанії
- Протестувати управління ставками (можливо працює краще)
- Використати спеціальну обробку для різних ендпоінтів

**Дата:** 29 вересня 2025  
**Статус:** Потребує додаткового тестування з async підходом
