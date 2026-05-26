#!/usr/bin/env bash
# One-command launcher for the Job Search Agent app
set -e

cd "$(dirname "$0")"

# Check Python
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo "❌ Python not found. Please install Python 3.9+ from python.org"
    exit 1
fi

PYTHON_CMD=$(command -v python3 || command -v python)

echo "📦 Installing dependencies (first run only)..."
$PYTHON_CMD -m pip install -q -r requirements.txt

echo "🚀 Launching Job Search Agent..."
echo "   Open the URL below in your browser."
echo ""
$PYTHON_CMD -m streamlit run app.py
