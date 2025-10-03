#!/usr/bin/env python3
"""
PropellerAds API Encyclopedia - Setup Script
Automated setup for easy installation and configuration
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def install_dependencies():
    """Install required Python packages"""
    print("📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def setup_env_file():
    """Setup .env file from template"""
    env_file = Path(".env")
    template_file = Path(".env.template")
    
    if env_file.exists():
        print("✅ .env file already exists")
        return True
    
    if not template_file.exists():
        print("❌ .env.template not found")
        return False
    
    print("📋 Creating .env file from template...")
    shutil.copy(template_file, env_file)
    
    print("\n🔑 Please configure your API keys:")
    print("1. Open .env file in a text editor")
    print("2. Replace 'your_propellerads_api_key_here' with your actual PropellerAds API key")
    print("3. Replace 'your_claude_api_key_here' with your actual Claude API key")
    print("\n📖 API Key Sources:")
    print("   - PropellerAds: https://ssp.propellerads.com/")
    print("   - Claude: https://console.anthropic.com/")
    
    return True

def create_desktop_shortcuts():
    """Create desktop shortcuts for different platforms"""
    system = sys.platform
    
    if system.startswith('win'):
        print("🖥️ Windows detected - use launch_app.bat")
    elif system.startswith('darwin'):
        print("🍎 macOS detected - use launch_app.sh")
    elif system.startswith('linux'):
        print("🐧 Linux detected - use launch_app.sh or .desktop file")
        
        # Try to install desktop file
        desktop_dir = Path.home() / ".local/share/applications"
        if desktop_dir.exists():
            desktop_file = desktop_dir / "PropellerAds-Encyclopedia.desktop"
            current_dir = Path.cwd()
            
            desktop_content = f"""[Desktop Entry]
Version=1.0
Type=Application
Name=PropellerAds API Encyclopedia
Comment=AI-powered PropellerAds API management tool
Exec={sys.executable} {current_dir}/launch_app.py
Icon={current_dir}/icon.png
Path={current_dir}
Terminal=false
StartupNotify=true
Categories=Development;Network;Office;"""
            
            try:
                desktop_file.write_text(desktop_content)
                os.chmod(desktop_file, 0o755)
                print(f"✅ Desktop shortcut created: {desktop_file}")
            except Exception as e:
                print(f"⚠️ Could not create desktop shortcut: {e}")

def run_tests():
    """Run basic tests to verify installation"""
    print("🧪 Running basic tests...")
    try:
        # Test imports
        import flask
        import requests
        import anthropic
        from propellerads.client import PropellerAdsClient
        print("✅ All imports successful")
        
        # Test basic functionality
        subprocess.check_call([sys.executable, "-c", "import propellerads; print('SDK version:', propellerads.__version__)"])
        print("✅ SDK test passed")
        
        return True
    except Exception as e:
        print(f"❌ Tests failed: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 PropellerAds API Encyclopedia - Setup")
    print("=" * 50)
    
    # Install dependencies
    if not install_dependencies():
        return False
    
    # Setup environment
    if not setup_env_file():
        return False
    
    # Create shortcuts
    create_desktop_shortcuts()
    
    # Run tests
    if not run_tests():
        print("⚠️ Some tests failed, but installation may still work")
    
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Edit .env file with your API keys")
    print("2. Run the application:")
    
    system = sys.platform
    if system.startswith('win'):
        print("   - Double-click launch_app.bat")
    else:
        print("   - Run: ./launch_app.sh")
        print("   - Or: python3 launch_app.py")
    
    print("\n🌐 The web interface will open at: http://127.0.0.1:5000")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        input("\nPress Enter to exit...")
        sys.exit(1)
