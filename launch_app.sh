#!/bin/bash

# PropellerAds API Encyclopedia - macOS/Linux Launcher
echo "🚀 PropellerAds API Encyclopedia Launcher"
echo "=================================================="

# Change to script directory
cd "$(dirname "$0")"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.9+"
    read -p "Press Enter to exit..."
    exit 1
fi

# Run the Python launcher
python3 launch_app.py
