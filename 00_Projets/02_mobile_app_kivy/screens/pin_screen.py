# -*- coding: utf-8 -*-
"""
screens/pin_screen.py

PinScreen : écran de verrouillage enfant avec pavé numérique.
Vérifie le PIN via Supabase → redirige vers ChildDashboardScreen si correct.
"""

import threading

from kivy.clock      import Clock
from kivy.properties import StringProperty, BooleanProperty

from database              import run_async
from database.auth_manager import verify_child_pin_db
from screens.base_screen   import DysScreen


class PinScreen(DysScreen):
    name:        str             = "pin"
    pin_code:    StringProperty  = StringProperty("")
    pin_error:   StringProperty  = StringProperty("")
    is_checking: BooleanProperty = BooleanProperty(False)

    def on_enter(self) -> None:
        super().on_enter()
        self.pin_code    = ""
        self.pin_error   = ""
        self.is_checking = False

    # ── Saisie ─────────────────────────────────────────────────────────────────
    def on_digit(self, digit: str) -> None:
        if self.is_checking or len(self.pin_code) >= 4:
            return
        self.pin_code  += digit
        self.pin_error  = ""
        if len(self.pin_code) == 4:
            Clock.schedule_once(lambda dt: self._check_pin(), 0.15)

    def on_erase(self) -> None:
        if self.is_checking:
            return
        self.pin_code  = self.pin_code[:-1]
        self.pin_error = ""

    # ── Vérification Supabase ──────────────────────────────────────────────────
    def _check_pin(self) -> None:
        self.is_checking = True
        threading.Thread(
            target=self._run_pin_thread,
            args=(self.pin_code,),
            daemon=True,
        ).start()

    def _run_pin_thread(self, pin: str) -> None:
        try:
            success, message, data = run_async(verify_child_pin_db(pin))
        except Exception as exc:
            success, message, data = False, str(exc), {}
        Clock.schedule_once(
            lambda dt: self._on_pin_result(success, message, data), 0
        )

    def _on_pin_result(self, success: bool, message: str, data: dict) -> None:
        self.is_checking = False
        if success:
            self.pin_code  = ""
            self.pin_error = ""
            self.manager.current = "child_dashboard"
        else:
            self.pin_code  = ""
            self.pin_error = message

    # ── Porte de secours Parent ────────────────────────────────────────────────
    def go_to_parent_login(self) -> None:
        """Redirige le parent vers le LoginScreen (sans toucher la session)."""
        self.pin_code    = ""
        self.pin_error   = ""
        self.is_checking = False
        self.manager.current = "login"
