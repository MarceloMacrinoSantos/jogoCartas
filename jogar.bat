@echo off
cd /d "%~dp0"
.venv\Scripts\python -c "import pygame" 2>nul
if errorlevel 1 call instalar.bat
.venv\Scripts\python visual.py
if errorlevel 1 pause
