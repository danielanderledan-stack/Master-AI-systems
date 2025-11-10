#!/bin/bash
# Start script for Master AI Orchestration System

echo "╔════════════════════════════════════════════════════════════════════════════╗"
echo "║          Master AI Orchestration System - Starting...                     ║"
echo "╚════════════════════════════════════════════════════════════════════════════╝"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.11 or later."
    exit 1
fi

echo "✅ Python found: $(python3 --version)"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Install/update dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt --quiet

# Check if orchestration_config.json exists
if [ ! -f "orchestration_config.json" ]; then
    echo "❌ orchestration_config.json not found!"
    exit 1
fi

echo "✅ Configuration file found"

# Start the server
echo ""
echo "🚀 Starting API server on http://localhost:8000"
echo "📖 API documentation available at http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python3 api_server.py
