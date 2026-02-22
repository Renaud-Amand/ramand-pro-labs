import os
import sys
from dotenv import load_dotenv

# Ajout du chemin parent pour importer db_manager
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db_manager import DBManager

def deactivate_zero():
    manager = DBManager()
    if not manager.client:
        return

    print("🚫 Désactivation du chiffre '0'...")
    try:
        # On cherche l'ID du 0
        data = manager.client.table("educational_content")\
            .select("id")\
            .eq("content", "0")\
            .eq("type", "number")\
            .execute()
        
        if data.data:
            for item in data.data:
                print(f"🔄 Désactivation de l'ID: {item['id']}")
                res = manager.client.table("educational_content")\
                    .update({"is_active": False})\
                    .eq("id", item['id'])\
                    .execute()
                print(f"✅ Résultat: {len(res.data)} mis à jour.")
        else:
            print("ℹ️ Aucun chiffre '0' actif trouvé.")
            
    except Exception as e:
        print(f"❌ Erreur lors de la désactivation : {e}")

if __name__ == "__main__":
    deactivate_zero()
