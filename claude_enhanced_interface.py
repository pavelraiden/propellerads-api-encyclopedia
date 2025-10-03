#!/usr/bin/env python3
"""
Enhanced Claude Interface with Comprehensive PropellerAds API Integration

This module provides Claude with complete access to all PropellerAds API functionality
with context-aware operations and intelligent campaign management.
"""

import os
import json
import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

from anthropic import AsyncAnthropic
from propellerads_api_service import PropellerAdsAPIService, CampaignContext


class EnhancedClaudeInterface:
    """
    Enhanced Claude Interface with comprehensive PropellerAds API access
    
    Features:
    - Complete CRUD operations for campaigns
    - Context-aware campaign editing
    - Real-time statistics and analytics
    - Intelligent campaign optimization
    - Multi-campaign management
    - Advanced targeting and creative management
    """
    
    def __init__(self):
        """Initialize the enhanced Claude interface"""
        # Initialize Anthropic client
        self.anthropic_client = AsyncAnthropic(
            api_key=os.environ.get("ANTHROPIC_API_KEY")
        )
        
        # Initialize PropellerAds API service
        self.api_service = PropellerAdsAPIService()
        
        # Conversation history
        self.conversation_history = []
        
        # Current context (for campaign-specific operations)
        self.current_context: Optional[CampaignContext] = None
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
        # Enhanced system prompt
        self.system_prompt = self._create_enhanced_system_prompt()
    
    def _create_enhanced_system_prompt(self) -> str:
        """Create comprehensive system prompt for Claude"""
        return """
        🚀 **ENHANCED PROPELLERADS AI ASSISTANT**
        
        You are an advanced AI assistant with COMPLETE access to PropellerAds API functionality.
        You can perform ALL operations available in the PropellerAds platform.
        
        **CORE CAPABILITIES:**
        
        🎯 **CAMPAIGN MANAGEMENT:**
        - Create campaigns (all types: onclick, push, in-page push)
        - Edit existing campaigns with context awareness
        - Start/pause/archive campaigns
        - Clone and duplicate campaigns
        - Bulk operations on multiple campaigns
        
        📊 **ANALYTICS & STATISTICS:**
        - Real-time campaign performance data
        - Account-wide statistics and insights
        - Custom date range reports
        - Performance optimization recommendations
        - ROI and conversion tracking
        
        🎨 **CREATIVE MANAGEMENT:**
        - Upload and manage creative assets
        - A/B test different creatives
        - Auto-creative generation
        - Creative performance analysis
        
        🎯 **TARGETING & OPTIMIZATION:**
        - Advanced targeting setup (geo, device, OS, browser)
        - Blacklist/whitelist management
        - Bid optimization strategies
        - Traffic quality analysis
        - Zone performance monitoring
        
        💰 **FINANCIAL OPERATIONS:**
        - Budget management and allocation
        - Spending analysis and forecasting
        - Cost optimization recommendations
        - Payment and billing information
        
        **CONTEXT-AWARE OPERATIONS:**
        When a user clicks "Edit" on a specific campaign, you automatically:
        - Load that campaign's complete context
        - Focus ALL operations on that specific campaign
        - Provide campaign-specific recommendations
        - Remember the campaign context throughout the conversation
        
        **CRITICAL RULES:**
        
        1. **3G/WiFi SEPARATION**: NEVER combine 3G and WiFi traffic in one campaign
        2. **REAL API CALLS**: Always use actual PropellerAds API - no simulations
        3. **VALIDATION**: Validate all data before API calls
        4. **ERROR HANDLING**: Provide clear, actionable error messages
        5. **CONTEXT AWARENESS**: When editing a specific campaign, stay focused on it
        6. **SYSTEMATIC APPROACH**: Follow checklists for complex operations
        
        **RESPONSE FORMAT:**
        - Use clear, professional language
        - Provide step-by-step explanations
        - Include relevant metrics and data
        - Offer optimization suggestions
        - Confirm successful operations
        
        **AVAILABLE COMMANDS:**
        - "создай кампанию" - Create new campaign
        - "редактируй кампанию [ID]" - Edit specific campaign
        - "запусти кампанию [ID]" - Start campaign
        - "останови кампанию [ID]" - Pause campaign
        - "статистика [ID]" - Get campaign statistics
        - "баланс" - Check account balance
        - "список кампаний" - List all campaigns
        - "оптимизируй [ID]" - Optimize campaign
        
        You have access to the complete PropellerAds API through the api_service.
        Always provide accurate, helpful, and actionable responses.
        """
    
    async def process_message(self, message: str, session_id: str = "default", campaign_context_id: int = None) -> str:
        """
        Process user message with enhanced capabilities
        
        Args:
            message: User message
            session_id: User session ID
            campaign_context_id: If provided, sets context for specific campaign
        """
        try:
            # Set campaign context if provided
            if campaign_context_id:
                self.current_context = self.api_service.set_campaign_context(
                    campaign_context_id, session_id
                )
            
            # Add message to conversation history
            self.conversation_history.append({
                'role': 'user',
                'content': message,
                'timestamp': datetime.now(),
                'session_id': session_id,
                'campaign_context': campaign_context_id
            })
            
            # Analyze message intent
            intent = await self._analyze_message_intent(message)
            
            # Process based on intent
            if intent['type'] == 'campaign_operation':
                response = await self._handle_campaign_operation(intent, message)
            elif intent['type'] == 'statistics_request':
                response = await self._handle_statistics_request(intent, message)
            elif intent['type'] == 'account_operation':
                response = await self._handle_account_operation(intent, message)
            elif intent['type'] == 'targeting_operation':
                response = await self._handle_targeting_operation(intent, message)
            elif intent['type'] == 'optimization_request':
                response = await self._handle_optimization_request(intent, message)
            elif intent['type'] == 'zone_operation':
                response = await self._handle_zone_operation(intent, message)
            else:
                # Use Claude for general conversation
                response = await self._get_claude_response(message)
            
            # Add response to conversation history
            self.conversation_history.append({
                'role': 'assistant',
                'content': response,
                'timestamp': datetime.now(),
                'intent': intent
            })
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error processing message: {str(e)}")
            return f"❌ Произошла ошибка при обработке запроса: {str(e)}"
    
    async def _analyze_message_intent(self, message: str) -> Dict[str, Any]:
        """Analyze message to determine intent and extract parameters"""
        message_lower = message.lower()
        
        # Campaign operations
        if any(word in message_lower for word in ['создай', 'create', 'новая кампания', 'new campaign']):
            return {
                'type': 'campaign_operation',
                'action': 'create',
                'params': self._extract_campaign_creation_params(message)
            }
        
        elif any(word in message_lower for word in ['редактируй', 'edit', 'изменить', 'modify']):
            return {
                'type': 'campaign_operation',
                'action': 'edit',
                'params': self._extract_campaign_edit_params(message)
            }
        
        elif any(word in message_lower for word in ['запусти', 'start', 'активируй', 'activate']):
            return {
                'type': 'campaign_operation',
                'action': 'start',
                'params': self._extract_campaign_id(message)
            }
        
        elif any(word in message_lower for word in ['останови', 'stop', 'pause', 'приостанови']):
            return {
                'type': 'campaign_operation',
                'action': 'pause',
                'params': self._extract_campaign_id(message)
            }
        
        elif any(word in message_lower for word in ['удали', 'delete', 'архивируй', 'archive']):
            return {
                'type': 'campaign_operation',
                'action': 'delete',
                'params': self._extract_campaign_id(message)
            }
        
        # Statistics requests
        elif any(word in message_lower for word in ['статистика', 'statistics', 'отчет', 'report']):
            return {
                'type': 'statistics_request',
                'params': self._extract_statistics_params(message)
            }
        
        # Account operations
        elif any(word in message_lower for word in ['баланс', 'balance', 'счет', 'account']):
            return {
                'type': 'account_operation',
                'action': 'balance'
            }
        
        elif any(word in message_lower for word in ['список кампаний', 'campaigns list', 'все кампании']):
            return {
                'type': 'account_operation',
                'action': 'list_campaigns'
            }
        
        # Optimization requests
        elif any(word in message_lower for word in ['оптимизируй', 'optimize', 'улучши', 'improve']):
            return {
                'type': 'optimization_request',
                'params': self._extract_optimization_params(message)
            }
        
        # Zone management operations
        elif any(word in message_lower for word in ['заблокируй зон', 'block zone', 'блокировка зон', 'blacklist']):
            return {
                'type': 'zone_operation',
                'action': 'block',
                'params': self._extract_zone_params(message)
            }
        
        elif any(word in message_lower for word in ['разблокируй зон', 'unblock zone', 'whitelist']):
            return {
                'type': 'zone_operation',
                'action': 'unblock',
                'params': self._extract_zone_params(message)
            }
        
        elif any(word in message_lower for word in ['ставка зон', 'zone rate', 'ставки по зонам']):
            return {
                'type': 'zone_operation',
                'action': 'set_rates',
                'params': self._extract_zone_rate_params(message)
            }
        
        elif any(word in message_lower for word in ['анализ зон', 'zone analysis', 'производительность зон']):
            return {
                'type': 'zone_operation',
                'action': 'analyze',
                'params': self._extract_zone_analysis_params(message)
            }
        
        elif any(word in message_lower for word in ['автооптимизация зон', 'auto optimize zones']):
            return {
                'type': 'zone_operation',
                'action': 'auto_optimize',
                'params': self._extract_zone_optimization_params(message)
            }
        
        # Default to general conversation
        return {
            'type': 'general_conversation',
            'params': {}
        }
    
    async def _handle_campaign_operation(self, intent: Dict[str, Any], message: str) -> str:
        """Handle campaign operations (create, edit, start, pause, delete)"""
        action = intent['action']
        params = intent['params']
        
        if action == 'create':
            return await self._create_campaign(params, message)
        elif action == 'edit':
            return await self._edit_campaign(params, message)
        elif action == 'start':
            return await self._start_campaign(params)
        elif action == 'pause':
            return await self._pause_campaign(params)
        elif action == 'delete':
            return await self._delete_campaign(params)
        else:
            return "❌ Неизвестная операция с кампанией"
    
    async def _create_campaign(self, params: Dict[str, Any], original_message: str) -> str:
        """Create a new campaign with comprehensive parameter extraction"""
        try:
            # Extract campaign parameters from message
            campaign_data = self._extract_comprehensive_campaign_data(original_message)
            
            # Validate campaign data
            validation = self.api_service.validate_campaign_data(campaign_data)
            if not validation['valid']:
                return f"❌ Ошибки валидации:\n" + "\n".join(f"- {error}" for error in validation['errors'])
            
            # Create campaign via API
            result = await self.api_service.create_campaign(campaign_data)
            
            if result['success']:
                campaign_id = result['campaign_id']
                
                response = f"✅ Кампания успешно создана!\n\n"
                response += f"🆔 ID кампании: {campaign_id}\n"
                response += f"📝 Название: {campaign_data.get('name', 'Без названия')}\n"
                response += f"🎯 Тип: {campaign_data.get('direction', 'onclick')}\n"
                response += f"💰 Модель: {campaign_data.get('rate_model', 'cpm')}\n"
                response += f"🌍 Гео: {', '.join(campaign_data.get('countries', []))}\n"
                response += f"💵 Бюджет: ${campaign_data.get('daily_amount', 'не указан')}/день\n\n"
                
                response += "🔍 **ПРОВЕРКА КАМПАНИИ:**\n"
                response += "✅ Кампания создана через API\n"
                response += "✅ Статус: DRAFT (черновик)\n"
                response += "✅ Все обязательные поля заполнены\n"
                
                # Check 3G/WiFi separation
                name = campaign_data.get('name', '').lower()
                if '3g' in name and 'wifi' in name:
                    response += "❌ ВНИМАНИЕ: Обнаружено смешение 3G и WiFi трафика!\n"
                elif '3g' in name or 'wifi' in name:
                    response += "✅ Правильное разделение типов соединения\n"
                
                response += f"\n💡 **Следующие шаги:**\n"
                response += f"1. Проверьте настройки кампании\n"
                response += f"2. Активируйте кампанию: 'Запусти кампанию {campaign_id}'\n"
                response += f"3. Мониторьте производительность\n"
                
                return response
            else:
                return f"❌ Ошибка создания кампании: {result['error']}"
                
        except Exception as e:
            return f"❌ Критическая ошибка: {str(e)}"
    
    async def _edit_campaign(self, params: Dict[str, Any], message: str) -> str:
        """Edit existing campaign with context awareness"""
        try:
            campaign_id = params.get('campaign_id')
            if not campaign_id:
                return "❌ Не указан ID кампании для редактирования"
            
            # Set context for this campaign
            context = self.api_service.set_campaign_context(campaign_id, "edit_session")
            self.current_context = context
            
            # Get current campaign data
            campaign_result = await self.api_service.get_campaign(campaign_id)
            if not campaign_result['success']:
                return f"❌ Не удалось получить данные кампании: {campaign_result['error']}"
            
            current_campaign = campaign_result['campaign']
            
            # Extract update parameters from message
            update_data = self._extract_campaign_update_data(message)
            
            if not update_data:
                # No specific updates found, show current campaign info and ask what to edit
                response = f"📝 **РЕДАКТИРОВАНИЕ КАМПАНИИ {campaign_id}**\n\n"
                response += f"📊 **Текущие настройки:**\n"
                response += f"• Название: {current_campaign.get('name', 'Не указано')}\n"
                response += f"• Статус: {self._get_status_name(current_campaign.get('status', 1))}\n"
                response += f"• URL: {current_campaign.get('target_url', 'Не указан')}\n"
                response += f"• Модель: {current_campaign.get('rate_model', 'Не указана')}\n"
                response += f"• Бюджет: ${current_campaign.get('daily_amount', 'Не указан')}/день\n\n"
                
                response += "🔧 **Что вы хотите изменить?**\n"
                response += "• Название кампании\n"
                response += "• Целевой URL\n"
                response += "• Дневной бюджет\n"
                response += "• Таргетинг (гео, устройства, ОС)\n"
                response += "• Ставки по странам\n"
                response += "• Креативы (для push-кампаний)\n\n"
                
                response += "💡 Просто скажите что изменить, например:\n"
                response += f"'Измени бюджет на $100' или 'Добавь США в таргетинг'"
                
                return response
            
            # Apply updates
            result = await self.api_service.update_campaign(campaign_id, update_data)
            
            if result['success']:
                response = f"✅ Кампания {campaign_id} успешно обновлена!\n\n"
                response += "📝 **Внесенные изменения:**\n"
                
                for field, value in update_data.items():
                    if field == 'name':
                        response += f"• Название: {value}\n"
                    elif field == 'target_url':
                        response += f"• URL: {value}\n"
                    elif field == 'daily_amount':
                        response += f"• Дневной бюджет: ${value}\n"
                    elif field == 'targeting':
                        response += f"• Обновлен таргетинг\n"
                    elif field == 'rates':
                        response += f"• Обновлены ставки\n"
                
                response += f"\n💡 Кампания остается в текущем статусе. "
                response += f"Для активации используйте: 'Запусти кампанию {campaign_id}'"
                
                return response
            else:
                return f"❌ Ошибка обновления кампании: {result['error']}"
                
        except Exception as e:
            return f"❌ Ошибка редактирования: {str(e)}"
    
    async def _start_campaign(self, params: Dict[str, Any]) -> str:
        """Start/activate campaign"""
        campaign_id = params.get('campaign_id')
        if not campaign_id:
            return "❌ Не указан ID кампании для запуска"
        
        result = await self.api_service.start_campaign(campaign_id)
        
        if result['success']:
            return f"✅ Кампания {campaign_id} успешно запущена!\n\n" \
                   f"📊 Статус: {result['status_name']}\n" \
                   f"💡 Кампания начнет получать трафик в течение нескольких минут."
        else:
            return f"❌ Ошибка запуска кампании: {result['error']}"
    
    async def _pause_campaign(self, params: Dict[str, Any]) -> str:
        """Pause campaign"""
        campaign_id = params.get('campaign_id')
        if not campaign_id:
            return "❌ Не указан ID кампании для остановки"
        
        result = await self.api_service.pause_campaign(campaign_id)
        
        if result['success']:
            return f"⏸️ Кампания {campaign_id} приостановлена!\n\n" \
                   f"📊 Статус: {result['status_name']}\n" \
                   f"💡 Трафик прекратится в течение нескольких минут."
        else:
            return f"❌ Ошибка остановки кампании: {result['error']}"
    
    async def _delete_campaign(self, params: Dict[str, Any]) -> str:
        """Delete/archive campaign"""
        campaign_id = params.get('campaign_id')
        if not campaign_id:
            return "❌ Не указан ID кампании для удаления"
        
        result = await self.api_service.archive_campaign(campaign_id)
        
        if result['success']:
            return f"🗑️ Кампания {campaign_id} архивирована!\n\n" \
                   f"📊 Статус: Архивирована\n" \
                   f"💡 Кампания больше не будет получать трафик."
        else:
            return f"❌ Ошибка архивирования кампании: {result['error']}"
    
    async def _handle_statistics_request(self, intent: Dict[str, Any], message: str) -> str:
        """Handle statistics requests"""
        params = intent['params']
        
        campaign_id = params.get('campaign_id')
        date_from = params.get('date_from')
        date_to = params.get('date_to')
        
        if campaign_id:
            # Campaign-specific statistics
            result = await self.api_service.get_campaign_statistics(campaign_id, date_from, date_to)
        else:
            # Account-wide statistics
            result = await self.api_service.get_account_statistics(date_from, date_to)
        
        if result['success']:
            stats = result['statistics']
            
            response = "📊 **СТАТИСТИКА**\n\n"
            
            if campaign_id:
                response += f"🎯 Кампания: {campaign_id}\n"
            else:
                response += "🏢 Аккаунт: Общая статистика\n"
            
            if date_from and date_to:
                response += f"📅 Период: {date_from} - {date_to}\n"
            
            response += "\n📈 **Основные метрики:**\n"
            response += f"• Показы: {stats.get('impressions', 0):,}\n"
            response += f"• Клики: {stats.get('clicks', 0):,}\n"
            response += f"• CTR: {stats.get('ctr', 0):.2%}\n"
            response += f"• Конверсии: {stats.get('conversions', 0):,}\n"
            response += f"• CR: {stats.get('cr', 0):.2%}\n"
            response += f"• Затраты: ${stats.get('cost', 0):.2f}\n"
            response += f"• CPC: ${stats.get('cpc', 0):.3f}\n"
            response += f"• CPA: ${stats.get('cpa', 0):.2f}\n"
            
            if stats.get('revenue'):
                response += f"• Доход: ${stats.get('revenue', 0):.2f}\n"
                response += f"• ROI: {stats.get('roi', 0):.1%}\n"
            
            return response
        else:
            return f"❌ Ошибка получения статистики: {result['error']}"
    
    async def _handle_account_operation(self, intent: Dict[str, Any], message: str) -> str:
        """Handle account operations"""
        action = intent['action']
        
        if action == 'balance':
            result = await self.api_service.get_balance()
            
            if result['success']:
                balance = result['balance']
                return f"💰 **БАЛАНС АККАУНТА**\n\n" \
                       f"💵 Доступно: ${balance.get('amount', 0):.2f}\n" \
                       f"💳 Валюта: {balance.get('currency', 'USD')}"
            else:
                return f"❌ Ошибка получения баланса: {result['error']}"
        
        elif action == 'list_campaigns':
            result = await self.api_service.get_campaigns()
            
            if result['success']:
                campaigns = result['campaigns']
                
                if not campaigns:
                    return "📝 У вас пока нет кампаний.\n\n💡 Создайте первую кампанию: 'Создай кампанию'"
                
                response = f"📋 **СПИСОК КАМПАНИЙ** ({len(campaigns)} шт.)\n\n"
                
                for campaign in campaigns[:10]:  # Show first 10
                    status_name = self._get_status_name(campaign.get('status', 1))
                    response += f"🎯 **{campaign.get('name', 'Без названия')}**\n"
                    response += f"   ID: {campaign.get('id')}\n"
                    response += f"   Статус: {status_name}\n"
                    response += f"   Модель: {campaign.get('rate_model', 'N/A')}\n\n"
                
                if len(campaigns) > 10:
                    response += f"... и еще {len(campaigns) - 10} кампаний\n\n"
                
                response += "💡 Для редактирования: 'Редактируй кампанию [ID]'"
                
                return response
            else:
                return f"❌ Ошибка получения списка кампаний: {result['error']}"
    
    async def _handle_optimization_request(self, intent: Dict[str, Any], message: str) -> str:
        """Handle optimization requests"""
        params = intent['params']
        campaign_id = params.get('campaign_id')
        
        if not campaign_id:
            return "❌ Не указан ID кампании для оптимизации"
        
        # Get campaign statistics for analysis
        stats_result = await self.api_service.get_campaign_statistics(campaign_id)
        campaign_result = await self.api_service.get_campaign(campaign_id)
        
        if not stats_result['success'] or not campaign_result['success']:
            return "❌ Не удалось получить данные для анализа кампании"
        
        stats = stats_result['statistics']
        campaign = campaign_result['campaign']
        
        response = f"🔍 **АНАЛИЗ КАМПАНИИ {campaign_id}**\n\n"
        response += f"📊 **Текущая производительность:**\n"
        response += f"• CTR: {stats.get('ctr', 0):.2%}\n"
        response += f"• CR: {stats.get('cr', 0):.2%}\n"
        response += f"• CPC: ${stats.get('cpc', 0):.3f}\n"
        response += f"• CPA: ${stats.get('cpa', 0):.2f}\n\n"
        
        response += "💡 **РЕКОМЕНДАЦИИ ПО ОПТИМИЗАЦИИ:**\n"
        
        # CTR optimization
        ctr = stats.get('ctr', 0)
        if ctr < 0.01:  # Less than 1%
            response += "📈 **CTR слишком низкий:**\n"
            response += "   • Обновите креативы\n"
            response += "   • Пересмотрите таргетинг\n"
            response += "   • Проверьте релевантность оффера\n\n"
        
        # Conversion optimization
        cr = stats.get('cr', 0)
        if cr < 0.005:  # Less than 0.5%
            response += "🎯 **Низкая конверсия:**\n"
            response += "   • Оптимизируйте лендинг\n"
            response += "   • Проверьте качество трафика\n"
            response += "   • Настройте более точный таргетинг\n\n"
        
        # Budget optimization
        daily_amount = campaign.get('daily_amount', 0)
        if daily_amount > 0:
            daily_spend = stats.get('cost', 0)
            if daily_spend < daily_amount * 0.5:
                response += "💰 **Недорасход бюджета:**\n"
                response += "   • Увеличьте ставки\n"
                response += "   • Расширьте таргетинг\n"
                response += "   • Добавьте новые гео\n\n"
        
        response += "🚀 **Хотите применить оптимизацию?**\n"
        response += f"Скажите: 'Примени оптимизацию для кампании {campaign_id}'"
        
        return response
    
    async def _handle_zone_operation(self, intent: Dict[str, Any], message: str) -> str:
        """Handle zone management operations"""
        action = intent['action']
        params = intent['params']
        
        if action == 'block':
            return await self._block_zones(params, message)
        elif action == 'unblock':
            return await self._unblock_zones(params, message)
        elif action == 'set_rates':
            return await self._set_zone_rates(params, message)
        elif action == 'analyze':
            return await self._analyze_zones(params, message)
        elif action == 'auto_optimize':
            return await self._auto_optimize_zones(params, message)
        else:
            return "❌ Неизвестная операция с зонами"
    
    async def _block_zones(self, params: Dict[str, Any], message: str) -> str:
        """Block zones in campaign"""
        try:
            campaign_id = params.get('campaign_id')
            zone_ids = params.get('zone_ids', [])
            reason = params.get('reason', 'Manual blocking via AI assistant')
            
            if not campaign_id:
                return "❌ Не указан ID кампании для блокировки зон"
            
            if not zone_ids:
                return "❌ Не указаны ID зон для блокировки"
            
            result = await self.api_service.block_zones(campaign_id, zone_ids, reason)
            
            if result['success']:
                response = f"🚫 **ЗОНЫ ЗАБЛОКИРОВАНЫ**\n\n"
                response += f"🎯 Кампания: {campaign_id}\n"
                response += f"📊 Заблокировано зон: {len(zone_ids)}\n"
                response += f"🔢 ID зон: {', '.join(map(str, zone_ids))}\n"
                response += f"📝 Причина: {reason}\n"
                response += f"📈 Всего в черном списке: {result['total_blocked']}\n\n"
                response += "✅ Зоны больше не будут показывать рекламу в этой кампании."
                
                return response
            else:
                return f"❌ Ошибка блокировки зон: {result['error']}"
                
        except Exception as e:
            return f"❌ Ошибка обработки блокировки: {str(e)}"
    
    async def _unblock_zones(self, params: Dict[str, Any], message: str) -> str:
        """Unblock zones in campaign"""
        try:
            campaign_id = params.get('campaign_id')
            zone_ids = params.get('zone_ids', [])
            
            if not campaign_id:
                return "❌ Не указан ID кампании для разблокировки зон"
            
            if not zone_ids:
                return "❌ Не указаны ID зон для разблокировки"
            
            result = await self.api_service.unblock_zones(campaign_id, zone_ids)
            
            if result['success']:
                response = f"✅ **ЗОНЫ РАЗБЛОКИРОВАНЫ**\n\n"
                response += f"🎯 Кампания: {campaign_id}\n"
                response += f"📊 Разблокировано зон: {len(zone_ids)}\n"
                response += f"🔢 ID зон: {', '.join(map(str, zone_ids))}\n"
                response += f"📈 Осталось в черном списке: {result['total_blocked']}\n\n"
                response += "✅ Зоны снова могут показывать рекламу в этой кампании."
                
                return response
            else:
                return f"❌ Ошибка разблокировки зон: {result['error']}"
                
        except Exception as e:
            return f"❌ Ошибка обработки разблокировки: {str(e)}"
    
    async def _set_zone_rates(self, params: Dict[str, Any], message: str) -> str:
        """Set zone-specific rates"""
        try:
            campaign_id = params.get('campaign_id')
            zone_rates = params.get('zone_rates', {})
            
            if not campaign_id:
                return "❌ Не указан ID кампании для установки ставок"
            
            if not zone_rates:
                return "❌ Не указаны ставки для зон"
            
            result = await self.api_service.set_zone_rates(campaign_id, zone_rates)
            
            if result['success']:
                response = f"💰 **СТАВКИ ПО ЗОНАМ ОБНОВЛЕНЫ**\n\n"
                response += f"🎯 Кампания: {campaign_id}\n"
                response += f"📊 Обновлено зон: {len(zone_rates)}\n\n"
                response += "💵 **Новые ставки:**\n"
                
                for zone_id, rate in zone_rates.items():
                    response += f"• Зона {zone_id}: ${rate:.3f}\n"
                
                response += "\n✅ Ставки применены и будут действовать для новых показов."
                
                return response
            else:
                return f"❌ Ошибка установки ставок: {result['error']}"
                
        except Exception as e:
            return f"❌ Ошибка обработки ставок: {str(e)}"
    
    async def _analyze_zones(self, params: Dict[str, Any], message: str) -> str:
        """Analyze zone performance"""
        try:
            campaign_id = params.get('campaign_id')
            min_impressions = params.get('min_impressions', 1000)
            
            if not campaign_id:
                return "❌ Не указан ID кампании для анализа зон"
            
            result = await self.api_service.analyze_zone_performance(campaign_id, min_impressions)
            
            if result['success']:
                recommendations = result['recommendations']
                
                response = f"🔍 **АНАЛИЗ ПРОИЗВОДИТЕЛЬНОСТИ ЗОН**\n\n"
                response += f"🎯 Кампания: {campaign_id}\n"
                response += f"📊 Проанализировано зон: {result['total_zones_analyzed']}\n"
                response += f"📈 Минимум показов: {min_impressions:,}\n\n"
                
                # Zones to block
                zones_to_block = recommendations['zones_to_block']
                if zones_to_block:
                    response += f"🚫 **ЗОНЫ ДЛЯ БЛОКИРОВКИ** ({len(zones_to_block)} шт.):\n"
                    for zone in zones_to_block[:5]:  # Show first 5
                        response += f"• Зона {zone['zone_id']}: {zone['reason']} ({zone['impressions']:,} показов)\n"
                    if len(zones_to_block) > 5:
                        response += f"... и еще {len(zones_to_block) - 5} зон\n"
                    response += "\n"
                
                # High performing zones
                high_performing = recommendations['high_performing_zones']
                if high_performing:
                    response += f"🌟 **ВЫСОКОПРОИЗВОДИТЕЛЬНЫЕ ЗОНЫ** ({len(high_performing)} шт.):\n"
                    for zone in high_performing[:5]:  # Show first 5
                        response += f"• Зона {zone['zone_id']}: CTR {zone['ctr']:.3%}, CR {zone['cr']:.3%}\n"
                    if len(high_performing) > 5:
                        response += f"... и еще {len(high_performing) - 5} зон\n"
                    response += "\n"
                
                # Rate recommendations
                rate_increases = recommendations['zones_to_increase_rates']
                if rate_increases:
                    response += f"📈 **РЕКОМЕНДАЦИИ ПО ПОВЫШЕНИЮ СТАВОК** ({len(rate_increases)} шт.):\n"
                    for zone in rate_increases[:3]:
                        response += f"• Зона {zone['zone_id']}: {zone['reason']} (рекомендуется +{zone['suggested_increase']})\n"
                    response += "\n"
                
                response += "🚀 **Хотите применить рекомендации?**\n"
                response += f"Скажите: 'Автооптимизация зон для кампании {campaign_id}'"
                
                return response
            else:
                return f"❌ Ошибка анализа зон: {result['error']}"
                
        except Exception as e:
            return f"❌ Ошибка обработки анализа: {str(e)}"
    
    async def _auto_optimize_zones(self, params: Dict[str, Any], message: str) -> str:
        """Auto-optimize zones based on performance"""
        try:
            campaign_id = params.get('campaign_id')
            apply_changes = params.get('apply_changes', True)
            
            if not campaign_id:
                return "❌ Не указан ID кампании для автооптимизации"
            
            result = await self.api_service.auto_optimize_zones(campaign_id, apply_changes)
            
            if result['success']:
                recommendations = result['recommendations']
                actions_taken = result['actions_taken']
                
                response = f"🤖 **АВТООПТИМИЗАЦИЯ ЗОН**\n\n"
                response += f"🎯 Кампания: {campaign_id}\n"
                response += f"⚡ Применены изменения: {'Да' if apply_changes else 'Нет'}\n\n"
                
                if apply_changes and actions_taken:
                    response += "✅ **ВЫПОЛНЕННЫЕ ДЕЙСТВИЯ:**\n"
                    for action in actions_taken:
                        response += f"• {action}\n"
                    response += "\n"
                
                # Show recommendations summary
                zones_to_block = len(recommendations['zones_to_block'])
                zones_to_increase = len(recommendations['zones_to_increase_rates'])
                zones_to_decrease = len(recommendations['zones_to_decrease_rates'])
                
                response += "📊 **АНАЛИЗ РЕКОМЕНДАЦИЙ:**\n"
                response += f"• Зон для блокировки: {zones_to_block}\n"
                response += f"• Зон для повышения ставок: {zones_to_increase}\n"
                response += f"• Зон для понижения ставок: {zones_to_decrease}\n\n"
                
                if not apply_changes:
                    response += "💡 Для применения изменений скажите: 'Примени автооптимизацию'\n"
                else:
                    response += "🎉 Оптимизация применена! Мониторьте результаты в течение 24-48 часов.\n"
                
                return response
            else:
                return f"❌ Ошибка автооптимизации: {result['error']}"
                
        except Exception as e:
            return f"❌ Ошибка обработки автооптимизации: {str(e)}"
    
    async def _get_claude_response(self, message: str) -> str:
        """Get response from Claude for general conversation"""
        try:
            # Prepare context
            context_info = ""
            if self.current_context:
                context_info = f"\n\nТекущий контекст: Редактирование кампании {self.current_context.campaign_id} '{self.current_context.campaign_name}'"
            
            # Prepare conversation history for Claude
            messages = []
            for msg in self.conversation_history[-5:]:  # Last 5 messages
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
            
            messages.append({
                "role": "user",
                "content": message + context_info
            })
            
            response = await self.anthropic_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=4096,
                temperature=0.3,
                system=self.system_prompt,
                messages=messages
            )
            
            return response.content[0].text
            
        except Exception as e:
            self.logger.error(f"Error getting Claude response: {str(e)}")
            return f"❌ Ошибка обращения к Claude: {str(e)}"
    
    # ==================== HELPER METHODS ====================
    
    def _extract_campaign_creation_params(self, message: str) -> Dict[str, Any]:
        """Extract campaign creation parameters from message"""
        # This would be a comprehensive parameter extraction
        # For now, return basic structure
        return {
            'extracted_info': {},
            'missing_info': []
        }
    
    def _extract_comprehensive_campaign_data(self, message: str) -> Dict[str, Any]:
        """Extract comprehensive campaign data from message"""
        # This is a simplified version - in reality, this would be much more sophisticated
        import re
        
        data = {}
        
        # Extract name
        name_match = re.search(r'(?:name|название|имя)[:\s]*([^\n,]+)', message, re.IGNORECASE)
        if name_match:
            data['name'] = name_match.group(1).strip()
        
        # Extract URL
        url_match = re.search(r'https?://[^\s]+', message)
        if url_match:
            data['target_url'] = url_match.group(0)
        
        # Extract budget
        budget_match = re.search(r'\$?(\d+(?:\.\d+)?)', message)
        if budget_match:
            data['daily_amount'] = float(budget_match.group(1))
        
        # Set defaults
        data.setdefault('direction', 'onclick')
        data.setdefault('rate_model', 'cpm')
        data.setdefault('status', 1)
        data.setdefault('countries', ['us'])
        
        return data
    
    def _extract_campaign_edit_params(self, message: str) -> Dict[str, Any]:
        """Extract campaign edit parameters"""
        import re
        
        # Extract campaign ID
        id_match = re.search(r'(?:кампани[ию]|campaign)\s*(\d+)', message, re.IGNORECASE)
        campaign_id = int(id_match.group(1)) if id_match else None
        
        return {'campaign_id': campaign_id}
    
    def _extract_campaign_id(self, message: str) -> Dict[str, Any]:
        """Extract campaign ID from message"""
        import re
        
        id_match = re.search(r'(\d+)', message)
        campaign_id = int(id_match.group(1)) if id_match else None
        
        return {'campaign_id': campaign_id}
    
    def _extract_campaign_update_data(self, message: str) -> Dict[str, Any]:
        """Extract update data from message"""
        # This would analyze the message to determine what to update
        # For now, return empty dict
        return {}
    
    def _extract_statistics_params(self, message: str) -> Dict[str, Any]:
        """Extract statistics parameters"""
        import re
        
        params = {}
        
        # Extract campaign ID
        id_match = re.search(r'(?:кампани[ию]|campaign)\s*(\d+)', message, re.IGNORECASE)
        if id_match:
            params['campaign_id'] = int(id_match.group(1))
        
        # Extract date range (simplified)
        if 'неделя' in message.lower() or 'week' in message.lower():
            params['date_from'] = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
            params['date_to'] = datetime.now().strftime('%Y-%m-%d')
        
        return params
    
    def _extract_optimization_params(self, message: str) -> Dict[str, Any]:
        """Extract optimization parameters"""
        import re
        
        id_match = re.search(r'(?:кампани[ию]|campaign)\s*(\d+)', message, re.IGNORECASE)
        campaign_id = int(id_match.group(1)) if id_match else None
        
        return {'campaign_id': campaign_id}
    
    def _get_status_name(self, status: int) -> str:
        """Get human-readable status name"""
        status_names = {
            1: 'Черновик',
            2: 'На модерации',
            3: 'Отклонена',
            4: 'Активна',
            5: 'Приостановлена',
            6: 'Архивирована'
        }
        return status_names.get(status, 'Неизвестно')
    
    def set_campaign_context(self, campaign_id: int, session_id: str = "default"):
        """Set context for campaign-specific operations (called from web interface)"""
        self.current_context = self.api_service.set_campaign_context(campaign_id, session_id)
        return self.current_context
    
    def clear_campaign_context(self):
        """Clear current campaign context"""
        self.current_context = None

    
    # ==================== ZONE PARAMETER EXTRACTION ====================
    
    def _extract_zone_params(self, message: str) -> Dict[str, Any]:
        """Extract zone blocking/unblocking parameters from message"""
        params = {}
        
        # Extract campaign ID
        campaign_match = re.search(r'кампани[ия]\s*(\d+)', message, re.IGNORECASE)
        if not campaign_match:
            campaign_match = re.search(r'campaign\s*(\d+)', message, re.IGNORECASE)
        if campaign_match:
            params['campaign_id'] = int(campaign_match.group(1))
        
        # Extract zone IDs
        zone_ids = []
        zone_matches = re.findall(r'зон[ауы]?\s*(\d+)', message, re.IGNORECASE)
        if not zone_matches:
            zone_matches = re.findall(r'zone\s*(\d+)', message, re.IGNORECASE)
        
        for match in zone_matches:
            zone_ids.append(int(match))
        
        # Also look for comma-separated lists
        zone_list_match = re.search(r'зон[ауы]?\s*[:\-]?\s*([\d,\s]+)', message, re.IGNORECASE)
        if not zone_list_match:
            zone_list_match = re.search(r'zone[s]?\s*[:\-]?\s*([\d,\s]+)', message, re.IGNORECASE)
        
        if zone_list_match:
            zone_list = zone_list_match.group(1)
            additional_zones = [int(x.strip()) for x in zone_list.split(',') if x.strip().isdigit()]
            zone_ids.extend(additional_zones)
        
        params['zone_ids'] = list(set(zone_ids))  # Remove duplicates
        
        # Extract reason for blocking
        reason_match = re.search(r'причин[ауе]?\s*[:\-]?\s*(.+)', message, re.IGNORECASE)
        if not reason_match:
            reason_match = re.search(r'reason\s*[:\-]?\s*(.+)', message, re.IGNORECASE)
        if reason_match:
            params['reason'] = reason_match.group(1).strip()
        
        return params
    
    def _extract_zone_rate_params(self, message: str) -> Dict[str, Any]:
        """Extract zone rate parameters from message"""
        params = {}
        
        # Extract campaign ID
        campaign_match = re.search(r'кампани[ия]\s*(\d+)', message, re.IGNORECASE)
        if not campaign_match:
            campaign_match = re.search(r'campaign\s*(\d+)', message, re.IGNORECASE)
        if campaign_match:
            params['campaign_id'] = int(campaign_match.group(1))
        
        # Extract zone rates (zone_id: rate pairs)
        zone_rates = {}
        
        # Look for patterns like "зона 123: $0.5" or "zone 456: 0.3"
        rate_matches = re.findall(r'зон[ауе]?\s*(\d+)\s*[:\-]\s*\$?(\d+\.?\d*)', message, re.IGNORECASE)
        if not rate_matches:
            rate_matches = re.findall(r'zone\s*(\d+)\s*[:\-]\s*\$?(\d+\.?\d*)', message, re.IGNORECASE)
        
        for zone_id, rate in rate_matches:
            zone_rates[int(zone_id)] = float(rate)
        
        params['zone_rates'] = zone_rates
        
        return params
    
    def _extract_zone_analysis_params(self, message: str) -> Dict[str, Any]:
        """Extract zone analysis parameters from message"""
        params = {}
        
        # Extract campaign ID
        campaign_match = re.search(r'кампани[ия]\s*(\d+)', message, re.IGNORECASE)
        if not campaign_match:
            campaign_match = re.search(r'campaign\s*(\d+)', message, re.IGNORECASE)
        if campaign_match:
            params['campaign_id'] = int(campaign_match.group(1))
        
        # Extract minimum impressions threshold
        impressions_match = re.search(r'минимум\s*(\d+)', message, re.IGNORECASE)
        if not impressions_match:
            impressions_match = re.search(r'minimum\s*(\d+)', message, re.IGNORECASE)
        if impressions_match:
            params['min_impressions'] = int(impressions_match.group(1))
        else:
            params['min_impressions'] = 1000  # Default
        
        return params
    
    def _extract_zone_optimization_params(self, message: str) -> Dict[str, Any]:
        """Extract zone auto-optimization parameters from message"""
        params = {}
        
        # Extract campaign ID
        campaign_match = re.search(r'кампани[ия]\s*(\d+)', message, re.IGNORECASE)
        if not campaign_match:
            campaign_match = re.search(r'campaign\s*(\d+)', message, re.IGNORECASE)
        if campaign_match:
            params['campaign_id'] = int(campaign_match.group(1))
        
        # Check if user wants to apply changes immediately
        apply_keywords = ['примени', 'применить', 'apply', 'execute', 'выполни']
        params['apply_changes'] = any(keyword in message.lower() for keyword in apply_keywords)
        
        return params
