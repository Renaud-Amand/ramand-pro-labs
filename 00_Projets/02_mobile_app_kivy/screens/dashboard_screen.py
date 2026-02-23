# -*- coding: utf-8 -*-
"""
screens/dashboard_screen.py

DashboardScreen: parent administration panel.
Features: child profile creation, child-mode lock, logout.
On entry it fetches the child's progress stats from Supabase via a
daemon thread and surfaces them through observable StringProperties.
"""

import threading

from kivy.app        import App
from kivy.clock      import Clock
from kivy.properties import StringProperty, BooleanProperty

from database              import run_async
from database.auth_manager import create_child_profile_db, logout_user
from screens.base_screen   import DysScreen


class DashboardScreen(DysScreen):
    """Parent dashboard — shows welcome info, child profile creation, lock/logout."""

    welcome_message: StringProperty  = StringProperty("Espace Parent")
    score_label:     StringProperty  = StringProperty("—")    # bound to KV
    sessions_label:  StringProperty  = StringProperty("—")    # bound to KV
    status_message:  StringProperty  = StringProperty("")
    status_ok:       BooleanProperty = BooleanProperty(False)
    is_creating:     BooleanProperty = BooleanProperty(False)

    PIN_LENGTH: int = 4

    # ── Lifecycle ──────────────────────────────────────────────────────────────
    def on_enter(self) -> None:
        """
        Called by Kivy when this screen becomes visible.

        Resets the child-profile form and launches a background thread
        to fetch the current user's progress stats from Supabase.
        """
        super().on_enter()
        self.welcome_message = "Espace Parent"
        self._reset_form()
        self._load_user_data_async()

    # ── Data loading ───────────────────────────────────────────────────────────
    def _load_user_data_async(self) -> None:
        """
        Spawn a daemon thread to call load_user_data() without blocking
        the Kivy main loop (Supabase calls are synchronous/blocking).
        """
        app    = App.get_running_app()
        prenom = app.user_prenom

        if not prenom:
            # No authenticated user yet — nothing to fetch.
            return

        threading.Thread(
            target=self._run_load_user_data_thread,
            args=(prenom, app),
            daemon=True,
        ).start()

    def _run_load_user_data_thread(self, prenom: str, app: "App") -> None:
        """
        Background thread: calls load_user_data() which performs the
        Supabase query and populates app.user_data in-place.
        Schedules the UI refresh on the main thread via Clock.
        """
        from main import load_user_data  # local import — avoids circular dependency

        try:
            load_user_data(prenom, app)
        except Exception:  # noqa: BLE001
            pass  # load_user_data already provides offline-first defaults

        Clock.schedule_once(lambda dt: self._on_user_data_loaded(), 0)

    def _on_user_data_loaded(self) -> None:
        """
        Main-thread callback: reads app.user_data and updates all bound
        StringProperties so the KV layer re-renders automatically.
        """
        data   = App.get_running_app().user_data
        prenom = data.get("prenom", "")

        self.welcome_message = f"Bonjour, {prenom} !" if prenom else "Espace Parent"
        self.score_label     = str(data.get("score_total", 0))
        self.sessions_label  = str(data.get("sessions", 0))

    # ── Helpers ────────────────────────────────────────────────────────────────
    def _reset_form(self) -> None:
        self.ids.child_name_input.text = ""
        self.ids.child_pin_input.text  = ""
        self.status_message            = ""
        self.status_ok                 = False
        self.is_creating               = False

    def _set_status(self, message: str, ok: bool) -> None:
        self.status_message = message
        self.status_ok      = ok

    # ── Child profile creation ─────────────────────────────────────────────────
    def create_child_profile(self) -> None:
        prenom = self.ids.child_name_input.text.strip()
        pin    = self.ids.child_pin_input.text.strip()

        if not prenom:
            self._set_status("Veuillez saisir le prénom de l'enfant.", ok=False)
            return
        if not pin.isdigit() or len(pin) != self.PIN_LENGTH:
            self._set_status("Le code PIN doit contenir exactement 4 chiffres.", ok=False)
            return

        token = App.get_running_app().session_data.get("token", "")
        if not token:
            self._set_status("Session expirée. Veuillez vous reconnecter.", ok=False)
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
        except Exception as exc:  # noqa: BLE001
            success, message = False, str(exc)
        Clock.schedule_once(lambda dt: self._on_create_result(success, message), 0)

    def _on_create_result(self, success: bool, message: str) -> None:
        self.is_creating = False
        self._set_status(message, ok=success)
        if success:
            self.ids.child_name_input.text = ""
            self.ids.child_pin_input.text  = ""

    # ── Logout ─────────────────────────────────────────────────────────────────
    def logout(self) -> None:
        threading.Thread(target=self._run_logout_thread, daemon=True).start()

    def _run_logout_thread(self) -> None:
        try:
            run_async(logout_user())
        except Exception:  # noqa: BLE001
            pass
        Clock.schedule_once(lambda dt: self._on_logout_done(), 0)

    def _on_logout_done(self) -> None:
        App.get_running_app().user_prenom = ""
        App.get_running_app().user_data   = {}
        self.manager.current = "login"

    # ── Child-mode lock ────────────────────────────────────────────────────────
    def lock_app(self) -> None:
        """Switch to PinScreen without disconnecting the parent."""
        self.manager.current = "pin"
