#!/usr/bin/env python3
"""
Build script to create standalone executables for EmailSummarizer.
Creates executables for Windows, macOS, and Linux.
"""

import os
import sys
import platform
import subprocess
import shutil
from pathlib import Path


def check_pyinstaller():
    """Check if PyInstaller is installed."""
    try:
        import PyInstaller

        return True
    except ImportError:
        print("❌ PyInstaller not found. Installing...")
        try:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", "pyinstaller"]
            )
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to install PyInstaller")
            return False


def build_executable():
    """Build executable for the current platform."""
    current_platform = platform.system().lower()

    print(f"🔨 Building executable for {current_platform}...")

    # Base PyInstaller command
    cmd = [
        "pyinstaller",
        "--onefile",
        "--name",
        f"EmailSummarizer-{current_platform}",
        "--add-data",
        (
            "templates;templates"
            if current_platform == "windows"
            else "templates:templates"
        ),
        "--add-data",
        "src;src" if current_platform == "windows" else "src:src",
        "--add-data",
        "requirements.txt;." if current_platform == "windows" else "requirements.txt:.",
        "--hidden-import",
        "flask",
        "--hidden-import",
        "openai",
        "--hidden-import",
        "PyPDF2",
        "--hidden-import",
        "dotenv",
        "--hidden-import",
        "werkzeug",
        "--noconsole" if current_platform == "windows" else "--console",
        "app.py",
    ]

    # Add platform-specific options
    if current_platform == "darwin":  # macOS
        cmd.extend(["--osx-bundle-identifier", "com.emailsummarizer.app"])

    print(f"🏃 Running: {' '.join(cmd)}")

    try:
        subprocess.check_call(cmd)
        print("✅ Build completed successfully!")

        # Create distribution folder
        dist_dir = Path("dist")
        if dist_dir.exists():
            print(f"📦 Executable created in: {dist_dir.absolute()}")

            # List created files
            for file in dist_dir.iterdir():
                if file.is_file():
                    size_mb = file.stat().st_size / (1024 * 1024)
                    print(f"   📄 {file.name} ({size_mb:.1f} MB)")

        return True

    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        return False


def create_installer():
    """Create a simple installer package."""
    current_platform = platform.system().lower()

    if current_platform == "windows":
        # Create a simple batch installer
        installer_content = """@echo off
echo Installing EmailSummarizer...
mkdir "%LOCALAPPDATA%\\EmailSummarizer" 2>nul
copy EmailSummarizer-windows.exe "%LOCALAPPDATA%\\EmailSummarizer\\"
echo Creating desktop shortcut...
echo Set oWS = WScript.CreateObject("WScript.Shell") > CreateShortcut.vbs
echo sLinkFile = "%USERPROFILE%\\Desktop\\EmailSummarizer.lnk" >> CreateShortcut.vbs
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> CreateShortcut.vbs
echo oLink.TargetPath = "%LOCALAPPDATA%\\EmailSummarizer\\EmailSummarizer-windows.exe" >> CreateShortcut.vbs
echo oLink.Save >> CreateShortcut.vbs
cscript CreateShortcut.vbs
del CreateShortcut.vbs
echo Installation complete!
pause
"""

        with open("dist/install.bat", "w") as f:
            f.write(installer_content)

        print("📦 Created Windows installer: dist/install.bat")

    elif current_platform == "darwin":  # macOS
        # Create a simple shell installer
        installer_content = """#!/bin/bash
echo "Installing EmailSummarizer..."
mkdir -p "$HOME/Applications"
cp EmailSummarizer-darwin "$HOME/Applications/"
chmod +x "$HOME/Applications/EmailSummarizer-darwin"

# Create alias
echo "alias emailsummarizer='$HOME/Applications/EmailSummarizer-darwin'" >> ~/.zshrc
echo "alias emailsummarizer='$HOME/Applications/EmailSummarizer-darwin'" >> ~/.bash_profile

echo "Installation complete!"
echo "You can run EmailSummarizer with: emailsummarizer"
echo "Or find it in: $HOME/Applications/"
"""

        with open("dist/install.sh", "w") as f:
            f.write(installer_content)

        os.chmod("dist/install.sh", 0o755)
        print("📦 Created macOS installer: dist/install.sh")

    else:  # Linux
        # Create a simple shell installer
        installer_content = """#!/bin/bash
echo "Installing EmailSummarizer..."
mkdir -p "$HOME/.local/bin"
cp EmailSummarizer-linux "$HOME/.local/bin/"
chmod +x "$HOME/.local/bin/EmailSummarizer-linux"

# Create desktop entry
mkdir -p "$HOME/.local/share/applications"
cat > "$HOME/.local/share/applications/emailsummarizer.desktop" << EOF
[Desktop Entry]
Name=EmailSummarizer
Comment=PDF Email Summarizer
Exec=$HOME/.local/bin/EmailSummarizer-linux
Icon=application-pdf
Terminal=false
Type=Application
Categories=Office;
EOF

echo "Installation complete!"
echo "You can run EmailSummarizer from the applications menu"
echo "Or from terminal: $HOME/.local/bin/EmailSummarizer-linux"
"""

        with open("dist/install.sh", "w") as f:
            f.write(installer_content)

        os.chmod("dist/install.sh", 0o755)
        print("📦 Created Linux installer: dist/install.sh")


def main():
    """Main build process."""
    print("🔨 EmailSummarizer Executable Builder")
    print("=" * 40)

    # Check PyInstaller
    if not check_pyinstaller():
        return 1

    # Clean previous builds
    if Path("dist").exists():
        print("🧹 Cleaning previous builds...")
        shutil.rmtree("dist")

    if Path("build").exists():
        shutil.rmtree("build")

    # Build executable
    if not build_executable():
        return 1

    # Create installer
    create_installer()

    print("\n🎉 Build process completed!")
    print(f"📦 Check the 'dist' folder for your executable and installer")

    return 0


if __name__ == "__main__":
    sys.exit(main())
