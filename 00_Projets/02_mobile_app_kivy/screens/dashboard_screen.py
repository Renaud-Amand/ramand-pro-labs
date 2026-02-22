# -*- coding: utf-8 -*-
"""
screens/dashboard_screen.py

DashboardScreen : panneau d'administration du parent.
Fonctionnalités : création de profil enfant, verrouillage, déconnexion.
"""

import threading

from kivy.app        import App
from kivy.clock      import Clock
from kivy.properties import StringProperty, BooleanProperty

from database              import run_async
from database.auth_manager import create_child_profile_db, logout_user
from screens.base_screen   import DysScreen


class DashboardScreen(DysScreen):
    name:            str             = "dashboard"
    welcome_message: StringProperty  = StringProperty("Espace Parent")
    status_message:  StringProperty  = StringProperty("")
    status_ok:       BooleanProperty = BooleanProperty(False)
    is_creating:     BooleanProperty = BooleanProperty(False)

    PIN_LENGTH: int = 4

    def on_enter(self) -> None:
        super().on_enter()
        self.welcome_message = "Espace Parent"
        self._reset_form()

    def _reset_form(self) -> None:
        self.ids.child_name_input.text = ""
        self.ids.child_pin_input.text  = ""
        self.status_message            = ""
        self.status_ok                 = False
        self.is_creating               = False

    # ── Création du profil enfant ──────────────────────────────────────────────
    def create_child_profile(self) -> None:
        prenom = self.ids.child_name_input.text.strip()
        pin    = self.ids.child_pin_input.text.strip()

        if not prenom:
            self._set_status("Veuillez saisir le prenom de l'enfant.", ok=False)
            return
        if not pin.isdigit() or len(pin) != self.PIN_LENGTH:
            self._set_status("Le code PIN doit contenir exactement 4 chiffres.", ok=False)
            return

        token = App.get_running_app().session_data.get("token", "")
        if not token:
            self._set_status("Session expiree. Veuillez vous reconnecter.", ok=False)
            return

        self.is_creating    = True
        self.status_message = ""
        threading.Thread(
            target=self._run_create_thread,
            args=(prenom, pin, token),
            daemon=True,
        ).start()

    def _run_create_thread(self, prenom: str, pin: str, token: str) -> None:
        try:
            success, message = run_async(create_child_profile_db(prenom, pin, token))
        except Exception as exc:
            success, message = False, str(exc)
        Clock.schedule_once(lambda dt: self._on_create_result(success, message), 0)

    def _on_create_result(self, success: bool, message: str) -> None:
        self.is_creating = False
        self._set_status(message, ok=success)
        if success:
            self.ids.child_name_input.text = ""
            self.ids.child_pin_input.text  = ""

    # ── Déconnexion asynchrone ─────────────────────────────────────────────────
    def logout(self) -> None:
        threading.Thread(target=self._run_logout_thread, daemon=True).start()

    def _run_logout_thread(self) -> None:
        try:
            run_async(logout_user())
        except Exception:
            pass
        Clock.schedule_once(lambda dt: self._on_logout_done(), 0)

    def _on_logout_done(self) -> None:
        self.manager.current = "login"

    # ── Verrouillage (Mode Enfant) ─────────────────────────────────────────────
    def lock_app(self) -> None:
        """Bascule vers le PinScreen sans déconnecter le parent."""
        self.manager.current = "pin"

    # ── Helper statut ──────────────────────────────────────────────────────────
    def _set_status(self, message: str, ok: bool) -> None:
        self.status_message = message
        self.status_ok      = ok
