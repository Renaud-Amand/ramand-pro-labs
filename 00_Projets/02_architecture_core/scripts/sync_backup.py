import os
import json
import sys
from dotenv import load_dotenv
from supabase import create_client, Client

# Chargement des variables d'environnement
load_dotenv()

def sync_letters():
    """
    Récupère les lettres depuis Supabase et les sauvegarde localement pour le mode hors-ligne.
    """
    print("--- Démarrage de la synchronisation du backup ---")
    
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    
    if not url or not key:
        print("❌ ERREUR : SUPABASE_URL ou SUPABASE_KEY manquante dans le .env")
        sys.exit(1)

    try:
        # Initialisation du client
        supabase: Client = create_client(url, key)
        
        # Récupération des lettres
        print("Récupération des lettres depuis Supabase...")
        response = supabase.table("educational_content")\
            .select("content, word, image_url, sound_url, type")\
            .eq("type", "letter")\
            .eq("is_active", True)\
            .execute()

        
        letters = response.data
        
        # Sécurité critique : Vérifier la longueur
        letter_count = len(letters)
        print(f"Nombre de lettres reçues : {letter_count}")
        
        if letter_count < 26:
            print(f"❌ ERREUR CRITIQUE : Seules {letter_count} lettres ont été récupérées (26 minimum attendues).")
            print("Arrêt du script pour éviter de corrompre le backup local.")
            sys.exit(1)
            
        # Sauvegarde dans backup_list.json à la racine
        backup_path = os.path.join(os.path.dirname(__file__), "..", "backup_list.json")
        backup_path = os.path.abspath(backup_path)
        
        print(f"Sauvegarde de {letter_count} lettres dans {backup_path}...")
        with open(backup_path, "w", encoding="utf-8") as f:
            json.dump(letters, f, indent=4, ensure_ascii=False)
            
        print("✅ Synchronisation réussie !")
        
    except Exception as e:
        print(f"❌ ERREUR lors de la synchronisation : {e}")
        sys.exit(1)

if __name__ == "__main__":
    sync_letters()
