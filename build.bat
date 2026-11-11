@echo off
chcp 65001 >nul 2>&1
title OptimPC - Build EXE v2.0
color 0A

echo.
echo  ╔══════════════════════════════════════╗
echo  ║   OptimPC v2.0 — Build .exe          ║
echo  ║   by CedricPoint                     ║
echo  ╚══════════════════════════════════════╝
echo.

:: ── Vérification Python ──────────────────────────────────────────────────────
python --version >nul 2>&1
if errorlevel 1 (
    echo  [ERREUR] Python introuvable dans le PATH.
    echo  Téléchargez Python 3.10+ sur https://www.python.org/downloads/
    echo  Cochez bien "Add Python to PATH" à l'installation.
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('python --version 2^>^&1') do echo  [OK] %%i trouvé

:: ── Installation des dépendances ─────────────────────────────────────────────
echo.
echo  [1/3] Installation des dépendances (rich, psutil, pyinstaller)...
pip install rich>=13.7.0 psutil>=5.9.0 pyinstaller>=6.3.0 --quiet --upgrade
if errorlevel 1 (
    echo  [ERREUR] Échec de l'installation des dépendances.
    pause
    exit /b 1
)
echo  [OK] Dépendances installées

:: ── Nettoyage ─────────────────────────────────────────────────────────────────
echo.
echo  [2/3] Nettoyage des anciens builds...
if exist build   rmdir /s /q build
if exist dist    rmdir /s /q dist
if exist *.spec  del /q *.spec
echo  [OK] Nettoyé

:: ── Compilation ───────────────────────────────────────────────────────────────
echo.
echo  [3/3] Compilation en cours (peut prendre 30-60s)...
echo.

pyinstaller ^
    --onefile ^
    --console ^
    --uac-admin ^
    --name "OptimPC-v2.0" ^
    --version-file "version_info.txt" ^
    --hidden-import "rich" ^
    --hidden-import "rich.console" ^
    --hidden-import "rich.panel" ^
    --hidden-import "rich.table" ^
    --hidden-import "rich.progress" ^
    --hidden-import "rich.prompt" ^
    --hidden-import "rich.columns" ^
    --hidden-import "rich.rule" ^
    --hidden-import "rich.align" ^
    --hidden-import "rich.theme" ^
    --hidden-import "rich.text" ^
    --hidden-import "psutil" ^
    --hidden-import "psutil._pswindows" ^
    optimizer.py

if not exist "dist\OptimPC-v2.0.exe" (
    echo.
    echo  [ERREUR] La compilation a échoué. Vérifiez les messages ci-dessus.
    pause
    exit /b 1
)

:: ── Copie finale ──────────────────────────────────────────────────────────────
copy "dist\OptimPC-v2.0.exe" "OptimPC-v2.0.exe" >nul
echo.
echo  ╔══════════════════════════════════════╗
echo  ║   BUILD RÉUSSI !                     ║
echo  ╠══════════════════════════════════════╣
for %%F in ("OptimPC-v2.0.exe") do echo  ║  Taille: %%~zF octets
echo  ║  Fichier: OptimPC-v2.0.exe           ║
echo  ╚══════════════════════════════════════╝
echo.
echo  Double-cliquez sur OptimPC-v2.0.exe pour lancer l'optimiseur.
echo.
pause
