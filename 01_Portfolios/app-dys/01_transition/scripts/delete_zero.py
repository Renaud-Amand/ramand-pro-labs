import os
import sys
from dotenv import load_dotenv

# Ajout du chemin parent pour importer db_manager
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db_manager import DBManager

def delete_zero():
    manager = DBManager()
    if not manager.client:
        print("❌ Erreur : Impossible d'initialiser le client Supabase.")
        return

    print("🗑️ Suppression du chiffre '0'...")
    try:
        response = manager.client.table("educational_content")\
            .delete()\
            .eq("content", "0")\
            .eq("type", "number")\
            .execute()
        print(f"✅ Supprimé : {len(response.data)} ligne(s).")
    except Exception as e:
        print(f"❌ Erreur lors de la suppression : {e}")

if __name__ == "__main__":
    delete_zero()
