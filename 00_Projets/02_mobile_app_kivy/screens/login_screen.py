# -*- coding: utf-8 -*-
"""
screens/login_screen.py

LoginScreen : connexion parent via Supabase (email + mot de passe).
Utilise un thread secondaire pour l'appel réseau (zéro freeze UI).
"""

import threading

from kivy.app   import App
from kivy.clock import Clock
from kivy.properties import BooleanProperty

from database              import run_async
from database.auth_manager import login_user
from screens.base_screen   import DysScreen


class LoginScreen(DysScreen):
    name:       str            = "login"
    is_loading: BooleanProperty = BooleanProperty(False)

    def on_enter(self) -> None:
        super().on_enter()
        self._reset_form()

    def _reset_form(self) -> None:
        self.ids.email_input.text    = ""
        self.ids.password_input.text = ""
        self.ids.error_label.text    = ""
        self.is_loading              = False

    def submit_login(self) -> None:
        email    = self.ids.email_input.text.strip()
        password = self.ids.password_input.text.strip()

        if not email:
            self._show_error("Veuillez saisir votre adresse email.")
            return
        if not password:
            self._show_error("Veuillez saisir votre mot de passe.")
            return

        self.is_loading           = True
        self.ids.error_label.text = ""

        threading.Thread(
            target=self._run_login_thread,
            args=(email, password),
            daemon=True,
        ).start()

    def _run_login_thread(self, email: str, password: str) -> None:
        try:
            success, message, data = run_async(login_user(email, password))
        except Exception as exc:
            success, message, data = False, str(exc), {}

        Clock.schedule_once(
            lambda dt: self._on_login_result(success, message, data), 0
        )

    def _on_login_result(self, success: bool, message: str, data: dict) -> None:
        self.is_loading = False
        if success:
            App.get_running_app().session_data = data
            self.manager.current = "dashboard"
        else:
            self._show_error(message)

    def _show_error(self, message: str) -> None:
        self.is_loading           = False
        self.ids.error_label.text = message
