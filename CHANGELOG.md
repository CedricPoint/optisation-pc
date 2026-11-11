# Changelog

## [2.0.0] — 2026-11-11

### Refonte complète

#### Ajouts majeurs
- **Interface TUI** entièrement réécrite avec `rich` : art ASCII, panneaux, barres de progression, tableaux colorés
- **Informations système** affichées au démarrage (CPU, RAM, disques, OS)
- **Journalisation** automatique dans `%APPDATA%\OptimPC\logs\`
- **Point de restauration** système créé automatiquement avant chaque profil

#### Nouvelles optimisations
- 🌐 **Réseau** : tweaks TCP/IP, DNS Cloudflare/Google, auto-tuning
- 🎮 **Gaming** : HAGS, timer 0.5ms, Game DVR off, priorité SystemProfile
- 🔒 **Confidentialité** : 16 tweaks (télémétrie, Cortana, publicités, localisation...)
- 🧠 **RAM** : purge standby list + vidage working sets via API Windows
- 🖥️ **GPU** : détection NVIDIA/AMD, PowerMizer, DWM overlay
- ⚡ **Services** : profils Bureautique (8 services) et Gaming (17 services)
- 🧹 **Nettoyage** : + miniatures, journaux d'événements, corbeille

#### Build
- `.exe` standalone via PyInstaller `--uac-admin --onefile`
- Métadonnées de version embarquées dans l'exécutable

---

## [1.0.0] — 2024

- Script PowerShell initial
- Profils Bureautique / Gaming
- Nettoyage temp, prefetch, Update cache
- Plan Haute Performance
- Télémétrie basique
- Gestionnaire de démarrage (registre)
