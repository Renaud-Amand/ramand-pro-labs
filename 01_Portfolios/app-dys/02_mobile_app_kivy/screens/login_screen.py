# -*- coding: utf-8 -*-
"""
screens/login_screen.py

LoginScreen: parent email/password authentication via Supabase Auth.
Uses a daemon thread for the network call (zero UI freeze).
On success, the JWT access token is stored on app.session_data so that
downstream screens (DashboardScreen.create_child_profile) can use it.
"""

import threading

from kivy.app        import App
from kivy.clock      import Clock
from kivy.properties import BooleanProperty

from screens.base_screen import DysScreen


class LoginScreen(DysScreen):
    """Authentication screen — validates parent credentials against Supabase Auth."""

    is_loading: BooleanProperty = BooleanProperty(False)

    # ── Lifecycle ──────────────────────────────────────────────────────────────
    def on_enter(self) -> None:
        super().on_enter()
        self._reset_form()

    # ── Helpers ────────────────────────────────────────────────────────────────
    def _reset_form(self) -> None:
        """Clear all input fields and error state on each screen entry."""
        self.ids.email_input.text    = ""
        self.ids.password_input.text = ""
        self.ids.error_label.text    = ""
        self.is_loading              = False

    def _show_error(self, message: str) -> None:
        self.is_loading           = False
        self.ids.error_label.text = message

    # ── Submit ─────────────────────────────────────────────────────────────────
    def submit_login(self) -> None:
        """
        Entry point called by the KV 'Se connecter' button.

        Reads the email and password fields, guards against empty input, then
        delegates the Supabase Auth call to a daemon thread.
        """
        email    = self.ids.email_input.text.strip()
        password = self.ids.password_input.text.strip()

        if not email or not password:
            self._show_error("Veuillez saisir votre email et mot de passe.")
            return

        self.is_loading           = True
        self.ids.error_label.text = ""

        threading.Thread(
            target=self._run_login_thread,
            args=(email, password),
            daemon=True,
        ).start()

    # ── Thread worker ──────────────────────────────────────────────────────────
    def _run_login_thread(self, email: str, password: str) -> None:
        """
        Background thread: calls auth_manager.login_user() (synchronous
        Supabase Auth call), then schedules the UI update on the main thread
        via Clock.

        login_user() returns (success: bool, message: str, data: dict).
        On success, data contains {"token": <access_token>}.
        """
        from database.auth_manager import login_user  # local import — avoids circular dependency
        from database              import run_async   # local import — avoids circular dependency

        try:
            success, message, data = run_async(login_user(email, password))
        except Exception as exc:  # noqa: BLE001
            success, message, data = False, str(exc), {}

        Clock.schedule_once(
            lambda dt: self._on_login_result(success, message, data, email), 0
        )

    # ── UI callback (main thread) ──────────────────────────────────────────────
    def _on_login_result(
        self, success: bool, message: str, data: dict, email: str
    ) -> None:
        """
        Called on the main thread once the Supabase Auth check completes.

        On success:
            - Stores the JWT access token on app.session_data (used by
              DashboardScreen.create_child_profile for RLS-protected calls).
            - Populates app.user_prenom with the email prefix as a temporary
              display name; DashboardScreen._on_user_data_loaded overwrites it
              with the real prenom fetched from Supabase.
            - Transitions to the dashboard screen.
        On failure:
            - Surfaces the error message without leaving the screen.
        """
        self.is_loading = False
        if success:
            app = App.get_running_app()
            app.session_data = data                               # {"token": <access_token>}
            app.user_prenom  = email.split("@")[0].capitalize()  # temporary; overwritten by dashboard
            self.manager.current = "dashboard"
        else:
            self._show_error(message or "Identifiants incorrects. Vérifiez votre email et mot de passe.")
