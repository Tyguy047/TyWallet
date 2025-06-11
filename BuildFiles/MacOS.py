#!/usr/bin/env python3
"""
TyWallet macOS Build Script
Builds the TyWallet application for macOS using PyInstaller
Creates a .app bundle with all dependencies included
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

# Configuration
APP_NAME = "TyWallet"
MAIN_SCRIPT = "../main.py"
ICON_PATH = "../assets/tywallet.icns"  # Add this icon file if available
BUNDLE_ID = "xyz.tywallet.app"

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
    """Build the macOS application using PyInstaller"""
    print("🔨 Building TyWallet for macOS...")
    
    # PyInstaller command arguments
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name", APP_NAME,
        "--windowed",  # No console window (GUI app)
        "--onedir",    # One directory mode for faster startup
        "--noconfirm", # Overwrite output directory without confirmation
        "--clean",     # Clean PyInstaller cache
        
        # Add data files
        "--add-data", "../assets:assets",  # Include assets folder
        "--add-data", "../btc.py:.",       # Include coin modules
        "--add-data", "../eth.py:.",
        "--add-data", "../xmr.py:.",
        "--add-data", "../utils.py:.",
        
        # Add bitcoinlib data files (required for the library to work)
        "--collect-data", "bitcoinlib",
        "--copy-metadata", "bitcoinlib",
        
        # macOS specific options
        "--osx-bundle-identifier", BUNDLE_ID,
        
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
        
        MAIN_SCRIPT
    ]
    
    # Add icon if available
    if os.path.exists(ICON_PATH):
        cmd.extend(["--icon", ICON_PATH])
        print(f"✅ Using icon: {ICON_PATH}")
    else:
        print(f"⚠️ Icon not found: {ICON_PATH} (app will use default icon)")
    
    print(f"🚀 Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"❌ Build failed:")
        print(result.stderr)
        sys.exit(1)
    
    print("✅ Build completed successfully!")

def post_build_setup():
    """Perform post-build setup and optimizations"""
    print("🔧 Performing post-build setup...")
    
    app_path = f"dist/{APP_NAME}.app"
    
    if not os.path.exists(app_path):
        print(f"❌ Built app not found: {app_path}")
        sys.exit(1)
    
    # Create Info.plist with proper metadata
    info_plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleDisplayName</key>
    <string>{APP_NAME}</string>
    <key>CFBundleExecutable</key>
    <string>{APP_NAME}</string>
    <key>CFBundleIdentifier</key>
    <string>{BUNDLE_ID}</string>
    <key>CFBundleName</key>
    <string>{APP_NAME}</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0.0</string>
    <key>CFBundleVersion</key>
    <string>1.0.0</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>LSApplicationCategoryType</key>
    <string>public.app-category.finance</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.15</string>
    <key>NSHighResolutionCapable</key>
    <true/>
    <key>NSRequiresAquaSystemAppearance</key>
    <false/>
    <key>CFBundleDocumentTypes</key>
    <array>
        <dict>
            <key>CFBundleTypeName</key>
            <string>TyWallet Configuration</string>
            <key>CFBundleTypeExtensions</key>
            <array>
                <string>json</string>
            </array>
            <key>CFBundleTypeRole</key>
            <string>Editor</string>
        </dict>
    </array>
</dict>
</plist>"""
    
    info_plist_path = f"{app_path}/Contents/Info.plist"
    with open(info_plist_path, 'w') as f:
        f.write(info_plist_content)
    
    print("✅ Created Info.plist")
    
    # Set executable permissions
    exec_path = f"{app_path}/Contents/MacOS/{APP_NAME}"
    if os.path.exists(exec_path):
        os.chmod(exec_path, 0o755)
        print("✅ Set executable permissions")

def create_dmg():
    """Create a DMG installer (optional)"""
    print("📦 Creating DMG installer...")
    
    try:
        # Check if create-dmg is available and accessible
        result = subprocess.run(["which", "create-dmg"], capture_output=True, text=True)
        if result.returncode != 0:
            raise FileNotFoundError("create-dmg not found in PATH")
        
        # Test if create-dmg is executable
        subprocess.run(["create-dmg", "--version"], capture_output=True, check=True)
        
        dmg_cmd = [
            "create-dmg",
            "--volname", f"{APP_NAME} Installer",
            "--window-pos", "200", "120",
            "--window-size", "600", "400",
            "--icon-size", "100",
            "--app-drop-link", "425", "120",
            f"dist/{APP_NAME}.dmg",
            f"dist/{APP_NAME}.app"
        ]
        
        result = subprocess.run(dmg_cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ DMG created: dist/{APP_NAME}.dmg")
        else:
            print(f"⚠️ DMG creation failed: {result.stderr}")
            print("💡 You can manually drag the .app to Applications folder")
        
    except FileNotFoundError:
        print("⚠️ create-dmg not found. Install with: brew install create-dmg")
        print("💡 You can manually drag the .app to Applications folder")
    except subprocess.CalledProcessError as e:
        print(f"⚠️ create-dmg execution failed: {e}")
        print("💡 Try installing create-dmg: brew install create-dmg")
        print("💡 You can manually drag the .app to Applications folder")
    except PermissionError:
        print("⚠️ Permission denied when running create-dmg")
        print("💡 Try: chmod +x $(which create-dmg)")
        print("💡 You can manually drag the .app to Applications folder")

def main():
    """Main build process"""
    print(f"🍎 Building {APP_NAME} for macOS")
    print("=" * 50)
    
    # Change to script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    try:
        check_dependencies()
        clean_build()
        build_app()
        post_build_setup()
        
        print("\n" + "=" * 50)
        print("🎉 Build completed successfully!")
        print(f"📱 App location: dist/{APP_NAME}.app")
        print("💡 You can now:")
        print("   • Test the app by double-clicking it")
        print("   • Move it to /Applications folder")
        print("   • Distribute to other macOS users")
        
        # Try to create DMG
        try:
            create_dmg()
        except Exception as e:
            print(f"⚠️ DMG creation failed: {e}")
        
    except KeyboardInterrupt:
        print("\n❌ Build cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Build failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()