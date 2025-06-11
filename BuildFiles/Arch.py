#!/usr/bin/env python3
# filepath: /Users/tyler/Developer/TyWallet/BuildFiles/Arch.py
"""
TyWallet Arch Linux Build Script
Builds the TyWallet application for Arch Linux using PyInstaller
Creates a standalone executable with all dependencies included
"""

import os
import sys
import subprocess
import shutil
import stat
from pathlib import Path

# Configuration
APP_NAME = "TyWallet"
MAIN_SCRIPT = "../main.py"
ICON_PATH = "../assets/app_icon.png"  # Use app_icon from assets folder
DESKTOP_FILE_NAME = "tywallet.desktop"

def check_dependencies():
    """Check if required dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    try:
        import PyInstaller
        print(f"✅ PyInstaller {PyInstaller.__version__} found")
    except ImportError:
        print("❌ PyInstaller not found. Installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
        print("✅ PyInstaller installed")
    
    # Check if main script exists
    if not os.path.exists(MAIN_SCRIPT):
        print(f"❌ Main script not found: {MAIN_SCRIPT}")
        sys.exit(1)
    print(f"✅ Main script found: {MAIN_SCRIPT}")

def check_system_packages():
    """Check if required system packages are installed"""
    print("🔍 Checking system packages...")
    
    required_packages = {
        "python": "python",
        "python-pip": "python-pip", 
        "qt6-base": "qt6-base (for PySide6)",
        "gcc": "gcc (for compilation)"
    }
    
    missing_packages = []
    
    for package, description in required_packages.items():
        try:
            # Check if package is installed using pacman
            result = subprocess.run(["pacman", "-Q", package], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ {description} is installed")
            else:
                missing_packages.append(package)
        except FileNotFoundError:
            print("⚠️ pacman not found - assuming packages are available")
            break
    
    if missing_packages:
        print(f"❌ Missing packages: {', '.join(missing_packages)}")
        print(f"💡 Install with: sudo pacman -S {' '.join(missing_packages)}")
        response = input("Continue anyway? (y/N): ")
        if response.lower() != 'y':
            sys.exit(1)

def clean_build():
    """Clean previous build artifacts"""
    print("🧹 Cleaning previous builds...")
    
    dirs_to_clean = ["build", "dist", "__pycache__"]
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"✅ Removed {dir_name}")
    
    # Remove .spec files
    for spec_file in Path(".").glob("*.spec"):
        spec_file.unlink()
        print(f"✅ Removed {spec_file}")

def build_app():
    """Build the Linux application using PyInstaller"""
    print("🔨 Building TyWallet for Arch Linux...")
    
    # Check for icon in different formats
    icon_formats = [
        "../assets/app_icon.png",
        "../assets/app_icon.jpg",
        "../assets/app_icon.jpeg"
    ]
    
    icon_path = None
    for path in icon_formats:
        if os.path.exists(path):
            icon_path = path
            break
    
    # PyInstaller command arguments
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name", APP_NAME,
        "--windowed",  # No console window (GUI app)
        "--onefile",   # Single executable file
        "--noconfirm", # Overwrite output directory without confirmation
        "--clean",     # Clean PyInstaller cache
        
        # Add data files
        "--add-data", "../assets:assets",  # Include assets folder
        "--add-data", "../btc.py:.",       # Include coin modules
        "--add-data", "../eth.py:.",
        "--add-data", "../xmr.py:.",
        "--add-data", "../utils.py:.",
        
        # Exclude unnecessary modules to reduce size
        "--exclude-module", "tkinter",
        "--exclude-module", "matplotlib",
        "--exclude-module", "IPython",
        "--exclude-module", "jupyter",
        
        # Hidden imports that PyInstaller might miss
        "--hidden-import", "PySide6.QtCore",
        "--hidden-import", "PySide6.QtWidgets", 
        "--hidden-import", "PySide6.QtGui",
        "--hidden-import", "cryptography.fernet",
        "--hidden-import", "requests",
        "--hidden-import", "bitcoinlib",
        "--hidden-import", "web3",
        "--hidden-import", "eth_account",
        
        # Linux specific optimizations
        "--strip",     # Strip debug symbols to reduce size
        
        MAIN_SCRIPT
    ]
    
    # Add icon if available
    if icon_path:
        cmd.extend(["--icon", icon_path])
        print(f"✅ Using app icon: {icon_path}")
    else:
        print("⚠️ No app_icon found in assets folder - app will use default icon")
    
    print(f"🚀 Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"❌ Build failed:")
        print(result.stderr)
        sys.exit(1)
    
    print("✅ Build completed successfully!")

def create_desktop_file():
    """Create a .desktop file for system integration"""
    print("🖥️ Creating desktop file...")
    
    executable_path = os.path.abspath(f"dist/{APP_NAME}")
    
    # Check for icon in different formats
    icon_formats = [
        "../assets/app_icon.png",
        "../assets/app_icon.jpg",
        "../assets/app_icon.jpeg"
    ]
    
    icon_path = "accessories-calculator"  # Default fallback
    for path in icon_formats:
        if os.path.exists(path):
            icon_path = os.path.abspath(path)
            break
    
    desktop_content = f"""[Desktop Entry]
Version=1.0
Type=Application
Name=TyWallet
Comment=Open Source Cryptocurrency Wallet
Exec={executable_path}
Icon={icon_path}
Terminal=false
StartupNotify=true
Categories=Office;Finance;Qt;
Keywords=cryptocurrency;bitcoin;ethereum;monero;wallet;crypto;blockchain;
MimeType=application/json;
StartupWMClass=TyWallet
"""
    
    desktop_file_path = f"dist/{DESKTOP_FILE_NAME}"
    with open(desktop_file_path, 'w') as f:
        f.write(desktop_content)
    
    # Make desktop file executable
    os.chmod(desktop_file_path, stat.S_IRWXU | stat.S_IRGRP | stat.S_IROTH)
    
    print(f"✅ Desktop file created: {desktop_file_path}")
    return desktop_file_path

def create_install_script():
    """Create an installation script for easy system installation"""
    print("📦 Creating installation script...")
    
    install_script_content = f"""#!/bin/bash
# TyWallet Installation Script for Arch Linux

set -e

APP_NAME="{APP_NAME}"
INSTALL_DIR="/opt/tywallet"
BIN_DIR="/usr/local/bin"
DESKTOP_DIR="/usr/share/applications"
ICON_DIR="/usr/share/pixmaps"

echo "🔐 Installing TyWallet..."

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo "❌ This script must be run as root (use sudo)"
   exit 1
fi

# Create installation directory
echo "📁 Creating installation directory..."
mkdir -p "$INSTALL_DIR"

# Copy executable
echo "📋 Copying executable..."
cp "$APP_NAME" "$INSTALL_DIR/"
chmod +x "$INSTALL_DIR/$APP_NAME"

# Copy desktop file
echo "🖥️ Installing desktop file..."
cp "{DESKTOP_FILE_NAME}" "$DESKTOP_DIR/"

# Copy icon if available
if [ -f "../assets/app_icon.png" ]; then
    echo "🎨 Installing icon..."
    cp "../assets/app_icon.png" "$ICON_DIR/tywallet.png"
fi

# Create symlink in PATH
echo "🔗 Creating symlink..."
ln -sf "$INSTALL_DIR/$APP_NAME" "$BIN_DIR/tywallet"

# Update desktop database
echo "🔄 Updating desktop database..."
update-desktop-database "$DESKTOP_DIR" 2>/dev/null || true

# Update icon cache
echo "🎨 Updating icon cache..."
gtk-update-icon-cache -f -t "$ICON_DIR" 2>/dev/null || true

echo "✅ TyWallet installed successfully!"
echo "💡 You can now:"
echo "   • Run 'tywallet' from terminal"
echo "   • Find TyWallet in your application menu"
echo "   • Run: $INSTALL_DIR/$APP_NAME"

echo ""
echo "🗑️ To uninstall, run:"
echo "   sudo rm -rf $INSTALL_DIR"
echo "   sudo rm -f $BIN_DIR/tywallet"
echo "   sudo rm -f $DESKTOP_DIR/{DESKTOP_FILE_NAME}"
echo "   sudo rm -f $ICON_DIR/tywallet.png"
"""
    
    install_script_path = "dist/install.sh"
    with open(install_script_path, 'w') as f:
        f.write(install_script_content)
    
    # Make install script executable
    os.chmod(install_script_path, stat.S_IRWXU | stat.S_IRGRP | stat.S_IROTH)
    
    print(f"✅ Installation script created: {install_script_path}")
    return install_script_path

def create_package_info():
    """Create package information file"""
    print("📋 Creating package info...")
    
    package_info = f"""TyWallet for Arch Linux
======================

Build Information:
- Built on: {subprocess.check_output(['date'], text=True).strip()}
- Python Version: {sys.version}
- Architecture: {subprocess.check_output(['uname', '-m'], text=True).strip()}
- Build Host: {subprocess.check_output(['uname', '-n'], text=True).strip()}

Installation:
1. Run: sudo ./install.sh
2. Or manually copy files to desired locations

Files included:
- {APP_NAME} (main executable)
- {DESKTOP_FILE_NAME} (desktop integration)
- install.sh (installation script)
- README.txt (this file)

System Requirements:
- Arch Linux (or compatible)
- Qt6 libraries
- Python 3.8+ (for development)
- Internet connection (for price updates and transactions)

Support:
- Website: https://www.tywallet.xyz
- GitHub: https://github.com/Tyguy047/TyWallet
- Issues: https://github.com/Tyguy047/TyWallet/issues
"""
    
    with open("dist/README.txt", 'w') as f:
        f.write(package_info)
    
    print("✅ Package info created: dist/README.txt")

def post_build_setup():
    """Perform post-build setup and create distribution files"""
    print("🔧 Performing post-build setup...")
    
    executable_path = f"dist/{APP_NAME}"
    
    if not os.path.exists(executable_path):
        print(f"❌ Built executable not found: {executable_path}")
        sys.exit(1)
    
    # Ensure executable has correct permissions
    os.chmod(executable_path, stat.S_IRWXU | stat.S_IRGRP | stat.S_IROTH)
    print("✅ Set executable permissions")
    
    # Create desktop file
    create_desktop_file()
    
    # Create installation script
    create_install_script()
    
    # Create package info
    create_package_info()

def create_tar_package():
    """Create a tar.gz package for distribution"""
    print("📦 Creating distribution package...")
    
    package_name = f"{APP_NAME.lower()}-linux-x86_64"
    
    try:
        # Create tar.gz package
        subprocess.run([
            "tar", "-czf", f"dist/{package_name}.tar.gz",
            "-C", "dist",
            APP_NAME, DESKTOP_FILE_NAME, "install.sh", "README.txt"
        ], check=True)
        
        print(f"✅ Package created: dist/{package_name}.tar.gz")
        
    except subprocess.CalledProcessError as e:
        print(f"⚠️ Failed to create package: {e}")

def main():
    """Main build process"""
    print(f"🐧 Building {APP_NAME} for Arch Linux")
    print("=" * 50)
    
    # Change to script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    try:
        check_dependencies()
        check_system_packages()
        clean_build()
        build_app()
        post_build_setup()
        create_tar_package()
        
        print("\n" + "=" * 50)
        print("🎉 Build completed successfully!")
        print(f"🐧 Executable: dist/{APP_NAME}")
        print(f"🖥️ Desktop file: dist/{DESKTOP_FILE_NAME}")
        print(f"📦 Package: dist/{APP_NAME.lower()}-linux-x86_64.tar.gz")
        print("\n💡 Installation options:")
        print("   • Run: sudo ./dist/install.sh")
        print("   • Extract package and run install.sh")
        print(f"   • Manually run: ./dist/{APP_NAME}")
        
    except KeyboardInterrupt:
        print("\n❌ Build cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Build failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

