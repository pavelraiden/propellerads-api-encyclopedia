#!/usr/bin/env python3
"""
PropellerAds Financial Control Workflow
Фінансовий контроль та алерти
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from propellerads_client import PropellerAdsUltimateClient
from datetime import datetime, timedelta
import json

class FinancialController:
    """Клас для фінансового контролю PropellerAds акаунта"""
    
    def __init__(self, api_key: str = None):
        self.client = PropellerAdsUltimateClient(api_key)
        self.alerts = []
        
        # Налаштування лімітів (можна винести в конфіг)
        self.balance_limits = {
            "critical": 50.0,    # Критичний рівень
            "low": 100.0,        # Низький рівень  
            "medium": 500.0,     # Середній рівень
            "optimal": 1000.0    # Оптимальний рівень
        }
    
    def run_financial_control(self) -> dict:
        """Запуск повного фінансового контролю"""
        print("💰 ЗАПУСК ФІНАНСОВОГО КОНТРОЛЮ")
        print("=" * 40)
        
        control_results = {
            "timestamp": datetime.now().isoformat(),
            "current_balance": None,
            "balance_status": None,
            "spending_analysis": None,
            "campaigns_cost_analysis": [],
            "alerts": [],
            "recommendations": [],
            "actions_taken": []
        }
        
        # 1. Перевірка поточного балансу
        print("1️⃣ Перевірка поточного балансу...")
        balance_info = self.check_current_balance()
        control_results.update(balance_info)
        
        # 2. Аналіз витрат по кампаніях
        print("2️⃣ Аналіз витрат по кампаніях...")
        campaigns_analysis = self.analyze_campaigns_costs()
        control_results["campaigns_cost_analysis"] = campaigns_analysis
        
        # 3. Генерація алертів та рекомендацій
        print("3️⃣ Генерація алертів та рекомендацій...")
        alerts_and_recs = self.generate_financial_alerts_and_recommendations(control_results)
        control_results["alerts"] = alerts_and_recs["alerts"]
        control_results["recommendations"] = alerts_and_recs["recommendations"]
        
        # 4. Автоматичні дії (якщо потрібно)
        print("4️⃣ Перевірка необхідності автоматичних дій...")
        actions = self.execute_automatic_actions(control_results)
        control_results["actions_taken"] = actions
        
        # 5. Вивід результатів
        self.print_financial_summary(control_results)
        
        return control_results
    
    def check_current_balance(self) -> dict:
        """Перевірка поточного балансу"""
        balance_result = self.client.get_balance()
        
        if not balance_result["success"]:
            return {
                "current_balance": None,
                "balance_status": "ERROR",
                "error": balance_result.get("error", "Unknown error")
            }
        
        current_balance = float(balance_result["data"])
        balance_status = self.determine_balance_status(current_balance)
        
        print(f"   💰 Поточний баланс: ${current_balance}")
        print(f"   📊 Статус балансу: {balance_status}")
        
        return {
            "current_balance": current_balance,
            "balance_status": balance_status
        }
    
    def determine_balance_status(self, balance: float) -> str:
        """Визначення статусу балансу"""
        if balance < self.balance_limits["critical"]:
            return "CRITICAL"
        elif balance < self.balance_limits["low"]:
            return "LOW"
        elif balance < self.balance_limits["medium"]:
            return "MEDIUM"
        elif balance < self.balance_limits["optimal"]:
            return "GOOD"
        else:
            return "EXCELLENT"
    
    def analyze_campaigns_costs(self) -> list:
        """Аналіз витрат по кампаніях"""
        campaigns_analysis = []
        
        # Отримуємо список кампаній
        campaigns_result = self.client.get_campaigns(page_size=100)
        
        if not campaigns_result["success"]:
            print(f"   ❌ Помилка отримання кампаній: {campaigns_result.get('error')}")
            return campaigns_analysis
        
        campaigns = campaigns_result["data"]["result"]
        print(f"   📊 Аналіз {len(campaigns)} кампаній...")
        
        for campaign in campaigns:
            campaign_id = campaign["id"]
            campaign_name = campaign["name"]
            
            analysis = {
                "id": campaign_id,
                "name": campaign_name,
                "status": campaign["status"],
                "rate_model": campaign.get("rate_model", "unknown"),
                "rates_configured": False,
                "estimated_daily_spend": 0.0,
                "risk_level": "LOW",
                "issues": []
            }
            
            # Аналіз ставок кампанії
            rates_result = self.client.get_campaign_rates(campaign_id)
            if rates_result["success"] and rates_result["data"]:
                analysis["rates_configured"] = True
                
                # Простий розрахунок потенційних витрат
                rates = rates_result["data"]
                if isinstance(rates, list) and rates:
                    # Беремо середню ставку
                    total_amount = sum(float(rate.get("amount", 0)) for rate in rates)
                    avg_rate = total_amount / len(rates)
                    
                    # Оцінюємо денні витрати (приблизно)
                    # Припускаємо 1000 показів на день при CPM або 100 кліків при CPC
                    if campaign.get("rate_model") == "cpm":
                        estimated_daily = (avg_rate * 1000) / 1000  # CPM
                    else:
                        estimated_daily = avg_rate * 100  # CPC/CPA
                    
                    analysis["estimated_daily_spend"] = round(estimated_daily, 2)
                    
                    # Визначення рівня ризику
                    if estimated_daily > 100:
                        analysis["risk_level"] = "HIGH"
                        analysis["issues"].append("Високі потенційні денні витрати")
                    elif estimated_daily > 50:
                        analysis["risk_level"] = "MEDIUM"
                        analysis["issues"].append("Середні потенційні денні витрати")
            else:
                analysis["issues"].append("Ставки не налаштовані")
            
            # Перевірка статусу кампанії
            if analysis["status"] == 1 and not analysis["rates_configured"]:
                analysis["issues"].append("Активна кампанія без налаштованих ставок")
                analysis["risk_level"] = "HIGH"
            
            campaigns_analysis.append(analysis)
        
        return campaigns_analysis
    
    def generate_financial_alerts_and_recommendations(self, results: dict) -> dict:
        """Генерація фінансових алертів та рекомендацій"""
        alerts = []
        recommendations = []
        
        current_balance = results.get("current_balance", 0)
        balance_status = results.get("balance_status", "UNKNOWN")
        campaigns_analysis = results.get("campaigns_cost_analysis", [])
        
        # Алерти по балансу
        if balance_status == "CRITICAL":
            alerts.append({
                "type": "BALANCE_CRITICAL",
                "severity": "CRITICAL",
                "message": f"Критично низький баланс: ${current_balance}. Кампанії можуть зупинитися!",
                "timestamp": datetime.now().isoformat()
            })
            recommendations.append({
                "type": "FINANCIAL",
                "priority": "CRITICAL",
                "message": "НЕГАЙНО поповніть баланс мінімум на $100"
            })
        elif balance_status == "LOW":
            alerts.append({
                "type": "BALANCE_LOW",
                "severity": "HIGH",
                "message": f"Низький баланс: ${current_balance}. Рекомендується поповнення",
                "timestamp": datetime.now().isoformat()
            })
            recommendations.append({
                "type": "FINANCIAL",
                "priority": "HIGH",
                "message": "Поповніть баланс до $500 для стабільної роботи"
            })
        elif balance_status == "MEDIUM":
            recommendations.append({
                "type": "FINANCIAL",
                "priority": "MEDIUM",
                "message": "Розгляньте поповнення балансу до оптимального рівня ($1000+)"
            })
        
        # Аналіз ризиків по кампаніях
        high_risk_campaigns = [c for c in campaigns_analysis if c["risk_level"] == "HIGH"]
        medium_risk_campaigns = [c for c in campaigns_analysis if c["risk_level"] == "MEDIUM"]
        
        if high_risk_campaigns:
            alerts.append({
                "type": "HIGH_SPEND_RISK",
                "severity": "HIGH",
                "message": f"{len(high_risk_campaigns)} кампаній з високими потенційними витратами",
                "timestamp": datetime.now().isoformat()
            })
            recommendations.append({
                "type": "CAMPAIGNS",
                "priority": "HIGH",
                "message": f"Перевірити налаштування {len(high_risk_campaigns)} кампаній з високими витратами"
            })
        
        if medium_risk_campaigns:
            recommendations.append({
                "type": "CAMPAIGNS",
                "priority": "MEDIUM",
                "message": f"Моніторити {len(medium_risk_campaigns)} кампаній з середніми витратами"
            })
        
        # Аналіз загальних потенційних витрат
        total_estimated_daily = sum(c.get("estimated_daily_spend", 0) for c in campaigns_analysis)
        days_remaining = current_balance / total_estimated_daily if total_estimated_daily > 0 else float('inf')
        
        if days_remaining < 3:
            alerts.append({
                "type": "BUDGET_DEPLETION",
                "severity": "CRITICAL",
                "message": f"При поточних витратах баланс вистачить на {days_remaining:.1f} днів",
                "timestamp": datetime.now().isoformat()
            })
        elif days_remaining < 7:
            alerts.append({
                "type": "BUDGET_WARNING",
                "severity": "HIGH",
                "message": f"При поточних витратах баланс вистачить на {days_remaining:.1f} днів",
                "timestamp": datetime.now().isoformat()
            })
        
        return {"alerts": alerts, "recommendations": recommendations}
    
    def execute_automatic_actions(self, results: dict) -> list:
        """Виконання автоматичних дій (якщо налаштовано)"""
        actions_taken = []
        
        # Поки що тільки логування, без реальних дій
        # В майбутньому можна додати:
        # - Автоматичну паузу кампаній при критичному балансі
        # - Відправку email/SMS алертів
        # - Інтеграцію з системами поповнення балансу
        
        balance_status = results.get("balance_status")
        
        if balance_status == "CRITICAL":
            actions_taken.append({
                "action": "LOG_CRITICAL_BALANCE",
                "message": "Зафіксовано критичний рівень балансу",
                "timestamp": datetime.now().isoformat()
            })
            
            # Тут можна додати реальні дії:
            # self.pause_high_risk_campaigns(results)
            # self.send_critical_alert_notification()
        
        return actions_taken
    
    def print_financial_summary(self, results: dict):
        """Вивід фінансового підсумку"""
        print("\n" + "="*40)
        print("💰 ФІНАНСОВИЙ ПІДСУМОК")
        print("="*40)
        
        # Баланс
        balance = results.get("current_balance", 0)
        status = results.get("balance_status", "UNKNOWN")
        status_emoji = {
            "EXCELLENT": "🟢",
            "GOOD": "🟡", 
            "MEDIUM": "🟠",
            "LOW": "🔴",
            "CRITICAL": "🚨",
            "ERROR": "❌"
        }
        
        print(f"{status_emoji.get(status, '❓')} Баланс: ${balance} ({status})")
        
        # Аналіз кампаній
        campaigns = results.get("campaigns_cost_analysis", [])
        if campaigns:
            total_estimated = sum(c.get("estimated_daily_spend", 0) for c in campaigns)
            high_risk = len([c for c in campaigns if c["risk_level"] == "HIGH"])
            medium_risk = len([c for c in campaigns if c["risk_level"] == "MEDIUM"])
            
            print(f"📊 Кампанії: {len(campaigns)} всього")
            print(f"   Оцінені денні витрати: ${total_estimated:.2f}")
            print(f"   Високий ризик: {high_risk} кампаній")
            print(f"   Середній ризик: {medium_risk} кампаній")
            
            if total_estimated > 0:
                days_remaining = balance / total_estimated
                print(f"   Баланс вистачить на: {days_remaining:.1f} днів")
        
        # Алерти
        alerts = results.get("alerts", [])
        if alerts:
            print(f"\n🚨 Алерти ({len(alerts)}):")
            for alert in alerts:
                severity_emoji = {"CRITICAL": "🚨", "HIGH": "⚠️", "MEDIUM": "⚡"}
                print(f"   {severity_emoji.get(alert['severity'], '📢')} {alert['message']}")
        
        # Рекомендації
        recommendations = results.get("recommendations", [])
        if recommendations:
            print(f"\n💡 Рекомендації ({len(recommendations)}):")
            for rec in recommendations:
                priority_emoji = {"CRITICAL": "🚨", "HIGH": "⚠️", "MEDIUM": "💡"}
                print(f"   {priority_emoji.get(rec['priority'], '📝')} {rec['message']}")
        
        print("\n✅ Фінансовий контроль завершено!")

def main():
    """Основна функція для запуску фінансового контролю"""
    try:
        controller = FinancialController()
        results = controller.run_financial_control()
        
        # Збереження результатів
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"financial_control_{timestamp}.json"
        
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\n📁 Результати збережено в: {filename}")
        
        return results
        
    except Exception as e:
        print(f"❌ Помилка фінансового контролю: {e}")
        return None

if __name__ == "__main__":
    main()
