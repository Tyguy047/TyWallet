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
ICON_PATH = "../assets/app_icon.icns"  # Use app_icon from assets folder
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
    
    # Check if main script exists - use absolute path
    main_script_abs = os.path.abspath(MAIN_SCRIPT)
    if not os.path.exists(main_script_abs):
        print(f"❌ Main script not found: {main_script_abs}")
        sys.exit(1)
    print(f"✅ Main script found: {main_script_abs}")

def prepare_icon():
    """Prepare the app icon for macOS"""
    print("🎨 Preparing app icon...")
    
    # Use absolute paths for better reliability
    script_dir = os.path.dirname(os.path.abspath(__file__))
    assets_dir = os.path.join(script_dir, "../assets")
    icon_path_abs = os.path.abspath(ICON_PATH)
    
    # Check if .icns file exists
    if os.path.exists(icon_path_abs):
        print(f"✅ Using existing .icns icon: {icon_path_abs}")
        return icon_path_abs
    
    # If .icns doesn't exist, check for other formats and convert
    icon_formats = [
        "app_icon.png",
        "app_icon.jpg", 
        "app_icon.jpeg",
        "app_icon.ico"
    ]
    
    source_icon = None
    for icon_name in icon_formats:
        icon_full_path = os.path.join(assets_dir, icon_name)
        if os.path.exists(icon_full_path):
            source_icon = icon_full_path
            break
    
    if not source_icon:
        print("⚠️ No app_icon found in assets folder. App will use default icon.")
        return None
    
    print(f"📱 Found source icon: {source_icon}")
    print("🔄 Converting to .icns format for macOS...")
    
    try:
        # Create iconset directory with absolute path
        iconset_dir = os.path.join(assets_dir, "app_icon.iconset")
        os.makedirs(iconset_dir, exist_ok=True)
        
        # Standard macOS icon sizes
        icon_sizes = [
            (16, "icon_16x16.png"),
            (32, "icon_16x16@2x.png"),
            (32, "icon_32x32.png"),
            (64, "icon_32x32@2x.png"),
            (128, "icon_128x128.png"),
            (256, "icon_128x128@2x.png"),
            (256, "icon_256x256.png"),
            (512, "icon_256x256@2x.png"),
            (512, "icon_512x512.png"),
            (1024, "icon_512x512@2x.png")
        ]
        
        # Generate all required icon sizes using sips (macOS built-in tool)
        print("🔧 Generating icon sizes...")
        for size, filename in icon_sizes:
            output_path = os.path.join(iconset_dir, filename)
            cmd = ["sips", "-z", str(size), str(size), source_icon, "--out", output_path]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                print(f"⚠️ Failed to create {filename}: {result.stderr}")
            else:
                print(f"✅ Created {filename}")
        
        # Convert iconset to .icns using absolute paths
        print("🔄 Converting iconset to .icns...")
        icns_cmd = ["iconutil", "-c", "icns", iconset_dir, "-o", icon_path_abs]
        result = subprocess.run(icns_cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ Created .icns icon: {icon_path_abs}")
            # Clean up iconset directory
            shutil.rmtree(iconset_dir)
            return icon_path_abs
        else:
            print(f"⚠️ Failed to create .icns: {result.stderr}")
            return None
            
    except Exception as e:
        print(f"⚠️ Icon conversion failed: {e}")
        return None

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
    
    # Get absolute paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    main_script_abs = os.path.abspath(MAIN_SCRIPT)
    
    # Prepare icon
    icon_path = prepare_icon()
    
    # PyInstaller command arguments
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name", APP_NAME,
        "--windowed",  # No console window (GUI app)
        "--onedir",    # One directory mode for faster startup
        "--noconfirm", # Overwrite output directory without confirmation
        "--clean",     # Clean PyInstaller cache
        
        # Add data files with absolute paths
        f"--add-data={os.path.abspath('../assets')}:assets",  # Include assets folder
        f"--add-data={os.path.abspath('../btc.py')}:.",       # Include coin modules
        f"--add-data={os.path.abspath('../eth.py')}:.",
        f"--add-data={os.path.abspath('../xmr.py')}:.",
        f"--add-data={os.path.abspath('../utils.py')}:.",
        
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
        
        main_script_abs
    ]
    
    # Add icon if available - use absolute path
    if icon_path and os.path.exists(icon_path):
        cmd.extend(["--icon", icon_path])
        print(f"✅ Using app icon: {icon_path}")
    else:
        print("⚠️ No icon available - app will use default macOS icon")
    
    print(f"🚀 Running PyInstaller...")
    print(f"📍 Working directory: {os.getcwd()}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"❌ Build failed:")
        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)
        sys.exit(1)
    
    print("✅ Build completed successfully!")

def post_build_setup():
    """Perform post-build setup and optimizations"""
    print("🔧 Performing post-build setup...")
    
    app_path = f"dist/{APP_NAME}.app"
    
    if not os.path.exists(app_path):
        print(f"❌ Built app not found: {app_path}")
        sys.exit(1)
    
    # Check if icon was included and copy it to Resources if needed
    icon_path = prepare_icon()
    resources_dir = f"{app_path}/Contents/Resources"
    os.makedirs(resources_dir, exist_ok=True)
    
    icon_filename = "app_icon.icns"
    if icon_path and os.path.exists(icon_path):
        dest_icon_path = os.path.join(resources_dir, icon_filename)
        shutil.copy2(icon_path, dest_icon_path)
        print(f"✅ Copied icon to Resources: {dest_icon_path}")
    else:
        icon_filename = None
        print("⚠️ No icon to copy to Resources")
    
    # Create Info.plist with proper metadata and icon reference
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
    <string>APPL</string>"""
    
    # Add icon reference if available
    if icon_filename:
        info_plist_content += f"""
    <key>CFBundleIconFile</key>
    <string>{icon_filename}</string>"""
    
    info_plist_content += f"""
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
    
    print("✅ Created Info.plist with icon reference")
    
    # Set executable permissions
    exec_path = f"{app_path}/Contents/MacOS/{APP_NAME}"
    if os.path.exists(exec_path):
        os.chmod(exec_path, 0o755)
        print("✅ Set executable permissions")
    
    # Force macOS to refresh icon cache
    print("🔄 Refreshing macOS icon cache...")
    try:
        subprocess.run(["touch", app_path], check=True)
        subprocess.run(["killall", "Finder"], check=False)  # Don't fail if Finder isn't running
        print("✅ Icon cache refreshed")
    except Exception as e:
        print(f"⚠️ Could not refresh icon cache: {e}")

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
    print(f"🍎 Building {APP_NAME} for macOS (Apple Silicon)")
    print("=" * 50)
    
    # Change to script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # Print system info for debugging
    import platform
    print(f"🖥️  System: {platform.system()} {platform.release()}")
    print(f"🏗️  Architecture: {platform.machine()}")
    print(f"🐍 Python: {sys.version}")
    
    # Clean up any existing .spec files that might have universal2 settings
    for spec_file in Path(".").glob("*.spec"):
        spec_file.unlink()
        print(f"✅ Removed old spec file: {spec_file}")
    
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
        print("   • Distribute to other Apple Silicon Macs")
        
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