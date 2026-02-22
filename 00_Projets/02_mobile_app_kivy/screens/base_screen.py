# -*- coding: utf-8 -*-
"""
screens/base_screen.py

Classe de base DysScreen partagée par tous les écrans de l'application.

Rôle :
    - Centralise les constantes de design DYS (polices, couleurs, espacements).
    - Fournit un point d'héritage unique pour Screen.
    - N'importe aucun autre module de l'application (zéro risque de cycle).
"""

from kivy.metrics   import dp, sp
from kivy.uix.screenmanager import Screen


class DysScreen(Screen):
    """Écran de base avec les constantes de design DYS pré-chargées."""

    # ── Typographie ────────────────────────────────────────────────────────────
    FONT_NAME:         str   = "OpenDyslexic"
    FONT_SIZE_BODY:    float = sp(18)
    FONT_SIZE_TITLE:   float = sp(28)

    # ── Dimensions ─────────────────────────────────────────────────────────────
    MIN_BUTTON_HEIGHT: float = dp(56)
    SPACING:           float = dp(16)

    # ── Palette de couleurs (crème / bleu / texte sombre) ─────────────────────
    COLOR_BG:      tuple = (0.98, 0.96, 0.90, 1)
    COLOR_PRIMARY: tuple = (0.26, 0.52, 0.96, 1)
    COLOR_TEXT:    tuple = (0.15, 0.15, 0.20, 1)
