# SKILL: KIVY CORE ARCHITECTURE

## 📱 Framework Specifics

- **Version:** Kivy 2.3.0+
- **Pattern:** Mandatory **Observer Pattern** (Kivy Properties & Bindings).
- **Separation:** UI logic in `.kv` files (Layer 1) vs Business Logic in Python (Layer 2).

## 🎨 UI/UX Rules

- **Responsive:** Use `dp()` and `sp()` for ALL dimensions and fonts.
- **Navigation:** Use `ScreenManager` for all transitions.
- **Feedback:** Every action must trigger visual or haptic feedback.

## 🎯 MISSION: UI/UX DYS SPECIALIST

Convert business logic into a visual interface tailored for dyslexic children (Accessibility, Clarity, Engagement).

## 🛡️ GOLDEN RULES

1. **Typography:** Use only adapted fonts (e.g., OpenDyslexic).
2. **Contrast:** Avoid pure black on pure white. Use pastel/cream backgrounds.
3. **Accessibility:** Minimum button size of 48dp; generous spacing between elements.

## 🚨 CRITICAL RULE: FAILURE PROTOCOL

Upon identifying a Kivy syntax error or a visual inconsistency: **HALT PRODUCTION.** Analyze the cause, update the "LEARNING LOG" below, and resolve before attempting new code.

## 🧠 LEARNING LOG (REtex)

### ✅ Décisions Architecturales (2026-02-22)

- **`DysScreen(Screen)` comme classe de base** : Tous les écrans héritent de `DysScreen` pour centraliser les constantes d'accessibilité (`FONT_NAME`, `MIN_BUTTON_HEIGHT = dp(48)`, couleurs pastels). Ne pas créer d'écran qui hérite directement de `Screen`.
- **Chemins absolus via `os.path`** : `BASE_DIR = os.path.dirname(os.path.abspath(__file__))`. Utiliser `ASSETS_DIR`, `FONTS_DIR`, `IMAGES_DIR`, `SOUNDS_DIR` définis en haut de `main.py`. Ne jamais hardcoder de chemin relatif.
- **Police OpenDyslexic** : Enregistrée via `LabelBase.register()` au démarrage de l'app. Chemin : `assets/fonts/OpenDyslexic-Regular.otf`. Le `if os.path.exists()` évite un crash si la police n'est pas encore présente.
- **`ScreenManager` avec `SlideTransition`** : Transition par défaut. Changer uniquement si un écran spécifique impose une autre transition (ex. FadeTransition pour le splash).

### ✅ Décisions Architecture Séparation KV (2026-02-22)

- **`dys_style.kv` créé** : Feuille de style globale. Couvre `<Label>`, `<Button>`, `<TextInput>` et `<DysScreen>`. Chargé via `Builder.load_file(kv_path)` dans `DysApp.build()` — AVANT la création du ScreenManager.
- **Skill dédié créé** : `skill-kivy-interface.md` pour les conventions de style KV (séparation Python/KV, nommage, `size_hint_y: None` obligatoire avec `height` fixe).
- **Guard `if os.path.exists()`** : Appliqué aussi bien sur `FONT_PATH` que sur `kv_path` pour éviter tout crash si le fichier est absent.

### ❌ Past Failures & Solutions:

- (À remplir au premier bug rencontré)
