# SKILL: KIVY INTERFACE & STYLE CONVENTIONS

> **Mis à jour le : 2026-02-22** — Architecture v2 stabilisée, 3 écrans opérationnels.

## 📐 Séparation des Responsabilités

| Fichier        | Rôle                                           | Couche          |
| -------------- | ---------------------------------------------- | --------------- |
| `main.py`      | Logique, navigation, stubs Supabase, constants | Layer 2 (Logic) |
| `dys_style.kv` | Styles globaux, couleurs, polices, layouts     | Layer 1 (UI)    |
| `screens/*.kv` | Layout spécifique par écran (phase future)     | Layer 1 (UI)    |

## 🗺️ Architecture Actuelle des Écrans

```
DysApp (build)
 └── ScreenManager (SlideTransition)
      ├── SplashScreen  [name="splash"]    → auto-navigue vers "login" après 3s
      ├── LoginScreen   [name="login"]     → validate_login() → navigue vers "dashboard"
      └── DashboardScreen [name="dashboard"] → affiche welcome_message (StringProperty)
```

### Classe de base : `DysScreen(Screen)`

- **Règle absolue** : Tous les écrans héritent de `DysScreen`, jamais directement de `Screen`.
- Centralise les constantes d'accessibilité : `FONT_NAME`, `FONT_SIZE_BODY`, `FONT_SIZE_TITLE`,
  `MIN_BUTTON_HEIGHT`, `SPACING`, `COLOR_BG`, `COLOR_PRIMARY`, `COLOR_TEXT`.

### SplashScreen

- Durée : `SPLASH_DURATION = 3.0` s (constante modifiable en tête de classe).
- Feedback visuel : `ProgressBar` animée via `Clock.schedule_interval`.
- Sortie automatique : `Clock.schedule_once(_go_to_login, 3.0)`.
- Nettoyage : `_clock_progress.cancel()` dans `on_leave()` (évite les fuite de callbacks).

### LoginScreen

- Champ `DysTextInput` (id: `prenom_input`) + bouton `DysButton` (`on_press: root.validate_login()`).
- `validate_login()` : stocke le prénom dans `App.user_prenom`, navigue vers `"dashboard"`.
- **SUPABASE HOOK** : méthode `validate_login()` contient le stub commenté à brancher.

### DashboardScreen

- `welcome_message` = `StringProperty` → liaison automatique KV ↔ Python.
- `on_enter()` construit le message avec `app.user_prenom`.
- **SUPABASE HOOK** : `on_enter()` contient le stub `load_user_data()` à décommenter.

## 🔌 Stubs Supabase (Layer 3 — à implémenter)

| Fonction           | Signature                            | Rôle                                               |
| ------------------ | ------------------------------------ | -------------------------------------------------- |
| `check_login()`    | `(prenom: str) -> dict`              | Vérifie l'utilisateur en BDD, retourne ses données |
| `load_user_data()` | `(prenom: str, app: DysApp) -> None` | Charge la progression, remplit `app.user_data`     |

> **Règle** : Ne jamais modifier l'UI (`dys_style.kv`) lors du branchement Supabase.
> Seuls les stubs dans `main.py` sont à toucher.

## 🎨 Conventions de Style KV

- **Un seul fichier de style global :** `dys_style.kv` — chargé manuellement via `Builder.load_file()` dans `DysApp.build()`.
- **Styles par widget :** Utiliser la syntaxe `<NomWidget>:` pour les règles globales.
- **Styles par écran :** Utiliser la syntaxe `<NomEcran>:` dans le fichier `.kv` dédié à l'écran.
- **Jamais de dimensions en pixels bruts :** Toujours `dp()` pour tailles, `sp()` pour polices.

## 🔤 Gestion des Polices

- **Police principale :** `OpenDyslexic` (enregistrée dans `main.py` via `LabelBase.register()`).
- **Chemin de référence :** `assets/fonts/OpenDyslexic-Regular.otf` (chemin absolu via `FONTS_DIR`).
- **Référence dans `.kv` :** Utiliser le nom enregistré : `font_name: "OpenDyslexic"`.

## 🔗 Chargement du Fichier KV Global

```python
# Dans DysApp.build() — à ajouter quand dys_style.kv est chargé manuellement
from kivy.lang import Builder
KV_PATH = os.path.join(BASE_DIR, "dys_style.kv")
Builder.load_file(KV_PATH)
```

> **Note :** Si le fichier KV porte le même nom que l'App (ex. `dysapp.kv` pour `DysApp`),
> Kivy le charge automatiquement. `dys_style.kv` doit être chargé explicitement.

## 🛡️ Règles d'Or Interface

1. **Fond global :** Fond crème `(0.98, 0.96, 0.90, 1)` sur tous les `DysScreen` via `canvas.before`.
2. **Boutons :** `height: "48dp"` minimum, `size_hint_y: None` obligatoire pour forcer la hauteur.
3. **Espacement :** `spacing: "16dp"` minimum entre éléments de layout.
4. **Pas de couleurs hexadécimales** dans les `.kv` → utiliser les tuples RGBA normalisés (0–1).

## 🧠 LEARNING LOG (REtex)

### ✅ Session 2026-02-22 — Résultats

- **`dys_style.kv` créé** : Fichier de style global couvrant `<Label>`, `<DysButton@Button>`,
  `<DysTextInput@TextInput>`, `<DysScreen>`. Chargement explicite via `Builder.load_file()` dans
  `DysApp.build()` (le nom `dys_style` ≠ `dysapp`, donc pas de chargement automatique).
- **Séparation stricte** : Zéro style inline dans `main.py`. Toutes les valeurs visuelles
  vivent exclusivement dans `dys_style.kv`.
- **`size_hint_y: None`** obligatoire sur tout widget avec `height` fixe dans un `BoxLayout`
  vertical — omis = Kivy ignore silencieusement le `height` explicite.
- **Polices** : 4 variantes `OpenDyslexic` présentes dans `assets/fonts/`. Chargement
  conditionnel via `os.path.exists()` pour éviter un crash si le fichier est absent.
- **StringProperty** : `welcome_message` dans `DashboardScreen` démontre le pattern de
  liaison KV ↔ Python. Toujours déclarer `StringProperty` au niveau classe.
- **Venv** : `.venv` créé dans `02_mobile_app_kivy/`. Activer avec :
  `& c:/Users/Dev_Renaud/Documents/00_Dev/00_Projets/.venv/Scripts/Activate.ps1`

### ❌ Past Failures & Solutions

- **Font crash** : Si `OpenDyslexic-Regular.otf` est absent et `LabelBase.register()` est
  appelé sans le guard `os.path.exists()`, Kivy lève une `FileNotFoundError` au lancement.
  → **Solution** : guard `if os.path.exists(FONT_PATH):` toujours présent dans `main.py`.
