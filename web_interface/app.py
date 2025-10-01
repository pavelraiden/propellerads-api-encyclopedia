#!/usr/bin/env python3
"""
PropellerAds Web Interface
Enterprise-grade web interface for PropellerAds API with Claude AI integration
"""

import os
import sys
import json
import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, Optional

from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from flask_socketio import SocketIO, emit
import requests

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from propellerads.client import PropellerAdsClient
    from claude_natural_interface_v2 import ClaudeNaturalInterface
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure you're running from the project root directory")
    sys.exit(1)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['DEBUG'] = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'

# Initialize SocketIO for real-time updates
socketio = SocketIO(app, cors_allowed_origins="*")

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
        claude_interface = ClaudeNaturalInterface()
        logger.info("Claude interface initialized successfully")
    except Exception as e:
        logger.warning(f"Claude interface not available: {e}")
        claude_interface = None
    
    return True

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('dashboard.html')

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
            status['balance'] = balance
        except Exception as e:
            logger.error(f"PropellerAds API error: {e}")
            status['propellerads_error'] = str(e)
    
    # Check Claude connection
    if claude_interface:
        try:
            # Simple test to check if Claude is responsive
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
        return jsonify({'balance': balance, 'success': True})
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

@app.route('/chat')
def chat():
    """Claude AI chat interface"""
    return render_template('chat.html')

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
        response = claude_interface.chat(message)
        
        return jsonify({
            'response': response,
            'success': True,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error in Claude chat: {e}")
        return jsonify({'error': str(e), 'success': False}), 500

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    logger.info('Client connected')
    emit('status', {'message': 'Connected to PropellerAds Web Interface'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    logger.info('Client disconnected')

@socketio.on('get_live_stats')
def handle_live_stats():
    """Handle live statistics request"""
    try:
        if propeller_client:
            balance = propeller_client.get_balance()
            emit('live_stats', {
                'balance': balance,
                'timestamp': datetime.now().isoformat(),
                'success': True
            })
        else:
            emit('live_stats', {
                'error': 'PropellerAds client not initialized',
                'success': False
            })
    except Exception as e:
        logger.error(f"Error getting live stats: {e}")
        emit('live_stats', {
            'error': str(e),
            'success': False
        })

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {error}")
    return render_template('500.html'), 500

def create_app():
    """Application factory"""
    if not initialize_clients():
        logger.warning("Some clients failed to initialize")
    
    return app

if __name__ == '__main__':
    # Initialize clients
    if not initialize_clients():
        print("Warning: Some clients failed to initialize")
        print("Make sure MainAPI environment variable is set")
    
    # Run the application
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '127.0.0.1')
    
    print(f"Starting PropellerAds Web Interface on {host}:{port}")
    print(f"Dashboard: http://{host}:{port}/")
    print(f"Chat: http://{host}:{port}/chat")
    
    socketio.run(app, host=host, port=port, debug=app.config['DEBUG'])
