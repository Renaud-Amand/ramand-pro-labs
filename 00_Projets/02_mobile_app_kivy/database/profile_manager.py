import hashlib
import secrets
import hmac
# On importe le gestionnaire existant pour récupérer le client Supabase
from database import auth_manager 

class ProfileManager:
    @staticmethod
    def hash_pin(pin_raw):
        """Generates a secure SHA-256 hash with a unique hex salt."""
        pin_salt = secrets.token_hex(16)
        # Salt + Pin is the industry standard for concatenation
        hash_input = (pin_salt + pin_raw).encode()
        pin_hash = hashlib.sha256(hash_input).hexdigest()
        return pin_hash, pin_salt

    @staticmethod
    def verify_pin(pin_raw, stored_hash, stored_salt):
        """Time-attack resistant PIN verification."""
        hash_input = (stored_salt + pin_raw).encode()
        current_hash = hashlib.sha256(hash_input).hexdigest()
        return hmac.compare_digest(stored_hash, current_hash)

    @staticmethod
    def create_child_profile(prenom, age, pin_raw, avatar_config, dys_settings):
        """Hashes PIN and inserts a new child profile linked to the current parent user."""
        supabase = auth_manager.get_supabase_client()
        
        # 1. Hachage du PIN
        pin_hash, pin_salt = ProfileManager.hash_pin(pin_raw)
        
        # 2. Récupération de l'ID du parent (Session actuelle)
        # Assure-toi que l'utilisateur est bien loggé
        user = supabase.auth.get_user()
        if not user:
            return False, "User not authenticated"
        
        # 3. Préparation des données
        data = {
            'user_id': user.user.id, # Lien crucial vers le compte parent
            'prenom': prenom,
            'age': age,
            'pin_hash': pin_hash,
            'pin_salt': pin_salt,
            'avatar_config': avatar_config,
            'dys_settings': dys_settings
        }
        
        # 4. Insertion
        try:
            response = supabase.from_('child_profiles').insert(data).execute()
            return True, "Profile created successfully"
        except Exception as e:
            return False, str(e)