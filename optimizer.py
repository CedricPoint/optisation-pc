#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OptimPC v2.0.0 - Windows Optimizer
100% Gratuit & Open Source by CedricPoint
https://github.com/CedricPoint/optisation-pc
"""

VERSION = "2.0.0"
AUTHOR  = "CedricPoint"
GITHUB  = "https://github.com/CedricPoint/optisation-pc"

import os, sys, ctypes, subprocess, shutil, tempfile, time, logging, platform, winreg
from pathlib import Path
from datetime import datetime

# ── Bootstrap deps (dev mode; .exe les embarque) ──────────────────────────────
if not getattr(sys, "frozen", False):
    try:
        import rich, psutil
    except ImportError:
        print("[!] Installation des dependances en cours...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "rich>=13", "psutil>=5"],
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn
from rich.prompt import Prompt, Confirm
from rich.text import Text
from rich.align import Align
from rich.rule import Rule
from rich.columns import Columns
from rich.theme import Theme
import psutil

# ── Logging ───────────────────────────────────────────────────────────────────
LOG_DIR = Path(os.environ.get("APPDATA", ".")) / "OptimPC" / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / f"optimpc_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(filename=LOG_FILE, level=logging.INFO,
                    format="%(asctime)s [%(levelname)s] %(message)s", encoding="utf-8")

THEME = Theme({
    "success": "bold green", "error": "bold red", "warning": "bold yellow",
    "info": "bold cyan", "accent": "bold magenta", "dim_w": "dim white",
})
console = Console(theme=THEME)

# ── Admin ─────────────────────────────────────────────────────────────────────
def is_admin() -> bool:
    try: return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except: return False

def elevate():
    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(f'"{a}"' for a in sys.argv), None, 1)
        sys.exit(0)

# ── Helpers ───────────────────────────────────────────────────────────────────
def fmt_bytes(b: int) -> str:
    for u in ("o", "Ko", "Mo", "Go", "To"):
        if b < 1024: return f"{b:.1f} {u}"
        b /= 1024
    return f"{b:.1f} Po"

def run(cmd: list, capture=True) -> tuple[int, str]:
    try:
        r = subprocess.run(cmd, capture_output=capture, text=True, timeout=60,
                           creationflags=subprocess.CREATE_NO_WINDOW if capture else 0)
        return r.returncode, (r.stdout or "") + (r.stderr or "")
    except Exception as e:
        return -1, str(e)

def reg_set(hive, path: str, name: str, value, vtype=winreg.REG_DWORD) -> bool:
    try:
        k = winreg.CreateKeyEx(hive, path, 0, winreg.KEY_SET_VALUE | winreg.KEY_WOW64_64KEY)
        winreg.SetValueEx(k, name, 0, vtype, value)
        winreg.CloseKey(k)
        logging.info(f"REG SET {path}\\{name} = {value}")
        return True
    except Exception as e:
        logging.error(f"REG ERR {path}\\{name}: {e}")
        return False

def reg_del(hive, path: str, name: str) -> bool:
    try:
        k = winreg.OpenKey(hive, path, 0, winreg.KEY_SET_VALUE | winreg.KEY_WOW64_64KEY)
        winreg.DeleteValue(k, name)
        winreg.CloseKey(k)
        return True
    except FileNotFoundError:
        return True
    except Exception as e:
        logging.error(f"REG DEL ERR {path}\\{name}: {e}")
        return False

def svc(name: str, start: str) -> bool:
    c, _ = run(["sc", "config", name, f"start={start}"])
    return c == 0

def svc_stop(name: str):
    run(["sc", "stop", name])

# ── UI ────────────────────────────────────────────────────────────────────────
def _ok(msg):   console.print(f"  [success]✓[/]  {msg}"); logging.info(f"OK: {msg}")
def _err(msg):  console.print(f"  [error]✗[/]  {msg}"); logging.error(f"ERR: {msg}")
def _info(msg): console.print(f"  [info]→[/]  {msg}"); logging.info(f"INFO: {msg}")
def _warn(msg): console.print(f"  [warning]⚠[/]  {msg}"); logging.warning(f"WARN: {msg}")
def _sec(title): console.print(); console.print(Rule(f"[bold cyan]{title}[/]", style="cyan"))
def _pause():   Prompt.ask("\n  [dim_w]Appuyez sur Entrée pour continuer[/]", default="")

def header():
    console.clear()
    art = Text(justify="center")
    art.append("  ██████╗ ██████╗ ████████╗██╗███╗   ███╗    ██████╗  ██████╗ \n", "bold cyan")
    art.append("  ██╔══██╗██╔══██╗╚══██╔══╝██║████╗ ████║    ██╔══██╗██╔════╝ \n", "bold cyan")
    art.append("  ██║  ██║██████╔╝   ██║   ██║██╔████╔██║    ██████╔╝██║      \n", "bold blue")
    art.append("  ██║  ██║██╔═══╝    ██║   ██║██║╚██╔╝██║    ██╔═══╝ ██║      \n", "bold blue")
    art.append("  ██████╔╝██║        ██║   ██║██║ ╚═╝ ██║    ██║     ╚██████╗ \n", "bold magenta")
    art.append("  ╚═════╝ ╚═╝        ╚═╝   ╚═╝╚═╝     ╚═╝    ╚═╝      ╚═════╝ ", "bold magenta")
    console.print(Panel(
        Align(art, align="center"),
        title=f"[bold white]v{VERSION}[/] — [cyan]Windows Optimizer[/] — [dim]{AUTHOR}[/]",
        subtitle=f"[dim]{GITHUB}[/]",
        border_style="bright_blue", padding=(0, 2),
    ))
    console.print()

def show_sysinfo():
    t = Table(show_header=False, box=None, padding=(0, 1))
    t.add_column("K", style="dim", width=16)
    t.add_column("V", style="bold white")
    # OS
    wv = platform.win32_ver()
    t.add_row("🖥  OS", f"Windows {wv[0]} {wv[2]}  ({platform.architecture()[0]})")
    # CPU
    cpu_name = platform.processor() or "Inconnu"
    cpus_p = psutil.cpu_count(logical=False) or "?"
    cpus_l = psutil.cpu_count(logical=True) or "?"
    freq = psutil.cpu_freq()
    freq_str = f"  @{freq.current:.0f}/{freq.max:.0f} MHz" if freq else ""
    t.add_row("⚙  CPU", f"{cpu_name}  ({cpus_p}C/{cpus_l}T){freq_str}")
    # RAM
    m = psutil.virtual_memory()
    col = "green" if m.percent < 70 else "yellow" if m.percent < 85 else "red"
    t.add_row("🧠  RAM",
        f"{fmt_bytes(m.total)}  ({fmt_bytes(m.available)} libre)  "
        f"[[{col}]{m.percent:.0f}% utilisé[/]]")
    # Disks
    for dp in psutil.disk_partitions():
        if "cdrom" in dp.opts or not dp.mountpoint: continue
        try:
            du = psutil.disk_usage(dp.mountpoint)
            col = "green" if du.percent < 75 else "yellow" if du.percent < 90 else "red"
            t.add_row(f"💾  {dp.mountpoint}",
                f"{fmt_bytes(du.total)}  ({fmt_bytes(du.free)} libre)  "
                f"[[{col}]{du.percent:.0f}%[/]]  [{dp.fstype}]")
        except: pass
    console.print(Panel(t, title="[bold]Système[/]", border_style="blue"))
    console.print()

# ═════════════════════════════════════════════════════════════════════════════
# 1. NETTOYAGE
# ═════════════════════════════════════════════════════════════════════════════
def _del_folder(path: Path) -> int:
    n = 0
    if not path.exists(): return 0
    for item in path.iterdir():
        try:
            if item.is_file() or item.is_symlink(): item.unlink(); n += 1
            elif item.is_dir(): shutil.rmtree(item, ignore_errors=True); n += 1
        except: pass
    return n

def clean_temp():
    _sec("🧹 Fichiers temporaires")
    paths = [
        (Path(tempfile.gettempdir()),                              "Temp utilisateur"),
        (Path(os.environ.get("WINDIR","C:\\Windows")) / "Temp",   "Temp Windows"),
        (Path(os.environ.get("LOCALAPPDATA","")) / "Temp",        "Temp LocalAppData"),
    ]
    total = 0
    with Progress(SpinnerColumn(), TextColumn("{task.description}"), BarColumn(),
                  TextColumn("{task.completed} éléments"), console=console) as pg:
        t = pg.add_task("Nettoyage...", total=len(paths))
        for p, label in paths:
            n = _del_folder(p)
            total += n
            pg.advance(t)
            _info(f"{label}: {n} éléments supprimés")
    _ok(f"Total: {total} éléments supprimés")

def clean_update_cache():
    _sec("🔄 Cache Windows Update")
    if not Confirm.ask("  Vider le cache Windows Update ?", default=True): return
    with Progress(SpinnerColumn(), TextColumn("{task.description}"), console=console) as pg:
        t = pg.add_task("Arrêt des services...")
        run(["net", "stop", "wuauserv"]); run(["net", "stop", "bits"])
        pg.update(t, description="Suppression du cache...")
        cache = Path(os.environ.get("WINDIR","C:\\Windows")) / "SoftwareDistribution" / "Download"
        n = _del_folder(cache)
        pg.update(t, description="Redémarrage des services...")
        run(["net", "start", "wuauserv"]); run(["net", "start", "bits"])
        pg.update(t, description="Terminé ✓", completed=1, total=1)
    _ok(f"Cache Windows Update nettoyé ({n} éléments)")

def clean_prefetch():
    _sec("⚡ Prefetch")
    if not Confirm.ask("  Nettoyer le Prefetch ? (non recommandé sur SSD)", default=False): return
    p = Path(os.environ.get("WINDIR","C:\\Windows")) / "Prefetch"
    _ok(f"Prefetch nettoyé ({_del_folder(p)} éléments)")

def clean_thumbnails():
    _sec("🖼  Cache miniatures")
    p = Path(os.environ.get("LOCALAPPDATA","")) / "Microsoft" / "Windows" / "Explorer"
    n = 0
    if p.exists():
        for f in p.glob("thumbcache_*.db"):
            try: f.unlink(); n += 1
            except: pass
    _ok(f"Miniatures supprimées ({n} fichiers)")

def clean_dns():
    _sec("🌐 Cache DNS")
    c, _ = run(["ipconfig", "/flushdns"])
    _ok("Cache DNS vidé") if c == 0 else _err("Erreur flush DNS")

def clean_event_logs():
    _sec("📋 Journaux d'événements")
    if not Confirm.ask("  Vider les journaux ? (Application, System)", default=True): return
    for lg in ["Application", "System", "Setup"]:
        c, _ = run(["wevtutil", "cl", lg])
        _ok(f"Journal '{lg}' vidé") if c == 0 else _warn(f"Journal '{lg}' — accès refusé")

def clean_recycle():
    _sec("🗑  Corbeille")
    try:
        ctypes.windll.shell32.SHEmptyRecycleBinW(None, None, 0x0007)
        _ok("Corbeille vidée")
    except Exception as e:
        _err(f"Erreur: {e}")

def clean_all():
    clean_temp(); clean_update_cache(); clean_prefetch()
    clean_thumbnails(); clean_dns(); clean_recycle()

# ═════════════════════════════════════════════════════════════════════════════
# 2. PERFORMANCE
# ═════════════════════════════════════════════════════════════════════════════
def perf_ultimate_power():
    _sec("⚡ Plan d'alimentation Ultimate Performance")
    # Duplicate the scheme (unlocks it on Home editions)
    run(["powercfg", "-duplicatescheme", "e9a42b02-d5df-448d-aa00-03f14749eb61"])
    # Find the GUID in the list
    _, out = run(["powercfg", "-list"])
    guid = None
    for line in out.splitlines():
        if "e9a42b02" in line.lower() or "ultimate" in line.lower():
            for p in line.split():
                if len(p) == 36 and p.count("-") == 4:
                    guid = p; break
    if guid:
        c, _ = run(["powercfg", "-setactive", guid])
        _ok(f"Plan Ultimate Performance activé") if c == 0 else _err("Activation échouée")
    else:
        c, _ = run(["powercfg", "-setactive", "8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c"])
        _ok("Plan Haute Performance activé (Ultimate non disponible sur cette édition)") if c == 0 else _err("Erreur")

def perf_visual_effects():
    _sec("🎨 Effets visuels — Mode Performance")
    HKCU = winreg.HKEY_CURRENT_USER
    tweaks = [
        (HKCU, r"Software\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects", "VisualFXSetting", 2),
        (HKCU, r"Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced",      "ListviewAlphaSelect", 0),
        (HKCU, r"Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced",      "ListviewShadow", 0),
        (HKCU, r"Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced",      "TaskbarAnimations", 0),
        (HKCU, r"Control Panel\Desktop\WindowMetrics",                              "MinAnimate", "0", winreg.REG_SZ),
        (HKCU, r"Software\Microsoft\Windows\DWM",                                  "EnableAeroPeek", 0),
    ]
    for args in tweaks:
        reg_set(*args) if len(args) == 4 else reg_set(args[0], args[1], args[2], args[3], args[4])
    _ok("Effets visuels optimisés")
    _warn("Reconnectez-vous ou redémarrez pour voir les changements")

def perf_cpu_priority():
    _sec("🔧 Priorité CPU (foreground priority)")
    reg_set(winreg.HKEY_LOCAL_MACHINE,
            r"SYSTEM\CurrentControlSet\Control\PriorityControl",
            "Win32PrioritySeparation", 0x26)
    _ok("Priorité foreground maximisée (0x26)")

def perf_ssd():
    _sec("💾 Optimisation SSD")
    c, out = run(["fsutil", "behavior", "query", "DisableDeleteNotify"])
    if "DisableDeleteNotify = 0" in out:
        _ok("TRIM actif ✓")
    else:
        c, _ = run(["fsutil", "behavior", "set", "DisableDeleteNotify", "0"])
        _ok("TRIM activé") if c == 0 else _err("Erreur TRIM")
    # Disable last access timestamp
    c, _ = run(["fsutil", "behavior", "set", "disablelastaccess", "1"])
    if c == 0: _ok("Horodatage dernier accès désactivé")

def perf_hibernation():
    _sec("💤 Hibernation")
    mem_gb = psutil.virtual_memory().total / 1024**3
    if Confirm.ask(f"  Désactiver l'hibernation (libère ~{mem_gb:.0f} Go) ?", default=True):
        c, _ = run(["powercfg", "-h", "off"])
        _ok("Hibernation désactivée") if c == 0 else _err("Erreur")

def perf_vram_schedule():
    _sec("🖥  Planificateur GPU (HAGS)")
    reg_set(winreg.HKEY_LOCAL_MACHINE,
            r"SYSTEM\CurrentControlSet\Control\GraphicsDrivers",
            "HwSchMode", 2)
    _ok("Hardware-Accelerated GPU Scheduling activé (redémarrage requis)")

# ═════════════════════════════════════════════════════════════════════════════
# 3. GAMING
# ═════════════════════════════════════════════════════════════════════════════
def gaming_tweaks():
    _sec("🎮 Optimisations Gaming")
    HKCU = winreg.HKEY_CURRENT_USER
    HKLM = winreg.HKEY_LOCAL_MACHINE

    steps = [
        ("Game Mode",          HKCU, r"Software\Microsoft\GameBar",                          "AllowAutoGameMode",  1),
        ("",                   HKCU, r"Software\Microsoft\GameBar",                          "AutoGameModeEnabled",1),
        ("Game DVR off",       HKCU, r"Software\Microsoft\Windows\CurrentVersion\GameDVR",   "AppCaptureEnabled",  0),
        ("",                   HKCU, r"System\GameConfigStore",                               "GameDVR_Enabled",    0),
        ("",                   HKLM, r"SOFTWARE\Policies\Microsoft\Windows\GameDVR",          "AllowGameDVR",       0),
        ("FSE Compat",         HKCU, r"System\GameConfigStore",                               "GameDVR_FSEBehaviorMode",             2),
        ("",                   HKCU, r"System\GameConfigStore",                               "GameDVR_HonorUserFSEBehaviorMode",    1),
        ("",                   HKCU, r"System\GameConfigStore",                               "GameDVR_DXGIHonorFSEWindowsCompatible",1),
        ("Net throttle off",   HKLM, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile", "NetworkThrottlingIndex", 0xffffffff),
        ("System responsiv=0", HKLM, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile", "SystemResponsiveness",  0),
        ("GPU Prio=8 (games)", HKLM, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games", "GPU Priority", 8),
        ("CPU Prio=6 (games)", HKLM, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games", "Priority",     6),
        ("HAGS",               HKLM, r"SYSTEM\CurrentControlSet\Control\GraphicsDrivers",    "HwSchMode",          2),
        ("Xbox services",      HKCU, r"Software\Microsoft\Windows\CurrentVersion\GameDVR",   "AppCaptureEnabled",  0),
    ]

    with Progress(SpinnerColumn(), TextColumn("{task.description}"), BarColumn(),
                  TextColumn("{task.completed}/{task.total}"), console=console) as pg:
        task = pg.add_task("Application des tweaks gaming...", total=len(steps))
        for label, hive, path, name, val in steps:
            reg_set(hive, path, name, val)
            if label: _info(label)
            pg.advance(task)

    # Scheduling category for games (REG_SZ)
    reg_set(HKLM, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games",
            "Scheduling Category", "High", winreg.REG_SZ)

    _ok("Tweaks gaming appliqués")
    _warn("Redémarrage requis pour HAGS + Game DVR")

def gaming_timer():
    _sec("⏱  Résolution du Timer (0.5ms)")
    try:
        ntdll  = ctypes.WinDLL("ntdll", use_last_error=True)
        actual = ctypes.c_ulong(0)
        # 5000 = 0.5ms (100-ns units)
        r = ntdll.NtSetTimerResolution(5000, True, ctypes.byref(actual))
        if r == 0:
            _ok(f"Timer résolution: {actual.value / 10000:.2f} ms")
        else:
            ntdll.NtSetTimerResolution(10000, True, ctypes.byref(actual))
            _ok(f"Timer résolution: {actual.value / 10000:.2f} ms")
        _warn("Temporaire — se réinitialise au redémarrage")
    except Exception as e:
        _err(f"Erreur timer: {e}")

# ═════════════════════════════════════════════════════════════════════════════
# 4. RÉSEAU
# ═════════════════════════════════════════════════════════════════════════════
def net_optimize():
    _sec("🌐 Optimisation réseau")
    HKLM = winreg.HKEY_LOCAL_MACHINE

    reg_set(HKLM, r"SYSTEM\CurrentControlSet\Services\Tcpip\Parameters", "TcpTimedWaitDelay", 30)
    reg_set(HKLM, r"SYSTEM\CurrentControlSet\Services\Tcpip\Parameters", "MaxUserPort",        65534)
    reg_set(HKLM, r"SYSTEM\CurrentControlSet\Services\Tcpip\Parameters", "TcpNumConnections",  0xfffffe)
    _ok("Paramètres TCP/IP optimisés")

    run(["netsh", "int", "tcp", "set", "global", "autotuninglevel=normal"])
    run(["netsh", "int", "tcp", "set", "global", "chimney=disabled"])
    run(["netsh", "int", "tcp", "set", "global", "rss=enabled"])
    _ok("TCP auto-tuning + RSS activés")

    # DNS choice
    choice = Prompt.ask(
        "\n  Choisir un DNS rapide",
        choices=["cloudflare", "google", "passer"], default="cloudflare"
    )
    if choice != "passer":
        dns = {"cloudflare": ("1.1.1.1", "1.0.0.1"), "google": ("8.8.8.8", "8.8.4.4")}
        p1, p2 = dns[choice]
        _, out = run(["netsh", "interface", "show", "interface"])
        set_count = 0
        for line in out.splitlines():
            if "Connected" not in line: continue
            parts = line.split(None, 3)
            if len(parts) < 4: continue
            iface = parts[3].strip()
            c1, _ = run(["netsh", "interface", "ipv4", "set", "dns",
                          f"name={iface}", "static", p1, "primary", "validate=no"])
            c2, _ = run(["netsh", "interface", "ipv4", "add", "dns",
                          f"name={iface}", p2, "index=2", "validate=no"])
            if c1 == 0: set_count += 1
        if set_count:
            _ok(f"DNS {choice.capitalize()} configuré ({p1} / {p2}) sur {set_count} interface(s)")
        else:
            _warn("Aucune interface connectée trouvée — DNS non modifié")

    run(["ipconfig", "/flushdns"])
    _ok("Cache DNS vidé")

# ═════════════════════════════════════════════════════════════════════════════
# 5. CONFIDENTIALITÉ
# ═════════════════════════════════════════════════════════════════════════════
def privacy_tweaks():
    _sec("🔒 Confidentialité & Télémétrie")
    HKCU = winreg.HKEY_CURRENT_USER
    HKLM = winreg.HKEY_LOCAL_MACHINE

    tweaks = [
        (HKLM, r"SOFTWARE\Policies\Microsoft\Windows\DataCollection",           "AllowTelemetry",                     0,  "Télémétrie = 0"),
        (HKLM, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\DataCollection","AllowTelemetry",                 0,  ""),
        (HKLM, r"SOFTWARE\Policies\Microsoft\Windows\Windows Search",            "AllowCortana",                       0,  "Cortana désactivée"),
        (HKLM, r"SOFTWARE\Policies\Microsoft\Windows\Windows Search",            "ConnectedSearchUseWeb",              0,  ""),
        (HKCU, r"SOFTWARE\Microsoft\Windows\CurrentVersion\AdvertisingInfo",     "Enabled",                            0,  "Publicité personnalisée off"),
        (HKLM, r"SOFTWARE\Policies\Microsoft\Windows\System",                    "EnableActivityFeed",                 0,  "Historique activités off"),
        (HKLM, r"SOFTWARE\Policies\Microsoft\Windows\System",                    "PublishUserActivities",              0,  ""),
        (HKLM, r"SOFTWARE\Policies\Microsoft\Windows\TabletPC",                  "PreventHandwritingDataSharing",      1,  "Partage écriture off"),
        (HKLM, r"SOFTWARE\Policies\Microsoft\Windows\CloudContent",              "DisableSoftLanding",                 1,  "Conseils Windows off"),
        (HKLM, r"SOFTWARE\Policies\Microsoft\Windows\CloudContent",              "DisableWindowsConsumerFeatures",     1,  ""),
        (HKLM, r"SOFTWARE\Policies\Microsoft\Windows\LocationAndSensors",        "DisableLocation",                    1,  "Localisation off"),
        (HKLM, r"SOFTWARE\Policies\Microsoft\Windows\Windows Error Reporting",   "Disabled",                           1,  "Rapport d'erreurs off"),
        (HKCU, r"SOFTWARE\Microsoft\Windows\CurrentVersion\ContentDeliveryManager","SilentInstalledAppsEnabled",       0,  "Apps silencieuses off"),
        (HKCU, r"SOFTWARE\Microsoft\Windows\CurrentVersion\ContentDeliveryManager","SystemPaneSuggestionsEnabled",     0,  ""),
        (HKCU, r"SOFTWARE\Microsoft\InputPersonalization",                        "RestrictImplicitInkCollection",      1,  "Collecte encre off"),
        (HKCU, r"SOFTWARE\Microsoft\InputPersonalization",                        "RestrictImplicitTextCollection",     1,  ""),
    ]

    with Progress(SpinnerColumn(), TextColumn("{task.description}"), BarColumn(),
                  TextColumn("{task.completed}/{task.total}"), console=console) as pg:
        t = pg.add_task("Application...", total=len(tweaks))
        for args in tweaks:
            hive, path, name, val, msg = args
            reg_set(hive, path, name, val)
            if msg: _info(msg)
            pg.advance(t)

    svc("DiagTrack", "disabled");    svc_stop("DiagTrack")
    svc("dmwappushservice", "disabled")
    _ok("Confidentialité renforcée — DiagTrack désactivé")

# ═════════════════════════════════════════════════════════════════════════════
# 6. SERVICES
# ═════════════════════════════════════════════════════════════════════════════
def optimize_services(profile: str = "gaming"):
    _sec(f"🔧 Services — Profil {profile.capitalize()}")
    base = [
        ("Fax",            "disabled",  "Fax"),
        ("XblGameSave",    "demand",    "Xbox Game Save"),
        ("XboxNetApiSvc",  "demand",    "Xbox Network API"),
        ("XboxGipSvc",     "demand",    "Xbox Input"),
        ("WMPNetworkSvc",  "demand",    "Windows Media Player Network"),
        ("RemoteRegistry", "disabled",  "Registre distant"),
        ("MapsBroker",     "disabled",  "Gestionnaire Maps"),
        ("RetailDemo",     "disabled",  "Mode Démo"),
    ]
    gaming_extra = [
        ("DiagTrack",      "disabled",  "Télémétrie DiagTrack"),
        ("WSearch",        "demand",    "Windows Search (demand)"),
        ("SysMain",        "demand",    "SysMain/SuperFetch"),
        ("Spooler",        "demand",    "Spouleur d'impression"),
        ("SSDPSRV",        "disabled",  "Découverte SSDP"),
        ("upnphost",       "disabled",  "UPnP"),
        ("WerSvc",         "demand",    "Rapport d'erreurs"),
        ("wlidsvc",        "demand",    "Microsoft Account"),
        ("TabletInputService","demand", "Tablette/Stylet"),
    ]
    services = base + (gaming_extra if profile == "gaming" else [])
    with Progress(SpinnerColumn(), TextColumn("{task.description}"), BarColumn(),
                  TextColumn("{task.completed}/{task.total}"), console=console) as pg:
        t = pg.add_task("Configuration services...", total=len(services))
        for name, start, desc in services:
            ok_svc = svc(name, start)
            status = "✓" if ok_svc else "⚠"
            _info(f"{status} {desc}: {start}")
            pg.advance(t)
    _ok(f"Services optimisés (profil {profile})")

# ═════════════════════════════════════════════════════════════════════════════
# 7. DÉMARRAGE
# ═════════════════════════════════════════════════════════════════════════════
def manage_startup():
    _sec("🚀 Gestionnaire de démarrage")
    hives = [
        (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run",   "HKCU"),
        (winreg.HKEY_LOCAL_MACHINE,r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run",   "HKLM"),
    ]
    entries = []
    for hive, path, hname in hives:
        try:
            k = winreg.OpenKey(hive, path, 0, winreg.KEY_READ | winreg.KEY_WOW64_64KEY)
            i = 0
            while True:
                try:
                    name, val, _ = winreg.EnumValue(k, i)
                    entries.append((hive, path, hname, name, val)); i += 1
                except OSError: break
            winreg.CloseKey(k)
        except: pass

    if not entries:
        _info("Aucun programme de démarrage trouvé"); return

    t = Table(title="Programmes au démarrage", border_style="cyan")
    t.add_column("#",       style="dim",      width=4)
    t.add_column("Reg",     style="cyan",     width=5)
    t.add_column("Nom",     style="bold white")
    t.add_column("Chemin",  style="dim",      max_width=55, no_wrap=True)
    for i, (_, _, hname, name, val) in enumerate(entries, 1):
        v = (val[:52] + "...") if len(val) > 55 else val
        t.add_row(str(i), hname, name, v)
    console.print(t)

    while True:
        c = Prompt.ask("\n  Numéro à désactiver (0 = terminer)", default="0")
        if c == "0": break
        try:
            idx = int(c) - 1
            if 0 <= idx < len(entries):
                hive, path, _, name, _ = entries[idx]
                if Confirm.ask(f"  Supprimer '{name}' du démarrage ?", default=False):
                    if reg_del(hive, path, name):
                        _ok(f"'{name}' retiré du démarrage")
                        entries.pop(idx)
                        # Reprint
                        manage_startup(); return
                    else:
                        _err(f"Impossible de supprimer '{name}'")
        except ValueError:
            _warn("Entrée invalide")

# ═════════════════════════════════════════════════════════════════════════════
# 8. RAM
# ═════════════════════════════════════════════════════════════════════════════
def clean_ram():
    _sec("🧠 Nettoyage mémoire RAM")
    before = psutil.virtual_memory()
    _info(f"Avant: {fmt_bytes(before.available)} libre ({before.percent:.0f}% utilisé)")

    with Progress(SpinnerColumn(), TextColumn("{task.description}"), console=console) as pg:
        t = pg.add_task("Vidage working sets...", total=None)
        try:
            k32 = ctypes.WinDLL("kernel32", use_last_error=True)
            for proc in psutil.process_iter(["pid"]):
                try:
                    h = k32.OpenProcess(0x1F0FFF, False, proc.info["pid"])
                    if h:
                        k32.SetProcessWorkingSetSize(h, ctypes.c_size_t(-1), ctypes.c_size_t(-1))
                        k32.CloseHandle(h)
                except: pass
        except: pass

        pg.update(t, description="Purge standby list...")
        try:
            ntdll = ctypes.WinDLL("ntdll", use_last_error=True)
            cmd   = ctypes.c_uint(4)  # MemoryPurgeStandbyList
            ntdll.NtSetSystemInformation(80, ctypes.byref(cmd), ctypes.sizeof(cmd))
        except: pass

        pg.update(t, description="Terminé ✓")

    time.sleep(1)
    after = psutil.virtual_memory()
    freed = after.available - before.available
    _ok(f"RAM libérée: {fmt_bytes(max(freed,0))}  ({after.percent:.0f}% utilisé)")

# ═════════════════════════════════════════════════════════════════════════════
# 9. GPU
# ═════════════════════════════════════════════════════════════════════════════
def optimize_gpu():
    _sec("🖥  Optimisation GPU")
    _, out = run(["wmic", "path", "win32_VideoController", "get", "name"])
    gpus = [l.strip() for l in out.splitlines() if l.strip() and "Name" not in l]
    if gpus:
        for g in gpus:
            if g: _info(f"GPU: {g}")
    else:
        _warn("GPU non détecté via WMI")

    is_nvidia = any("nvidia" in (g or "").lower() for g in gpus)
    is_amd    = any(("amd" in (g or "").lower() or "radeon" in (g or "").lower()) for g in gpus)

    # HAGS
    reg_set(winreg.HKEY_LOCAL_MACHINE,
            r"SYSTEM\CurrentControlSet\Control\GraphicsDrivers", "HwSchMode", 2)
    _ok("HAGS activé")

    # DWM overlay mode
    reg_set(winreg.HKEY_LOCAL_MACHINE,
            r"SOFTWARE\Microsoft\Windows\Dwm", "OverlayTestMode", 5)
    _ok("DWM overlay optimisé")

    if is_nvidia:
        _info("NVIDIA détecté — application des tweaks driver...")
        # PowerMizer to max performance (sub-key 0000, adjust if needed)
        for sk in ["0000", "0001"]:
            base = fr"SYSTEM\CurrentControlSet\Control\Class\{{4d36e968-e325-11ce-bfc1-08002be10318}}\{sk}"
            reg_set(winreg.HKEY_LOCAL_MACHINE, base, "PowerMizerEnable", 1)
            reg_set(winreg.HKEY_LOCAL_MACHINE, base, "PowerMizerLevel",  1)
            reg_set(winreg.HKEY_LOCAL_MACHINE, base, "PerfLevelSrc",     0x2222)
        _ok("NVIDIA: mode performance maximum")

    if is_amd:
        _info("AMD/Radeon — tweaks disponibles dans Radeon Software → Performance")

    _warn("Redémarrage requis pour HAGS")

# ═════════════════════════════════════════════════════════════════════════════
# 10. RESTAURATION
# ═════════════════════════════════════════════════════════════════════════════
def create_restore_point():
    _sec("🛡  Point de restauration système")
    _info("Création d'un point de restauration avant optimisation...")
    run(["powershell", "-Command", 'Enable-ComputerRestore -Drive "C:\\"'])
    c, _ = run(["powershell", "-Command",
                f'Checkpoint-Computer -Description "OptimPC v{VERSION}" -RestorePointType MODIFY_SETTINGS'])
    _ok("Point de restauration créé") if c == 0 else _warn("Impossible (non critique — continuez)")

# ═════════════════════════════════════════════════════════════════════════════
# PROFILS
# ═════════════════════════════════════════════════════════════════════════════
def profile_bureautique():
    console.print(Panel("[bold blue]PROFIL BUREAUTIQUE[/] — Optimisation douce, sans casse",
                        border_style="blue"))
    create_restore_point()
    clean_temp(); clean_thumbnails(); clean_dns()
    perf_ultimate_power(); perf_cpu_priority(); perf_ssd()
    optimize_services("bureautique")
    console.print()
    console.print(Panel("[bold green]✓  Profil Bureautique appliqué ![/]", border_style="green"))

def profile_gaming():
    console.print(Panel("[bold red]PROFIL GAMING[/] — Optimisation complète pour les jeux",
                        border_style="red"))
    create_restore_point()
    clean_temp(); clean_thumbnails(); clean_dns(); clean_recycle()
    perf_ultimate_power(); perf_cpu_priority(); perf_visual_effects(); perf_ssd()
    gaming_tweaks(); gaming_timer()
    optimize_services("gaming"); optimize_gpu()
    console.print()
    console.print(Panel("[bold green]✓  Profil Gaming appliqué ! Redémarrez votre PC.[/]", border_style="green"))

def profile_all():
    console.print(Panel("[bold bright_red]⚡  OPTIMISATION COMPLÈTE[/] — Tout en une passe",
                        border_style="bright_red"))
    create_restore_point()
    clean_all()
    perf_ultimate_power(); perf_cpu_priority(); perf_visual_effects(); perf_ssd()
    gaming_tweaks(); gaming_timer()
    net_optimize(); optimize_services("gaming")
    privacy_tweaks(); optimize_gpu(); clean_ram()
    console.print()
    console.print(Panel("[bold green]✓  Optimisation complète terminée ! Redémarrez votre PC.[/]",
                        border_style="green"))

# ═════════════════════════════════════════════════════════════════════════════
# MENUS
# ═════════════════════════════════════════════════════════════════════════════
def _menu_table(items: list[tuple[str, str]], num_style: str = "bold cyan") -> Table:
    t = Table(box=None, padding=(0, 2), show_header=False)
    t.add_column("N", style=num_style, width=4)
    t.add_column("Option", style="white")
    for key, label in items:
        t.add_row(key, label)
    return t

def _run_sub(title: str, items: list[tuple[str, str, callable]], num_style: str = "bold cyan"):
    dispatch = {k: fn for k, _, fn in items}
    menu_items = [(k, lbl) for k, lbl, _ in items] + [("0", "[dim_w]Retour[/]")]
    while True:
        console.clear(); header()
        console.print(Panel(_menu_table(menu_items, num_style), title=f"[bold]{title}[/]",
                            border_style="cyan"))
        c = Prompt.ask("\n  [bold cyan]Choix[/]", default="0").strip()
        if c == "0": break
        if c in dispatch: dispatch[c](); _pause()

def menu_nettoyage():
    _run_sub("🧹 Nettoyage", [
        ("1", "Fichiers temporaires",        clean_temp),
        ("2", "Cache Windows Update",        clean_update_cache),
        ("3", "Prefetch",                    clean_prefetch),
        ("4", "Cache miniatures",            clean_thumbnails),
        ("5", "Cache DNS",                   clean_dns),
        ("6", "Journaux d'événements",       clean_event_logs),
        ("7", "Corbeille",                   clean_recycle),
        ("8", "[bold]TOUT nettoyer[/]",      clean_all),
    ], "bold green")

def menu_performance():
    _run_sub("⚡ Performance", [
        ("1", "Plan Ultimate Performance",   perf_ultimate_power),
        ("2", "Effets visuels — Performance",perf_visual_effects),
        ("3", "Priorité CPU (foreground)",   perf_cpu_priority),
        ("4", "Optimisation SSD",            perf_ssd),
        ("5", "Désactiver hibernation",      perf_hibernation),
        ("6", "HAGS (GPU Scheduling)",       perf_vram_schedule),
    ], "bold yellow")

def menu_gaming():
    _run_sub("🎮 Gaming", [
        ("1", "Tweaks gaming complets",      gaming_tweaks),
        ("2", "Résolution timer (0.5ms)",    gaming_timer),
        ("3", "Optimisation GPU",            optimize_gpu),
    ], "bold red")

def main_menu():
    elevate()

    while True:
        console.clear(); header(); show_sysinfo()

        left = _menu_table([
            ("1",  "🧹  Nettoyage"),
            ("2",  "⚡  Performance"),
            ("3",  "🎮  Gaming"),
            ("4",  "🌐  Réseau"),
            ("5",  "🔒  Confidentialité"),
            ("6",  "🚀  Démarrage"),
            ("7",  "🔧  Services"),
            ("8",  "🧠  Nettoyage RAM"),
            ("9",  "🖥   GPU"),
        ], "bold cyan")

        right = _menu_table([
            ("P1", "[blue]Profil Bureautique[/]"),
            ("P2", "[red]Profil Gaming[/]"),
            ("P3", "[bold bright_red]⚡ TOUT OPTIMISER[/]"),
            ("",   ""),
            ("R",  "🛡   Point de restauration"),
            ("L",  "📋  Voir le fichier de log"),
            ("0",  "[dim_w]Quitter[/]"),
        ], "bold green")

        console.print(Columns([
            Panel(left,  title="[bold]Menu Principal[/]",  border_style="cyan"),
            Panel(right, title="[bold]Profils & Outils[/]", border_style="green"),
        ]))

        c = Prompt.ask("\n  [bold cyan]Votre choix[/]").strip().upper()

        handlers = {
            "1":  menu_nettoyage,
            "2":  menu_performance,
            "3":  menu_gaming,
            "4":  lambda: (net_optimize(),             _pause()),
            "5":  lambda: (privacy_tweaks(),           _pause()),
            "6":  lambda: (manage_startup(),           _pause()),
            "7":  lambda: (optimize_services(
                              Prompt.ask("  Profil", choices=["bureautique","gaming"],
                                         default="gaming")), _pause()),
            "8":  lambda: (clean_ram(),                _pause()),
            "9":  lambda: (optimize_gpu(),             _pause()),
            "P1": lambda: (profile_bureautique(),      _pause()),
            "P2": lambda: (profile_gaming(),           _pause()),
            "P3": lambda: (profile_all(),              _pause()),
            "R":  lambda: (create_restore_point(),     _pause()),
            "L":  lambda: (console.print(f"\n  [dim]Log: {LOG_FILE}[/]\n"), _pause()),
        }

        if c == "0":
            console.print("\n  [dim_w]Au revoir ![/]\n")
            break
        elif c in handlers:
            handlers[c]()
        else:
            _warn("Choix invalide")
            time.sleep(0.8)


if __name__ == "__main__":
    main_menu()
