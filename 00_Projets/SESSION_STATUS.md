# 📋 SESSION STATUS — DYS & Moi (Mobile App Kivy)

> **Date de la session :** 2026-02-22  
> **Statut général :** ✅ Fondations stables — prêt pour la Phase 2 (Supabase + Exercices)

---

## ✅ CE QUI A ÉTÉ FAIT

### 1. Environnement

- Venv Python créé et activé : `.venv/` à la racine de `00_Projets`
- Kivy installé et fonctionnel
- Connexion Supabase testée via `execution/test_supabase_conn.py` (credentials en `.env`)
- `.gitignore` mis en place (exclut `.venv`, `.env`, `__pycache__`)

### 2. Structure du projet

```
02_mobile_app_kivy/
├── main.py              ← Point d'entrée, logique, navigation, stubs Supabase
├── dys_style.kv         ← Feuille de style globale DYS (UI Layer)
├── requirements.txt     ← Dépendances Kivy
└── assets/
    └── fonts/
        ├── OpenDyslexic-Regular.otf     ✅ présent
        ├── OpenDyslexic-Bold.otf        ✅ présent
        ├── OpenDyslexic-Italic.otf      ✅ présent
        └── OpenDyslexic-BoldItalic.otf  ✅ présent
```

### 3. Navigation (100% fonctionnelle)

```
SplashScreen (3s) ──auto──▶ LoginScreen ──[C'est parti!]──▶ DashboardScreen
```

- **SplashScreen** : logo 🌟, progress bar animée, transition auto après 3 secondes
- **LoginScreen** : saisie du prénom + validation basique (mode offline)
- **DashboardScreen** : message de bienvenue dynamique `"Bonjour [Prénom] ! 🌟"`

### 4. Architecture DYS-Ready

- **`DysScreen`** : classe de base pour tous les écrans (accessibilité centralisée)
- **`DysButton`** : composant réutilisable KV (hauteur min 56dp, coin arrondi, bleu doux)
- **`DysTextInput`** : composant réutilisable KV (fond crème, bordure focus bleue)
- Police `OpenDyslexic` enregistrée avec guard `os.path.exists()` (pas de crash si absente)
- Tous les chemins sont **absolus** (construits depuis `BASE_DIR`)

### 5. Stubs Supabase prêts

- `check_login(prenom)` → stub documenté dans `main.py` (lignes ~226–268)
- `load_user_data(prenom, app)` → stub documenté dans `main.py` (lignes ~271–306)
- Commentaires `# SUPABASE HOOK` marquent précisément les points de branchement
- **Règle** : ne jamais toucher au design (`dys_style.kv`) lors du branchement

---

## 🔲 CE QU'IL RESTE À FAIRE

### Phase 2 — Connexion Supabase (priorité haute)

- [ ] Créer `database/supabase_client.py` : initialiser le client Supabase depuis `.env`
- [ ] Implémenter `check_login()` : requête `SELECT * FROM users WHERE prenom = ?`
- [ ] Implémenter `load_user_data()` : requête sur table `progress`
- [ ] Gérer le mode offline (fallback JSON local si Supabase indisponible)
- [ ] Créer les tables Supabase : `users (id, prenom, created_at, niveau)` + `progress (user_id, activite, score, updated_at)`
  - Schema de référence : `database/schema.sql`

### Phase 3 — Premiers Exercices Pédagogiques

- [ ] Concevoir l'écran `ExerciceScreen` (hérite de `DysScreen`)
- [ ] Intégrer un premier exercice : lecture de syllabes ou lettres
- [ ] Sauvegarder la progression après chaque exercice (via `load_user_data`)
- [ ] Remplacer les boutons placeholder du Dashboard (Lire / Écrire / Jouer) par une vraie navigation

### Phase 4 — Polissage UI

- [ ] Ajouter un vrai logo à la place de l'emoji 🌟 (fichier image dans `assets/images/`)
- [ ] Créer un écran de profil (modifier le prénom, voir la progression)
- [ ] Tester sur Android (Buildozer)

---

## 🚀 COMMANDES POUR REPRENDRE LA PROCHAINE FOIS

### 1. Activer l'environnement virtuel

```powershell
& c:/Users/Dev_Renaud/Documents/00_Dev/00_Projets/.venv/Scripts/Activate.ps1
```

### 2. Lancer l'application

```powershell
cd c:\Users\Dev_Renaud\Documents\00_Dev\00_Projets\02_mobile_app_kivy
python main.py
```

### 3. Tester la connexion Supabase

```powershell
cd c:\Users\Dev_Renaud\Documents\00_Dev\00_Projets
python execution/test_supabase_conn.py
```

### 4. Installer les dépendances (si nouvel environnement)

```powershell
pip install -r 02_mobile_app_kivy/requirements.txt
```

---

## 📁 FICHIERS CLÉS

| Fichier                                     | Rôle                                                       |
| ------------------------------------------- | ---------------------------------------------------------- |
| `02_mobile_app_kivy/main.py`                | Point d'entrée + stubs Supabase                            |
| `02_mobile_app_kivy/dys_style.kv`           | Style global (ne pas toucher lors du branchement Supabase) |
| `directives/skills/skill-kivy-interface.md` | Conventions Kivy & LEARNING LOG                            |
| `directives/global_rules.md`                | Règles globales du projet                                  |
| `database/schema.sql`                       | Schéma des tables Supabase                                 |
| `.env`                                      | Credentials Supabase (ne jamais commiter)                  |
| `execution/test_supabase_conn.py`           | Script de test de connexion Supabase                       |

---

## 🤖 CONTEXTE POUR LES IAs LOCALES (Llama / Codestral)

> Si tu es une IA locale qui reprend ce projet, voici ce que tu dois savoir :
>
> 1. **Ne jamais modifier `dys_style.kv`** pour brancher Supabase — seul `main.py` doit changer.
> 2. **Les stubs sont marqués** `# SUPABASE HOOK` dans `main.py` — c'est l'unique point d'entrée.
> 3. **Chemins toujours absolus** : construire depuis `BASE_DIR = os.path.dirname(os.path.abspath(__file__))`.
> 4. **Classe de base `DysScreen`** : tout nouvel écran doit en hériter.
> 5. **Le client Supabase** sera dans `database/supabase_client.py` (à créer en Phase 2).
