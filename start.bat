@echo off
REM Resume Screening System Startup Script for Windows

echo 🚀 Starting MCP-Based RAG Resume Screening System...
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo 📥 Installing dependencies...
pip install -r requirements.txt

REM Check for .env file
if not exist ".env" (
    echo ⚠️  .env file not found. Creating from .env.example...
    if exist ".env.example" (
        copy .env.example .env
        echo ✅ Created .env file. Please edit it with your API keys.
    ) else (
        echo ⚠️  .env.example not found. You may need to create .env manually.
    )
)

REM Start Streamlit app
echo.
echo 🌟 Starting Streamlit application...
echo 📱 The app will open in your browser automatically.
echo.
streamlit run app.py

pause

