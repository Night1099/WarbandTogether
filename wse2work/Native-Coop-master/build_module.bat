@echo off
cd /d "%~dp0"
python run_module_build.py
exit /b %errorlevel%
