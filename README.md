# 🖥️ Windows Optimizer

Script PowerShell d’optimisation Windows pour **bureautique** et **gaming**, avec choix de profils et de modes (Performance / Silencieux).  
Compatible **Windows 10** et **Windows 11**.

---

## 📦 Ce dépôt (édition gratuite)

Cette version **FREE** propose :

- **Profils** : Bureautique | Gaming  
- **Modes** : Performance (réactivité max) | Silencieux (calme / autonomie)  
- **Nettoyage** : fichiers temporaires, cache Windows Update, Prefetch  
- **Système** : plan d’alimentation, options de performance visuelle, vérification TRIM (SSD), réduction basique de la télémétrie  
- **Démarrage** : lister et désactiver les programmes au démarrage (registre)  
- **Détection** : demande du système d’exploitation (Windows 10 / 11) au lancement  

Aucune modification agressive du registre dans cette édition : usage sûr au quotidien.

---

## ⚙️ Prérequis

- **Windows 10** ou **Windows 11**
- **PowerShell** (intégré à Windows)
- **Droits administrateur** (obligatoire)

---

## 🚀 Installation & utilisation

### Méthode simple (recommandée)

1. Télécharge ou clone ce dépôt.
2. **Double-clique** sur `Lancer-Optimisation-Free.bat`.
3. Accepte la demande de **droits administrateur** (UAC).
4. Le script s’ouvre sans avoir à activer l’exécution des scripts. Choisis ton **système d’exploitation** (Windows 10 / 11) puis utilise le menu.

---

### Méthode manuelle (PowerShell)

1. Télécharge ou clone ce dépôt.
2. *(Une seule fois)* Si tu as l’erreur *« L’exécution de scripts est désactivée »* : double-clique sur **`Activer-Execution-Scripts.bat`**. Cela autorise les scripts PowerShell pour ton compte.
3. Ouvre **PowerShell en tant qu’administrateur** (clic droit sur le menu Démarrer → *Windows PowerShell (Admin)*).
4. Va dans le dossier du projet puis lance :

```powershell
cd "D:\OPTIMISATION PC"   # adapte le chemin si besoin
.\Optimisation-PC-Free.ps1
```

Si tu n’as pas exécuté `Activer-Execution-Scripts.bat` et que l’erreur apparaît encore, lance cette commande **une fois** dans PowerShell (admin) :

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned -Force
```

Puis relance `.\Optimisation-PC-Free.ps1`.

---

## 📋 Menu principal (édition Free)

| Option | Description |
|--------|-------------|
| **1** | Profil **Bureautique** (Performance ou Silencieux) |
| **2** | Profil **Gaming** (Performance ou Silencieux) |
| **3** | **Nettoyage** (Temp, Windows Update, Prefetch) |
| **4** | **Système & Performance** (options visuelles, TRIM, télémétrie) |
| **5** | **Démarrage** (lister / désactiver programmes au démarrage) |
| **0** | Quitter |

---

## ⚠️ Avertissements

- **Toujours lancer le script en administrateur** pour que les changements système soient appliqués.
- Créer un **point de restauration Windows** avant des optimisations importantes est recommandé.
- La désactivation de programmes au démarrage est **irréversible** depuis le script (tu peux les réactiver manuellement si besoin).
- Ce script est fourni **tel quel** ; l’auteur décline toute responsabilité en cas de dommage. Utilise à tes risques.

---

## 📜 Licence

Ce projet est diffusé sous licence **MIT**. Tu peux l’utiliser, le modifier et le redistribuer librement.

---

## 🔷 Version Premium

Une **édition Premium** existe avec des optimisations avancées :

- Nettoyages **étendus** (miniatures, cache DNS, polices, Delivery Optimization)
- **Plan d’alimentation ULTRA** (CPU min 100 %, PCI Express)
- **Tweaks registre gaming** (TCP, Game DVR, réseau, GPU scheduling)
- **Télémétrie poussée** et **services étendus** (liste complète en Manuel)
- **Backup registre** conseillé avant modifications
- Profil **Gaming ULTRA** (tout-en-un)

Pour obtenir la version Premium (script complet + support), rejoins le Discord : **[https://discord.gg/P8NPUUwtYw](https://discord.gg/P8NPUUwtYw)** ou consulte les liens ci-dessous.

---

---

## ☕ Me soutenir & contact

Si ce projet t’est utile, tu peux m’offrir un café :

**[https://buymeacoffee.com/cedricpoint](https://buymeacoffee.com/cedricpoint)**

**Contact / Discord :** [https://discord.gg/P8NPUUwtYw](https://discord.gg/P8NPUUwtYw) (Informaclique)

Merci !

---

**Bon optim ! 🚀**
