@echo off
chcp 65001 >nul
title Windows Optimizer - Free
:: Demande les droits administrateur puis lance le script avec Bypass (pas besoin d'activer l'execution des scripts au prealable)
>nul 2>&1 "%SYSTEMROOT%\system32\cacls.exe" "%SYSTEMROOT%\system32\config\system"
if '%errorlevel%' NEQ '0' (
    echo Demande des droits administrateur...
    goto UACPrompt
) else ( goto gotAdmin )
:UACPrompt
    echo Set UAC = CreateObject^("Shell.Application"^) > "%temp%\getadmin.vbs"
    echo UAC.ShellExecute "%~s0", "", "", "runas", 1 >> "%temp%\getadmin.vbs"
    "%temp%\getadmin.vbs"
    exit /B
:gotAdmin
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File ".\Optimisation-PC-Free.ps1"
pause
