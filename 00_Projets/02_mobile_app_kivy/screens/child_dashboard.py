# -*- coding: utf-8 -*-
"""
screens/child_dashboard.py

ChildDashboardScreen : espace enfant — squelette Phase 3.
"""

from screens.base_screen import DysScreen


class ChildDashboardScreen(DysScreen):
    """Tableau de bord de l'enfant — squelette pour la Phase 3."""

    name: str = "child_dashboard"

    def on_enter(self) -> None:
        super().on_enter()
