import os
import sys
from dotenv import load_dotenv

# Ajout du chemin parent pour importer db_manager
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db_manager import DBManager

def cleanup():
    manager = DBManager()
    if not manager.client:
        return

    data = manager.get_educational_content(content_type="number")
    for d in data:
        if d['content'] == "0":
            print(f"🗑️ Trouvé '0' avec ID: {d['id']}")
            res = manager.client.table("educational_content").delete().eq("id", d['id']).execute()
            print(f"✅ Résultat: {len(res.data)} supprimé.")
            break
    else:
        print("ℹ️ Aucun '0' trouvé dans Content.")

if __name__ == "__main__":
    cleanup()
