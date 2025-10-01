#!/usr/bin/env python3
"""
WSGI entry point for PropellerAds Web Interface
Production-ready deployment configuration
"""

import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import the Flask application
from web_interface.app import create_app, socketio

# Create the application instance
application = create_app()

if __name__ == "__main__":
    # For development only
    socketio.run(application, debug=False, host='0.0.0.0', port=5000)
