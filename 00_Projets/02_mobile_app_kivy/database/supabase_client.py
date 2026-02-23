# -*- coding: utf-8 -*-
"""
database/supabase_client.py

Supabase client initialisation for the Dys-Pédagogie mobile app.

Provides a thread-safe Singleton ``SupabaseManager`` that:
- Loads credentials from a ``.env`` file via ``python-dotenv``.
- Exposes only the ``ANON_KEY`` / ``SUPABASE_URL`` (Zero-Trust rule).
- Degrades gracefully to *offline mode* when the ``.env`` file is
  missing, credentials are incomplete, or the Supabase SDK raises
  during import / initialisation.

Usage::

    from database.supabase_client import db_manager

    if db_manager.is_online:
        result = db_manager.client.table("users").select("*").execute()
    else:
        # Fall back to local JSON cache
        ...
"""

import logging
import os
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# UTF-8 stdout — required on Windows to avoid UnicodeEncodeError
# ---------------------------------------------------------------------------
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Resolve project root and .env path
# ---------------------------------------------------------------------------
# BASE_DIR  →  .../00_Projets/02_mobile_app_kivy/database/
# ROOT_DIR  →  .../00_Projets/   (where .env lives)
BASE_DIR: Path = Path(os.path.dirname(os.path.abspath(__file__)))
ROOT_DIR: Path = BASE_DIR.parents[1]  # two levels up from database/
ENV_PATH: Path = ROOT_DIR / ".env"


class SupabaseManager:
    """
    Singleton wrapper around the Supabase ``Client``.

    Attributes
    ----------
    is_online : bool
        ``True`` when the Supabase client was successfully initialised.
        ``False`` when the app is running in offline / degraded mode.
    client : supabase.Client | None
        The authenticated Supabase client, or ``None`` in offline mode.
    """

    _instance: "SupabaseManager | None" = None

    # ------------------------------------------------------------------
    # Singleton enforcement
    # ------------------------------------------------------------------
    def __new__(cls) -> "SupabaseManager":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialised = False
        return cls._instance

    # ------------------------------------------------------------------
    # Public initialisation
    # ------------------------------------------------------------------
    def initialise(self) -> None:
        """
        Load credentials and create the Supabase client.

        This method is idempotent: calling it more than once is a no-op.
        It NEVER raises; any failure silently activates offline mode and
        logs a warning so the application can keep running.
        """
        if self._initialised:
            return

        self.client = None
        self.is_online = False
        self._initialised = True

        # --- Step 1: load .env --------------------------------------------
        try:
            from dotenv import load_dotenv  # type: ignore[import]
        except ImportError:
            logger.warning(
                "python-dotenv is not installed. "
                "Running in offline mode."
            )
            return

        if not ENV_PATH.exists():
            logger.warning(
                ".env file not found at '%s'. "
                "Running in offline mode.",
                ENV_PATH,
            )
            return

        load_dotenv(dotenv_path=ENV_PATH)

        # --- Step 2: read credentials (Zero-Trust: ANON_KEY only) --------
        supabase_url: str | None = os.getenv("SUPABASE_URL")
        supabase_key: str | None = os.getenv("SUPABASE_KEY")  # ANON_KEY

        if not supabase_url or not supabase_key:
            logger.warning(
                "SUPABASE_URL or SUPABASE_KEY is missing from '%s'. "
                "Running in offline mode.",
                ENV_PATH,
            )
            return

        # --- Step 3: create client ----------------------------------------
        try:
            from supabase import create_client, Client  # type: ignore[import]

            self.client: Client = create_client(supabase_url, supabase_key)
            self.is_online = True
            logger.info("Supabase client initialised successfully.")

        except Exception as exc:  # noqa: BLE001
            logger.warning(
                "Supabase client creation failed (%s). "
                "Running in offline mode.",
                exc,
            )

    # ------------------------------------------------------------------
    # Convenience helpers
    # ------------------------------------------------------------------
    def __repr__(self) -> str:
        status = "online" if self.is_online else "offline"
        return f"<SupabaseManager [{status}]>"


# ---------------------------------------------------------------------------
# Module-level Singleton — import and use directly:
#   from database.supabase_client import db_manager
# ---------------------------------------------------------------------------
db_manager = SupabaseManager()
db_manager.initialise()
