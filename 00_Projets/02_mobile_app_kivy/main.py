# -*- coding: utf-8 -*-
"""
main.py — Point d'entrée de l'application mobile DYS.

Objectif    : Initialiser l'application Kivy, gérer la navigation entre écrans
              (SplashScreen → LoginScreen → DashboardScreen) et préparer les
              interfaces de connexion à Supabase.

Architecture : Couche UI/Logique (Layer 1 + Layer 2) — les fonctions marquées
               "SUPABASE HOOK" sont des stubs intentionnels à brancher par une
               IA spécialisée (Llama/Codestral) sans modifier le design.
"""

import os

from kivy.app import App
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.metrics import dp, sp
from kivy.properties import StringProperty
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.core.text import LabelBase

# ──────────────────────────────────────────────────────────────────────────────
# CHEMINS ABSOLUS (RULES.md §Paths)
# Convention : TOUJOURS construire les chemins depuis BASE_DIR.
#              Ne jamais utiliser de chemins relatifs ou codés en dur.
# ──────────────────────────────────────────────────────────────────────────────
BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
FONTS_DIR  = os.path.join(ASSETS_DIR, "fonts")
IMAGES_DIR = os.path.join(ASSETS_DIR, "images")
SOUNDS_DIR = os.path.join(ASSETS_DIR, "sounds")
KV_PATH    = os.path.join(BASE_DIR, "dys_style.kv")

# ──────────────────────────────────────────────────────────────────────────────
# ENREGISTREMENT DES POLICES DYS
# Prérequis : placer OpenDyslexic-Regular.otf dans assets/fonts/
#             Téléchargement : https://opendyslexic.org
# ──────────────────────────────────────────────────────────────────────────────
FONT_PATH = os.path.join(FONTS_DIR, "OpenDyslexic-Regular.otf")
if os.path.exists(FONT_PATH):
    LabelBase.register(name="OpenDyslexic", fn_regular=FONT_PATH)


# ══════════════════════════════════════════════════════════════════════════════
# CLASSE DE BASE — DysScreen
# RÈGLE ABSOLUE : Tous les écrans DOIVENT hériter de cette classe, jamais
#                 directement de Screen.
# ══════════════════════════════════════════════════════════════════════════════
class DysScreen(Screen):
    """
    Classe de base centralisant les règles d'accessibilité DYS.

    Constantes disponibles dans chaque sous-écran :
        FONT_NAME         → "OpenDyslexic"
        FONT_SIZE_BODY    → sp(18) — corps de texte
        FONT_SIZE_TITLE   → sp(28) — titres
        MIN_BUTTON_HEIGHT → dp(56) — boutons tactiles
        SPACING           → dp(16) — espacement générique
        COLOR_BG          → fond crème (0.98, 0.96, 0.90, 1)
        COLOR_PRIMARY     → bleu doux (0.26, 0.52, 0.96, 1)
        COLOR_TEXT        → gris foncé (0.15, 0.15, 0.20, 1)
    """

    FONT_NAME:         str   = "OpenDyslexic"
    FONT_SIZE_BODY:    float = sp(18)
    FONT_SIZE_TITLE:   float = sp(28)
    MIN_BUTTON_HEIGHT: float = dp(56)
    SPACING:           float = dp(16)

    COLOR_BG:      tuple = (0.98, 0.96, 0.90, 1)
    COLOR_PRIMARY: tuple = (0.26, 0.52, 0.96, 1)
    COLOR_TEXT:    tuple = (0.15, 0.15, 0.20, 1)

    def on_enter(self) -> None:
        """Callback Kivy — écran actif."""
        super().on_enter()

    def on_leave(self) -> None:
        """Callback Kivy — écran en arrière-plan."""
        super().on_leave()


# ══════════════════════════════════════════════════════════════════════════════
# ÉCRAN 1 — SplashScreen
# ══════════════════════════════════════════════════════════════════════════════
class SplashScreen(DysScreen):
    """
    Écran de démarrage : logo + barre de progression animée.

    Durée    : 3 secondes (SPLASH_DURATION).
    Sortie   : Transition automatique vers "login" via Clock.schedule_once.
    Feedback : Barre de progression animée (Clock.schedule_interval).
    """

    name: str = "splash"
    SPLASH_DURATION: float = 3.0   # secondes — ajustable sans toucher au reste

    def on_enter(self) -> None:
        """Lance l'animation et programme la sortie automatique."""
        super().on_enter()
        self._progress_step = 0.0
        self._clock_progress = Clock.schedule_interval(
            self._animate_progress, self.SPLASH_DURATION / 100
        )
        Clock.schedule_once(self._go_to_login, self.SPLASH_DURATION)

    def _animate_progress(self, dt: float) -> None:
        """Incrémente la barre de progression de 0 à 100."""
        bar = self.ids.get("progress_bar")
        if bar:
            self._progress_step = min(self._progress_step + 1, 100)
            bar.value = self._progress_step

    def _go_to_login(self, dt: float) -> None:
        """Navigue vers l'écran de connexion."""
        if self._clock_progress:
            self._clock_progress.cancel()
        self.manager.current = "login"

    def on_leave(self) -> None:
        """Nettoyage des callbacks Kivy à la sortie de l'écran."""
        super().on_leave()
        if hasattr(self, "_clock_progress") and self._clock_progress:
            self._clock_progress.cancel()


# ══════════════════════════════════════════════════════════════════════════════
# ÉCRAN 2 — LoginScreen
# ══════════════════════════════════════════════════════════════════════════════
class LoginScreen(DysScreen):
    """
    Écran de saisie du prénom.

    Interface : Un champ DysTextInput + un bouton DysButton.
    Sortie    : Appel de check_login() puis navigation vers "dashboard".

    ──────────────────────────────────────────────────────────────────────────
    SUPABASE HOOK : validate_login()
    ──────────────────────────────────────────────────────────────────────────
    Pour brancher Supabase, modifier uniquement la méthode validate_login() :
        1. Récupérer le prénom depuis self.ids.prenom_input.text.
        2. Appeler load_user_data(prenom) pour interroger Supabase.
        3. Stocker le résultat dans app.user_data (dict).
        4. Naviguer vers "dashboard".
    Le design (dys_style.kv) ne doit PAS être modifié lors de ce branchement.
    """

    name: str = "login"

    def validate_login(self) -> None:
        """
        Valide la saisie du prénom et navigue vers le dashboard.

        Étapes actuelles (mode offline) :
            1. Lecture du prénom depuis le champ.
            2. Validation basique (non vide).
            3. Stockage dans App.user_prenom.
            4. Navigation vers "dashboard".

        Étapes futures (branchement Supabase) :
            → Remplacer l'étape 3 par un appel à load_user_data(prenom)
              qui retournera un dict {prenom, progression, niveau}.
        """
        prenom = self.ids.prenom_input.text.strip()
        if not prenom:
            self.ids.prenom_input.hint_text = "⚠️ Écris ton prénom d'abord !"
            return

        app = App.get_running_app()
        app.user_prenom = prenom.capitalize()

        # ── SUPABASE HOOK : décommenter et implémenter quand Supabase prêt ──
        # user_data = check_login(prenom)       # vérifie si l'utilisateur existe
        # load_user_data(prenom, app)           # charge progression locale/cloud
        # ────────────────────────────────────────────────────────────────────

        self.manager.current = "dashboard"


# ══════════════════════════════════════════════════════════════════════════════
# ÉCRAN 3 — DashboardScreen
# ══════════════════════════════════════════════════════════════════════════════
class DashboardScreen(DysScreen):
    """
    Premier écran pédagogique — tableau de bord de l'apprenant.

    Affiche le message de bienvenue dynamique : "Bonjour [Prénom] !".
    welcome_message est une Kivy StringProperty : elle se met à jour
    automatiquement dans le KV quand sa valeur change en Python.

    ──────────────────────────────────────────────────────────────────────────
    SUPABASE HOOK : on_enter()
    ──────────────────────────────────────────────────────────────────────────
    À l'entrée sur cet écran, appeler load_user_data() pour récupérer
    la progression depuis Supabase et mettre à jour les widgets.
    Pattern suggéré :
        progression = app.user_data.get("niveau", 1)
        # mise à jour des boutons d'activité selon le niveau
    """

    name:            str          = "dashboard"
    welcome_message: StringProperty = StringProperty("Bonjour !")

    def on_enter(self) -> None:
        """Met à jour le message de bienvenue avec le prénom stocké."""
        super().on_enter()
        app = App.get_running_app()
        prenom = getattr(app, "user_prenom", "")
        self.welcome_message = f"Bonjour {prenom} ! 🌟" if prenom else "Bonjour !"

        # ── SUPABASE HOOK : décommenter pour charger la progression ──
        # user_data = load_user_data(prenom)
        # self._update_activities(user_data)
        # ─────────────────────────────────────────────────────────────


# ══════════════════════════════════════════════════════════════════════════════
# STUBS SUPABASE — À IMPLÉMENTER PAR UNE IA SPÉCIALISÉE
# Ces fonctions forment l'interface contractuelle entre la couche UI (Layer 1)
# et la couche Data (Layer 3). Le design ne doit PAS être modifié lors du
# branchement de Supabase.
# ══════════════════════════════════════════════════════════════════════════════

def check_login(prenom: str) -> dict:
    """
    Vérifie si un utilisateur existe dans Supabase et retourne ses données.

    ── CONTRAT D'INTERFACE (ne pas modifier la signature) ──────────────────

    Args:
        prenom (str): Prénom saisi par l'enfant (ex: "Emma").

    Returns:
        dict: {
            "exists":     bool,        # True si l'utilisateur est connu
            "prenom":     str,         # prénom normalisé depuis la BDD
            "niveau":     int,         # niveau pédagogique (1–5)
            "progression": float,      # progression globale (0.0 à 1.0)
        }
        En cas d'erreur réseau : retourner {"exists": False, "prenom": prenom,
                                             "niveau": 1, "progression": 0.0}

    ── INSTRUCTIONS POUR L'IA QUI IMPLÉMENTERA CETTE FONCTION ─────────────

    1. Importer le client Supabase depuis `database/supabase_client.py`
       (déjà configuré dans la session précédente).
    2. Requête cible :
           supabase.table("users").select("*").eq("prenom", prenom).execute()
    3. Gérer les cas : utilisateur inconnu (créer le profil), erreur réseau
       (fallback mode offline).
    4. Logger le résultat (niveau DEBUG) dans le logger Kivy.
    5. NE PAS modifier l'interface graphique ici — uniquement retourner le dict.

    ── TABLES SUPABASE ATTENDUES ───────────────────────────────────────────
    Table "users"   : id, prenom, created_at, niveau
    Table "progress": user_id, activite, score, updated_at

    ── EXEMPLE D'IMPLÉMENTATION (stub) ────────────────────────────────────
    """
    # TODO: Remplacer par la vraie requête Supabase
    return {
        "exists":      False,
        "prenom":      prenom.capitalize(),
        "niveau":      1,
        "progression": 0.0,
    }


def load_user_data(prenom: str, app: "DysApp") -> None:
    """
    Charge les données de progression depuis Supabase et les injecte dans l'App.

    ── CONTRAT D'INTERFACE (ne pas modifier la signature) ──────────────────

    Args:
        prenom (str):   Prénom de l'utilisateur (clé de recherche).
        app (DysApp):   Instance de l'application Kivy en cours.
                        Les données doivent être stockées dans `app.user_data`.

    Side effects:
        Remplit `app.user_data` (dict) avec les données Supabase.

    ── INSTRUCTIONS POUR L'IA QUI IMPLÉMENTERA CETTE FONCTION ─────────────

    1. Appeler check_login(prenom) pour obtenir les données de base.
    2. Requête secondaire pour charger la progression :
           supabase.table("progress").select("*")
                   .eq("user_id", user["id"]).execute()
    3. Stocker dans app.user_data :
           app.user_data = {
               "prenom": ..., "niveau": ..., "progression": [...],
           }
    4. Gérer le mode offline : si Supabase indisponible, charger depuis
       un fichier JSON local (assets/cache/user_data.json).
    5. NE PAS naviguer entre les écrans ici — uniquement charger les données.

    ── EXEMPLE D'IMPLÉMENTATION (stub) ────────────────────────────────────
    """
    # TODO: Remplacer par la vraie logique Supabase
    app.user_data = {
        "prenom":      prenom.capitalize(),
        "niveau":      1,
        "progression": 0.0,
    }


# ══════════════════════════════════════════════════════════════════════════════
# APPLICATION PRINCIPALE
# ══════════════════════════════════════════════════════════════════════════════
class DysApp(App):
    """
    Application principale Kivy — DYS & Moi.

    Attributs d'état (accessibles depuis tous les écrans via App.get_running_app()) :
        user_prenom (str)  : Prénom de l'enfant connecté.
        user_data   (dict) : Données de progression (alimenté par load_user_data).
    """

    def build(self) -> ScreenManager:
        """
        Initialise l'application : police, styles KV, écrans.

        Returns:
            ScreenManager : widget racine avec tous les écrans enregistrés.
        """
        # État global de l'application
        self.user_prenom: str  = ""
        self.user_data:   dict = {}

        # Chargement du style global DYS (AVANT la création des widgets)
        if os.path.exists(KV_PATH):
            Builder.load_file(KV_PATH)

        # Construction du ScreenManager
        sm = ScreenManager(transition=SlideTransition())
        sm.add_widget(SplashScreen())
        sm.add_widget(LoginScreen())
        sm.add_widget(DashboardScreen())
        return sm


# ──────────────────────────────────────────────────────────────────────────────
# POINT D'ENTRÉE
# ──────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    DysApp().run()
