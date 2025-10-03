#!/usr/bin/env python3
"""
Claude Interface Wrapper for Web API
Provides a simple synchronous interface for the web application
"""

import asyncio
from claude_natural_interface_v2 import EnhancedClaudeInterface
from claude_advanced_system_prompt import CLAUDE_ADVANCED_SYSTEM_PROMPT


class ClaudeWebWrapper:
    """Wrapper for Claude interface to work with web API"""
    
    def __init__(self):
        self.interface = EnhancedClaudeInterface()
        self.loop = None
        self.conversation_context = {}  # Store conversation context
        self.system_prompt = CLAUDE_ADVANCED_SYSTEM_PROMPT
        self.first_interaction = True  # Track first interaction to avoid duplicate welcome
    
    def process_message(self, message: str) -> str:
        """Process a single message and return response"""
        try:
            # Create event loop if needed
            if self.loop is None or self.loop.is_closed():
                self.loop = asyncio.new_event_loop()
                asyncio.set_event_loop(self.loop)
            
            # Update conversation context with user message
            if 'messages' not in self.conversation_context:
                self.conversation_context['messages'] = []
            
            self.conversation_context['messages'].append({
                'role': 'user',
                'content': message,
                'timestamp': asyncio.get_event_loop().time()
            })
            
            # Extract intent and parameters with context
            intent_data = self.interface._extract_intent_and_params(message)
            intent = intent_data['intent']
            params = intent_data['params']
            
            # Add conversation context to params
            params['conversation_context'] = self.conversation_context
            
            # Process with intelligence (async)
            response = self.loop.run_until_complete(
                self.interface._process_intent_with_intelligence(intent, params)
            )
            
            # Add response to context
            self.conversation_context['messages'].append({
                'role': 'assistant', 
                'content': response,
                'timestamp': asyncio.get_event_loop().time()
            })
            
            # Keep only last 10 messages to avoid memory issues
            if len(self.conversation_context['messages']) > 10:
                self.conversation_context['messages'] = self.conversation_context['messages'][-10:]
            
            # Add to interface conversation history
            self.interface.add_to_conversation_history(message, response)
            
            return response.replace('\n', '<br>')
            
        except Exception as e:
            error_msg = f"Извините, произошла ошибка при обработке вашего сообщения: {str(e)}"
            # Add error to context
            if 'messages' in self.conversation_context:
                self.conversation_context['messages'].append({
                    'role': 'system',
                    'content': f"Error: {str(e)}",
                    'timestamp': asyncio.get_event_loop().time()
                })
            return error_msg
    
    def get_balance(self) -> str:
        """Quick balance check"""
        return self.process_message("покажи баланс")
    
    def get_campaigns(self) -> str:
        """Quick campaigns overview"""
        return self.process_message("покажи мои кампании")
