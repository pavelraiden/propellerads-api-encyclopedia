# Інтеграція PropellerAds з Binom

**Повний гід по інтеграції PropellerAds API з Binom для AI агентів**

## 🎯 Концепція інтеграції

### Архітектура системи
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   PropellerAds  │    │    AI Agent     │    │     Binom       │
│   (Traffic)     │◄──►│   (Control)     │◄──►│   (Tracking)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
        │                        │                        │
        ▼                        ▼                        ▼
   • Кампанії              • Аналіз даних           • Трекінг ссылки
   • Таргетинг             • Оптимізація            • Статистика
   • Ставки                • Автоматизація          • Конверсії
   • Баланс                • Алерти                 • ROI аналіз
```

### Потік даних
1. **PropellerAds** → створює кампанії та налаштовує таргетинг
2. **Binom** → генерує трекінгові ссылки для кампаній
3. **AI Agent** → аналізує дані з обох систем та оптимізує
4. **Циклічна оптимізація** → на основі результатів з Binom

## 🔗 Базова інтеграція

### 1. Налаштування клієнтів
```python
from propellerads_client import PropellerAdsUltimateClient
from binom_client import BinomClient  # З binom-api-encyclopedia

# Ініціалізація клієнтів
propeller = PropellerAdsUltimateClient()
binom = BinomClient()

# Перевірка підключень
propeller_health = propeller.health_check()
binom_health = binom.health_check()

print(f"PropellerAds: {propeller_health['overall_health']}")
print(f"Binom: {binom_health['status']}")
```

### 2. Створення інтегрованої кампанії
```python
def create_integrated_campaign(campaign_data):
    """Створення кампанії з інтеграцією PropellerAds + Binom"""
    
    # 1. Створення кампанії в Binom (спочатку для отримання ссылки)
    binom_campaign = binom.create_campaign({
        "name": campaign_data["name"],
        "traffic_source": "PropellerAds",
        "cost_model": campaign_data.get("rate_model", "cpm"),
        "cost_value": campaign_data.get("default_rate", 0.5)
    })
    
    if not binom_campaign["success"]:
        raise Exception(f"Помилка створення Binom кампанії: {binom_campaign['error']}")
    
    # Отримуємо трекінгову ссылку
    tracking_url = binom_campaign["data"]["url"]
    
    # 2. Створення кампанії в PropellerAds з Binom ссылкою
    propeller_campaign_data = {
        **campaign_data,
        "target_url": tracking_url  # Використовуємо Binom ссылку
    }
    
    propeller_campaign = propeller.create_campaign(propeller_campaign_data)
    
    if not propeller_campaign["success"]:
        # Якщо PropellerAds не вдалося, видаляємо Binom кампанію
        binom.delete_campaign(binom_campaign["data"]["id"])
        raise Exception(f"Помилка створення PropellerAds кампанії: {propeller_campaign['error']}")
    
    # 3. Оновлюємо Binom кампанію з PropellerAds ID
    binom.update_campaign(binom_campaign["data"]["id"], {
        "external_id": propeller_campaign["data"]["id"],
        "notes": f"PropellerAds Campaign ID: {propeller_campaign['data']['id']}"
    })
    
    return {
        "propeller_campaign_id": propeller_campaign["data"]["id"],
        "binom_campaign_id": binom_campaign["data"]["id"],
        "tracking_url": tracking_url,
        "integration_status": "success"
    }
```

## 📊 Синхронізація даних

### 1. Синхронізація статистики
```python
def sync_campaign_statistics(propeller_id, binom_id, date_from, date_to):
    """Синхронізація статистики між PropellerAds та Binom"""
    
    # Отримання статистики з PropellerAds
    propeller_stats = propeller.get_statistics(
        day_from=date_from,
        day_to=date_to,
        campaign_ids=[propeller_id],
        group_by=["campaign_id", "day"]
    )
    
    # Отримання статистики з Binom
    binom_stats = binom.get_campaign_stats(
        campaign_id=binom_id,
        date_from=date_from,
        date_to=date_to
    )
    
    # Об'єднання даних
    combined_stats = {
        "propeller_data": {
            "impressions": propeller_stats.get("impressions", 0),
            "clicks": propeller_stats.get("clicks", 0),
            "spend": propeller_stats.get("spend", 0),
            "ctr": propeller_stats.get("ctr", 0)
        },
        "binom_data": {
            "visits": binom_stats.get("visits", 0),
            "conversions": binom_stats.get("conversions", 0),
            "revenue": binom_stats.get("revenue", 0),
            "roi": binom_stats.get("roi", 0)
        }
    }
    
    # Розрахунок інтегрованих метрик
    combined_stats["integrated_metrics"] = {
        "conversion_rate": combined_stats["binom_data"]["conversions"] / max(combined_stats["propeller_data"]["clicks"], 1),
        "cost_per_conversion": combined_stats["propeller_data"]["spend"] / max(combined_stats["binom_data"]["conversions"], 1),
        "profit": combined_stats["binom_data"]["revenue"] - combined_stats["propeller_data"]["spend"]
    }
    
    return combined_stats
```

### 2. Автоматична оптимізація
```python
class IntegratedCampaignOptimizer:
    """Оптимізатор кампаній на базі даних з обох систем"""
    
    def __init__(self, propeller_client, binom_client):
        self.propeller = propeller_client
        self.binom = binom_client
    
    def optimize_campaign(self, propeller_id, binom_id):
        """Оптимізація кампанії на базі даних з обох систем"""
        
        # Отримання даних
        stats = sync_campaign_statistics(
            propeller_id, binom_id,
            date_from=(datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S"),
            date_to=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        
        optimization_actions = []
        
        # Аналіз ROI
        roi = stats["binom_data"]["roi"]
        if roi < 0:
            # Негативний ROI - зменшуємо ставки або паузимо
            if roi < -50:  # Критичні втрати
                self.propeller.stop_campaigns([propeller_id])
                optimization_actions.append("Кампанія зупинена через критичні втрати")
            else:
                # Зменшуємо ставки на 20%
                current_rates = self.propeller.get_campaign_rates(propeller_id)
                if current_rates["success"]:
                    for rate in current_rates["data"]:
                        new_amount = float(rate["amount"]) * 0.8
                        # Оновлення ставки (якщо API підтримує)
                        optimization_actions.append(f"Ставка зменшена до ${new_amount:.3f}")
        
        elif roi > 100:  # Дуже прибуткова кампанія
            # Збільшуємо ставки на 15%
            optimization_actions.append("Ставки збільшені через високий ROI")
        
        # Аналіз CTR
        ctr = stats["propeller_data"]["ctr"]
        if ctr < 0.5:  # Низький CTR
            optimization_actions.append("Рекомендується оновити креативи - низький CTR")
        
        # Аналіз конверсій
        conversion_rate = stats["integrated_metrics"]["conversion_rate"]
        if conversion_rate < 0.01:  # Менше 1% конверсій
            optimization_actions.append("Рекомендується перевірити лендинг - низька конверсія")
        
        return {
            "campaign_stats": stats,
            "optimization_actions": optimization_actions,
            "recommendations": self.generate_recommendations(stats)
        }
    
    def generate_recommendations(self, stats):
        """Генерація рекомендацій на базі аналізу"""
        recommendations = []
        
        # Рекомендації по трафіку
        if stats["propeller_data"]["ctr"] < 1.0:
            recommendations.append({
                "type": "CREATIVE",
                "message": "Низький CTR. Спробуйте нові креативи або змініть таргетинг"
            })
        
        # Рекомендації по конверсіях
        if stats["integrated_metrics"]["conversion_rate"] < 0.02:
            recommendations.append({
                "type": "LANDING",
                "message": "Низька конверсія. Оптимізуйте лендинг або змініть оффер"
            })
        
        # Рекомендації по прибутковості
        profit = stats["integrated_metrics"]["profit"]
        if profit > 0:
            recommendations.append({
                "type": "SCALING",
                "message": f"Прибуток ${profit:.2f}. Розгляньте масштабування кампанії"
            })
        
        return recommendations
```

## 🤖 AI-керована автоматизація

### 1. Інтелектуальний моніторинг
```python
class AIIntegratedMonitor:
    """AI-керований моніторинг інтегрованих кампаній"""
    
    def __init__(self, propeller_client, binom_client, ai_client=None):
        self.propeller = propeller_client
        self.binom = binom_client
        self.ai = ai_client  # Claude/GPT клієнт для аналізу
        self.optimizer = IntegratedCampaignOptimizer(propeller_client, binom_client)
    
    def run_ai_analysis(self, campaign_pairs):
        """Запуск AI аналізу для списку кампаній"""
        
        analysis_results = []
        
        for pair in campaign_pairs:
            propeller_id = pair["propeller_id"]
            binom_id = pair["binom_id"]
            
            # Отримання даних
            optimization_result = self.optimizer.optimize_campaign(propeller_id, binom_id)
            
            # AI аналіз (якщо доступний)
            if self.ai:
                ai_insights = self.get_ai_insights(optimization_result)
                optimization_result["ai_insights"] = ai_insights
            
            analysis_results.append({
                "propeller_id": propeller_id,
                "binom_id": binom_id,
                "analysis": optimization_result
            })
        
        return analysis_results
    
    def get_ai_insights(self, optimization_data):
        """Отримання AI інсайтів через Claude/GPT"""
        
        if not self.ai:
            return {"error": "AI клієнт не налаштований"}
        
        # Підготовка даних для AI
        prompt = f"""
        Проаналізуй результати рекламної кампанії та дай рекомендації:
        
        Статистика PropellerAds:
        - Покази: {optimization_data['campaign_stats']['propeller_data']['impressions']}
        - Кліки: {optimization_data['campaign_stats']['propeller_data']['clicks']}
        - Витрати: ${optimization_data['campaign_stats']['propeller_data']['spend']}
        - CTR: {optimization_data['campaign_stats']['propeller_data']['ctr']}%
        
        Статистика Binom:
        - Візити: {optimization_data['campaign_stats']['binom_data']['visits']}
        - Конверсії: {optimization_data['campaign_stats']['binom_data']['conversions']}
        - Дохід: ${optimization_data['campaign_stats']['binom_data']['revenue']}
        - ROI: {optimization_data['campaign_stats']['binom_data']['roi']}%
        
        Інтегровані метрики:
        - Конверсія: {optimization_data['campaign_stats']['integrated_metrics']['conversion_rate']*100:.2f}%
        - Вартість конверсії: ${optimization_data['campaign_stats']['integrated_metrics']['cost_per_conversion']:.2f}
        - Прибуток: ${optimization_data['campaign_stats']['integrated_metrics']['profit']:.2f}
        
        Дай конкретні рекомендації для оптимізації.
        """
        
        try:
            ai_response = self.ai.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            return {
                "insights": ai_response.content[0].text,
                "generated_at": datetime.now().isoformat()
            }
        except Exception as e:
            return {"error": f"Помилка AI аналізу: {str(e)}"}
```

## 📋 Готові воркфлоу інтеграції

### 1. Повний цикл кампанії
```python
def full_campaign_lifecycle():
    """Повний цикл кампанії: створення → моніторинг → оптимізація"""
    
    # 1. Створення інтегрованої кампанії
    campaign_data = {
        "name": "AI Test Campaign",
        "direction": "onclick",
        "rate_model": "cpm",
        "default_rate": 0.5,
        "targeting": {
            "country": {"list": ["US"], "is_excluded": False},
            "traffic_categories": {"list": ["mainstream"], "is_excluded": False}
        }
    }
    
    integrated_campaign = create_integrated_campaign(campaign_data)
    print(f"✅ Кампанія створена: PropellerAds ID {integrated_campaign['propeller_campaign_id']}")
    
    # 2. Моніторинг (кожні 4 години)
    monitor = AIIntegratedMonitor(propeller, binom)
    
    for day in range(7):  # Тиждень моніторингу
        time.sleep(4 * 3600)  # 4 години
        
        analysis = monitor.run_ai_analysis([{
            "propeller_id": integrated_campaign['propeller_campaign_id'],
            "binom_id": integrated_campaign['binom_campaign_id']
        }])
        
        print(f"📊 День {day + 1}: {len(analysis[0]['analysis']['optimization_actions'])} дій оптимізації")
    
    print("✅ Повний цикл завершено")
```

### 2. Масове управління кампаніями
```python
def bulk_campaign_management():
    """Масове управління інтегрованими кампаніями"""
    
    # Отримання всіх кампаній
    propeller_campaigns = propeller.get_campaigns(page_size=100)
    binom_campaigns = binom.get_campaigns()
    
    # Знаходження пар (PropellerAds ↔ Binom)
    campaign_pairs = []
    for p_campaign in propeller_campaigns["data"]["result"]:
        for b_campaign in binom_campaigns["data"]:
            if str(p_campaign["id"]) in b_campaign.get("notes", ""):
                campaign_pairs.append({
                    "propeller_id": p_campaign["id"],
                    "binom_id": b_campaign["id"],
                    "name": p_campaign["name"]
                })
    
    print(f"🔗 Знайдено {len(campaign_pairs)} інтегрованих кампаній")
    
    # Масовий аналіз та оптимізація
    monitor = AIIntegratedMonitor(propeller, binom)
    results = monitor.run_ai_analysis(campaign_pairs)
    
    # Підсумок
    total_actions = sum(len(r["analysis"]["optimization_actions"]) for r in results)
    profitable_campaigns = sum(1 for r in results 
                             if r["analysis"]["campaign_stats"]["integrated_metrics"]["profit"] > 0)
    
    print(f"📊 Результати масового управління:")
    print(f"   Всього дій оптимізації: {total_actions}")
    print(f"   Прибуткових кампаній: {profitable_campaigns}/{len(campaign_pairs)}")
    
    return results
```

## 🔧 Налаштування та конфігурація

### 1. Конфігураційний файл
```yaml
# config/integration.yaml
propellerads:
  api_key: "${MainAPI}"
  base_url: "https://ssp-api.propellerads.com/v5"
  rate_limits:
    get: 30
    post: 150

binom:
  api_key: "${binomPublic}"
  base_url: "https://pierdun.com/public/api/v1"
  timezone: "UTC"

integration:
  sync_interval: 3600  # 1 година
  optimization_interval: 14400  # 4 години
  ai_analysis: true
  auto_optimization: false  # Безпека: тільки рекомендації

monitoring:
  balance_alerts:
    critical: 50
    low: 100
    medium: 500
  roi_thresholds:
    stop_campaign: -50
    reduce_bids: 0
    increase_bids: 100
```

### 2. Запуск інтеграції
```python
# integration_runner.py
import yaml
from propellerads_client import PropellerAdsUltimateClient
from binom_client import BinomClient

def load_config():
    with open("config/integration.yaml", "r") as f:
        return yaml.safe_load(f)

def main():
    config = load_config()
    
    # Ініціалізація клієнтів
    propeller = PropellerAdsUltimateClient(config["propellerads"]["api_key"])
    binom = BinomClient(config["binom"]["api_key"])
    
    # Запуск інтегрованого моніторингу
    monitor = AIIntegratedMonitor(propeller, binom)
    
    # Основний цикл
    while True:
        try:
            # Отримання кампаній для моніторингу
            campaign_pairs = get_integrated_campaigns()
            
            # Запуск аналізу
            results = monitor.run_ai_analysis(campaign_pairs)
            
            # Збереження результатів
            save_analysis_results(results)
            
            # Очікування до наступного циклу
            time.sleep(config["integration"]["sync_interval"])
            
        except Exception as e:
            print(f"❌ Помилка інтеграції: {e}")
            time.sleep(300)  # 5 хвилин перерви при помилці

if __name__ == "__main__":
    main()
```

## 🎯 Висновки

### Переваги інтеграції:
- **Повний контроль** над рекламними кампаніями
- **Автоматична оптимізація** на базі реальних даних
- **AI-керований аналіз** для кращих рішень
- **Єдина система** для трафіку та трекінгу

### Рекомендації:
1. **Почніть з тестових кампаній** для відлагодження інтеграції
2. **Налаштуйте алерти** для критичних ситуацій
3. **Використовуйте AI аналіз** для глибших інсайтів
4. **Регулярно оновлюйте** конфігурацію оптимізації

---

**📅 Останнє оновлення:** 29 вересня 2025  
**🔗 Інтеграція:** PropellerAds + Binom + AI  
**✅ Статус:** Готово до використання
