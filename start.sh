#!/bin/bash

# Resume Screening System Startup Script

echo "🚀 Starting MCP-Based RAG Resume Screening System..."
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Check for .env file
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Creating from .env.example..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "✅ Created .env file. Please edit it with your API keys."
    else
        echo "⚠️  .env.example not found. You may need to create .env manually."
    fi
fi

# Start Streamlit app
echo ""
echo "🌟 Starting Streamlit application..."
echo "📱 The app will open in your browser automatically."
echo ""
streamlit run app.py

