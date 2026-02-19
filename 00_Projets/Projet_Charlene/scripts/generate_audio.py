import os
import sys
from gtts import gTTS
from dotenv import load_dotenv

# Ajout du chemin parent pour importer db_manager
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db_manager import DBManager

def generate_audio():
    manager = DBManager()
    if not manager.client:
        print("❌ Erreur : Impossible d'initialiser le client Supabase.")
        return

    # Configuration des dossiers
    base_dir = "assets/sounds"
    letters_dir = os.path.join(base_dir, "letters")
    numbers_dir = os.path.join(base_dir, "numbers")

    for d in [letters_dir, numbers_dir]:
        if not os.path.exists(d):
            os.makedirs(d)
            print(f"📁 Création du dossier : {d}")

    # 1. Génération pour les Lettres (A-Z)
    print("🔤 Génération des fichiers audio pour les lettres...")
    letters_data = manager.get_educational_content(content_type="letter")
    for item in letters_data:
        char = item['content']
        # Pour les lettres, on prononce juste la lettre (en majuscule pour être sûr)
        # Mais pour certaines comme 'Y', gTTS est parfois capricieux si c'est minuscule.
        filename = f"{char}.mp3"
        filepath = os.path.join(letters_dir, filename)
        db_path = f"assets/sounds/letters/{filename}"
        
        print(f"   Génération de : {char}...", end=" ", flush=True)
        try:
            tts = gTTS(text=char, lang='fr')
            tts.save(filepath)
            
            # Mise à jour DB
            manager.client.table("educational_content")\
                .update({"sound_url": db_path})\
                .eq("id", item['id'])\
                .execute()
            print("OK")
        except Exception as e:
            print(f"ERREUR : {e}")

    # 2. Génération pour les Chiffres (1-30)
    print("🔢 Génération des fichiers audio pour les chiffres...")
    numbers_data = manager.get_educational_content(content_type="number")
    for item in numbers_data:
        char = item['content']
        word = item['word']
        filename = f"{char}.mp3"
        filepath = os.path.join(numbers_dir, filename)
        db_path = f"assets/sounds/numbers/{filename}"
        
        print(f"   Génération de : {word}...", end=" ", flush=True)
        try:
            # Pour les chiffres, on utilise le mot complet (ex: "vingt-deux")
            tts = gTTS(text=word, lang='fr')
            tts.save(filepath)
            
            # Mise à jour DB
            manager.client.table("educational_content")\
                .update({"sound_url": db_path})\
                .eq("id", item['id'])\
                .execute()
            print("OK")
        except Exception as e:
            print(f"ERREUR : {e}")

    print("✅ Génération audio et mise à jour DB terminées.")

if __name__ == "__main__":
    generate_audio()
