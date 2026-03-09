import os
import sys
from dotenv import load_dotenv

# Ajout du chemin parent pour importer db_manager
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db_manager import DBManager

def list_letters():
    manager = DBManager()
    data = manager.get_educational_content(content_type="letter")
    if data:
        # Trier par contenu (A-Z)
        data.sort(key=lambda x: x.get('content', ''))
        for item in data:
            print(f"{item.get('content')} : {item.get('word')}")
    else:
        print("Aucune donnée trouvée.")

if __name__ == "__main__":
    list_letters()
