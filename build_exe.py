"""
Build script for creating ROV Control GUI executable
"""
import PyInstaller.__main__
import os
import sys
import shutil

def build_executable():
    """Build the executable using PyInstaller"""
    
    # Define the main script
    main_script = "main.py"
    
    # Define PyInstaller arguments
    args = [
        main_script,
        '--name=ROV_Control_GUI',
        '--onefile',
        '--windowed',
        '--add-data=assets;assets',
        '--add-data=config.ini;.',
        '--hidden-import=PyQt6',
        '--hidden-import=pyqtgraph',
        '--hidden-import=pyserial',
        '--hidden-import=opencv-python',
        '--hidden-import=numpy',
        '--hidden-import=PIL',
        '--hidden-import=pygame',
        '--collect-submodules=gui',
        '--collect-submodules=communication',
        '--collect-submodules=controller',
        '--collect-submodules=sensors',
        '--collect-submodules=utils',
        '--distpath=dist',
        '--workpath=build',
        '--specpath=.',
        '--clean',
    ]
    
    # Add icon if it exists
    icon_path = 'assets/icons/logo.ico'
    if os.path.exists(icon_path):
        args.insert(4, f'--icon={icon_path}')
        print(f"Using icon: {icon_path}")
    else:
        print("Warning: Icon file not found, building without icon")
    
    print("Building ROV Control GUI executable...")
    print(f"Arguments: {args}")
    
    try:
        # Run PyInstaller
        PyInstaller.__main__.run(args)
        
        print("\n" + "="*50)
        print("BUILD COMPLETED SUCCESSFULLY!")
        print("="*50)
        print(f"Executable created: dist/ROV_Control_GUI.exe")
        print("You can now distribute this file to users.")
        
        # Create a simple installer batch file
        create_installer_batch()
        
    except Exception as e:
        print(f"Build failed: {e}")
        sys.exit(1)

def create_installer_batch():
    """Create a simple installer batch file"""
    installer_content = """@echo off
echo ROV Control GUI Installer
echo =======================
echo.
echo This will copy the ROV Control GUI to your system.
echo.
pause

if not exist "C:\\Program Files\\ROV_Control_GUI" (
    mkdir "C:\\Program Files\\ROV_Control_GUI"
)

copy "ROV_Control_GUI.exe" "C:\\Program Files\\ROV_Control_GUI\\"
copy "config.ini" "C:\\Program Files\\ROV_Control_GUI\\" 2>nul

echo.
echo Creating desktop shortcut...
echo Set oWS = WScript.CreateObject("WScript.Shell") > CreateShortcut.vbs
echo sLinkFile = "%USERPROFILE%\\Desktop\\ROV Control GUI.lnk" >> CreateShortcut.vbs
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> CreateShortcut.vbs
echo oLink.TargetPath = "C:\\Program Files\\ROV_Control_GUI\\ROV_Control_GUI.exe" >> CreateShortcut.vbs
echo oLink.Save >> CreateShortcut.vbs
cscript CreateShortcut.vbs
del CreateShortcut.vbs

echo.
echo Installation completed!
echo ROV Control GUI has been installed to C:\\Program Files\\ROV_Control_GUI\\
echo A desktop shortcut has been created.
echo.
pause
"""
    
    with open('dist/install.bat', 'w') as f:
        f.write(installer_content)
    
    print("Installer batch file created: dist/install.bat")

if __name__ == "__main__":
    build_executable()
