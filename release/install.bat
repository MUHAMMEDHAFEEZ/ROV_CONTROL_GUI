@echo off
echo ROV Control GUI Installer
echo =======================
echo.
echo This will copy the ROV Control GUI to your system.
echo.
pause

if not exist "C:\Program Files\ROV_Control_GUI" (
    mkdir "C:\Program Files\ROV_Control_GUI"
)

copy "ROV_Control_GUI.exe" "C:\Program Files\ROV_Control_GUI\"
copy "config.ini" "C:\Program Files\ROV_Control_GUI\" 2>nul

echo.
echo Creating desktop shortcut...
echo Set oWS = WScript.CreateObject("WScript.Shell") > CreateShortcut.vbs
echo sLinkFile = "%USERPROFILE%\Desktop\ROV Control GUI.lnk" >> CreateShortcut.vbs
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> CreateShortcut.vbs
echo oLink.TargetPath = "C:\Program Files\ROV_Control_GUI\ROV_Control_GUI.exe" >> CreateShortcut.vbs
echo oLink.Save >> CreateShortcut.vbs
cscript CreateShortcut.vbs
del CreateShortcut.vbs

echo.
echo Installation completed!
echo ROV Control GUI has been installed to C:\Program Files\ROV_Control_GUI\
echo A desktop shortcut has been created.
echo.
pause
