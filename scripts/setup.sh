#!/bin/bash

# Cross-Platform Setup Script for EmailSummarizer
# Works on macOS, Linux, and Windows (via Git Bash/WSL)

echo "🚀 Setting up EmailSummarizer..."
echo "=================================="

# Detect operating system
OS="Unknown"
if [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macOS"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="Linux"
elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
    OS="Windows (Git Bash)"
fi

echo "📱 Detected OS: $OS"

# Check if Python is installed
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo "❌ Python is not installed!"
    echo "Please install Python 3.8+ from https://python.org"
    exit 1
fi

# Use python3 if available, otherwise python
PYTHON_CMD="python3"
if ! command -v python3 &> /dev/null; then
    PYTHON_CMD="python"
fi

echo "🐍 Using Python command: $PYTHON_CMD"

# Check Python version
PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | grep -oE '[0-9]+\.[0-9]+')
MAJOR_VERSION=$(echo $PYTHON_VERSION | cut -d. -f1)
MINOR_VERSION=$(echo $PYTHON_VERSION | cut -d. -f2)

if [[ $MAJOR_VERSION -lt 3 ]] || [[ $MAJOR_VERSION -eq 3 && $MINOR_VERSION -lt 8 ]]; then
    echo "❌ Python 3.8+ is required. Found version $PYTHON_VERSION"
    exit 1
fi

echo "✅ Python version $PYTHON_VERSION is compatible"

# Create virtual environment
echo "📦 Creating virtual environment..."
$PYTHON_CMD -m venv venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
if [[ "$OS" == "Windows (Git Bash)" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "🔑 Creating .env file..."
    cp .env_example .env
    echo "✏️ Please edit .env file to add your OpenAI API key (optional)"
fi

# Create uploads directory
mkdir -p uploads

echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "🚀 To start the application:"
echo "   1. Activate virtual environment:"
if [[ "$OS" == "Windows (Git Bash)" ]]; then
    echo "      source venv/Scripts/activate"
else
    echo "      source venv/bin/activate"
fi
echo "   2. Run the application:"
echo "      $PYTHON_CMD app.py"
echo "   3. Open browser to: http://localhost:5000"
echo ""
echo "💡 You can also use the run script:"
echo "   ./run.sh"
echo ""