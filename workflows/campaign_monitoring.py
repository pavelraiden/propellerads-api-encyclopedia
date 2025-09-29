#!/usr/bin/env python3
"""
PropellerAds Campaign Monitoring Workflow
Повний моніторинг кампаній з аналітикою
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from propellerads_client import PropellerAdsUltimateClient
from datetime import datetime, timedelta
import json

class CampaignMonitor:
    """Клас для моніторингу кампаній PropellerAds"""
    
    def __init__(self, api_key: str = None):
        self.client = PropellerAdsUltimateClient(api_key)
        self.alerts = []
    
    def run_full_monitoring(self) -> dict:
        """Запуск повного моніторингу"""
        print("🚀 ЗАПУСК ПОВНОГО МОНІТОРИНГУ КАМПАНІЙ")
        print("=" * 50)
        
        monitoring_results = {
            "timestamp": datetime.now().isoformat(),
            "api_health": None,
            "account_balance": None,
            "campaigns_summary": None,
            "campaigns_details": [],
            "alerts": [],
            "recommendations": []
        }
        
        # 1. Перевірка здоров'я API
        print("1️⃣ Перевірка здоров'я API...")
        health = self.client.health_check()
        monitoring_results["api_health"] = health
        
        if health["overall_health"] != "healthy":
            self.add_alert("API_HEALTH", "API не в здоровому стані", "HIGH")
        
        # 2. Перевірка балансу
        print("2️⃣ Перевірка балансу акаунта...")
        balance = self.client.get_balance()
        if balance["success"]:
            current_balance = float(balance["data"])
            monitoring_results["account_balance"] = current_balance
            
            # Алерти по балансу
            if current_balance < 50:
                self.add_alert("LOW_BALANCE", f"Критично низький баланс: ${current_balance}", "CRITICAL")
            elif current_balance < 100:
                self.add_alert("LOW_BALANCE", f"Низький баланс: ${current_balance}", "HIGH")
            elif current_balance < 500:
                self.add_alert("MEDIUM_BALANCE", f"Середній баланс: ${current_balance}", "MEDIUM")
            
            print(f"   💰 Поточний баланс: ${current_balance}")
        
        # 3. Аналіз кампаній
        print("3️⃣ Аналіз кампаній...")
        campaigns = self.client.get_campaigns(page_size=100)
        
        if campaigns["success"]:
            campaigns_list = campaigns["data"]["result"]
            monitoring_results["campaigns_summary"] = {
                "total_campaigns": len(campaigns_list),
                "active_campaigns": 0,
                "paused_campaigns": 0,
                "campaigns_with_issues": 0
            }
            
            print(f"   📊 Знайдено кампаній: {len(campaigns_list)}")
            
            # Детальний аналіз кожної кампанії
            for campaign in campaigns_list:
                campaign_analysis = self.analyze_campaign(campaign)
                monitoring_results["campaigns_details"].append(campaign_analysis)
                
                # Підрахунок статистики
                if campaign_analysis["status"] == 1:
                    monitoring_results["campaigns_summary"]["active_campaigns"] += 1
                else:
                    monitoring_results["campaigns_summary"]["paused_campaigns"] += 1
                
                if campaign_analysis["issues"]:
                    monitoring_results["campaigns_summary"]["campaigns_with_issues"] += 1
        
        # 4. Додавання алертів до результатів
        monitoring_results["alerts"] = self.alerts
        
        # 5. Генерація рекомендацій
        monitoring_results["recommendations"] = self.generate_recommendations(monitoring_results)
        
        # 6. Вивід результатів
        self.print_monitoring_summary(monitoring_results)
        
        return monitoring_results
    
    def analyze_campaign(self, campaign: dict) -> dict:
        """Детальний аналіз окремої кампанії"""
        campaign_id = campaign["id"]
        campaign_name = campaign["name"]
        
        print(f"   🔍 Аналіз кампанії: {campaign_name} (ID: {campaign_id})")
        
        analysis = {
            "id": campaign_id,
            "name": campaign_name,
            "status": campaign["status"],
            "direction": campaign.get("direction", "unknown"),
            "rate_model": campaign.get("rate_model", "unknown"),
            "issues": [],
            "recommendations": [],
            "full_info": None
        }
        
        # Отримання повної інформації
        try:
            full_info = self.client.get_campaign_full_info(campaign_id)
            if full_info["success"]:
                analysis["full_info"] = full_info["data"]
                
                # Аналіз ставок
                rates = full_info["data"].get("rates", [])
                if not rates:
                    analysis["issues"].append("Не налаштовані ставки")
                    analysis["recommendations"].append("Налаштувати ставки для кампанії")
                
                # Аналіз таргетингу зон
                included_zones = full_info["data"].get("included_zones", [])
                excluded_zones = full_info["data"].get("excluded_zones", [])
                
                if not included_zones and not excluded_zones:
                    analysis["issues"].append("Не налаштований таргетинг зон")
                    analysis["recommendations"].append("Налаштувати включені або виключені зони")
                
                # Аналіз підзон
                included_sub_zones = full_info["data"].get("included_sub_zones", [])
                excluded_sub_zones = full_info["data"].get("excluded_sub_zones", [])
                
                if len(included_sub_zones) > 1000:
                    analysis["issues"].append("Занадто багато включених підзон")
                    analysis["recommendations"].append("Оптимізувати список включених підзон")
                
        except Exception as e:
            analysis["issues"].append(f"Помилка отримання повної інформації: {str(e)}")
        
        # Перевірка статусу кампанії
        if analysis["status"] == 0:
            analysis["issues"].append("Кампанія на паузі")
            analysis["recommendations"].append("Перевірити причину паузи та запустити при необхідності")
        
        return analysis
    
    def add_alert(self, alert_type: str, message: str, severity: str):
        """Додавання алерту"""
        alert = {
            "type": alert_type,
            "message": message,
            "severity": severity,
            "timestamp": datetime.now().isoformat()
        }
        self.alerts.append(alert)
        
        # Вивід алерту
        severity_emoji = {
            "CRITICAL": "🚨",
            "HIGH": "⚠️",
            "MEDIUM": "⚡",
            "LOW": "ℹ️"
        }
        print(f"   {severity_emoji.get(severity, '📢')} {severity}: {message}")
    
    def generate_recommendations(self, results: dict) -> list:
        """Генерація рекомендацій на основі аналізу"""
        recommendations = []
        
        # Рекомендації по балансу
        balance = results.get("account_balance", 0)
        if balance < 100:
            recommendations.append({
                "type": "FINANCIAL",
                "priority": "HIGH",
                "message": "Поповніть баланс акаунта для безперервної роботи кампаній"
            })
        
        # Рекомендації по кампаніях
        summary = results.get("campaigns_summary", {})
        if summary.get("campaigns_with_issues", 0) > 0:
            recommendations.append({
                "type": "CAMPAIGNS",
                "priority": "MEDIUM",
                "message": f"Виправити проблеми в {summary['campaigns_with_issues']} кампаніях"
            })
        
        if summary.get("paused_campaigns", 0) > summary.get("active_campaigns", 0):
            recommendations.append({
                "type": "CAMPAIGNS",
                "priority": "MEDIUM",
                "message": "Більшість кампаній на паузі - перевірити причини"
            })
        
        # Рекомендації по API
        if results.get("api_health", {}).get("overall_health") != "healthy":
            recommendations.append({
                "type": "TECHNICAL",
                "priority": "HIGH",
                "message": "Перевірити стан PropellerAds API"
            })
        
        return recommendations
    
    def print_monitoring_summary(self, results: dict):
        """Вивід підсумку моніторингу"""
        print("\n" + "="*50)
        print("📊 ПІДСУМОК МОНІТОРИНГУ")
        print("="*50)
        
        # API здоров'я
        health = results.get("api_health", {}).get("overall_health", "unknown")
        health_emoji = "✅" if health == "healthy" else "❌"
        print(f"{health_emoji} API Health: {health}")
        
        # Баланс
        balance = results.get("account_balance", 0)
        print(f"💰 Баланс: ${balance}")
        
        # Кампанії
        summary = results.get("campaigns_summary", {})
        print(f"🎯 Кампанії:")
        print(f"   Всього: {summary.get('total_campaigns', 0)}")
        print(f"   Активних: {summary.get('active_campaigns', 0)}")
        print(f"   На паузі: {summary.get('paused_campaigns', 0)}")
        print(f"   З проблемами: {summary.get('campaigns_with_issues', 0)}")
        
        # Алерти
        alerts = results.get("alerts", [])
        if alerts:
            print(f"\n🚨 Алерти ({len(alerts)}):")
            for alert in alerts:
                print(f"   {alert['severity']}: {alert['message']}")
        
        # Рекомендації
        recommendations = results.get("recommendations", [])
        if recommendations:
            print(f"\n💡 Рекомендації ({len(recommendations)}):")
            for rec in recommendations:
                print(f"   {rec['priority']}: {rec['message']}")
        
        print("\n✅ Моніторинг завершено!")

def main():
    """Основна функція для запуску моніторингу"""
    try:
        monitor = CampaignMonitor()
        results = monitor.run_full_monitoring()
        
        # Збереження результатів
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"monitoring_results_{timestamp}.json"
        
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\n📁 Результати збережено в: {filename}")
        
        return results
        
    except Exception as e:
        print(f"❌ Помилка моніторингу: {e}")
        return None

if __name__ == "__main__":
    main()
