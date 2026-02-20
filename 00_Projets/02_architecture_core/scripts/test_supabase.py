from db_manager import DBManager

def test_connection():
    print("--- Test de récupération 'A' depuis Supabase ---")
    manager = DBManager()
    
    if not manager.client:
        print("❌ Erreur : Le client Supabase n'a pas pu être initialisé.")
        return

    print("\nLecture de la table 'educational_content'...")
    data = manager.get_educational_content()
    
    if not data:
        print("⚠️ Aucune donnée reçue. Vérifiez que la table n'est pas vide et que 'is_active' est à TRUE.")
    else:
        print(f"✅ {len(data)} ligne(s) trouvée(s).")
        for item in data:
            if item['content'] == 'A':
                print(f"🌟 Succès ! Lettre trouvée : {item['content']} (Mot: {item['word']})")
                print(f"   Image: {item['image_url']}")
                print(f"   Son: {item['sound_url']}")
            else:
                print(f" - Autre ligne trouvée : {item['content']}")

if __name__ == "__main__":
    test_connection()
