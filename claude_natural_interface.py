#!/usr/bin/env python3
"""
Advanced Natural Language Interface for Claude-PropellerAds Integration

This provides a natural language interface where you can talk to Claude
in plain text about PropellerAds campaign management.
"""

import os
import asyncio
import json
import re
from typing import Dict, Any, List, Optional
from claude_propellerads_integration import ClaudePropellerAdsIntegration

class ClaudeNaturalInterface:
    """Natural language interface for Claude-PropellerAds integration"""
    
    def __init__(self):
        self.integration = ClaudePropellerAdsIntegration()
        self.conversation_history = []
        print("🤖 Claude Natural Language Interface Ready!")
        print("=" * 60)
        print("💬 Говорите со мной естественным языком о PropellerAds!")
        print("📝 Примеры:")
        print("   • 'Покажи баланс аккаунта'")
        print("   • 'Создай кампанию для мобильного трафика в США'")
        print("   • 'Оптимизируй ставки для кампании 123'")
        print("   • 'Добавь Россию в блеклист кампании 456'")
        print("   • 'Покажи статистику за последнюю неделю'")
        print("=" * 60)
        self._show_account_status()
    
    def _show_account_status(self):
        """Show initial account status"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self.integration.get_balance())
            loop.close()
            if result["success"]:
                print(f"💰 Текущий баланс: {result['balance']['formatted']}")
            print()
        except:
            print("💰 Баланс: Загружается...")
            print()
    
    def _extract_intent(self, text: str) -> Dict[str, Any]:
        """Extract intent from natural language text"""
        text = text.lower().strip()
        
        # Balance queries
        if any(word in text for word in ['баланс', 'balance', 'деньги', 'средства']):
            return {'intent': 'balance', 'params': {}}
        
        # Campaign queries
        if any(word in text for word in ['кампани', 'campaign']):
            if any(word in text for word in ['создай', 'создать', 'create', 'новая', 'new']):
                return self._extract_campaign_creation(text)
            elif any(word in text for word in ['список', 'list', 'покажи', 'show']):
                return {'intent': 'list_campaigns', 'params': {}}
            elif any(word in text for word in ['удали', 'delete', 'убери']):
                return self._extract_campaign_id(text, 'delete_campaign')
            elif any(word in text for word in ['оптимизируй', 'optimize', 'улучши']):
                return self._extract_campaign_id(text, 'optimize_campaign')
            elif any(word in text for word in ['детали', 'details', 'информация', 'info']):
                return self._extract_campaign_id(text, 'campaign_details')
        
        # Statistics queries
        if any(word in text for word in ['статистика', 'stats', 'отчет', 'report', 'аналитика']):
            return self._extract_statistics_request(text)
        
        # Targeting/Blacklist/Whitelist
        if any(word in text for word in ['блеклист', 'blacklist', 'заблокируй', 'block']):
            return self._extract_blacklist_request(text)
        
        if any(word in text for word in ['вайтлист', 'whitelist', 'разреши', 'allow']):
            return self._extract_whitelist_request(text)
        
        # Bid optimization
        if any(word in text for word in ['ставк', 'bid', 'цена', 'price']):
            return self._extract_bid_optimization(text)
        
        # Creative management
        if any(word in text for word in ['креатив', 'creative', 'объявление', 'ad']):
            return self._extract_creative_request(text)
        
        # Overview/Status
        if any(word in text for word in ['обзор', 'overview', 'статус', 'status', 'общая']):
            return {'intent': 'overview', 'params': {}}
        
        # Help
        if any(word in text for word in ['помощь', 'help', 'что можешь', 'команды']):
            return {'intent': 'help', 'params': {}}
        
        return {'intent': 'unknown', 'params': {'text': text}}
    
    def _extract_campaign_creation(self, text: str) -> Dict[str, Any]:
        """Extract campaign creation parameters"""
        params = {}
        
        # Extract countries
        countries = []
        if 'сша' in text or 'usa' in text or 'америк' in text:
            countries.append('US')
        if 'росси' in text or 'russia' in text or 'рф' in text:
            countries.append('RU')
        if 'герман' in text or 'germany' in text:
            countries.append('DE')
        if 'франц' in text or 'france' in text:
            countries.append('FR')
        
        # Extract device types
        devices = []
        if 'мобильн' in text or 'mobile' in text or 'телефон' in text:
            devices.append('mobile')
        if 'десктоп' in text or 'desktop' in text or 'компьютер' in text:
            devices.append('desktop')
        if 'планшет' in text or 'tablet' in text:
            devices.append('tablet')
        
        # Extract budget
        budget_match = re.search(r'(\$?\d+)', text)
        budget = int(budget_match.group(1).replace('$', '')) if budget_match else 100
        
        # Extract campaign name
        name = f"Campaign {len(countries)}geo {len(devices)}dev ${budget}"
        
        params = {
            'name': name,
            'countries': countries,
            'devices': devices,
            'budget': budget
        }
        
        return {'intent': 'create_campaign', 'params': params}
    
    def _extract_campaign_id(self, text: str, intent: str) -> Dict[str, Any]:
        """Extract campaign ID from text"""
        # Look for numbers in text
        numbers = re.findall(r'\d+', text)
        campaign_id = int(numbers[0]) if numbers else None
        
        return {'intent': intent, 'params': {'campaign_id': campaign_id}}
    
    def _extract_statistics_request(self, text: str) -> Dict[str, Any]:
        """Extract statistics request parameters"""
        params = {}
        
        # Extract time period
        if 'неделя' in text or 'week' in text:
            params['days_back'] = 7
        elif 'месяц' in text or 'month' in text:
            params['days_back'] = 30
        elif 'день' in text or 'day' in text or 'сегодня' in text:
            params['days_back'] = 1
        else:
            params['days_back'] = 7
        
        # Extract campaign ID if specified
        numbers = re.findall(r'\d+', text)
        if numbers:
            params['campaign_id'] = int(numbers[0])
        
        return {'intent': 'statistics', 'params': params}
    
    def _extract_blacklist_request(self, text: str) -> Dict[str, Any]:
        """Extract blacklist request"""
        params = {}
        
        # Extract campaign ID
        numbers = re.findall(r'\d+', text)
        if numbers:
            params['campaign_id'] = int(numbers[0])
        
        # Extract countries to blacklist
        countries = []
        if 'росси' in text or 'russia' in text:
            countries.append('RU')
        if 'китай' in text or 'china' in text:
            countries.append('CN')
        if 'индия' in text or 'india' in text:
            countries.append('IN')
        
        params['countries'] = countries
        
        return {'intent': 'blacklist', 'params': params}
    
    def _extract_whitelist_request(self, text: str) -> Dict[str, Any]:
        """Extract whitelist request"""
        params = {}
        
        # Extract campaign ID
        numbers = re.findall(r'\d+', text)
        if numbers:
            params['campaign_id'] = int(numbers[0])
        
        # Extract countries to whitelist
        countries = []
        if 'сша' in text or 'usa' in text:
            countries.append('US')
        if 'герман' in text or 'germany' in text:
            countries.append('DE')
        if 'франц' in text or 'france' in text:
            countries.append('FR')
        
        params['countries'] = countries
        
        return {'intent': 'whitelist', 'params': params}
    
    def _extract_bid_optimization(self, text: str) -> Dict[str, Any]:
        """Extract bid optimization request"""
        params = {}
        
        # Extract campaign ID
        numbers = re.findall(r'\d+', text)
        if numbers:
            params['campaign_id'] = int(numbers[0])
        
        # Extract bid change
        if 'увеличь' in text or 'increase' in text or 'повыс' in text:
            params['action'] = 'increase'
        elif 'уменьш' in text or 'decrease' in text or 'сниз' in text:
            params['action'] = 'decrease'
        else:
            params['action'] = 'optimize'
        
        return {'intent': 'bid_optimization', 'params': params}
    
    def _extract_creative_request(self, text: str) -> Dict[str, Any]:
        """Extract creative management request"""
        params = {}
        
        if 'создай' in text or 'create' in text:
            return {'intent': 'create_creative', 'params': params}
        elif 'список' in text or 'list' in text:
            return {'intent': 'list_creatives', 'params': params}
        
        return {'intent': 'creative_info', 'params': params}
    
    async def process_natural_language(self, text: str) -> str:
        """Process natural language input and return response"""
        # Extract intent
        intent_data = self._extract_intent(text)
        intent = intent_data['intent']
        params = intent_data['params']
        
        try:
            if intent == 'balance':
                result = await self.integration.get_balance()
                if result['success']:
                    return f"💰 Ваш текущий баланс: {result['balance']['formatted']}"
                else:
                    return f"❌ Ошибка получения баланса: {result['error']}"
            
            elif intent == 'list_campaigns':
                result = await self.integration.get_campaigns()
                if result['success']:
                    campaigns = result['campaigns']
                    response = f"📋 Найдено {len(campaigns)} кампаний:\n"
                    for i, campaign in enumerate(campaigns[:5], 1):
                        name = campaign.get('name', 'Без названия')
                        status = campaign.get('status', 'Неизвестно')
                        campaign_id = campaign.get('id', 'N/A')
                        response += f"  {i}. {name} (ID: {campaign_id}, Статус: {status})\n"
                    if len(campaigns) > 5:
                        response += f"  ... и еще {len(campaigns) - 5} кампаний"
                    return response
                else:
                    return f"❌ Ошибка получения кампаний: {result['error']}"
            
            elif intent == 'create_campaign':
                # Simulate campaign creation
                name = params.get('name', 'Новая кампания')
                countries = params.get('countries', ['US'])
                devices = params.get('devices', ['mobile'])
                budget = params.get('budget', 100)
                
                response = f"🎯 Создаю кампанию '{name}'...\n"
                response += f"🌍 Страны: {', '.join(countries)}\n"
                response += f"📱 Устройства: {', '.join(devices)}\n"
                response += f"💰 Бюджет: ${budget}/день\n"
                response += f"✅ Кампания будет создана (демо режим)"
                return response
            
            elif intent == 'campaign_details':
                campaign_id = params.get('campaign_id')
                if campaign_id:
                    result = await self.integration.get_campaign_details(campaign_id)
                    if result['success']:
                        campaign = result['campaign']
                        name = campaign.get('name', 'Неизвестно')
                        status = campaign.get('status', 'Неизвестно')
                        return f"📋 Кампания {campaign_id}:\n  Название: {name}\n  Статус: {status}"
                    else:
                        return f"❌ Кампания {campaign_id} не найдена"
                else:
                    return "❌ Укажите ID кампании"
            
            elif intent == 'optimize_campaign':
                campaign_id = params.get('campaign_id')
                if campaign_id:
                    result = await self.integration.analyze_campaign_performance(campaign_id)
                    if result['success']:
                        analysis = result['analysis']
                        response = f"🔍 Анализ кампании {campaign_id}:\n"
                        response += f"📊 CTR: {analysis.get('ctr', 'N/A')}%\n"
                        response += f"💰 Общие затраты: ${analysis.get('total_cost', 'N/A')}\n"
                        
                        recommendations = analysis.get('recommendations', [])
                        if recommendations:
                            response += "💡 Рекомендации:\n"
                            for rec in recommendations[:3]:
                                response += f"  • {rec}\n"
                        
                        return response
                    else:
                        return f"❌ Не удалось проанализировать кампанию {campaign_id}"
                else:
                    return "❌ Укажите ID кампании для оптимизации"
            
            elif intent == 'statistics':
                days_back = params.get('days_back', 7)
                campaign_id = params.get('campaign_id')
                
                result = await self.integration.get_statistics(days_back, campaign_id)
                if result['success']:
                    period = result['period']
                    response = f"📊 Статистика за {period}:\n"
                    response += f"📅 Период: {result['date_range']['from']} - {result['date_range']['to']}\n"
                    if campaign_id:
                        response += f"🎯 Кампания: {campaign_id}\n"
                    response += "✅ Данные получены успешно"
                    return response
                else:
                    return f"❌ Ошибка получения статистики: {result['error']}"
            
            elif intent == 'blacklist':
                campaign_id = params.get('campaign_id')
                countries = params.get('countries', [])
                
                if campaign_id and countries:
                    response = f"🚫 Добавляю в блеклист кампании {campaign_id}:\n"
                    response += f"🌍 Страны: {', '.join(countries)}\n"
                    response += "✅ Изменения будут применены (демо режим)"
                    return response
                else:
                    return "❌ Укажите ID кампании и страны для блокировки"
            
            elif intent == 'whitelist':
                campaign_id = params.get('campaign_id')
                countries = params.get('countries', [])
                
                if campaign_id and countries:
                    response = f"✅ Добавляю в вайтлист кампании {campaign_id}:\n"
                    response += f"🌍 Страны: {', '.join(countries)}\n"
                    response += "✅ Изменения будут применены (демо режим)"
                    return response
                else:
                    return "❌ Укажите ID кампании и страны для разрешения"
            
            elif intent == 'bid_optimization':
                campaign_id = params.get('campaign_id')
                action = params.get('action', 'optimize')
                
                if campaign_id:
                    response = f"💰 Оптимизация ставок для кампании {campaign_id}:\n"
                    if action == 'increase':
                        response += "📈 Увеличиваю ставки на 10%\n"
                    elif action == 'decrease':
                        response += "📉 Уменьшаю ставки на 10%\n"
                    else:
                        response += "🎯 Автоматическая оптимизация ставок\n"
                    response += "✅ Изменения будут применены (демо режим)"
                    return response
                else:
                    return "❌ Укажите ID кампании для оптимизации ставок"
            
            elif intent == 'overview':
                result = await self.integration.get_account_overview()
                if result['success']:
                    overview = result['overview']
                    balance = overview.get('balance', {})
                    campaigns = overview.get('campaigns', {})
                    
                    response = f"📊 Обзор аккаунта:\n"
                    response += f"💰 Баланс: ${balance.get('amount', 'N/A')} {balance.get('currency', '')}\n"
                    response += f"📋 Кампании: {campaigns.get('total', 0)} всего, {campaigns.get('active', 0)} активных\n"
                    response += f"📈 Статус: {overview.get('status', 'Неизвестно')}"
                    return response
                else:
                    return f"❌ Ошибка получения обзора: {result['error']}"
            
            elif intent == 'help':
                return """📚 Доступные команды (естественным языком):

💰 БАЛАНС И АККАУНТ:
  • "Покажи баланс аккаунта"
  • "Общий обзор аккаунта"

📋 КАМПАНИИ:
  • "Покажи список кампаний"
  • "Создай кампанию для мобильного трафика в США с бюджетом $200"
  • "Покажи детали кампании 123"
  • "Оптимизируй кампанию 456"

📊 СТАТИСТИКА:
  • "Покажи статистику за неделю"
  • "Статистика кампании 123 за месяц"

🎯 ТАРГЕТИНГ:
  • "Добавь Россию в блеклист кампании 123"
  • "Разреши трафик из США для кампании 456"

💰 СТАВКИ:
  • "Увеличь ставки для кампании 123"
  • "Оптимизируй ставки кампании 456"

Говорите естественным языком! 🗣️"""
            
            else:
                return f"🤔 Не понял запрос: '{text}'\n💡 Попробуйте: 'помощь' для списка команд"
        
        except Exception as e:
            return f"❌ Ошибка обработки: {str(e)}"
    
    async def run_interactive(self):
        """Run interactive natural language loop"""
        print("💬 Начинаем разговор! Говорите естественным языком.")
        print("Напишите 'выход' или 'quit' для завершения\n")
        
        while True:
            try:
                user_input = input("Вы: ").strip()
                
                if user_input.lower() in ["выход", "quit", "exit", "пока", "bye"]:
                    print("👋 До свидания! Удачных кампаний!")
                    break
                
                if not user_input:
                    continue
                
                print("🤖 Claude: Обрабатываю...")
                response = await self.process_natural_language(user_input)
                print(f"🤖 Claude: {response}")
                print()
                
                # Add to conversation history
                self.conversation_history.append({
                    'user': user_input,
                    'claude': response
                })
                
            except KeyboardInterrupt:
                print("\n👋 До свидания!")
                break
            except Exception as e:
                print(f"❌ Ошибка: {e}")

async def main():
    """Main function"""
    interface = ClaudeNaturalInterface()
    await interface.run_interactive()

if __name__ == "__main__":
    asyncio.run(main())
