# -*- coding: utf-8 -*-
"""
main.py — Chef d'orchestre de l'application mobile DYS.

Responsabilités (UNIQUEMENT) :
    1. Configuration du moteur Kivy (fps, input)
    2. Enregistrement des polices DYS
    3. Chargement des fichiers KV (styles globaux + écrans)
    4. Construction du ScreenManager
    5. Définition de DysApp

Toute logique métier se trouve dans screens/ et database/.
"""

import os

# ══════════════════════════════════════════════════════════════════════════════
# ⚡ OPTIMISATIONS MOTEUR — DOIT PRÉCÉDER TOUS LES AUTRES IMPORTS KIVY
# ══════════════════════════════════════════════════════════════════════════════
from kivy.config import Config
Config.set('graphics', 'maxfps', '30')
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')

# ── Imports Kivy ───────────────────────────────────────────────────────────────
from kivy.app        import App
from kivy.lang       import Builder
from kivy.properties import StringProperty, DictProperty
from kivy.uix.screenmanager import ScreenManager, SlideTransition
from kivy.core.text  import LabelBase

# ── Imports Écrans ─────────────────────────────────────────────────────────────
from screens import (
    SplashScreen,
    LoginScreen,
    DashboardScreen,
    PinScreen,
    ChildDashboardScreen,
)

# ── Imports Data Layer ─────────────────────────────────────────────────────────
from database.supabase_client import db_manager

# ══════════════════════════════════════════════════════════════════════════════
# CHEMINS ABSOLUS
# ══════════════════════════════════════════════════════════════════════════════
BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
FONTS_DIR  = os.path.join(ASSETS_DIR, "fonts")

KV_SCREENS_DIR = os.path.join(ASSETS_DIR, "screens_kv")

KV_FILES = [
    os.path.join(BASE_DIR, "dys_style.kv"),                      # widgets globaux (doit être en premier)
    os.path.join(KV_SCREENS_DIR, "splash.kv"),
    os.path.join(KV_SCREENS_DIR, "login.kv"),
    os.path.join(KV_SCREENS_DIR, "dashboard.kv"),
    os.path.join(KV_SCREENS_DIR, "pin.kv"),
    os.path.join(KV_SCREENS_DIR, "child_dashboard.kv"),
]

# ══════════════════════════════════════════════════════════════════════════════
# ENREGISTREMENT DES POLICES DYS
# ══════════════════════════════════════════════════════════════════════════════
_font_path = os.path.join(FONTS_DIR, "OpenDyslexic-Regular.otf")
if os.path.exists(_font_path):
    LabelBase.register(name="OpenDyslexic", fn_regular=_font_path)


# ══════════════════════════════════════════════════════════════════════════════
# APPLICATION PRINCIPALE
# ══════════════════════════════════════════════════════════════════════════════
class DysApp(App):
    user_prenom  = StringProperty("")
    user_data    = DictProperty({})
    session_data = DictProperty({})

    def build(self):
        # Chargement des fichiers KV
        for kv in KV_FILES:
            Builder.load_file(kv)

        # ScreenManager — ordre = ordre de navigation logique
        sm = ScreenManager(transition=SlideTransition())
        sm.add_widget(SplashScreen(name="splash"))
        sm.add_widget(LoginScreen(name="login"))
        sm.add_widget(DashboardScreen(name="dashboard"))
        sm.add_widget(PinScreen(name="pin"))
        sm.add_widget(ChildDashboardScreen(name="child_dashboard"))
        sm.current = "splash"
        return sm

    def on_start(self) -> None:
        """Called by Kivy after build(). Safe place to trigger I/O."""
        # db_manager.initialise() is already called at import time, but
        # we call it here again — it is idempotent — to ensure the online
        # state is logged after the Kivy window is fully ready.
        db_manager.initialise()


# ══════════════════════════════════════════════════════════════════════════════
# BUSINESS FUNCTIONS  (SUPABASE HOOKS)
# ══════════════════════════════════════════════════════════════════════════════

def check_login(prenom: str) -> bool:
    """
    Verify that *prenom* exists in the ``users`` table.

    Offline-First rule: if the Supabase client is unavailable, we
    optimistically allow login so the app remains usable without network.

    Args:
        prenom: The child's first name as entered on the login screen.

    Returns:
        ``True``  — user found, or offline fallback.
        ``False`` — user not found (online mode only).
    """
    # SUPABASE HOOK — Offline-First fallback
    if not db_manager.is_online:
        return True

    try:
        result = (
            db_manager.client
            .table("users")
            .select("prenom")
            .eq("prenom", prenom.strip().capitalize())
            .execute()
        )
        return bool(result.data)
    except Exception:  # noqa: BLE001
        # Network error after initialisation → degrade gracefully
        return True


def load_user_data(prenom: str, app: "DysApp") -> None:
    """
    Fetch the child's progress stats from Supabase and store them on *app*.

    Populates ``app.user_data`` with keys:
        - ``prenom``      (str)  child's display name
        - ``score_total`` (int)  cumulative score across all sessions
        - ``sessions``    (int)  number of completed sessions

    Offline-First rule: if offline, ``app.user_data`` is populated with
    safe default values so every screen that reads it can render normally.

    Args:
        prenom: The child's first name (used as query key).
        app:    The running ``DysApp`` instance (target for ``user_data``).
    """
    # SUPABASE HOOK — Offline-First defaults
    _defaults: dict = {
        "prenom": prenom.strip().capitalize(),
        "score_total": 0,
        "sessions": 0,
    }

    if not db_manager.is_online:
        app.user_data = _defaults
        return

    try:
        result = (
            db_manager.client
            .table("progress")
            .select("score_total, sessions")
            .eq("prenom", prenom.strip().capitalize())
            .execute()
        )
        if result.data:
            row = result.data[0]
            app.user_data = {
                "prenom":      prenom.strip().capitalize(),
                "score_total": int(row.get("score_total", 0)),
                "sessions":    int(row.get("sessions", 0)),
            }
        else:
            # User exists in ``users`` but has no progress row yet
            app.user_data = _defaults
    except Exception:  # noqa: BLE001
        # Network error after initialisation → fall back to defaults
        app.user_data = _defaults


# ══════════════════════════════════════════════════════════════════════════════
# LANCEMENT
# ══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    DysApp().run()