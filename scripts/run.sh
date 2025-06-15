#!/bin/bash

# Cross-Platform Run Script for EmailSummarizer
# Works on macOS, Linux, and Windows (via Git Bash/WSL)

echo "🚀 Starting EmailSummarizer..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Please run setup first: ./setup.sh"
    exit 1
fi

# Detect operating system for activation path
OS="Unknown"
if [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macOS"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="Linux"
elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
    OS="Windows (Git Bash)"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
if [[ "$OS" == "Windows (Git Bash)" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

# Use python3 if available, otherwise python
PYTHON_CMD="python3"
if ! command -v python3 &> /dev/null; then
    PYTHON_CMD="python"
fi

echo "🌐 Starting Flask server..."
echo "📱 Open your browser to: http://localhost:5000"
echo "🛑 Press Ctrl+C to stop the server"
echo ""

# Start the application
$PYTHON_CMD app.py
