import os
import json
from dotenv import load_dotenv
from supabase import create_client, Client

# Chargement des variables d'environnement (.env)
load_dotenv()

class DBManager:
    """
    Gestionnaire de la base de données Supabase pour le projet Alphabet Kids.
    """
    
    def __init__(self):
        # Récupération des secrets depuis le fichier .env
        self.url = os.getenv("SUPABASE_URL")
        self.key = os.getenv("SUPABASE_KEY")
        
        if not self.url or not self.key:
            print("⚠️ Erreur : SUPABASE_URL ou SUPABASE_KEY manquants dans le .env")
            self.client = None
        else:
            # Initialisation du client Supabase
            self.client: Client = create_client(self.url, self.key)
            print("✅ Client Supabase initialisé avec succès.")

    def get_educational_content(self, content_type: str = None):
        """
        Récupère le contenu pédagogique (lettres ou chiffres).
        :param content_type: Filtre optionnel ('letter' ou 'number')
        :return: Liste de dictionnaires contenant les données
        """
        if not self.client:
            return []

        try:
            # Construction de la requête
            query = self.client.table("educational_content").select("*").eq("is_active", True)
            
            # Filtre par type si spécifié
            if content_type:
                query = query.eq("type", content_type)
            
            # Exécution de la requête
            response = query.execute()
            
            # Tri intelligent : 
            # 1. Type ('letter' avant 'number')
            # 2. Contenu (numérique si possible, sinon alphabétique)
            def sort_key(x):
                t_val = 0 if x["type"] == "letter" else 1
                content = x["content"]
                try:
                    # Si c'est un nombre, on trie numériquement
                    return (t_val, int(content), content)
                except (ValueError, TypeError):
                    return (t_val, float('inf'), content)

            data = sorted(response.data, key=sort_key)
            
            return data
            
        except Exception as e:
            print(f"❌ Erreur lors de la récupération des données : {e}")
            return []

    def load_progress(self):
        """Charge le nombre total de découvertes depuis progress.json."""
        path = "progress.json"
        if not os.path.exists(path):
            return {"total_discovered": 0}
        
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ progress.json corrompu ou illisible, réinitialisation : {e}")
            self.save_progress(0)
            return {"total_discovered": 0}

    def save_progress(self, count):
        """Sauvegarde le nombre total de découvertes dans progress.json."""
        path = "progress.json"
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump({"total_discovered": count}, f, indent=4)
        except Exception as e:
            print(f"❌ Erreur sauvegarde progress.json : {e}")

# --- TEST RAPIDE (S'exécute uniquement si le fichier est lancé directement) ---
if __name__ == "__main__":
    manager = DBManager()
    content = manager.get_educational_content()
    print(f"Nombre d'éléments récupérés : {len(content)}")
    for item in content:
        print(f"- {item['content']} : {item['word']}")
