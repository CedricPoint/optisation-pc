<#
.SYNOPSIS
    Windows Optimizer - Edition FREE / Community
.DESCRIPTION
    Script d'optimisation Windows (bureautique & gaming).
    Profils : Bureautique / Gaming | Modes : Performance / Silencieux
.NOTES
    À lancer en tant qu'administrateur.
    Windows 10 / Windows 11
#>

#Requires -RunAsAdministrator

$Script:Version = "1.0.0-Free"
$Script:OSChoisi = ""

########### FONCTIONS GÉNÉRALES ###########

function Test-Admin {
    $currentUser = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
    return $currentUser.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

if (-not (Test-Admin)) {
    Write-Host ""
    Write-Host "  [!] Lance PowerShell en tant qu'administrateur puis relance ce script." -ForegroundColor Red
    Write-Host ""
    Read-Host "Appuie sur Entrée pour quitter"
    exit 1
}

function Show-Banner {
    Clear-Host
    Write-Host ""
    Write-Host "  =============================================" -ForegroundColor Cyan
    Write-Host "       WINDOWS OPTIMIZER - FREE EDITION       " -ForegroundColor Cyan
    Write-Host "  =============================================" -ForegroundColor Cyan
    Write-Host "  Version $Script:Version  |  OS: $Script:OSChoisi" -ForegroundColor DarkGray
    Write-Host "  =============================================" -ForegroundColor Cyan
    Write-Host ""
}

function Pause-Console {
    Write-Host ""
    Read-Host "  Appuie sur Entrée pour continuer"
}

function Confirm-Action($message) {
    $rep = Read-Host "  $message (o/n)"
    return ($rep -match '^[oOyY]')
}

function Demander-OS {
    $osDetected = (Get-CimInstance Win32_OperatingSystem).Caption
    Write-Host "  Systeme detecte : $osDetected" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  Confirme ton systeme :" -ForegroundColor Yellow
    Write-Host "  1. Windows 10"
    Write-Host "  2. Windows 11"
    Write-Host "  3. Autre / Ne pas specifier"
    $choix = Read-Host "  Ton choix"

    switch ($choix) {
        "1" { return "Windows 10" }
        "2" { return "Windows 11" }
        default { return "Inconnu" }
    }
}

# Demande OS au démarrage
$Script:OSChoisi = Demander-OS

########### NETTOYAGES ###########

function Nettoyage-Temp {
    Write-Host "  Nettoyage des fichiers temporaires..." -ForegroundColor Cyan
    $paths = @("$env:TEMP\*", "$env:WINDIR\Temp\*", "$env:LOCALAPPDATA\Temp\*")
    foreach ($p in $paths) {
        try {
            Remove-Item $p -Recurse -Force -ErrorAction SilentlyContinue
            Write-Host "    OK : $p" -ForegroundColor Green
        } catch {
            Write-Host "    Ignore : $p" -ForegroundColor Yellow
        }
    }
    Write-Host "  Termine." -ForegroundColor Green
    Pause-Console
}

function Nettoyage-UpdateCache {
    Write-Host "  Nettoyage du cache Windows Update..." -ForegroundColor Cyan
    if (-not (Confirm-Action "Arreter les services Windows Update pour vider le cache ?")) {
        Pause-Console
        return
    }
    try { net stop wuauserv /y 2>$null; net stop bits /y 2>$null } catch { }
    $folder = "$env:WINDIR\SoftwareDistribution\Download"
    try {
        Remove-Item "$folder\*" -Recurse -Force -ErrorAction SilentlyContinue
        Write-Host "  Cache Windows Update vide." -ForegroundColor Green
    } catch { Write-Host "  Erreur : $($_.Exception.Message)" -ForegroundColor Yellow }
    try { net start wuauserv 2>$null; net start bits 2>$null } catch { }
    Pause-Console
}

function Nettoyage-PreFetch {
    Write-Host "  Nettoyage du dossier Prefetch..." -ForegroundColor Cyan
    if (-not (Confirm-Action "Vider Prefetch ?")) {
        Pause-Console
        return
    }
    try {
        Remove-Item "$env:WINDIR\Prefetch\*" -Recurse -Force -ErrorAction SilentlyContinue
        Write-Host "  Prefetch vide." -ForegroundColor Green
    } catch { Write-Host "  Erreur : $($_.Exception.Message)" -ForegroundColor Yellow }
    Pause-Console
}

########### PLAN D'ALIMENTATION ###########

function Activer-Plan-Performance {
    param(
        [ValidateSet("Performance","Equilibre","Silencieux")]
        [string]$Mode = "Performance"
    )
    Write-Host "  Configuration du plan : $Mode" -ForegroundColor Cyan

    # GUID officiels des plans Windows (indépendants de la langue)
    $guidBalanced  = "381b4222-f694-41f0-9685-ff5bb260df2e"
    $guidHighPerf  = "8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c"

    $guidCible = $null

    if ($Mode -eq "Performance") {
        # D'abord : tenter le plan Haute performance
        $guidCible = $guidHighPerf
        try {
            powercfg -setactive $guidCible 2>$null
            Write-Host "  Plan 'Haute performance' active (GUID standard)." -ForegroundColor Green
            Pause-Console
            return
        } catch {
            # Si échec (plan supprimé), on retombe sur l'équilibré
            $guidCible = $guidBalanced
            Write-Host "  Plan 'Haute performance' indisponible, utilisation du plan 'Equilibre'." -ForegroundColor Yellow
        }
    } else {
        $guidCible = $guidBalanced
    }

    try {
        powercfg -setactive $guidCible 2>$null
        Write-Host "  Plan d'alimentation active." -ForegroundColor Green
    } catch {
        Write-Host "  Impossible d'appliquer le plan d'alimentation (droits / GUID manquant)." -ForegroundColor Yellow
    }
    Pause-Console
}

function Lancer-UI-PerformanceVisuelle {
    Write-Host "  Ouverture des options de performance visuelle..." -ForegroundColor Cyan
    Write-Host "  Choisis 'Ajuster pour les meilleures performances' si tu veux max FPS." -ForegroundColor Yellow
    Start-Process "SystemPropertiesPerformance.exe"
    Pause-Console
}

function Verifier-TRIM {
    Write-Host "  Etat du TRIM (SSD) :" -ForegroundColor Cyan
    try { fsutil behavior query DisableDeleteNotify } catch { Write-Host "  Erreur." -ForegroundColor Yellow }
    Pause-Console
}

########### SERVICES ###########

function Optimiser-Services-Bureautique {
    param([ValidateSet("Performance","Silencieux")][string]$Mode = "Performance")
    Write-Host "  Optimisation services BUREAUTIQUE ($Mode)..." -ForegroundColor Cyan
    $servicesManuel = @("Fax","XblGameSave","XboxNetApiSvc","XboxGipSvc")
    if ($Mode -eq "Silencieux") { $servicesManuel += "WSearch" }
    foreach ($svc in $servicesManuel) {
        try {
            $s = Get-Service -Name $svc -ErrorAction SilentlyContinue
            if ($null -ne $s) {
                Set-Service -Name $svc -StartupType Manual -ErrorAction SilentlyContinue
                Write-Host "    Manuel : $svc" -ForegroundColor Green
            }
        } catch { }
    }
    Pause-Console
}

function Optimiser-Services-Gaming {
    param([ValidateSet("Performance","Silencieux")][string]$Mode = "Performance")
    Write-Host "  Optimisation services GAMING ($Mode)..." -ForegroundColor Cyan
    $servicesManuel = @("WSearch","DiagTrack")
    if ($Mode -eq "Silencieux") { $servicesManuel += "SysMain" }
    foreach ($svc in $servicesManuel) {
        try {
            $s = Get-Service -Name $svc -ErrorAction SilentlyContinue
            if ($null -ne $s) {
                Set-Service -Name $svc -StartupType Manual -ErrorAction SilentlyContinue
                Write-Host "    Manuel : $svc" -ForegroundColor Green
            }
        } catch { }
    }
    Pause-Console
}

########### DÉMARRAGE ###########

function Lister-Programmes-Demarrage {
    Write-Host "  Programmes au demarrage (HKCU / HKLM) :" -ForegroundColor Cyan
    $paths = @("HKCU:\Software\Microsoft\Windows\CurrentVersion\Run","HKLM:\Software\Microsoft\Windows\CurrentVersion\Run")
    foreach ($p in $paths) {
        Write-Host "  $p" -ForegroundColor Yellow
        try {
            Get-ItemProperty -Path $p -ErrorAction SilentlyContinue | Get-Member -MemberType NoteProperty |
                Where-Object { $_.Name -notmatch '^PS' } | ForEach-Object { Write-Host "    - $($_.Name)" }
        } catch { }
    }
    Pause-Console
}

function Desactiver-Programme-Demarrage {
    Write-Host "  Desactivation d'un programme au demarrage..." -ForegroundColor Cyan
    $hive = Read-Host "  Ruche (1=HKCU, 2=HKLM, autre=annuler)"
    $base = $null
    switch ($hive) {
        "1" { $base = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run" }
        "2" { $base = "HKLM:\Software\Microsoft\Windows\CurrentVersion\Run" }
    }
    if (-not $base) { Pause-Console; return }
    try {
        $props = Get-ItemProperty -Path $base -ErrorAction Stop
    } catch { Write-Host "  Impossible de lire." -ForegroundColor Yellow; Pause-Console; return }
    $noms = $props.PSObject.Properties | Where-Object { $_.Name -notin @("PSPath","PSParentPath","PSChildName","PSDrive","PSProvider") } | Select-Object -ExpandProperty Name
    if (-not $noms) { Write-Host "  Aucune entree." -ForegroundColor Yellow; Pause-Console; return }
    $i = 1; $map = @{}
    foreach ($n in $noms) { Write-Host "  $i. $n"; $map[$i] = $n; $i++ }
    $choix = Read-Host "  Numero a desactiver (Entree=annuler)"
    if (-not $choix -or -not $map[[int]$choix]) { Pause-Console; return }
    $entry = $map[[int]$choix]
    if (-not (Confirm-Action "Supprimer '$entry' ?")) { Pause-Console; return }
    try {
        Remove-ItemProperty -Path $base -Name $entry -ErrorAction Stop
        Write-Host "  Supprime." -ForegroundColor Green
    } catch { Write-Host "  Erreur." -ForegroundColor Red }
    Pause-Console
}

########### TÉLÉMÉTRIE ###########

function Limiter-Telemetrie-Basique {
    Write-Host "  Reduction basique de la telemetrie..." -ForegroundColor Cyan
    if (-not (Confirm-Action "Continuer ?")) { Pause-Console; return }
    try {
        New-Item -Path "HKLM:\SOFTWARE\Policies\Microsoft\Windows\DataCollection" -Force | Out-Null
        Set-ItemProperty -Path "HKLM:\SOFTWARE\Policies\Microsoft\Windows\DataCollection" -Name "AllowTelemetry" -Type DWord -Value 0 -Force
        New-Item -Path "HKLM:\SOFTWARE\Policies\Microsoft\Windows\TabletPC" -Force | Out-Null
        Set-ItemProperty -Path "HKLM:\SOFTWARE\Policies\Microsoft\Windows\TabletPC" -Name "PreventHandwritingDataSharing" -Type DWord -Value 1 -Force
        Write-Host "  Applique (redemarrage conseille)." -ForegroundColor Green
    } catch { Write-Host "  Erreur." -ForegroundColor Yellow }
    Pause-Console
}

########### PROFILS ###########

function Profil-Bureautique {
    Show-Banner
    Write-Host "  PROFIL BUREAUTIQUE" -ForegroundColor Cyan
    Write-Host "  1. Mode Performance"
    Write-Host "  2. Mode Silencieux"
    $choix = Read-Host "  Choix"
    switch ($choix) {
        "1" { Activer-Plan-Performance -Mode "Performance"; Optimiser-Services-Bureautique -Mode "Performance" }
        "2" { Activer-Plan-Performance -Mode "Silencieux"; Optimiser-Services-Bureautique -Mode "Silencieux" }
        default { Write-Host "  Choix invalide." -ForegroundColor Red; Pause-Console }
    }
}

function Profil-Gaming {
    Show-Banner
    Write-Host "  PROFIL GAMING" -ForegroundColor Cyan
    Write-Host "  1. Mode Performance (FPS max)"
    Write-Host "  2. Mode Silencieux"
    $choix = Read-Host "  Choix"
    switch ($choix) {
        "1" { Activer-Plan-Performance -Mode "Performance"; Optimiser-Services-Gaming -Mode "Performance" }
        "2" { Activer-Plan-Performance -Mode "Silencieux"; Optimiser-Services-Gaming -Mode "Silencieux" }
        default { Write-Host "  Choix invalide." -ForegroundColor Red; Pause-Console }
    }
}

########### MENUS ###########

function Menu-Nettoyage {
    do {
        Show-Banner
        Write-Host "  MENU NETTOYAGE" -ForegroundColor Cyan
        Write-Host "  1. Fichiers temporaires"
        Write-Host "  2. Cache Windows Update"
        Write-Host "  3. Prefetch"
        Write-Host "  0. Retour"
        $c = Read-Host "  Choix"
        switch ($c) {
            "1" { Nettoyage-Temp }
            "2" { Nettoyage-UpdateCache }
            "3" { Nettoyage-PreFetch }
            "0" { break }
            default { Write-Host "  Invalide." -ForegroundColor Red; Pause-Console }
        }
    } while ($c -ne "0")
}

function Menu-Systeme {
    do {
        Show-Banner
        Write-Host "  MENU SYSTÈME & PERFORMANCE" -ForegroundColor Cyan
        Write-Host "  1. Options performance visuelle"
        Write-Host "  2. Verifier TRIM (SSD)"
        Write-Host "  3. Limiter telemetrie"
        Write-Host "  0. Retour"
        $c = Read-Host "  Choix"
        switch ($c) {
            "1" { Lancer-UI-PerformanceVisuelle }
            "2" { Verifier-TRIM }
            "3" { Limiter-Telemetrie-Basique }
            "0" { break }
            default { Write-Host "  Invalide." -ForegroundColor Red; Pause-Console }
        }
    } while ($c -ne "0")
}

function Menu-Demarrage {
    do {
        Show-Banner
        Write-Host "  MENU DÉMARRAGE" -ForegroundColor Cyan
        Write-Host "  1. Lister programmes demarrage"
        Write-Host "  2. Desactiver un programme"
        Write-Host "  0. Retour"
        $c = Read-Host "  Choix"
        switch ($c) {
            "1" { Lister-Programmes-Demarrage }
            "2" { Desactiver-Programme-Demarrage }
            "0" { break }
            default { Write-Host "  Invalide." -ForegroundColor Red; Pause-Console }
        }
    } while ($c -ne "0")
}

function Afficher-Menu-Principal {
    do {
        Show-Banner
        Write-Host "  1. Profil Bureautique"
        Write-Host "  2. Profil Gaming"
        Write-Host "  3. Nettoyage (Temp, Update, Prefetch)"
        Write-Host "  4. Systeme & Performance"
        Write-Host "  5. Demarrage (programmes auto)"
        Write-Host "  0. Quitter"
        Write-Host ""
        $choix = Read-Host "  Ton choix"
        switch ($choix) {
            "1" { Profil-Bureautique }
            "2" { Profil-Gaming }
            "3" { Menu-Nettoyage }
            "4" { Menu-Systeme }
            "5" { Menu-Demarrage }
            "0" { Write-Host "  A bientot." -ForegroundColor Green; break }
            default { Write-Host "  Choix invalide." -ForegroundColor Red; Pause-Console }
        }
    } while ($choix -ne "0")
}

########### LANCEMENT ###########

Afficher-Menu-Principal
