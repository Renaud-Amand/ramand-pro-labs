# -*- coding: utf-8 -*-
"""
database/auth_manager.py

Authentication helpers for the Dys-Pédagogie mobile app.

All Supabase access goes through the shared ``db_manager`` singleton
from ``database.supabase_client``.  Every public function includes an
offline guard so the app degrades gracefully when the network or the
``.env`` file is unavailable.
"""

import logging
import sys

from kivy.storage.jsonstore import JsonStore

# Singleton Supabase client — single source of truth
from database.supabase_client import db_manager

# Security: PIN hashing/verification is delegated to ProfileManager (Sprint 0)
from database.profile_manager import ProfileManager

# ---------------------------------------------------------------------------
# UTF-8 stdout — required on Windows to avoid UnicodeEncodeError
# ---------------------------------------------------------------------------
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Local session store (offline-first)
# ---------------------------------------------------------------------------
store = JsonStore("session.json")

# ---------------------------------------------------------------------------
# Offline-mode sentinel
# ---------------------------------------------------------------------------
_OFFLINE_MSG = "Mode hors-ligne : action impossible sans connexion."


def _require_online() -> bool:
    """Return ``True`` when the Supabase client is available."""
    return db_manager.is_online


# ===================================================================
# Public API
# ===================================================================


async def login_user(
    email: str,
    password: str,
) -> tuple[bool, str, dict]:
    """Authenticate a parent via Supabase and persist the token locally."""
    if not _require_online():
        return False, _OFFLINE_MSG, {}

    try:
        response = db_manager.client.auth.sign_in_with_password(
            {"email": email, "password": password}
        )

        if response.user:
            store.put("session", token=response.session.access_token)
            return True, "Connexion réussie", {
                "token": response.session.access_token,
            }

        return False, "Erreur de connexion inconnue", {}

    except Exception as exc:  # noqa: BLE001
        logger.error("login_user failed: %s", exc)
        return False, f"Erreur : {exc}", {}


async def check_local_session() -> bool:
    """Return ``True`` if a session token exists in local storage."""
    return store.exists("session")


async def logout_user() -> tuple[bool, str]:
    """Sign out from Supabase and clear the local session."""
    if not _require_online():
        # Still clear local data even if offline
        if store.exists("session"):
            store.delete("session")
        return True, "Session locale supprimée (hors-ligne)."

    try:
        db_manager.client.auth.sign_out()
        if store.exists("session"):
            store.delete("session")
        return True, "Déconnexion réussie"

    except Exception as exc:  # noqa: BLE001
        logger.error("logout_user failed: %s", exc)
        return False, f"Erreur lors de la déconnexion : {exc}"


async def create_child_profile_db(
    prenom: str,
    pin_raw: str,
    access_token: str,
) -> tuple[bool, str]:
    """Insert a child profile into Supabase with a securely hashed PIN.

    Steps
    -----
    1. Retrieve parent UUID from *access_token* via ``get_user()``.
    2. Hash the raw PIN using ``ProfileManager.hash_pin()``
       (SHA-256 + unique salt).
    3. Insert ``{user_id, prenom, pin_hash, pin_salt}`` — NEVER the raw PIN.
    """
    if not _require_online():
        return False, _OFFLINE_MSG

    try:
        user_response = db_manager.client.auth.get_user(access_token)
        if not user_response or not user_response.user:
            return False, "Impossible de récupérer l'utilisateur connecté."

        user_id = user_response.user.id

        pin_hash, pin_salt = ProfileManager.hash_pin(pin_raw.strip())

        result = (
            db_manager.client
            .table("child_profiles")
            .insert({
                "user_id":  user_id,
                "prenom":   prenom.strip().capitalize(),
                "pin_hash": pin_hash,
                "pin_salt": pin_salt,
            })
            .execute()
        )

        if result.data:
            return True, f"Profil de {prenom.capitalize()} créé avec succès !"

        return False, "Insertion échouée : aucune donnée retournée."

    except Exception as exc:  # noqa: BLE001
        logger.error("create_child_profile_db failed: %s", exc)
        return False, f"Erreur Supabase : {exc}"


async def verify_child_pin_db(
    pin_raw: str,
) -> tuple[bool, str, dict]:
    """Verify a child PIN using secure constant-time comparison.

    Steps
    -----
    1. Read access token from local ``JsonStore`` (``session.json``).
    2. Set Supabase session with this token (respects RLS).
    3. Fetch ALL child profiles for this parent (``pin_hash`` + ``pin_salt``).
    4. Delegate comparison to ``ProfileManager.verify_pin()`` — constant-time
       via ``hmac.compare_digest`` to prevent timing attacks.
    """
    if not _require_online():
        return False, _OFFLINE_MSG, {}

    try:
        if not store.exists("session"):
            return False, "Session expirée. Reconnectez-vous.", {}

        token = store.get("session").get("token", "")
        if not token:
            return False, "Token invalide. Reconnectez-vous.", {}

        db_manager.client.auth.set_session(token, "")

        result = (
            db_manager.client
            .table("child_profiles")
            .select("id, prenom, pin_hash, pin_salt")
            .execute()
        )

        if result.data:
            for child in result.data:
                stored_hash = child.get("pin_hash", "")
                stored_salt = child.get("pin_salt", "")
                if stored_hash and stored_salt and ProfileManager.verify_pin(
                    pin_raw.strip(), stored_hash, stored_salt,
                ):
                    return (
                        True,
                        f"Bonjour {child.get('prenom', '')} !",
                        child,
                    )

        return False, "Code PIN incorrect.", {}

    except Exception as exc:  # noqa: BLE001
        logger.error("verify_child_pin_db failed: %s", exc)
        return False, f"Erreur vérification PIN : {exc}", {}
