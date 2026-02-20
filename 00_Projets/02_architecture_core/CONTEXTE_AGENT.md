# 🎯 SOURCE DE VÉRITÉ : APPLICATION ALPHABET KIDS (CHARLÈNE)

## 📖 1. VISION DU PROJET

- **Cible :** Charlène, 3 ans.
- **Objectif Pédagogique :** Transition du **SON** vers la **LETTRE**.
- **Philosophie UX :** Zéro frustration. L'application doit être joyeuse, colorée et encourageante. Pas de score négatif, uniquement des récompenses.

## 🛠️ 2. STACK TECHNIQUE

- **Langage :** Python 3.12+
- **Moteur :** Pygame (gestion multimédia et entrées clavier).
- **Base de Données :** Supabase (via `db_manager.py`).
- **Assets :** Dossier local `./assets/images/` et `./assets/sounds/`.

## 🏗️ 3. ARCHITECTURE LOGICIELLE (REFACTORISATION)

L'application doit être structurée de manière **Orientée Objet (OOP)** pour garantir la modularité.

### A. Classes attendues :

- **`AssetManager` :** Gère le chargement sécurisé (try/except) et le **cache** des ressources. Aucune ressource ne doit être rechargée à chaque frame.
- **`GameState` (Enum) :**
  - `START` : Écran d'accueil.
  - `PLAYING_QUESTION` : Affiche uniquement la lettre.
  - `PLAYING_HINT` : Affiche la lettre + image + mot + joue le son.
  - `CELEBRATION_SMALL` : Récompense après une série de 5 justes.
  - `CELEBRATION_BIG` : Récompense "Feu d'artifice" après une série parfaite.
- **`GameApp` :** Classe maîtresse orchestrant la boucle principale (`run`), la mise à jour de la logique (`update`) et le rendu (`draw`).

## ⚙️ 4. LOGIQUE MÉTIER & WORKFLOW

1. **Initialisation :** Chargement des données via `DBManager` (avec fallback local si hors ligne).
2. **Cycle d'une Lettre :**
   - L'état passe à `PLAYING_QUESTION`. On affiche la lettre géante.
   - Un timer de **3 secondes** (non-bloquant via `pygame.time.get_ticks()`) se déclenche.
   - Une fois le délai expiré, l'état passe à `PLAYING_HINT`. On joue le son et on affiche les indices visuels (mot + image).
3. **Navigation :**
   - `Flèche Droite` : Lettre suivante.
   - `Flèche Gauche` : Lettre précédente.
4. **Récompenses :**
   - Système de compteur pour déclencher les états `CELEBRATION` après une série de succès.

## 🎨 5. DIRECTIVES UI/UX

- **Police :** Priorité aux polices rondes/scolaires (Comic Sans MS en fallback, ou police personnalisée).
- **Couleurs :** Fond Rose Pastel, Texte Bleu Roi, Accents vifs pour les boutons.
- **Stabilité :** Si une image ou un son est manquant, l'application doit afficher un placeholder générique et ne **jamais crasher**.

## 🤖 6. INSTRUCTIONS POUR L'AGENT (SOP)

- **Langue :** Commentaires et explications en Français.
- **Style :** Code propre, modulaire, respectant la PEP 8.
- **Explications :** Pour chaque bloc généré, explique brièvement le choix technique pour accompagner la montée en compétence de l'utilisateur (Renaud).
- **Ordre de travail :** Attendre la validation du Chef d'Acte après chaque module (AssetManager -> States -> Main Loop).
