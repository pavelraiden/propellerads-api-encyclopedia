#!/usr/bin/env python3
"""
Claude Interface Wrapper for Web API
Provides a simple synchronous interface for the web application
"""

import asyncio
from claude_natural_interface_v2 import EnhancedClaudeInterface


class ClaudeWebWrapper:
    """Wrapper for Claude interface to work with web API"""
    
    def __init__(self):
        self.interface = EnhancedClaudeInterface()
        self.loop = None
    
    def process_message(self, message: str) -> str:
        """Process a single message and return response"""
        try:
            # Create event loop if needed
            if self.loop is None or self.loop.is_closed():
                self.loop = asyncio.new_event_loop()
                asyncio.set_event_loop(self.loop)
            
            # Extract intent and parameters
            intent_data = self.interface._extract_intent_and_params(message)
            intent = intent_data['intent']
            params = intent_data['params']
            
            # Process with intelligence (async)
            response = self.loop.run_until_complete(
                self.interface._process_intent_with_intelligence(intent, params)
            )
            
            # Add to conversation history
            self.interface.add_to_conversation_history(message, response)
            
            return response
            
        except Exception as e:
            return f"Извините, произошла ошибка при обработке вашего сообщения: {str(e)}"
    
    def get_balance(self) -> str:
        """Quick balance check"""
        return self.process_message("покажи баланс")
    
    def get_campaigns(self) -> str:
        """Quick campaigns overview"""
        return self.process_message("покажи мои кампании")
