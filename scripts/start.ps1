# EmailSummarizer PowerShell Setup Script
# Works on Windows 10/11 with PowerShell 5.1+

param(
    [switch]$Run,
    [switch]$Help
)

function Show-Help {
    Write-Host "EmailSummarizer PowerShell Script" -ForegroundColor Cyan
    Write-Host "=================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Usage:"
    Write-Host "  .\start.ps1          # Setup and run the application"
    Write-Host "  .\start.ps1 -Run     # Just run (skip setup)"
    Write-Host "  .\start.ps1 -Help    # Show this help"
    Write-Host ""
}

function Test-PythonInstallation {
    try {
        $pythonVersion = python --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Found: $pythonVersion" -ForegroundColor Green
            return $true
        }
    }
    catch {
        # Try python3 command
        try {
            $pythonVersion = python3 --version 2>&1
            if ($LASTEXITCODE -eq 0) {
                Write-Host "✅ Found: $pythonVersion" -ForegroundColor Green
                return $true
            }
        }
        catch {
            Write-Host "❌ Python not found!" -ForegroundColor Red
            Write-Host "Please install Python 3.8+ from https://python.org" -ForegroundColor Yellow
            Write-Host "Make sure to check 'Add Python to PATH' during installation" -ForegroundColor Yellow
            return $false
        }
    }
    return $false
}

function Setup-Environment {
    Write-Host "🚀 Setting up EmailSummarizer..." -ForegroundColor Cyan
    Write-Host ""

    # Check Python
    Write-Host "🐍 Checking Python installation..." -ForegroundColor Blue
    if (-not (Test-PythonInstallation)) {
        Read-Host "Press Enter to exit"
        exit 1
    }

    # Create virtual environment
    if (-not (Test-Path "venv")) {
        Write-Host "📦 Creating virtual environment..." -ForegroundColor Blue
        python -m venv venv
        if ($LASTEXITCODE -ne 0) {
            Write-Host "❌ Failed to create virtual environment" -ForegroundColor Red
            Read-Host "Press Enter to exit"
            exit 1
        }
    }

    # Activate virtual environment
    Write-Host "🔧 Activating virtual environment..." -ForegroundColor Blue
    & "venv\Scripts\Activate.ps1"

    # Upgrade pip
    Write-Host "⬆️ Upgrading pip..." -ForegroundColor Blue
    python -m pip install --upgrade pip

    # Install requirements
    Write-Host "📚 Installing dependencies..." -ForegroundColor Blue
    pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to install dependencies" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }

    # Create .env file
    if (-not (Test-Path ".env") -and (Test-Path ".env_example")) {
        Write-Host "🔑 Creating .env file..." -ForegroundColor Blue
        Copy-Item ".env_example" ".env"
        Write-Host "✏️ You can edit .env to add your OpenAI API key (optional)" -ForegroundColor Yellow
    }

    # Create uploads directory
    if (-not (Test-Path "uploads")) {
        New-Item -ItemType Directory -Name "uploads" | Out-Null
    }

    Write-Host ""
    Write-Host "🎉 Setup completed successfully!" -ForegroundColor Green
}

function Start-Application {
    Write-Host "🌐 Starting EmailSummarizer web server..." -ForegroundColor Cyan
    Write-Host "📱 Open your browser to: http://localhost:5000" -ForegroundColor Yellow
    Write-Host "🛑 Press Ctrl+C to stop the server" -ForegroundColor Yellow
    Write-Host ""

    # Try to open browser
    try {
        Start-Process "http://localhost:5000"
    }
    catch {
        # Browser opening failed, continue anyway
    }

    # Start the application
    python app.py
}

# Main execution
if ($Help) {
    Show-Help
    exit 0
}

try {
    if (-not $Run) {
        Setup-Environment
    }

    # Check if virtual environment exists
    if (-not (Test-Path "venv")) {
        Write-Host "❌ Virtual environment not found!" -ForegroundColor Red
        Write-Host "Please run setup first: .\start.ps1" -ForegroundColor Yellow
        Read-Host "Press Enter to exit"
        exit 1
    }

    # Activate virtual environment
    & "venv\Scripts\Activate.ps1"

    Start-Application
}
catch {
    Write-Host "❌ An error occurred: $($_.Exception.Message)" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}
