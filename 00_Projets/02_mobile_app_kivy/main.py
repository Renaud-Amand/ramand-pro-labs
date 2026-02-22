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


# ══════════════════════════════════════════════════════════════════════════════
# LANCEMENT
# ══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    DysApp().run()