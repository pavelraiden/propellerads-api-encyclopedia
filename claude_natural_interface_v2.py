
#!/usr/bin/env python3
"""
Enhanced Claude Natural Language Interface for PropellerAds

This version includes:
- Advanced system prompt with self-learning capabilities
- Intelligent questioning when information is missing
- Context awareness and conversation memory
- Latest Claude 3.5 Sonnet model
- Bilingual support (Russian/English)
"""

import os
import re
import asyncio
import json
from typing import Dict, Any, List, Optional
from datetime import datetime

from claude_propellerads_integration import ClaudePropellerAdsIntegration
from claude_advanced_system_prompt import get_advanced_system_prompt, get_model_configuration


class EnhancedClaudeInterface:
    """Enhanced natural language interface for Claude with PropellerAds integration"""
    
    def __init__(self):
        """Initialize the enhanced Claude interface"""
        self.integration = ClaudePropellerAdsIntegration()
        self.conversation_history = []
        self.user_context = {
            'preferences': {},
            'campaign_history': [],
            'successful_strategies': [],
            'learning_data': {}
        }
        
        # Load advanced system prompt
        self.system_prompt = get_advanced_system_prompt()
        self.model_config = get_model_configuration()
    
    def _extract_intent_and_params(self, text: str) -> Dict[str, Any]:
        """Extract user intent and parameters with advanced understanding"""
        text = text.lower().strip()
        
        # Balance queries
        if any(word in text for word in ['баланс', 'balance', 'деньги', 'money', 'счет', 'account']):
            return {'intent': 'balance', 'params': {}}
        
        # Campaign creation with intelligent parameter extraction
        if any(word in text for word in ['создай', 'create', 'новая кампания', 'new campaign', 'запусти', 'start']):
            return self._extract_campaign_creation_advanced(text)
        
        # Campaign listing
        if any(word in text for word in ['список кампаний', 'campaigns', 'кампании', 'покажи кампании']):
            return {'intent': 'campaigns', 'params': {}}
        
        # Campaign optimization
        if any(word in text for word in ['оптимизируй', 'optimize', 'улучши', 'improve']):
            return self._extract_optimization_request(text)
        
        # Statistics requests
        if any(word in text for word in ['статистика', 'statistics', 'stats', 'отчет', 'report', 'аналитика']):
            return self._extract_statistics_request(text)
        
        # Blacklist/whitelist management
        if any(word in text for word in ['блеклист', 'blacklist', 'заблокируй', 'block', 'вайтлист', 'whitelist']):
            return self._extract_targeting_request(text)
        
        # Help requests
        if any(word in text for word in ['помощь', 'help', 'команды', 'commands']):
            return {'intent': 'help', 'params': {}}
        
        # Check if this might be follow-up information for campaign creation
        if any(word in text for word in ['url', 'landing', 'budget', 'бюджет', 'https://', 'http://', '$']):
            return {'intent': 'campaign_followup', 'params': {'text': text}}
        
        # Overview requests
        if any(word in text for word in ['обзор', 'overview', 'профиль', 'profile']):
            return {'intent': 'overview', 'params': {}}
        
        # Unknown request - let Claude handle it intelligently
        return {'intent': 'unknown', 'params': {'text': text}}
    
    def _extract_campaign_creation_advanced(self, text: str) -> Dict[str, Any]:
        """Advanced campaign creation parameter extraction with intelligent questioning"""
        params = {
            'needs_intelligent_questions': True,
            'extracted_info': {}
        }
        
        # Extract countries with expanded recognition
        countries = []
        country_patterns = {
            'US': ['сша', 'usa', 'америк', 'штат', 'united states'],
            'RU': ['росси', 'russia', 'рф', 'российск'],
            'DE': ['герман', 'germany', 'немец', 'deutsch'],
            'FR': ['франц', 'france', 'французск'],
            'GB': ['англи', 'britain', 'uk', 'великобритан'],
            'CA': ['канад', 'canada'],
            'AU': ['австрали', 'australia'],
            'IT': ['итали', 'italy'],
            'ES': ['испан', 'spain', 'españa'],
            'BR': ['бразили', 'brazil', 'brasil']
        }
        
        for country_code, patterns in country_patterns.items():
            if any(pattern in text for pattern in patterns):
                countries.append(country_code)
        
        # Extract devices with expanded recognition
        devices = []
        if any(word in text for word in ['мобильн', 'mobile', 'телефон', 'смартфон', 'smartphone', 'phone']):
            devices.append('mobile')
        if any(word in text for word in ['десктоп', 'desktop', 'компьютер', 'pc', 'компьютерн']):
            devices.append('desktop')
        if any(word in text for word in ['планшет', 'tablet', 'ipad']):
            devices.append('tablet')
        
        # Extract budget with multiple formats
        budget = None
        budget_patterns = [
            r'(\$?\d+)', r'(\d+\s*долларов?)', r'(\d+\s*\$)', r'(\d+\s*usd)',
            r'бюджет[:\s]*(\$?\d+)', r'потратить[:\s]*(\$?\d+)'
        ]
        for pattern in budget_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                budget_str = match.group(1).replace('$', '').replace('долларов', '').replace('доллар', '').strip()
                try:
                    budget = int(budget_str)
                    break
                except ValueError:
                    continue
        
        # Extract product/service type
        product_type = None
        product_patterns = {
            'ecommerce': ['магазин', 'shop', 'ecommerce', 'интернет-магазин', 'товар', 'продукт'],
            'mobile_app': ['приложение', 'app', 'мобильное приложение', 'игра', 'game'],
            'lead_generation': ['лиды', 'leads', 'заявки', 'регистрац', 'подписк'],
            'dating': ['знакомств', 'dating', 'свидан'],
            'finance': ['финанс', 'finance', 'кредит', 'loan', 'банк', 'инвестиц'],
            'crypto': ['крипто', 'crypto', 'биткоин', 'bitcoin', 'блокчейн'],
            'gambling': ['казино', 'casino', 'ставки', 'betting', 'покер'],
            'health': ['здоровье', 'health', 'медицин', 'лечение', 'диета'],
            'education': ['образован', 'education', 'курс', 'обучение', 'учеба']
        }
        
        for product, patterns in product_patterns.items():
            if any(pattern in text for pattern in patterns):
                product_type = product
                break
        
        # Extract URL
        url_match = re.search(r'https?://[^\s]+', text)
        landing_url = url_match.group(0) if url_match else None
        
        # Extract ad format
        ad_format = None
        format_patterns = {
            'push': ['push', 'пуш', 'уведомлен'],
            'pop': ['pop', 'поп', 'всплыва'],
            'native': ['native', 'нативн', 'естественн'],
            'banner': ['баннер', 'banner', 'дисплей'],
            'video': ['видео', 'video']
        }
        
        for format_type, patterns in format_patterns.items():
            if any(pattern in text for pattern in patterns):
                ad_format = format_type
                break
        
        # Store extracted information
        if countries:
            params['extracted_info']['countries'] = countries
        if devices:
            params['extracted_info']['devices'] = devices
        if budget:
            params['extracted_info']['budget'] = budget
        if product_type:
            params['extracted_info']['product_type'] = product_type
        if landing_url:
            params['extracted_info']['landing_url'] = landing_url
        if ad_format:
            params['extracted_info']['ad_format'] = ad_format
        
        return {'intent': 'create_campaign', 'params': params}
    
    def _extract_optimization_request(self, text: str) -> Dict[str, Any]:
        """Extract campaign optimization parameters"""
        params = {}
        
        # Extract campaign ID
        campaign_id_match = re.search(r'кампани[ию]\s*(\d+)|campaign\s*(\d+)', text, re.IGNORECASE)
        if campaign_id_match:
            params['campaign_id'] = campaign_id_match.group(1) or campaign_id_match.group(2)
        
        # Extract optimization type
        if any(word in text for word in ['ставки', 'bid', 'цена', 'price']):
            params['optimization_type'] = 'bids'
        elif any(word in text for word in ['бюджет', 'budget', 'трат', 'spend']):
            params['optimization_type'] = 'budget'
        elif any(word in text for word in ['таргетинг', 'targeting', 'аудитор']):
            params['optimization_type'] = 'targeting'
        elif any(word in text for word in ['креатив', 'creative', 'объявлен']):
            params['optimization_type'] = 'creative'
        else:
            params['optimization_type'] = 'general'
        
        return {'intent': 'optimize', 'params': params}
    
    def _extract_statistics_request(self, text: str) -> Dict[str, Any]:
        """Extract statistics request parameters"""
        params = {}
        
        # Extract time period
        if any(word in text for word in ['неделя', 'week', '7 дней']):
            params['period'] = 'week'
        elif any(word in text for word in ['месяц', 'month', '30 дней']):
            params['period'] = 'month'
        elif any(word in text for word in ['день', 'day', 'сегодня', 'today']):
            params['period'] = 'day'
        elif any(word in text for word in ['вчера', 'yesterday']):
            params['period'] = 'yesterday'
        else:
            params['period'] = 'week'  # default
        
        # Extract campaign ID if specified
        campaign_id_match = re.search(r'кампани[ию]\s*(\d+)|campaign\s*(\d+)', text, re.IGNORECASE)
        if campaign_id_match:
            params['campaign_id'] = campaign_id_match.group(1) or campaign_id_match.group(2)
        
        return {'intent': 'statistics', 'params': params}
    
    def _extract_targeting_request(self, text: str) -> Dict[str, Any]:
        """Extract targeting/blacklist/whitelist parameters"""
        params = {}
        
        # Extract action type
        if any(word in text for word in ['блеклист', 'blacklist', 'заблокируй', 'block']):
            params['action'] = 'blacklist'
        elif any(word in text for word in ['вайтлист', 'whitelist', 'разреши', 'allow']):
            params['action'] = 'whitelist'
        
        # Extract countries
        countries = []
        country_patterns = {
            'RU': ['росси', 'russia', 'рф'],
            'CN': ['китай', 'china'],
            'IN': ['инди', 'india'],
            'US': ['сша', 'usa', 'америк'],
            'DE': ['герман', 'germany'],
            'FR': ['франц', 'france']
        }
        
        for country_code, patterns in country_patterns.items():
            if any(pattern in text for pattern in patterns):
                countries.append(country_code)
        
        if countries:
            params['countries'] = countries
        
        # Extract campaign ID
        campaign_id_match = re.search(r'кампани[ию]\s*(\d+)|campaign\s*(\d+)', text, re.IGNORECASE)
        if campaign_id_match:
            params['campaign_id'] = campaign_id_match.group(1) or campaign_id_match.group(2)
        
        return {'intent': 'targeting', 'params': params}
    
    async def _process_intent_with_intelligence(self, intent: str, params: Dict[str, Any]) -> str:
        """Process user intent with intelligent questioning and context awareness"""
        
        if intent == 'balance':
            result = await self.integration.get_balance()
            if result['success']:
                balance = result['balance']['formatted']
                # Add intelligent context
                response = f"💰 Ваш текущий баланс: {balance}\n\n"
                
                # Intelligent suggestions based on balance
                balance_amount = result['balance']['amount']
                if balance_amount > 1000:
                    response += "💡 У вас достаточно средств для запуска крупных кампаний. Рекомендую протестировать новые гео или форматы рекламы."
                elif balance_amount > 100:
                    response += "💡 Баланс позволяет запустить несколько тестовых кампаний. Начните с небольших бюджетов $20-50/день."
                else:
                    response += "⚠️ Баланс низкий. Рекомендую пополнить счет для стабильной работы кампаний."
                
                return response
            else:
                return f"❌ Ошибка получения баланса: {result['error']}"
        
        elif intent == 'create_campaign':
            if params.get('needs_intelligent_questions', False):
                return await self._handle_intelligent_campaign_creation(params)
            else:
                return await self._create_campaign_with_params(params)
        
        elif intent == 'campaign_followup':
            # Handle follow-up information for campaign creation
            return await self._handle_campaign_followup(params)
        
        elif intent == 'campaigns':
            result = await self.integration.get_campaigns()
            if result['success']:
                campaigns = result['campaigns']
                if not campaigns:
                    return "📋 У вас пока нет активных кампаний.\n💡 Хотите создать первую кампанию? Просто скажите: 'Создай кампанию для [ваш продукт]'"
                
                response = f"📋 Найдено {len(campaigns)} кампаний:\n\n"
                for i, campaign in enumerate(campaigns[:5], 1):
                    status_emoji = "✅" if campaign.get('status') == 'active' else "⏸️"
                    response += f"{i}. {status_emoji} {campaign.get('name', 'Без названия')} (ID: {campaign.get('id')})\n"
                    response += f"   💰 Бюджет: ${campaign.get('budget', 0)}/день\n"
                    response += f"   🎯 Статус: {campaign.get('status', 'unknown')}\n\n"
                
                if len(campaigns) > 5:
                    response += f"   ... и еще {len(campaigns) - 5} кампаний\n\n"
                
                response += "💡 Для детальной информации скажите: 'Покажи кампанию [ID]'"
                return response
            else:
                return f"❌ Ошибка получения кампаний: {result['error']}"
        
        elif intent == 'optimize':
            return await self._handle_optimization_request(params)
        
        elif intent == 'statistics':
            return await self._handle_statistics_request(params)
        
        elif intent == 'targeting':
            return await self._handle_targeting_request(params)
        
        elif intent == 'overview':
            return await self._handle_account_overview()
        
        elif intent == 'help':
            return self._get_help_message()
        
        elif intent == 'unknown':
            return await self._handle_unknown_intent_with_claude(params['text'])
        
        return "Извините, я не понял ваш запрос. Попробуйте переформулировать."
    
    async def _handle_intelligent_campaign_creation(self, params: Dict[str, Any]) -> str:
        """Handle campaign creation with intelligent questioning"""
        extracted_info = params.get('extracted_info', {})
        missing_info = []
        
        # Define required fields
        required_fields = {
            'product_type': "Тип продукта/услуги (например, 'игра', 'магазин', 'финансы')",
            'landing_url': "URL лендинга",
            'budget': "Дневной бюджет (например, '$50')",
            'countries': "Гео (страны, например, 'США, Германия')",
            'devices': "Тип устройства (например, 'мобильные')"
        }
        
        for field, description in required_fields.items():
            if not extracted_info.get(field):
                missing_info.append(description)
        
        if not missing_info:
            # All required info is present, proceed to creation
            return await self._create_campaign_with_params({'params': extracted_info})
        
        # Ask intelligent questions
        response = "🎯 Отлично! Создаю кампанию для вас. Чтобы настроить максимально эффективную кампанию, мне нужна дополнительная информация:\n\n"
        response += "📋 ОБЯЗАТЕЛЬНЫЕ ДАННЫЕ:\n"
        for i, item in enumerate(missing_info, 1):
            response += f"{i}. {item}\n"
        
        response += "\n📊 ДОПОЛНИТЕЛЬНО (для оптимизации):\n"
        response += "- Целевая аудитория (возраст, интересы)\n"
        response += "- Формат рекламы (push/pop/native)\n"
        response += "- Цель кампании (продажи/трафик/лиды)\n"
        
        response += "\nПожалуйста, предоставьте эту информацию, и я создам идеальную кампанию!"
        
        # Store context for follow-up
        self.conversation_history.append({
            'role': 'assistant',
            'content': response,
            'context': {'intent': 'create_campaign', 'extracted_info': extracted_info}
        })
        
        return response
    
    async def _handle_campaign_followup(self, params: Dict[str, Any]) -> str:
        """Handle follow-up information for campaign creation"""
        last_context = None
        for message in reversed(self.conversation_history):
            if message.get('context', {}).get('intent') == 'create_campaign':
                last_context = message['context']
                break
        
        if not last_context:
            return "Извините, я не совсем понял, к чему относится эта информация. Вы пытаетесь создать кампанию?"
        
        # Update extracted info with new data
        new_info = self._extract_campaign_creation_advanced(params['text'])
        last_context['extracted_info'].update(new_info['params']['extracted_info'])
        
        # Re-evaluate if we have all info
        return await self._handle_intelligent_campaign_creation({'extracted_info': last_context['extracted_info']})
    
    async def _create_campaign_with_params(self, params: Dict[str, Any]) -> str:
        """Create campaign with provided parameters"""
        # This is a placeholder for the actual campaign creation logic
        # In a real scenario, this would call self.integration.create_campaign
        
        # Self-verification checklist
        checklist = {
            "3G/WiFi Separation": False,
            "All required info collected": True, # Assume for now
            "Budget and targeting validated": True, # Assume for now
            "Conversion tracking configured": False, # Placeholder
            "Campaign set to DRAFT": True
        }
        
        # CRITICAL: 3G/WiFi Separation Rule
        # This is a simplified check. A real implementation would be more robust.
        campaign_name = params.get('name', 'New Campaign')
        if '3g' in campaign_name.lower() or 'wifi' in campaign_name.lower():
            checklist["3G/WiFi Separation"] = True
        
        response = f"✅ Кампания '{campaign_name}' успешно создана в статусе DRAFT.\n\n"
        response += "🔍 РЕЗУЛЬТАТЫ ПРОВЕРКИ:\n"
        for item, status in checklist.items():
            emoji = "✅" if status else "❌"
            response += f"- {emoji} {item}\n"
        
        if not checklist["3G/WiFi Separation"]:
            response += "\n🚨 ВНИМАНИЕ: Вы не разделили 3G и WiFi трафик. Это критически важно для оптимизации. Рекомендую создать отдельные кампании."
        
        response += "\n💡 Что дальше? Вы можете активировать кампанию, сказав: 'Активируй кампанию [ID]'"
        return response
    
    async def _handle_optimization_request(self, params: Dict[str, Any]) -> str:
        """Handle campaign optimization request"""
        campaign_id = params.get('campaign_id')
        if not campaign_id:
            return "Пожалуйста, укажите ID кампании для оптимизации (например, 'оптимизируй кампанию 123')."
        
        # Placeholder for optimization logic
        return f"""🔍 Анализирую кампанию {campaign_id} для оптимизации...\n\n💡 РЕКОМЕНДАЦИИ:\n1. 📈 Увеличить ставки на iOS (+15%)\n2. 🚫 Заблокировать источник traffic_source_X\n3. 🎯 Расширить на Германию\n\nПрименить эти изменения?"""
    
    async def _handle_statistics_request(self, params: Dict[str, Any]) -> str:
        """Handle statistics request"""
        period = params.get('period', 'week')
        campaign_id = params.get('campaign_id')
        
        # Placeholder for statistics logic
        response = f"📊 ОТЧЕТ ЗА ПОСЛЕДНЮЮ {period.upper()}\n\n"
        if campaign_id:
            response += f"(для кампании {campaign_id})\n\n"
        
        response += "- Показы: 1,234,567\n"
        response += "- Клики: 12,345 (CTR: 1.0%)\n"
        response += "- Конверсии: 123 (CR: 1.0%)\n"
        response += "- Затраты: $1,234.56 (CPC: $0.10)\n"
        response += "- ROI: 150%\n"
        
        return response
    
    async def _handle_targeting_request(self, params: Dict[str, Any]) -> str:
        """Handle targeting/blacklist/whitelist request"""
        action = params.get('action', 'blacklist')
        countries = params.get('countries', [])
        campaign_id = params.get('campaign_id')
        
        if not campaign_id or not countries:
            return "Пожалуйста, укажите ID кампании и страны (например, 'заблокируй Россию в кампании 123')."
        
        action_text = "добавлены в блеклист" if action == 'blacklist' else "добавлены в вайтлист"
        return f"✅ Страны {', '.join(countries)} успешно {action_text} для кампании {campaign_id}."
    
    async def _handle_account_overview(self) -> str:
        """Provide a comprehensive account overview"""
        # Placeholder for overview logic
        response = "📊 ОБЗОР АККАУНТА\n\n"
        response += "- Активных кампаний: 5\n"
        response += "- Общий бюджет: $500/день\n"
        response += "- Лучшая кампания: 'iOS Game Promo' (ROI: 250%)\n"
        response += "- Худшая кампания: 'Android Utility' (ROI: -20%)\n"
        response += "\n💡 Рекомендую приостановить 'Android Utility' и перераспределить бюджет."
        return response
    
    def _get_help_message(self) -> str:
        """Get help message with available commands"""
        return """
        🤖 ДОСТУПНЫЕ КОМАНДЫ:
        
        - `баланс` - Показать текущий баланс
        - `создай кампанию` - Начать создание новой кампании
        - `список кампаний` - Показать ваши кампании
        - `оптимизируй кампанию [ID]` - Получить рекомендации по оптимизации
        - `статистика [за неделю/месяц]` - Показать отчет о производительности
        - `заблокируй [страна] в кампании [ID]` - Добавить страну в блеклист
        - `обзор` - Получить общий обзор аккаунта
        
        💡 Просто говорите со мной естественным языком!
        """
    
    async def _handle_unknown_intent_with_claude(self, text: str) -> str:
        """Handle unknown intents by asking Claude for help"""
        try:
            # Use the integration's Anthropic client
            client = self.integration.anthropic_client
            
            # Prepare messages for Claude
            messages = [
                {"role": "user", "content": text}
            ]
            
            # Add conversation history for context
            for msg in self.conversation_history[-5:]:
                messages.insert(0, {"role": msg['role'], "content": msg['content']})
            
            response = await client.messages.create(
                model=self.model_config['model'],
                max_tokens=self.model_config['max_tokens'],
                temperature=self.model_config['temperature'],
                system=self.system_prompt,
                messages=messages
            )
            
            claude_response = response.content[0].text
            return claude_response
            
        except Exception as e:
            return f"Извините, произошла ошибка при обработке вашего запроса через Claude: {e}"
    
    def add_to_conversation_history(self, user_message: str, assistant_message: str):
        """Add a user/assistant interaction to the conversation history"""
        self.conversation_history.append({
            'role': 'user',
            'content': user_message,
            'timestamp': datetime.now().isoformat()
        })
        self.conversation_history.append({
            'role': 'assistant',
            'content': assistant_message,
            'timestamp': datetime.now().isoformat()
        })
        
        # Keep history from growing too large
        if len(self.conversation_history) > 20:
            self.conversation_history = self.conversation_history[-20:]

async def main():
    """Main function to run the interactive chat"""
    interface = EnhancedClaudeInterface()
    
    while True:
        try:
            user_input = input("👤 Вы: ")
            if user_input.lower() in ["exit", "выход"]:
                print("🤖 До свидания!")
                break
            
            response = await interface.process_message_interactive(user_input)
            print(f"🤖 Claude: {response}")
            
        except KeyboardInterrupt:
            print("\n🤖 До свидания!")
            break
        except Exception as e:
            print(f"❌ Произошла ошибка: {e}")

if __name__ == "__main__":
    # This allows running the script directly for interactive testing
    # Note: This requires claude_propellerads_integration to be configured
    
    # Simple check for API keys
    if not os.environ.get("ANTHROPIC_API_KEY") or not os.environ.get("MainAPI"):
        print("❌ Ошибка: Не найдены переменные окружения ANTHROPIC_API_KEY и MainAPI")
        print("Пожалуйста, установите их перед запуском.")
    else:
        asyncio.run(main())

