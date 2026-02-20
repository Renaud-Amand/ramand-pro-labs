import os
import sys
from dotenv import load_dotenv

# Ajout du chemin parent pour importer db_manager
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db_manager import DBManager

def populate_numbers():
    manager = DBManager()
    if not manager.client:
        print("❌ Erreur : Impossible d'initialiser le client Supabase.")
        return

    numbers_data = [
        ("1", "un"), ("2", "deux"), ("3", "trois"), ("4", "quatre"), ("5", "cinq"),
        ("6", "six"), ("7", "sept"), ("8", "huit"), ("9", "neuf"), ("10", "dix"),
        ("11", "onze"), ("12", "douze"), ("13", "treize"), ("14", "quatorze"), ("15", "quinze"),
        ("16", "seize"), ("17", "dix-sept"), ("18", "dix-huit"), ("19", "dix-neuf"), ("20", "vingt"),
        ("21", "vingt et un"), ("22", "vingt-deux"), ("23", "vingt-trois"), ("24", "vingt-quatre"), ("25", "vingt-cinq"),
        ("26", "vingt-six"), ("27", "vingt-sept"), ("28", "vingt-huit"), ("29", "vingt-neuf"), ("30", "trente")
    ]

    print(f"🚀 Insertion de {len(numbers_data)} nombres dans Supabase...")

    for char, word in numbers_data:
        data = {
            "content": char,
            "type": "number",
            "word": word,
            "image_url": None,
            "sound_url": f"assets/sounds/chiffre_{char}.mp3",
            "is_active": True
        }
        
        try:
            # On utilise upsert sur content + type si possible, 
            # mais ici on va juste faire un insert simple ou vérifier si ça existe déjà.
            # Pour éviter les doublons si on relance le script :
            existing = manager.client.table("educational_content")\
                .select("id")\
                .eq("content", char)\
                .eq("type", "number")\
                .execute()
            
            if existing.data:
                print(f"➖ {char} existe déjà, mise à jour...")
                manager.client.table("educational_content")\
                    .update(data)\
                    .eq("content", char)\
                    .eq("type", "number")\
                    .execute()
            else:
                print(f"➕ Insertion de {char} ({word})...")
                manager.client.table("educational_content").insert(data).execute()
                
        except Exception as e:
            print(f"❌ Erreur pour {char} : {e}")

    print("✅ Opération terminée.")

if __name__ == "__main__":
    populate_numbers()
