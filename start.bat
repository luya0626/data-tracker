@echo off
cd /d "%~dp0"
echo Starting L线...
start http://localhost:5000
python app.py
