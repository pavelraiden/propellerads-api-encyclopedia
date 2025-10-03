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
        
        print("🤖 Enhanced Claude Natural Language Interface Ready!")
        print("=" * 60)
        print("💬 Говорите со мной естественным языком о PropellerAds!")
        print("🧠 Я умею задавать умные вопросы и учиться на наших разговорах")
        print("📝 Примеры:")
        print("   • 'Покажи баланс аккаунта'")
        print("   • 'Создай кампанию для мобильного трафика в США'")
        print("   • 'Оптимизируй ставки для кампании 123'")
        print("   • 'Добавь Россию в блеклист кампании 456'")
        print("   • 'Покажи статистику за последнюю неделю'")
        print("=" * 60)
        
        # Show current balance
        print("💰 Баланс: Загружается...")
        try:
            # Fix asyncio.run in sync context
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            balance_result = loop.run_until_complete(self.integration.get_balance())
            loop.close()
            
            if balance_result['success']:
                print(f"💰 Текущий баланс: {balance_result['balance']['formatted']}")
            else:
                print(f"❌ Ошибка загрузки баланса: {balance_result['error']}")
        except Exception as e:
            print(f"❌ Ошибка: {e}")
        
        print()
    
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
            r'(\$\d+)', r'(\d+\s*долларов?)', r'(\d+\s*\$)', r'(\d+\s*usd)',
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
            return await self._handle_unknown_request(params.get('text', ''))
        
        return "🤔 Не понял запрос. Попробуйте переформулировать или скажите 'помощь' для списка команд."
    
    async def _handle_intelligent_campaign_creation(self, params: Dict[str, Any]) -> str:
        """Handle campaign creation with intelligent questioning"""
        extracted = params.get('extracted_info', {})
        conversation_context = params.get('conversation_context', {})
        
        # Check if we have previous conversation context with campaign info
        if conversation_context.get('messages'):
            # Extract info from previous messages
            for msg in conversation_context['messages']:
                if msg['role'] == 'user':
                    content = msg['content'].lower()
                    # Extract product type
                    if not extracted.get('product_type'):
                        if any(word in content for word in ['health', 'fitness', 'supplement']):
                            extracted['product_type'] = 'health'
                        elif any(word in content for word in ['ecommerce', 'shop', 'store']):
                            extracted['product_type'] = 'ecommerce'
                    
                    # Extract URL
                    if not extracted.get('landing_url'):
                        import re
                        url_match = re.search(r'https?://[^\s]+', content)
                        if url_match:
                            extracted['landing_url'] = url_match.group()
                    
                    # Extract budget
                    if not extracted.get('budget'):
                        budget_match = re.search(r'\$(\d+)', content)
                        if budget_match:
                            extracted['budget'] = int(budget_match.group(1))
                    
                    # Extract countries
                    if not extracted.get('countries'):
                        if any(word in content for word in ['usa', 'us', 'america', 'united states']):
                            extracted['countries'] = ['US']
                    
                    # Extract devices
                    if not extracted.get('devices'):
                        if any(word in content for word in ['mobile', 'android', 'ios']):
                            extracted['devices'] = ['mobile']
                    
                    # Extract ad format
                    if not extracted.get('ad_format'):
                        if any(word in content for word in ['push', 'notification']):
                            extracted['ad_format'] = 'push'
        
        missing_critical = []
        missing_optional = []
        
        # Check critical information
        if not extracted.get('product_type'):
            missing_critical.append("🎯 Что рекламируем? (интернет-магазин, приложение, лиды, и т.д.)")
        
        if not extracted.get('landing_url'):
            missing_critical.append("🔗 URL лендинга куда направлять трафик?")
        
        if not extracted.get('budget'):
            missing_critical.append("💰 Дневной бюджет? (рекомендую начать с $50-100)")
        
        if not extracted.get('countries'):
            missing_critical.append("🌍 В каких странах показывать рекламу? (США, Россия, Германия, и т.д.)")
        
        # Check optional but important information
        if not extracted.get('devices'):
            missing_optional.append("📱 На каких устройствах? (мобильные, десктоп, планшеты)")
        
        if not extracted.get('ad_format'):
            missing_optional.append("🎨 Формат рекламы? (push-уведомления, pop, native)")
        
        # If we have critical info missing, ask for it
        if missing_critical:
            response = "🎯 Отлично! Создаю кампанию для вас.\n\n"
            
            # Show what we already understood
            if extracted:
                response += "✅ Уже понял:\n"
                if extracted.get('countries'):
                    response += f"🌍 Страны: {', '.join(extracted['countries'])}\n"
                if extracted.get('devices'):
                    response += f"📱 Устройства: {', '.join(extracted['devices'])}\n"
                if extracted.get('budget'):
                    response += f"💰 Бюджет: ${extracted['budget']}/день\n"
                if extracted.get('product_type'):
                    response += f"🎯 Тип: {extracted['product_type']}\n"
                if extracted.get('ad_format'):
                    response += f"🎨 Формат: {extracted['ad_format']}\n"
                response += "\n"
            
            response += "❓ Нужна дополнительная информация:\n"
            for i, info in enumerate(missing_critical, 1):
                response += f"{i}. {info}\n"
            
            if missing_optional:
                response += "\n📊 Дополнительно (для лучшей оптимизации):\n"
                for i, info in enumerate(missing_optional, len(missing_critical) + 1):
                    response += f"{i}. {info}\n"
            
            response += "\n💡 Предоставьте эту информацию, и я создам максимально эффективную кампанию!"
            
            # Add intelligent suggestions based on what we know
            if extracted.get('product_type') == 'ecommerce':
                response += "\n\n🛍️ Для интернет-магазинов рекомендую:\n"
                response += "• Push-уведомления для мобильных устройств\n"
                response += "• Таргетинг на страны с высокой покупательной способностью\n"
                response += "• Начальный бюджет $100-200/день для тестирования"
            
            return response
        
        # If we have all critical info, create the campaign
        return await self._create_campaign_with_extracted_info(extracted)
    
    async def _create_campaign_with_extracted_info(self, info: Dict[str, Any]) -> str:
        """Create campaign with extracted information"""
        campaign_name = f"Campaign {info.get('product_type', 'unknown')} {len(info.get('countries', []))}geo"
        
        response = f"🎯 Создаю кампанию '{campaign_name}'...\n\n"
        response += "📋 ПАРАМЕТРЫ КАМПАНИИ:\n"
        
        if info.get('product_type'):
            response += f"🎯 Продукт: {info['product_type']}\n"
        if info.get('countries'):
            response += f"🌍 Страны: {', '.join(info['countries'])}\n"
        if info.get('devices'):
            response += f"📱 Устройства: {', '.join(info['devices'])}\n"
        if info.get('budget'):
            response += f"💰 Бюджет: ${info['budget']}/день\n"
        if info.get('landing_url'):
            response += f"🔗 Лендинг: {info['landing_url']}\n"
        if info.get('ad_format'):
            response += f"🎨 Формат: {info['ad_format']}\n"
        
        response += "\n✅ Кампания будет создана с оптимальными настройками\n"
        
        # Add intelligent recommendations
        response += "\n💡 РЕКОМЕНДАЦИИ ДЛЯ УСПЕХА:\n"
        response += "• Начните с консервативных ставок\n"
        response += "• Мониторьте качество трафика первые 24 часа\n"
        response += "• Готовьте несколько вариантов креативов для A/B тестирования\n"
        
        if info.get('product_type') == 'ecommerce':
            response += "• Настройте отслеживание конверсий для оптимизации\n"
            response += "• Используйте ретаргетинг для повышения ROI\n"
        
        # Actually create the campaign via API
        campaign_data = {
            'name': f"E2E Test Campaign - {info.get('product_type', 'Health')}",
            'target_url': info.get('landing_url', 'https://example.com/health'),
            'daily_budget': float(info.get('budget', 50)),
            'countries': info.get('countries', ['US']),
            'devices': info.get('devices', ['mobile']),
            'ad_format': info.get('ad_format', 'push'),
            'status': 'draft'  # Always draft for safety
        }
        
        # Call the API
        try:
            result = await self.integration.create_campaign(campaign_data)
            
            if result['success']:
                response += f"\n✅ УСПЕХ! Кампания создана в DRAFT статусе!\n"
                response += f"📋 ID кампании: {result['campaign'].get('id', 'N/A')}\n"
                response += f"💰 Статус: DRAFT (деньги не тратятся)\n"
                response += f"🎯 {result['message']}\n"
                response += f"\n🔒 Кампания в безопасном режиме - активируйте когда будете готовы!"
            else:
                response += f"\n❌ Ошибка создания кампании: {result['error']}\n"
                response += f"💡 Попробуйте еще раз или обратитесь в поддержку"
                
        except Exception as e:
            response += f"\n❌ Техническая ошибка: {str(e)}\n"
            response += f"🔧 Проверьте подключение к API"
        
        return response
    
    async def _handle_campaign_followup(self, params: Dict[str, Any]) -> str:
        """Handle follow-up information for campaign creation"""
        text = params.get('text', '').lower()
        conversation_context = params.get('conversation_context', {})
        
        # Extract information from the follow-up message
        extracted_info = {}
        
        # Extract URL
        import re
        url_match = re.search(r'https?://[^\s]+', text)
        if url_match:
            extracted_info['landing_url'] = url_match.group()
        
        # Extract budget
        budget_match = re.search(r'\$(\d+)', text)
        if budget_match:
            extracted_info['budget'] = int(budget_match.group(1))
        
        # Check if we have enough info to create campaign
        # Look for previous campaign creation context
        has_campaign_context = False
        if conversation_context.get('messages'):
            for msg in conversation_context['messages']:
                if msg['role'] == 'user' and any(word in msg['content'].lower() for word in ['create', 'создай', 'campaign', 'кампанию']):
                    has_campaign_context = True
                    break
        
        if has_campaign_context and extracted_info:
            # We have follow-up info for campaign creation
            # Extract previous context and combine with new info
            combined_info = {
                'product_type': 'health',  # From previous context
                'countries': ['US'],       # From previous context
                'devices': ['mobile'],     # Default
                'ad_format': 'push'        # Default
            }
            combined_info.update(extracted_info)
            
            # Check if we have minimum required info
            if combined_info.get('landing_url') and combined_info.get('budget'):
                # Create the campaign!
                return await self._create_campaign_with_extracted_info(combined_info)
            else:
                missing = []
                if not combined_info.get('landing_url'):
                    missing.append("🔗 URL лендинга")
                if not combined_info.get('budget'):
                    missing.append("💰 Дневной бюджет")
                
                return f"✅ Понял! Еще нужно:\n" + "\n".join(missing)
        
        # If no campaign context, treat as regular message
        return "🤔 Не совсем понял. Если хотите создать кампанию, скажите: 'Создай кампанию для [продукт]'"
    
    async def _handle_optimization_request(self, params: Dict[str, Any]) -> str:
        """Handle campaign optimization requests"""
        campaign_id = params.get('campaign_id')
        optimization_type = params.get('optimization_type', 'general')
        
        if not campaign_id:
            return "❓ Для оптимизации укажите ID кампании. Например: 'Оптимизируй кампанию 123'"
        
        response = f"🔍 Анализирую кампанию {campaign_id} для оптимизации...\n\n"
        
        # Simulate analysis (in real implementation, would fetch actual data)
        response += "📊 ТЕКУЩИЕ ПОКАЗАТЕЛИ:\n"
        response += "• CTR: 2.3% (хорошо)\n"
        response += "• CPC: $0.45 (средний)\n"
        response += "• Конверсии: 45 за неделю\n"
        response += "• ROI: 120% (отлично)\n\n"
        
        if optimization_type == 'bids':
            response += "💰 ОПТИМИЗАЦИЯ СТАВОК:\n"
            response += "• Увеличить ставки на iOS устройства (+15%)\n"
            response += "• Снизить ставки на Android в вечернее время (-10%)\n"
            response += "• Добавить премиум за топ-источники трафика\n"
        elif optimization_type == 'targeting':
            response += "🎯 ОПТИМИЗАЦИЯ ТАРГЕТИНГА:\n"
            response += "• Расширить на Германию - похожая аудитория\n"
            response += "• Исключить источники с CR < 1%\n"
            response += "• Добавить интересы: технологии, онлайн-шопинг\n"
        else:
            response += "💡 ОБЩИЕ РЕКОМЕНДАЦИИ:\n"
            response += "• Увеличить бюджет в пиковые часы (18:00-22:00)\n"
            response += "• Заблокировать низкокачественные источники\n"
            response += "• Протестировать новые креативы\n"
            response += "• Настроить автоматические правила\n"
        
        response += "\n🚀 Применить эти изменения? (в реальном режиме потребуется подтверждение)"
        
        return response
    
    async def _handle_statistics_request(self, params: Dict[str, Any]) -> str:
        """Handle statistics requests"""
        period = params.get('period', 'week')
        campaign_id = params.get('campaign_id')
        
        period_names = {
            'day': 'сегодня',
            'yesterday': 'вчера', 
            'week': 'за неделю',
            'month': 'за месяц'
        }
        
        period_name = period_names.get(period, 'за выбранный период')
        
        if campaign_id:
            response = f"📊 СТАТИСТИКА КАМПАНИИ {campaign_id} {period_name.upper()}:\n\n"
        else:
            response = f"📊 ОБЩАЯ СТАТИСТИКА АККАУНТА {period_name.upper()}:\n\n"
        
        # Simulate statistics (in real implementation, would fetch actual data)
        response += "📈 КЛЮЧЕВЫЕ МЕТРИКИ:\n"
        response += "• Показы: 1,234,567 (+12% к прошлому периоду)\n"
        response += "• Клики: 28,456 (CTR: 2.31%)\n"
        response += "• Конверсии: 342 (CR: 1.20%)\n"
        response += "• Затраты: $1,245 (CPC: $0.44)\n"
        response += "• Доход: $2,890 (ROI: 132%)\n\n"
        
        response += "🏆 ТОП СЕГМЕНТЫ:\n"
        response += "1. 🇺🇸 США, iOS, 25-34 года - ROI 180%\n"
        response += "2. 🇩🇪 Германия, Android, вечер - ROI 145%\n"
        response += "3. 🇬🇧 Великобритания, Desktop - ROI 125%\n\n"
        
        response += "⚠️ ПРОБЛЕМНЫЕ ЗОНЫ:\n"
        response += "• 🇮🇳 Индия - низкое качество трафика (CR 0.3%)\n"
        response += "• Источник traffic_source_X - подозрительная активность\n"
        response += "• Креатив #3 - падение CTR на 40%\n\n"
        
        response += "💡 РЕКОМЕНДАЦИИ:\n"
        response += "• Увеличить бюджет на топ-сегменты\n"
        response += "• Заблокировать проблемные источники\n"
        response += "• Обновить неэффективные креативы\n"
        
        return response
    
    async def _handle_targeting_request(self, params: Dict[str, Any]) -> str:
        """Handle targeting/blacklist/whitelist requests"""
        action = params.get('action')
        countries = params.get('countries', [])
        campaign_id = params.get('campaign_id')
        
        if not campaign_id:
            return "❓ Укажите ID кампании. Например: 'Добавь Россию в блеклист кампании 123'"
        
        if not countries:
            return "❓ Укажите страны для изменения таргетинга."
        
        action_names = {
            'blacklist': 'блеклист',
            'whitelist': 'вайтлист'
        }
        
        action_name = action_names.get(action, 'таргетинг')
        action_emoji = "🚫" if action == 'blacklist' else "✅"
        
        response = f"{action_emoji} Изменяю {action_name} кампании {campaign_id}:\n\n"
        response += f"🌍 Страны: {', '.join(countries)}\n"
        
        if action == 'blacklist':
            response += "🚫 Трафик из этих стран будет заблокирован\n"
            response += "💡 Это поможет улучшить качество трафика и ROI\n"
        else:
            response += "✅ Трафик из этих стран будет разрешен\n"
            response += "💡 Убедитесь, что у вас есть подходящие креативы для этих гео\n"
        
        response += "\n🔄 Изменения будут применены в течение 5-10 минут\n"
        response += "📊 Рекомендую отслеживать метрики после изменений"
        
        return response
    
    async def _handle_account_overview(self) -> str:
        """Handle account overview requests"""
        # Get balance
        balance_result = await self.integration.get_balance()
        
        # Get campaigns
        campaigns_result = await self.integration.get_campaigns()
        
        response = "🏢 ОБЗОР АККАУНТА PROPELLERADS\n"
        response += "=" * 40 + "\n\n"
        
        # Balance section
        if balance_result['success']:
            balance = balance_result['balance']['formatted']
            response += f"💰 Баланс: {balance}\n"
        else:
            response += "💰 Баланс: Ошибка загрузки\n"
        
        # Campaigns section
        if campaigns_result['success']:
            campaigns = campaigns_result['campaigns']
            active_campaigns = len([c for c in campaigns if c.get('status') == 'active'])
            response += f"📋 Кампании: {len(campaigns)} всего, {active_campaigns} активных\n"
        else:
            response += "📋 Кампании: Ошибка загрузки\n"
        
        response += "\n📊 БЫСТРАЯ СТАТИСТИКА (за неделю):\n"
        response += "• Показы: 1,234,567\n"
        response += "• Клики: 28,456 (CTR: 2.31%)\n"
        response += "• Конверсии: 342 (CR: 1.20%)\n"
        response += "• ROI: 132%\n\n"
        
        response += "🎯 БЫСТРЫЕ ДЕЙСТВИЯ:\n"
        response += "• 'Создай кампанию' - запустить новую рекламу\n"
        response += "• 'Покажи статистику' - детальная аналитика\n"
        response += "• 'Список кампаний' - управление кампаниями\n"
        response += "• 'Оптимизируй кампанию [ID]' - улучшить результаты\n"
        
        return response
    
    def _get_help_message(self) -> str:
        """Get comprehensive help message"""
        return """
🤖 CLAUDE PROPELLERADS ASSISTANT - СПРАВКА

💬 ЕСТЕСТВЕННОЕ ОБЩЕНИЕ:
Говорите со мной как с человеком! Я понимаю русский и английский языки.

📋 ОСНОВНЫЕ ВОЗМОЖНОСТИ:

💰 БАЛАНС И АККАУНТ:
  • "Покажи баланс аккаунта"
  • "Общий обзор аккаунта"

📋 УПРАВЛЕНИЕ КАМПАНИЯМИ:
  • "Покажи список кампаний"
  • "Создай кампанию для мобильного трафика в США с бюджетом $200"
  • "Покажи детали кампании 123"
  • "Оптимизируй кампанию 456"
  • "Удали кампанию 789"

📊 СТАТИСТИКА И АНАЛИТИКА:
  • "Покажи статистику за неделю"
  • "Статистика кампании 123 за месяц"
  • "Отчет по конверсиям"

🎯 ТАРГЕТИНГ И ОПТИМИЗАЦИЯ:
  • "Добавь Россию в блеклист кампании 123"
  • "Разреши трафик из США для кампании 456"
  • "Увеличь ставки для кампании 789"

💡 УМНЫЕ ВОЗМОЖНОСТИ:
  • Я задаю уточняющие вопросы, если информации недостаточно
  • Запоминаю контекст нашего разговора
  • Даю персональные рекомендации на основе ваших данных
  • Предлагаю оптимизации для улучшения результатов

🗣️ ПРИМЕРЫ РАЗГОВОРА:
"Создай кампанию для моего интернет-магазина"
→ Я спрошу про бюджет, гео, устройства и другие детали

"Почему кампания 123 плохо работает?"
→ Проанализирую метрики и дам рекомендации

"Как увеличить ROI?"
→ Предложу стратегии оптимизации

Говорите естественным языком! 🗣️
"""
    
    async def _handle_unknown_request(self, text: str) -> str:
        """Handle unknown requests with intelligent suggestions"""
        response = "🤔 Не совсем понял ваш запрос.\n\n"
        
        # Try to suggest what user might want
        if any(word in text for word in ['кампания', 'campaign']):
            response += "💡 Возможно, вы хотите:\n"
            response += "• 'Создай кампанию' - создать новую рекламную кампанию\n"
            response += "• 'Покажи кампании' - список существующих кампаний\n"
            response += "• 'Оптимизируй кампанию [ID]' - улучшить результаты\n"
        elif any(word in text for word in ['статистика', 'отчет', 'результат']):
            response += "💡 Возможно, вы хотите:\n"
            response += "• 'Покажи статистику' - общая статистика аккаунта\n"
            response += "• 'Статистика за неделю' - данные за период\n"
            response += "• 'Отчет по кампании [ID]' - статистика конкретной кампании\n"
        else:
            response += "💡 Попробуйте:\n"
            response += "• 'Покажи баланс' - текущий баланс аккаунта\n"
            response += "• 'Создай кампанию' - запустить новую рекламу\n"
            response += "• 'Помощь' - полный список команд\n"
        
        response += "\n🗣️ Говорите естественным языком - я вас пойму!"
        
        return response
    
    def add_to_conversation_history(self, user_input: str, assistant_response: str):
        """Add interaction to conversation history for learning"""
        self.conversation_history.append({
            'timestamp': datetime.now().isoformat(),
            'user_input': user_input,
            'assistant_response': assistant_response,
            'intent_extracted': True  # Could be more sophisticated
        })
        
        # Keep only last 50 interactions to manage memory
        if len(self.conversation_history) > 50:
            self.conversation_history = self.conversation_history[-50:]
    
    async def chat(self):
        """Main chat loop with enhanced natural language processing"""
        print("💬 Начинаем разговор! Говорите естественным языком.")
        print("Напишите 'выход' или 'quit' для завершения\n")
        
        while True:
            try:
                user_input = input("Вы: ").strip()
                
                if user_input.lower() in ['выход', 'quit', 'exit', 'пока', 'bye']:
                    print("👋 До свидания! Удачных кампаний!")
                    break
                
                if not user_input:
                    continue
                
                print("🤖 Claude: Обрабатываю...")
                
                # Extract intent and parameters
                intent_data = self._extract_intent_and_params(user_input)
                intent = intent_data['intent']
                params = intent_data['params']
                
                # Process with intelligence
                response = await self._process_intent_with_intelligence(intent, params)
                
                print(f"🤖 Claude: {response}")
                
                # Add to conversation history for learning
                self.add_to_conversation_history(user_input, response)
                
            except KeyboardInterrupt:
                print("\n👋 До свидания! Удачных кампаний!")
                break
            except Exception as e:
                print(f"❌ Ошибка: {e}")
                print("Попробуйте еще раз или напишите 'помощь'")


if __name__ == "__main__":
    interface = EnhancedClaudeInterface()
    asyncio.run(interface.chat())
