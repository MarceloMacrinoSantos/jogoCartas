@echo off
cd /d "%~dp0"
if exist .venv (
    echo Removendo ambiente antigo...
    rmdir /s /q .venv
)
echo Criando o ambiente virtual (.venv)...
py -m venv .venv || python -m venv .venv
if not exist .venv\Scripts\python.exe (
    echo ERRO: nao foi possivel criar o ambiente virtual. Verifique se o Python esta instalado.
    pause
    exit /b 1
)
echo Instalando dependencias...
.venv\Scripts\python -m pip install --upgrade pip
.venv\Scripts\python -m pip install --only-binary=:all: -r requirements.txt
.venv\Scripts\python -c "import pygame" 2>nul
if errorlevel 1 (
    echo ERRO ao instalar o pygame-ce.
    pause
    exit /b 1
)
echo.
echo Pronto! Agora de dois cliques em jogar.bat
pause
