# -*- coding: utf-8 -*-
from __future__ import annotations
from typing import Dict, List, Tuple
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
    COLOR_BG:      tuple = (0.98, 0.96, 0.90, 1)   # #FDFBEE — Ivoire doux
    COLOR_PRIMARY: tuple = (0.26, 0.52, 0.96, 1)   # #4285F4 — Bleu primaire
    COLOR_TEXT:    tuple = (0.15, 0.15, 0.20, 1)   # #262633 — Quasi-noir adouci

    # ── DYS_PALETTE : Palette complète pour le constructeur d'avatar ──────────
    # Toutes les couleurs sont normalisées (0.0–1.0) pour Kivy.
    # Utilisation : DysScreen.DYS_PALETTE['skin'][0]  →  tuple RGBA
    DYS_PALETTE: Dict[str, List[Tuple[float, float, float, float]]] = {

        # Fond de la preview avatar (neutre, aéré)
        "background": [
            (0.992, 0.984, 0.933, 1.0),  # #FDFBEE — Ivoire principal
            (0.933, 0.918, 0.886, 1.0),  # #EEEaE2 — Gris-crème
        ],

        # Teintes de peau (chaudes, inclusives)
        "skin": [
            (0.980, 0.875, 0.702, 1.0),  # #FADFB3 — Crème pêche
            (0.898, 0.761, 0.624, 1.0),  # #E5C29F — Beige sable
            (0.651, 0.486, 0.322, 1.0),  # #A67C52 — Brun doux
            (0.478, 0.329, 0.227, 1.0),  # #7A543A — Café au lait
        ],

        # Couleurs d'yeux (lisibles, non-agressives)
        "eyes": [
            (0.420, 0.557, 0.678, 1.0),  # #6B8EAD — Bleu ardoise
            (0.478, 0.620, 0.494, 1.0),  # #7A9E7E — Vert sauge
            (0.722, 0.522, 0.271, 1.0),  # #B88645 — Noisette ambre
            (0.290, 0.290, 0.290, 1.0),  # #4A4A4A — Gris foncé (pupille)
        ],

        # Cheveux (naturels + fantaisie pastel)
        "hair": [
            (0.902, 0.725, 0.380, 1.0),  # #E6B961 — Blond blé
            (0.600, 0.361, 0.235, 1.0),  # #995C3C — Châtain cuivré
            (0.259, 0.192, 0.161, 1.0),  # #423129 — Brun sombre
            (0.173, 0.208, 0.224, 1.0),  # #2C3539 — Noir adouci
            (0.514, 0.639, 0.714, 1.0),  # #83A3B6 — Bleu pastel grisé
            (0.847, 0.643, 0.714, 1.0),  # #D8A4B6 — Rose poudré
        ],

        # Habits (teintes unies, pastels mat)
        "clothes": [
            (0.627, 0.690, 0.820, 1.0),  # #A0B0D1 — Lavande délavée
            (0.639, 0.788, 0.659, 1.0),  # #A3C9A8 — Vert menthe
            (0.906, 0.776, 0.396, 1.0),  # #E7C665 — Jaune moutarde
            (0.839, 0.541, 0.486, 1.0),  # #D68A7C — Corail doux
        ],
    }
