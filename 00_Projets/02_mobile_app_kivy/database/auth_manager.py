import asyncio
import os
from supabase import create_client, Client
from kivy.storage.jsonstore import JsonStore
from dotenv import load_dotenv

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
    pin_code: str,
    access_token: str,
) -> tuple[bool, str]:
    """
    Insère un profil enfant dans la table child_profiles de Supabase.

    Étapes :
        1. Récupère l'UUID du parent connecté via get_user(access_token).
        2. Insère une ligne {user_id, prenom, pin_code} dans child_profiles.

    Returns:
        (True,  message_succès)  si l'insertion réussit.
        (False, message_erreur)  en cas d'erreur.
    """
    try:
        # Récupération de l'UUID du parent à partir du token de session
        user_response = supabase.auth.get_user(access_token)
        if not user_response or not user_response.user:
            return False, "Impossible de recuperer l'utilisateur connecte."

        user_id = user_response.user.id

        # Insertion dans la table child_profiles
        result = (
            supabase
            .table("child_profiles")
            .insert({
                "user_id":  user_id,
                "prenom":   prenom.strip().capitalize(),
                "pin_code": pin_code.strip(),
            })
            .execute()
        )

        # supabase-py v2 lève une exception si l'insertion échoue,
        # mais on vérifie aussi que data est non vide par sécurité.
        if result.data:
            return True, f"Profil de {prenom.capitalize()} cree avec succes !"
        else:
            return False, "Insertion echouee : aucune donnee retournee."

    except Exception as e:
        return False, f"Erreur Supabase : {str(e)}"


async def verify_child_pin_db(pin_code: str) -> tuple[bool, str, dict]:
    """
    Vérifie un code PIN enfant en interrogeant la table child_profiles.

    Étapes :
        1. Lit le token d'accès depuis le JsonStore local (session.json).
        2. Configure la session Supabase avec ce token.
        3. Recherche le PIN dans child_profiles.

    Returns:
        (True,  "Accès autorisé",    {"id": ..., "prenom": ...})  si PIN correct.
        (False, "Code PIN incorrect", {})                          si PIN inconnu.
        (False, "Session expirée…",  {})                          si pas de token local.
    """
    try:
        # Lecture du token stocké localement
        if not store.exists("session"):
            return False, "Session expiree. Reconnectez-vous.", {}

        token = store.get("session").get("token", "")
        if not token:
            return False, "Token invalide. Reconnectez-vous.", {}

        # Configuration de la session Supabase avec le token parent
        # (évite les erreurs RLS si Row Level Security est activée)
        supabase.auth.set_session(token, "")

        # Recherche du PIN dans child_profiles
        result = (
            supabase
            .table("child_profiles")
            .select("id, prenom, pin_code")
            .eq("pin_code", pin_code.strip())
            .execute()
        )

        if result.data:
            child = result.data[0]
            return True, f"Bonjour {child.get('prenom', '')} !", child
        else:
            return False, "Code PIN incorrect.", {}

    except Exception as e:
        return False, f"Erreur verification PIN : {str(e)}", {}

