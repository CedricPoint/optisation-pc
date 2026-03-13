@echo off
chcp 65001 >nul
title Activation des scripts PowerShell
echo.
echo ============================================
echo   Activation de l'execution des scripts
echo   PowerShell (politique : RemoteSigned)
echo ============================================
echo.
echo Cela autorise l'execution des scripts .ps1 sur ton compte.
echo Une seule execution suffit.
echo.
powershell -NoProfile -ExecutionPolicy Bypass -Command "Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned -Force; Write-Host ''; Write-Host 'C''est fait. Tu peux maintenant lancer Optimisation-PC-Free.ps1 en tant qu''administrateur.' -ForegroundColor Green; Write-Host ''"
echo.
pause
