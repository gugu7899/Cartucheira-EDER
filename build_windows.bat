@echo off
setlocal
cd /d "%~dp0"
title Gerar Cartucheira MBS.exe
echo Instalando dependencias...
py -3.12 -m pip install --upgrade pip
if errorlevel 1 goto error
py -3.12 -m pip install -r requirements.txt
if errorlevel 1 goto error
echo Gerando executavel Windows 64 bits...
py -3.12 -m PyInstaller --clean --noconfirm "Cartucheira EDER.spec"
if errorlevel 1 goto error
echo PRONTO: dist\Cartucheira MBS.exe
pause
exit /b 0
:error
echo Falha. Instale o Python 3.12 de 64 bits e execute novamente.
pause
exit /b 1
