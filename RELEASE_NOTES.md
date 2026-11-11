# ⚡ OptimPC v2.0.0 — Refonte Complète

> **Téléchargez `OptimPC-v2.0.exe` ci-dessous — aucune installation requise.**

---

## 🆕 Ce qui change dans la v2.0

La v1.0 était un script PowerShell basique. La v2.0 est une **refonte totale** en Python avec une interface TUI moderne et 3× plus d'optimisations.

---

## ✨ Nouveautés majeures

### Interface
- 🎨 TUI entièrement refaite avec **rich** : art ASCII, panneaux colorés, barres de progression
- 📊 **Informations système** affichées au démarrage (CPU, RAM, disques)
- 📋 Logs automatiques dans `%APPDATA%\OptimPC\logs\`
- 🛡️ **Point de restauration système** créé avant chaque profil

### Nouvelles optimisations
| Catégorie | Description |
|-----------|-------------|
| 🌐 **Réseau** | Tweaks TCP/IP, DNS Cloudflare/Google, auto-tuning RSS |
| 🎮 **Gaming** | HAGS, timer 0.5ms, Game DVR off, priorité SystemProfile |
| 🔒 **Confidentialité** | 16 tweaks télémétrie/Cortana/pub/localisation |
| 🧠 **RAM** | Purge standby list + vidage working sets |
| 🖥️ **GPU** | Détection NVIDIA/AMD, PowerMizer max, DWM overlay |
| 🔧 **Services** | Profil bureautique (8 services) + gaming (17 services) |
| 🧹 **Nettoyage** | + miniatures, journaux d'événements, corbeille |

---

## 📦 Installation

1. Téléchargez **`OptimPC-v2.0.exe`** (29 Mo, autonome)
2. Double-cliquez → acceptez l'UAC
3. Choisissez un profil ou explorez les menus

**Aucun Python requis** — tout est embarqué dans le `.exe`.

---

## 🎯 Profils disponibles

- **P1 Bureautique** — Nettoyage + performance douce
- **P2 Gaming** — Toutes les optimisations gaming
- **P3 TOUT OPTIMISER** — Passe complète en une fois

---

## ⚠️ Notes

- Windows 10 / 11 requis
- Droits administrateur requis (demandés automatiquement)
- Certains changements (HAGS, effets visuels) nécessitent un redémarrage
- Un point de restauration est créé automatiquement

---

## 📄 Licence

MIT — Gratuit, libre, open source.
