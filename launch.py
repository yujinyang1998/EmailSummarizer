#!/usr/bin/env python3
"""
Universal launcher for EmailSummarizer
Automatically detects platform and runs appropriate setup/launch sequence
"""

import os
import sys
import platform
import subprocess
import webbrowser
from pathlib import Path


def get_platform():
    """Detect the current platform."""
    system = platform.system().lower()
    if system == "windows":
        return "windows"
    elif system == "darwin":
        return "macos"
    elif system == "linux":
        return "linux"
    else:
        return "unknown"


def check_python():
    """Check Python version compatibility."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python 3.8+ required. Found {version.major}.{version.minor}")
        return False
    print(f"✅ Python {version.major}.{version.minor} detected")
    return True


def run_platform_setup():
    """Run platform-specific setup if needed."""
    current_platform = get_platform()
    venv_path = Path("venv")

    if venv_path.exists():
        print("✅ Virtual environment already exists")
        return True

    print(f"🔧 Setting up for {current_platform}...")

    if current_platform == "windows":
        # Try PowerShell first, then batch
        powershell_script = Path("start.ps1")
        batch_script = Path("setup.bat")

        if powershell_script.exists():
            try:
                result = subprocess.run(
                    [
                        "powershell",
                        "-ExecutionPolicy",
                        "Bypass",
                        "-File",
                        str(powershell_script),
                    ],
                    capture_output=True,
                    text=True,
                )
                if result.returncode == 0:
                    return True
            except:
                pass

        if batch_script.exists():
            try:
                result = subprocess.run([str(batch_script)], shell=True)
                return result.returncode == 0
            except:
                pass

    else:  # macOS/Linux
        setup_script = Path("setup.sh")
        if setup_script.exists():
            try:
                # Make executable
                os.chmod(setup_script, 0o755)
                result = subprocess.run(["bash", str(setup_script)])
                return result.returncode == 0
            except:
                pass

    # Fallback to Python setup
    return python_setup()


def python_setup():
    """Fallback Python-based setup."""
    print("🐍 Running Python-based setup...")

    try:
        # Create virtual environment
        subprocess.check_call([sys.executable, "-m", "venv", "venv"])

        # Determine activation script
        if get_platform() == "windows":
            python_path = Path("venv/Scripts/python.exe")
        else:
            python_path = Path("venv/bin/python")

        # Install requirements
        subprocess.check_call(
            [str(python_path), "-m", "pip", "install", "-r", "requirements.txt"]
        )

        return True

    except subprocess.CalledProcessError as e:
        print(f"❌ Setup failed: {e}")
        return False


def start_application():
    """Start the EmailSummarizer application."""
    print("🚀 Starting EmailSummarizer...")

    # Determine Python executable
    if get_platform() == "windows":
        if Path("venv/Scripts/python.exe").exists():
            python_cmd = "venv/Scripts/python.exe"
        else:
            python_cmd = "python"
    else:
        if Path("venv/bin/python").exists():
            python_cmd = "venv/bin/python"
        else:
            python_cmd = "python3"

    # Check if app.py exists
    if not Path("app.py").exists():
        print("❌ app.py not found in current directory")
        return False

    print("🌐 Starting web server...")
    print("📱 Server will be available at: http://localhost:5000")
    print("🛑 Press Ctrl+C to stop")
    print("-" * 50)

    try:
        # Try to open browser
        try:
            webbrowser.open("http://localhost:5000")
        except:
            pass

        # Start the application
        subprocess.run([python_cmd, "app.py"])
        return True

    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
        return True
    except Exception as e:
        print(f"❌ Failed to start application: {e}")
        return False


def main():
    """Main entry point."""
    print("🎯 EmailSummarizer Universal Launcher")
    print("=" * 40)
    print(f"🖥️ Platform: {get_platform().title()}")

    # Check Python version
    if not check_python():
        input("Press Enter to exit...")
        return 1

    # Run setup if needed
    if not run_platform_setup():
        print("❌ Setup failed")
        input("Press Enter to exit...")
        return 1

    # Start application
    if not start_application():
        input("Press Enter to exit...")
        return 1

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n👋 Launcher interrupted")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        input("Press Enter to exit...")
        sys.exit(1)
