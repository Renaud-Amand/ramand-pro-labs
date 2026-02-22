# -*- coding: utf-8 -*-
"""
screens/__init__.py

Point d'entrée du package `screens`.
Expose les classes d'écrans pour un import propre depuis main.py.
"""

from screens.base_screen import DysScreen
from screens.splash_screen    import SplashScreen
from screens.login_screen     import LoginScreen
from screens.dashboard_screen import DashboardScreen
from screens.pin_screen       import PinScreen
from screens.child_dashboard  import ChildDashboardScreen

__all__ = [
    "DysScreen",
    "SplashScreen",
    "LoginScreen",
    "DashboardScreen",
    "PinScreen",
    "ChildDashboardScreen",
]
