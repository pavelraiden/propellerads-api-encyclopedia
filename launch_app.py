#!/usr/bin/env python3
"""
PropellerAds API Encyclopedia - Desktop Launcher
Simple launcher that opens the web interface in browser
"""

import os
import sys
import time
import subprocess
import webbrowser
import threading
from pathlib import Path

def check_dependencies():
    """Check if all required dependencies are installed"""
    try:
        import flask
        import requests
        import anthropic
        print("✅ All dependencies installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Installing dependencies...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
            print("✅ Dependencies installed successfully")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to install dependencies")
            return False

def check_env_file():
    """Check if .env file exists and has required keys"""
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ .env file not found")
        print("📋 Creating .env file from template...")
        
        template_file = Path(".env.template")
        if template_file.exists():
            import shutil
            shutil.copy(template_file, env_file)
            print("✅ .env file created from template")
            print("🔑 Please edit .env file and add your API keys:")
            print("   - MainAPI (PropellerAds API key)")
            print("   - ANTHROPIC_API_KEY (Claude API key)")
            return False
        else:
            print("❌ .env.template not found")
            return False
    
    # Check if keys are set
    from dotenv import load_dotenv
    load_dotenv()
    
    main_api = os.getenv('MainAPI')
    claude_api = os.getenv('ANTHROPIC_API_KEY')
    
    if not main_api or main_api == 'your_propellerads_api_key_here':
        print("❌ MainAPI key not set in .env file")
        return False
        
    if not claude_api or claude_api == 'your_claude_api_key_here':
        print("❌ ANTHROPIC_API_KEY not set in .env file")
        return False
    
    print("✅ API keys configured")
    return True

def start_web_interface():
    """Start the web interface in background"""
    try:
        os.chdir("web_interface")
        subprocess.Popen([sys.executable, "app.py"], 
                        stdout=subprocess.DEVNULL, 
                        stderr=subprocess.DEVNULL)
        print("🌐 Web interface starting...")
        return True
    except Exception as e:
        print(f"❌ Failed to start web interface: {e}")
        return False

def open_browser():
    """Open browser after a delay"""
    time.sleep(3)  # Wait for server to start
    url = "http://127.0.0.1:5000"
    print(f"🚀 Opening browser: {url}")
    webbrowser.open(url)

def main():
    """Main launcher function"""
    print("🚀 PropellerAds API Encyclopedia Launcher")
    print("=" * 50)
    
    # Change to script directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    # Check dependencies
    if not check_dependencies():
        input("Press Enter to exit...")
        return
    
    # Check environment
    if not check_env_file():
        print("\n📝 Please configure your API keys in .env file and run again")
        input("Press Enter to exit...")
        return
    
    # Start web interface
    if not start_web_interface():
        input("Press Enter to exit...")
        return
    
    # Open browser
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    print("\n✅ Application launched successfully!")
    print("🌐 Web interface: http://127.0.0.1:5000")
    print("💬 Chat interface: http://127.0.0.1:5000/chat")
    print("\nPress Ctrl+C to stop the application")
    
    try:
        # Keep the launcher running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n👋 Shutting down...")

if __name__ == "__main__":
    main()
