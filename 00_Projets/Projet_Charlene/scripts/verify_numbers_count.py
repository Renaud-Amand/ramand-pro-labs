import os
import sys
from dotenv import load_dotenv

# Ajout du chemin parent pour importer db_manager
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db_manager import DBManager

def verify_count():
    manager = DBManager()
    if not manager.client:
        print("❌ Erreur : Impossible d'initialiser le client Supabase.")
        return

    data = manager.get_educational_content(content_type="number")
    print(f"📊 Nombre de chiffres trouvés : {len(data)}")
    
    # Tri numérique pour la vérification visuelle
    sorted_data = sorted(data, key=lambda x: int(x['content']) if x['content'].isdigit() else 999)
    
    for d in sorted_data:
        print(f" - {d}")

    # Vérification du mélange dans main.py simulé
    import random
    session_data = list(data)
    random.shuffle(session_data)
    print(f"🎲 Exemple de mélange (3 premiers) : {[d['content'] for d in session_data[:3]]}")

if __name__ == "__main__":
    verify_count()
