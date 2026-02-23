import asyncio
import os
import sys
from supabase import create_client, Client
from kivy.storage.jsonstore import JsonStore
from dotenv import load_dotenv

# Security: PIN hashing/verification is delegated to ProfileManager (Sprint 0)
from database.profile_manager import ProfileManager

# Enforce UTF-8 output to prevent UnicodeEncodeError on Windows
sys.stdout.reconfigure(encoding='utf-8')

# Charge le fichier .env qui se trouve à la racine de ton projet
load_dotenv()

# Initialisation de Supabase
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

if not url or not key:
    raise ValueError("Les clés Supabase sont introuvables. Vérifie ton fichier .env à la racine.")

supabase: Client = create_client(url, key)

# Initialisation du stockage local (Offline-first)
store = JsonStore('session.json')

async def login_user(email: str, password: str) -> tuple[bool, str, dict]:
    """Tente de connecter l'utilisateur via Supabase et sauvegarde le token en local."""
    try:
        response = supabase.auth.sign_in_with_password({"email": email, "password": password})
        
        if response.user:
            store.put('session', token=response.session.access_token)
            return True, "Connexion réussie", {"token": response.session.access_token}
        else:
            return False, "Erreur de connexion inconnue", {}
            
    except Exception as e:
        return False, f"Erreur : {str(e)}", {}

async def check_local_session() -> bool:
    """Vérifie si une session est déjà active en local."""
    return store.exists('session')

async def logout_user() -> tuple[bool, str]:
    """Déconnecte l'utilisateur et nettoie le stockage local."""
    try:
        supabase.auth.sign_out()
        if store.exists('session'):
            store.delete('session')
        return True, "Déconnexion réussie"
    except Exception as e:
        return False, f"Erreur lors de la déconnexion : {str(e)}"


async def create_child_profile_db(
    prenom: str,
    pin_raw: str,
    access_token: str,
) -> tuple[bool, str]:
    """
    Inserts a child profile into Supabase with a securely hashed PIN.

    Steps:
        1. Retrieve parent UUID from access_token via get_user().
        2. Hash the raw PIN using ProfileManager.hash_pin() (SHA-256 + unique salt).
        3. Insert {user_id, prenom, pin_hash, pin_salt} — NEVER the raw PIN.

    Returns:
        (True,  success_message)  on successful insert.
        (False, error_message)    on any failure.
    """
    try:
        # Step 1: Retrieve authenticated parent UUID
        user_response = supabase.auth.get_user(access_token)
        if not user_response or not user_response.user:
            return False, "Impossible de recuperer l'utilisateur connecte."

        user_id = user_response.user.id

        # Step 2: Hash the PIN — plaintext is NEVER stored (COPPA/RGPD compliance)
        pin_hash, pin_salt = ProfileManager.hash_pin(pin_raw.strip())

        # Step 3: Insert hashed credentials only
        result = (
            supabase
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
            return True, f"Profil de {prenom.capitalize()} cree avec succes !"
        else:
            return False, "Insertion echouee : aucune donnee retournee."

    except Exception as e:
        return False, f"Erreur Supabase : {str(e)}"


async def verify_child_pin_db(pin_raw: str) -> tuple[bool, str, dict]:
    """
    Verifies a child PIN using secure constant-time comparison.

    Steps:
        1. Read access token from local JsonStore (session.json).
        2. Set Supabase session with this token (respects RLS).
        3. Fetch ALL child profiles for this parent (pin_hash + pin_salt).
        4. Delegate comparison to ProfileManager.verify_pin() — constant-time
           via hmac.compare_digest to prevent timing attacks.

    Returns:
        (True,  "Bonjour {prenom} !", child_dict)  if PIN matches.
        (False, "Code PIN incorrect", {})           if no match.
        (False, "Session expiree…",  {})            if no local token.
    """
    try:
        # Step 1: Read local session token
        if not store.exists("session"):
            return False, "Session expiree. Reconnectez-vous.", {}

        token = store.get("session").get("token", "")
        if not token:
            return False, "Token invalide. Reconnectez-vous.", {}

        # Step 2: Set Supabase session (required for RLS enforcement)
        supabase.auth.set_session(token, "")

        # Step 3: Fetch hash + salt for all children — do NOT query by plaintext PIN
        result = (
            supabase
            .table("child_profiles")
            .select("id, prenom, pin_hash, pin_salt")
            .execute()
        )

        # Step 4: Constant-time comparison via ProfileManager (prevents timing attacks)
        if result.data:
            for child in result.data:
                stored_hash = child.get("pin_hash", "")
                stored_salt = child.get("pin_salt", "")
                if stored_hash and stored_salt and ProfileManager.verify_pin(
                    pin_raw.strip(), stored_hash, stored_salt
                ):
                    return True, f"Bonjour {child.get('prenom', '')} !", child

        return False, "Code PIN incorrect.", {}

    except Exception as e:
        return False, f"Erreur verification PIN : {str(e)}", {}

