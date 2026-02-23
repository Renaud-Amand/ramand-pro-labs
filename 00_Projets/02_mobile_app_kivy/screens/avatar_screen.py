# -*- coding: utf-8 -*-
"""
screens/avatar_screen.py

ChildAvatarScreen : constructeur d'avatar pour le profil enfant.

Rôle :
    - Permet à l'enfant de choisir une couleur par catégorie (peau, cheveux, yeux, habits).
    - Génère dynamiquement les boutons de couleur depuis DYS_PALETTE.
    - Stocke les choix dans avatar_config (prêt pour Supabase) et navigue vers l'écran suivant.
"""

from __future__ import annotations

from kivy.factory import Factory
from kivy.properties import ObjectProperty, StringProperty

from screens.base_screen import DysScreen


class ChildAvatarScreen(DysScreen):
    """Écran de construction d'avatar enfant."""

    name: str = "child_avatar"

    # Catégorie actuellement affichée (ex. : "skin", "hair", …)
    active_category: StringProperty = StringProperty("skin")

    # Stocke les choix de l'enfant : {'skin': rgba_tuple, 'hair': rgba_tuple, …}
    avatar_config: ObjectProperty = ObjectProperty({})

    # ── Cycle de vie ────────────────────────────────────────────────────────────

    def on_enter(self) -> None:
        """Initialise l'écran à chaque ouverture."""
        self.avatar_config = {}
        self.select_category("skin")

    # ── Logique UI ───────────────────────────────────────────────────────────────

    def select_category(self, category_name: str) -> None:
        """
        Active une catégorie et met à jour la grille de couleurs.

        Args:
            category_name: clé dans DYS_PALETTE ('skin', 'hair', 'eyes', 'clothes').
        """
        self.active_category = category_name
        self._highlight_category_button(category_name)
        self.populate_color_grid(category_name)

    def _highlight_category_button(self, category_name: str) -> None:
        """
        Met en surbrillance le bouton de catégorie actif (état 'down').
        Les autres boutons reviennent à l'état 'normal'.
        """
        mapping = {
            "skin":    "btn_skin",
            "hair":    "btn_hair",
            "eyes":    "btn_eyes",
            "clothes": "btn_clothes",
        }
        for key, btn_id in mapping.items():
            btn = self.ids.get(btn_id)
            if btn:
                btn.state = "down" if key == category_name else "normal"

    def populate_color_grid(self, category: str) -> None:
        """
        Vide la grille et injecte un AvatarColorButton par couleur de la catégorie.

        Args:
            category: clé dans DYS_PALETTE.
        """
        grid = self.ids.get("color_grid")
        if grid is None:
            return

        grid.clear_widgets()

        colors = self.DYS_PALETTE.get(category, [])
        for rgba in colors:
            btn = Factory.AvatarColorButton()
            # background_normal est réutilisé comme porteur de couleur (cf. canvas dans .kv)
            btn.background_normal = rgba
            btn.bind(on_press=lambda instance, c=rgba: self._on_color_selected(c))
            grid.add_widget(btn)

    # ── Gestion des sélections ───────────────────────────────────────────────────

    def _on_color_selected(self, rgba: tuple) -> None:
        """
        Enregistre la couleur choisie pour la catégorie active.

        Args:
            rgba: tuple RGBA normalisé (0.0–1.0).
        """
        self.avatar_config[self.active_category] = rgba

    # ── Sauvegarde ───────────────────────────────────────────────────────────────

    def save_avatar(self) -> None:
        """
        Finalise l'avatar :
        - Complète les catégories non sélectionnées avec la première couleur par défaut.
        - Stocke avatar_config (prêt pour Supabase).
        - Navigue vers l'écran enfant suivant.
        """
        # Valeurs par défaut pour les catégories non configurées
        for category, colors in self.DYS_PALETTE.items():
            if category not in self.avatar_config and colors:
                self.avatar_config[category] = colors[0]

        # TODO Phase 3 : envoyer avatar_config à Supabase via le service profil enfant
        print(f"[AvatarScreen] avatar_config sauvegardé : {self.avatar_config}")

        # Navigation vers le tableau de bord enfant
        if self.manager:
            self.manager.current = "child_dashboard"
