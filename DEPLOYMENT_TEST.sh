#!/bin/bash

echo "🚀 PropellerAds API Encyclopedia - Deployment Test"
echo "=================================================="

# Check Python version
echo "📋 Checking Python version..."
python3 --version
if [ $? -ne 0 ]; then
    echo "❌ Python 3 not found"
    exit 1
fi

# Install dependencies
echo "📦 Installing dependencies..."
pip3 install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi

# Test main module import
echo "🔍 Testing main module import..."
python3 -c "import propellerads; print('✅ PropellerAds SDK version:', propellerads.__version__)"
if [ $? -ne 0 ]; then
    echo "❌ Failed to import PropellerAds SDK"
    exit 1
fi

# Test Claude interface import
echo "🤖 Testing Claude interface import..."
python3 -c "from claude_natural_interface_v2 import EnhancedClaudeInterface; print('✅ Claude interface imported successfully')"
if [ $? -ne 0 ]; then
    echo "❌ Failed to import Claude interface"
    exit 1
fi

# Test web interface import
echo "🌐 Testing web interface import..."
cd web_interface
python3 -c "import app; print('✅ Web interface imported successfully')"
if [ $? -ne 0 ]; then
    echo "❌ Failed to import web interface"
    exit 1
fi
cd ..

# Run tests
echo "🧪 Running test suite..."
python3 -m pytest tests/ --tb=no -q
if [ $? -ne 0 ]; then
    echo "❌ Tests failed"
    exit 1
fi

echo ""
echo "🎉 All deployment tests passed!"
echo "✅ Repository is ready for deployment"
