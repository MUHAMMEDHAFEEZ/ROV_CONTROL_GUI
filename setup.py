"""
ROV Control System Dependency Manager
Checks and installs all required libraries
"""

import subprocess
import sys
import os
from pathlib import Path
import pyfiglet

ascii_banner = pyfiglet.figlet_format("ROV Control System Setup")
print(ascii_banner)

def check_python_version():
    """Check Python version"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Error: Python 3.8 or higher is required")
        print(f"Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    else:
        print(f"✅ Python version is suitable: {version.major}.{version.minor}.{version.micro}")
        return True

def install_package(package_name, import_name=None):
    """Install a Python package"""
    if import_name is None:
        import_name = package_name
    
    try:
        __import__(import_name)
        print(f"✅ {package_name} is already installed")
        return True
    except ImportError:
        print(f"⏳ Installing {package_name}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
            print(f"✅ Successfully installed {package_name}")
            return True
        except subprocess.CalledProcessError:
            print(f"❌ Failed to install {package_name}")
            return False

def check_and_install_requirements():
    """Check and install all requirements"""
    print("🔍 Checking requirements...")
    
    requirements = [
        ("PyQt6", "PyQt6"),
        ("pyserial", "serial"),
        ("opencv-python", "cv2"),
        ("numpy", "numpy"),
        ("pyqtgraph", "pyqtgraph"),
        ("pygame", "pygame"),
        ("PyYAML", "yaml"),
        ("configparser", "configparser"),
        ("Pillow", "PIL"),
    ]
    
    failed_packages = []
    
    for package_name, import_name in requirements:
        if not install_package(package_name, import_name):
            failed_packages.append(package_name)
    
    if failed_packages:
        print(f"\n❌ Failed to install: {', '.join(failed_packages)}")
        print("Try installing them manually using:")
        for package in failed_packages:
            print(f"  pip install {package}")
        return False
    else:
        print("\n✅ All requirements installed successfully!")
        return True

def check_hardware():
    """Check for available hardware"""
    print("\n🔌 Checking hardware...")
    
    # Check camera
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            print("✅ Camera found")
            cap.release()
        else:
            print("⚠️  No camera found (simulation will be used)")
    except:
        print("⚠️  Unable to check camera")
    
    # Check joystick
    try:
        import pygame
        pygame.init()
        pygame.joystick.init()
        joystick_count = pygame.joystick.get_count()
        if joystick_count > 0:
            print(f"✅ Found {joystick_count} joystick(s)")
            for i in range(joystick_count):
                joystick = pygame.joystick.Joystick(i)
                print(f"  - {joystick.get_name()}")
        else:
            print("⚠️  No joystick found")
        pygame.quit()
    except:
        print("⚠️  Unable to check joystick")

def create_directories():
    """Create required directories"""
    print("\n📁 Creating directories...")
    
    directories = [
        "logs",
        "recordings",
        "snapshots",
        "assets/icons",
        "assets/images", 
        "assets/sounds"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Directory created: {directory}")

def check_config_file():
    """Check for config file"""
    print("\n⚙️  Checking config file...")
    
    config_file = Path("config.ini")
    if config_file.exists():
        print("✅ Config file found")
    else:
        print("⚠️  Config file not found - a default one will be created")

def main():
    """Main function"""
    print("🚀 ROV Control System Dependency Manager")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Check and install requirements
    if not check_and_install_requirements():
        print("\n❌ Failed to install some requirements")
        input("Press Enter to continue or Ctrl+C to exit...")
    
    # Check hardware
    check_hardware()
    
    # Create directories
    create_directories()
    
    # Check config file
    check_config_file()
    
    print("\n" + "=" * 50)
    print("✅ System check complete!")
    print("\nYou can now run the app using:")
    print("  python main.py")
    print("\nOr use:")
    print("  python setup.py --run")
    
    return True

if __name__ == "__main__":
    # Check for arguments
    if len(sys.argv) > 1 and sys.argv[1] == "--run":
        # Run checks then run the app
        if main():
            print("\n🚀 Launching the app...")
            try:
                import main as rov_main
                rov_main.main()
            except Exception as e:
                print(f"❌ Error while running the app: {e}")
                sys.exit(1)
    else:
        # Only run system check
        main()
