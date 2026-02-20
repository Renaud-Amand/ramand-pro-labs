import os
import json
from json import JSONDecodeError
from dotenv import load_dotenv
from supabase import create_client, Client

# Chargement des variables d'environnement (.env)
load_dotenv()

class DBManager:
    """
    Gestionnaire de la base de données Supabase pour le projet Alphabet Kids.
    """
    
    def __init__(self):
        # État global du service ('online', 'offline', 'critical')
        self.status = 'offline'
        self.is_online = False
        
        # Vérification préventive du fichier .env
        if not os.path.exists(".env"):
            print("❌ ERREUR CRITIQUE : Fichier .env manquant !")
            print("Veuillez créer un fichier .env avec SUPABASE_URL et SUPABASE_KEY.")
            self.client = None
            self.status = 'critical'
            return

        # Récupération des secrets depuis le fichier .env
        self.url = os.getenv("SUPABASE_URL")
        self.key = os.getenv("SUPABASE_KEY")
        
        if not self.url or not self.key:
            print("⚠️ Erreur : SUPABASE_URL ou SUPABASE_KEY vides ou incorrects dans le .env.")
            self.client = None
            self.is_online = False
            self.status = 'critical'
        else:
            try:
                # Initialisation du client Supabase
                self.client: Client = create_client(self.url, self.key)
                self.is_online = True
                self.status = 'online'
                print("✅ Client Supabase connecté avec succès.")
            except Exception as e:
                print(f"❌ Impossible de se connecter à Supabase : {e}")
                self.client = None
                self.is_online = False
                self.status = 'offline'


    def get_educational_content(self, content_type: str = None):
        """
        Récupère le contenu pédagogique (lettres ou chiffres).
        Priorité : Supabase (Cloud) puis Backup (Local) si hors-ligne.
        :param content_type: Filtre optionnel ('letter' ou 'number')
        :return: Liste de dictionnaires contenant les données
        """
        data = []
        supabase_success = False

        # 1. Tentative TOUJOURS avec Supabase en premier
        if self.client:
            try:
                # Construction de la requête
                query = self.client.table("educational_content").select("*").eq("is_active", True)
                
                # Filtre par type si spécifié
                if content_type:
                    query = query.eq("type", content_type)
                
                # Exécution de la requête
                query = query.execute()
                data = query.data
                supabase_success = True
                self.is_online = True
                self.status = 'online'
                print(f"✅ Données récupérées avec succès depuis Supabase ({len(data)} éléments).")
            except Exception as e:
                self.is_online = False
                self.status = 'offline'
                print(f"⚠️ Échec de la connexion Supabase : {e}")
                print("🔄 Passage en mode fallback (secours)...")
        else:
            self.is_online = False
            self.status = 'offline'
            print("⚠️ Client Supabase non initialisé. Passage en mode fallback...")


        # 2. Fallback sur le backup local si Supabase échoue (uniquement pour les lettres)
        if not supabase_success:
            if content_type == "letter" or content_type is None:
                backup_path = "backup_list.json"
                if os.path.exists(backup_path):
                    try:
                        with open(backup_path, "r", encoding="utf-8") as f:
                            data = json.load(f)
                        # Si on a demandé 'None' (tout), on ne garde que les lettres du backup
                        # car le backup ne contient que ça.
                        if content_type is None:
                            data = [item for item in data if item.get("type") == "letter"]
                        
                        self.status = 'offline'
                        print(f"✅ Mode secours activé : {len(data)} lettres chargées depuis {backup_path}.")
                    except JSONDecodeError as e:
                        self.status = 'critical'
                        print(f"❌ ERREUR FORMAT : Le fichier backup est corrompu (JSON invalide) : {e}")
                    except Exception as e:
                        self.status = 'critical'
                        print(f"❌ ERREUR LECTURE : Impossible d'accéder au backup : {e}")
                else:
                    self.status = 'critical'
                    print(f"❌ ERREUR CRITIQUE : Fichier de backup {backup_path} introuvable.")
            else:
                # Si c'est pour des chiffres et que Supabase échoue, on n'a pas de backup pour ça.
                print("❌ ERREUR : Pas de mode fallback disponible pour ce type de contenu.")
                return []

        # 3. Tri des données (commun aux deux sources)
        try:
            def sort_key(x):
                # Gestion sécurisée du type
                c_type = x.get("type", "letter")
                t_val = 0 if c_type == "letter" else 1
                content = x.get("content", "")
                try:
                    # Si c'est un nombre, on trie numériquement
                    return (t_val, int(content), content)
                except (ValueError, TypeError):
                    return (t_val, float('inf'), content)

            sorted_data = sorted(data, key=sort_key)
            return sorted_data
        except Exception as e:
            print(f"⚠️ Erreur lors du tri des données : {e}")
            return data


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
