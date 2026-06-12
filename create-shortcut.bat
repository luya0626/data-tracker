@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo Generating icon from L.png...
python -c "from PIL import Image; img=Image.open('L.png'); img.save('icon.ico',format='ICO',sizes=[(64,64),(32,32),(16,16)])" 2>nul
if exist "icon.ico" (echo Icon OK) else (echo Skipped - run: pip install Pillow)

echo Creating desktop shortcut...
python create_shortcut.py

echo.
echo Done! Double-click "L线" on your desktop.
pause
