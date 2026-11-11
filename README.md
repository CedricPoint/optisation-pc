# ⚡ OptimPC v2.0 — Windows Optimizer

> Optimiseur Windows 10/11 — **100 % Gratuit & Open Source**

![GitHub release](https://img.shields.io/github/v/release/CedricPoint/optisation-pc?color=brightgreen&label=version)
![GitHub stars](https://img.shields.io/github/stars/CedricPoint/optisation-pc?style=flat&color=yellow)
![License](https://img.shields.io/badge/licence-MIT-blue)
![Windows](https://img.shields.io/badge/Windows-10%2F11-0078D6?logo=windows)
![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python)

---

## 📸 Aperçu

```
  ██████╗ ██████╗ ████████╗██╗███╗   ███╗    ██████╗  ██████╗
  ██╔══██╗██╔══██╗╚══██╔══╝██║████╗ ████║    ██╔══██╗██╔════╝
  ██║  ██║██████╔╝   ██║   ██║██╔████╔██║    ██████╔╝██║
  ██║  ██║██╔═══╝    ██║   ██║██║╚██╔╝██║    ██╔═══╝ ██║
  ██████╔╝██║        ██║   ██║██║ ╚═╝ ██║    ██║     ╚██████╗
  ╚═════╝ ╚═╝        ╚═╝   ╚═╝╚═╝     ╚═╝    ╚═╝      ╚═════╝
         v2.0 — Windows Optimizer — by CedricPoint
```

---

## ✨ Fonctionnalités

### 🧹 Nettoyage complet
- Fichiers temporaires (Temp utilisateur, Windows, LocalAppData)
- Cache Windows Update (arrêt/redémarrage des services automatique)
- Prefetch & miniatures
- Cache DNS, journaux d'événements, corbeille

### ⚡ Performance
- Plan **Ultimate Performance** (déverrouillé + activé, même sur Windows Home)
- Effets visuels en mode performance
- Priorité CPU foreground maximisée
- Optimisation SSD (TRIM, dernier accès)
- Désactivation de l'hibernation

### 🎮 Gaming
- **Game Mode** Windows activé
- **Hardware-Accelerated GPU Scheduling (HAGS)**
- Désactivation Game DVR, Xbox Game Bar
- Priorité GPU/CPU pour les jeux (SystemProfile Tasks)
- Désactivation du réseau throttling
- **Résolution du timer à 0.5 ms**
- Compatibilité plein écran exclusif

### 🌐 Réseau
- Tweaks TCP/IP (MaxUserPort, TcpNumConnections, TcpTimedWaitDelay)
- TCP auto-tuning + RSS activés
- DNS rapide au choix : **Cloudflare (1.1.1.1)** ou **Google (8.8.8.8)**
- Flush DNS automatique

### 🔒 Confidentialité
- Télémétrie Windows à 0
- Cortana désactivée
- Publicité personnalisée off
- Historique d'activités off
- Localisation off
- Rapport d'erreurs off
- Service DiagTrack désactivé

### 🔧 Services
- **Profil Bureautique** : désactive Fax, Xbox*, registre distant, démo
- **Profil Gaming** : + DiagTrack, SysMain demand, spouleur demand, SSDP off, UPnP off

### 🧠 Mémoire RAM
- Vidage des working sets de tous les processus
- Purge de la standby list (NtSetSystemInformation)

### 🖥️ GPU
- Détection NVIDIA / AMD automatique
- NVIDIA : PowerMizer en mode performance max
- HAGS activé pour tous les GPU

### 🚀 Démarrage
- Liste complète des programmes (HKCU + HKLM)
- Suppression interactive avec confirmation

---

## 📦 Téléchargement

> **[⬇️ Télécharger OptimPC-v2.0.exe](https://github.com/CedricPoint/optisation-pc/releases/latest)**

Double-cliquez sur `OptimPC-v2.0.exe` → acceptez l'UAC → c'est parti.

---

## 🛠️ Utilisation depuis les sources

### Prérequis
- Windows 10 / 11
- Python 3.10+
- Droits administrateur

### Lancement direct (Python)
```bash
pip install rich psutil
python optimizer.py
```

### Compilation .exe
```bash
build.bat
```
L'exécutable `OptimPC-v2.0.exe` sera créé à la racine du projet.

---

## 🎯 Profils tout-en-un

| Profil | Description |
|--------|-------------|
| **P1 — Bureautique** | Nettoyage + performance douce, sans toucher au gaming |
| **P2 — Gaming** | Toutes les optimisations gaming + réseau + services |
| **P3 — TOUT OPTIMISER** | Passe complète : nettoyage, performance, gaming, réseau, confidentialité, GPU, RAM |

---

## ⚠️ Précautions

- Un **point de restauration système** est créé automatiquement avant chaque profil
- Les logs sont sauvegardés dans `%APPDATA%\OptimPC\logs\`
- Certains changements (HAGS, effets visuels) nécessitent un **redémarrage**
- La suppression de programmes au démarrage est **irréversible** depuis ce script

---

## 🗂️ Structure du projet

```
optisation-pc/
├── optimizer.py       # Script principal
├── build.bat          # Script de compilation .exe
├── requirements.txt   # Dépendances Python
├── version_info.txt   # Métadonnées .exe (PyInstaller)
├── README.md
├── CHANGELOG.md
└── .gitignore
```

---

## 📄 Licence

MIT — Libre d'utilisation, modification et redistribution.

---

## 👨‍💻 Auteur

**CedricPoint**  
GitHub : [CedricPoint](https://github.com/CedricPoint)
