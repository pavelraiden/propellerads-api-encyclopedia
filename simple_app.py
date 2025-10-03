#!/usr/bin/env python3
"""
Simple PropellerAds Web Interface - Unified Dashboard
"""

import os
import sys
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional

from flask import Flask, render_template, request, jsonify
import requests

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from propellerads.client import PropellerAdsClient
    from claude_wrapper import ClaudeWebWrapper
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure you're running from the project root directory")
    sys.exit(1)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__, template_folder='web_interface/templates')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', os.urandom(24).hex())

# Global clients
propeller_client = None
claude_interface = None

def initialize_clients():
    """Initialize PropellerAds and Claude clients"""
    global propeller_client, claude_interface
    
    # Initialize PropellerAds client
    api_key = os.environ.get('MainAPI')
    if not api_key:
        logger.warning("MainAPI environment variable not set")
        return False
    
    try:
        propeller_client = PropellerAdsClient(api_key=api_key)
        logger.info("PropellerAds client initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize PropellerAds client: {e}")
        return False
    
    # Initialize Claude interface
    try:
        claude_interface = ClaudeWebWrapper()
        logger.info("Claude interface initialized successfully")
    except Exception as e:
        logger.warning(f"Claude interface not available: {e}")
        claude_interface = None
    
    return True

@app.route('/')
def index():
    """Unified dashboard page"""
    return render_template('unified_dashboard.html')

@app.route('/api/status')
def api_status():
    """Check API connection status"""
    status = {
        'propellerads': False,
        'claude': False,
        'timestamp': datetime.now().isoformat()
    }
    
    # Check PropellerAds connection
    if propeller_client:
        try:
            balance = propeller_client.get_balance()
            status['propellerads'] = True
            status["balance"] = balance.amount
        except Exception as e:
            logger.error(f"PropellerAds API error: {e}")
            status['propellerads_error'] = str(e)
    
    # Check Claude connection
    if claude_interface:
        try:
            status['claude'] = True
        except Exception as e:
            logger.error(f"Claude API error: {e}")
            status['claude_error'] = str(e)
    
    return jsonify(status)

@app.route('/api/balance')
def get_balance():
    """Get account balance"""
    if not propeller_client:
        return jsonify({'error': 'PropellerAds client not initialized'}), 500
    
    try:
        balance = propeller_client.get_balance()
        return jsonify({'balance': balance.amount, 'success': True})
    except Exception as e:
        logger.error(f"Error getting balance: {e}")
        return jsonify({'error': str(e), 'success': False}), 500

@app.route('/api/campaigns')
def get_campaigns():
    """Get campaigns list"""
    if not propeller_client:
        return jsonify({'error': 'PropellerAds client not initialized'}), 500
    
    try:
        campaigns = propeller_client.get_campaigns()
        return jsonify({'campaigns': campaigns, 'success': True})
    except Exception as e:
        logger.error(f"Error getting campaigns: {e}")
        return jsonify({'error': str(e), 'success': False}), 500

@app.route('/api/statistics')
def get_statistics():
    """Get statistics"""
    if not propeller_client:
        return jsonify({'error': 'PropellerAds client not initialized'}), 500
    
    try:
        # Get query parameters
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        
        stats = propeller_client.get_statistics(
            date_from=date_from,
            date_to=date_to
        )
        return jsonify({'statistics': stats, 'success': True})
    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        return jsonify({'error': str(e), 'success': False}), 500

@app.route('/api/chat', methods=['POST'])
def chat_with_claude():
    """Chat with Claude AI"""
    if not claude_interface:
        return jsonify({'error': 'Claude interface not available'}), 500
    
    try:
        data = request.get_json()
        message = data.get('message', '')
        
        if not message:
            return jsonify({'error': 'Message is required'}), 400
        
        # Get response from Claude
        response = claude_interface.process_message(message)
        
        return jsonify({
            'response': response,
            'success': True,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error in Claude chat: {e}")
        return jsonify({'error': str(e), 'success': False}), 500

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {error}")
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Initialize clients
    if not initialize_clients():
        print("Warning: Some clients failed to initialize")
        print("Make sure MainAPI and ANTHROPIC_API_KEY environment variables are set")
    
    # Configuration
    config = {
        'host': os.environ.get('HOST', '127.0.0.1'),
        'port': int(os.environ.get('PORT', 5000)),
        'debug': os.environ.get('DEBUG', 'False').lower() == 'true'
    }
    
    print(f"🚀 Starting PropellerAds Unified Interface on {config['host']}:{config['port']}")
    print(f"📊 Dashboard: http://{config['host']}:{config['port']}/")
    print(f"💡 Everything is now in one place!")
    print(f"🔧 Debug mode: {'ON' if config['debug'] else 'OFF'}")
    
    app.run(**config)
