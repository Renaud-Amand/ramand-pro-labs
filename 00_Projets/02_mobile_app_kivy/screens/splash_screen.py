# -*- coding: utf-8 -*-
"""
screens/splash_screen.py

SplashScreen : écran de démarrage avec animation de progression.
Redirige automatiquement vers PinScreen (session active) ou LoginScreen (pas de session).
"""

import threading

from kivy.clock import Clock

from database          import run_async
from database.auth_manager import check_local_session
from screens.base_screen   import DysScreen


class SplashScreen(DysScreen):
    name: str = "splash"
    SPLASH_DURATION: float = 3.0

    def on_enter(self) -> None:
        super().on_enter()
        self._progress_step  = 0.0
        self._clock_progress = Clock.schedule_interval(
            self._animate_progress, self.SPLASH_DURATION / 100
        )
        Clock.schedule_once(self._start_routing, self.SPLASH_DURATION)

    def _animate_progress(self, dt: float) -> None:
        bar = self.ids.get("progress_bar")
        if bar:
            self._progress_step = min(self._progress_step + 1, 100)
            bar.value = self._progress_step

    def _start_routing(self, dt: float) -> None:
        """Lance le check de session dans un thread pour ne pas bloquer l'UI."""
        if self._clock_progress:
            self._clock_progress.cancel()
        threading.Thread(
            target=self._check_session_thread,
            daemon=True,
        ).start()

    def _check_session_thread(self) -> None:
        try:
            has_session = run_async(check_local_session())
        except Exception:
            has_session = False

        target = "pin" if has_session else "login"
        Clock.schedule_once(lambda dt: setattr(self.manager, "current", target), 0)

    def on_leave(self) -> None:
        super().on_leave()
        if hasattr(self, "_clock_progress") and self._clock_progress:
            self._clock_progress.cancel()
