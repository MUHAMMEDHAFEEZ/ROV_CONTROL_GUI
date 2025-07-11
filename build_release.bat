@echo off
echo ROV Control GUI - Build Script
echo ==============================
echo.

echo [1/4] Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 goto error

echo.
echo [2/4] Installing build tools...
pip install -r requirements-build.txt
if errorlevel 1 goto error

echo.
echo [3/4] Building executable...
python build_exe.py
if errorlevel 1 goto error

echo.
echo [4/4] Creating release package...
if not exist "release" mkdir release
copy "dist\ROV_Control_GUI.exe" "release\"
copy "dist\install.bat" "release\"
copy "config.ini" "release\"
copy "README.md" "release\"
copy "LICENSE" "release\"
copy "assets\icons\logo.ico" "release\"
if exist "assets" xcopy "assets" "release\assets\" /E /I

echo.
echo =====================================
echo BUILD COMPLETED SUCCESSFULLY!
echo =====================================
echo.
echo Files created in 'release' folder:
dir release /B
echo.
echo You can now:
echo 1. Test the executable: release\ROV_Control_GUI.exe
echo 2. Create a zip file for distribution
echo 3. Upload to GitHub releases
echo.
pause
goto end

:error
echo.
echo =====================================
echo BUILD FAILED!
echo =====================================
echo Please check the error messages above.
echo.
pause

:end
