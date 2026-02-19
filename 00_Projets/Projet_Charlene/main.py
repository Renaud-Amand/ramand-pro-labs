import pygame
import os
import random
from enum import Enum, auto
from db_manager import DBManager

# --- CONFIGURATION DES DÉLAIS (ms) ---
DELAY_SOUND = 2000    # T+2s : Son de la lettre
DELAY_WORD  = 5000    # T+5s : Apparition du mot
DELAY_IMAGE = 10000   # T+10s : Apparition de l'image

# --- CONSTANTES VISUELLES ---
fond_rose = (255, 240, 245)
bleu_roi = (65, 105, 225)
blanc = (255, 255, 255)

class GameState(Enum):
    """
    Définit les différents états possibles de l'application.
    Utiliser un Enum permet d'éviter les erreurs de frappe et rend le code plus lisible.
    """
    START             = auto() # Écran d'accueil
    PLAYING_QUESTION  = auto() # Affiche uniquement la lettre
    PLAYING_HINT      = auto() # Affiche lettre + image + mot + son
    CELEBRATION       = auto() # Grande victoire avec confettis

class ConfettiParticle:
    """Un petit carré de couleur qui tombe."""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = random.randint(10, 20)
        self.color = (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))
        self.speed_y = random.uniform(3, 8)
        self.speed_x = random.uniform(-2, 2)
        self.rotation = random.randint(0, 360)
        self.rot_speed = random.randint(2, 10)

    def update(self):
        self.y += self.speed_y
        self.x += self.speed_x
        self.rotation += self.rot_speed

    def draw(self, screen):
        # Création d'une surface pour la rotation
        surf = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        surf.fill(self.color)
        rotated_surf = pygame.transform.rotate(surf, self.rotation)
        rect = rotated_surf.get_rect(center=(int(self.x), int(self.y)))
        screen.blit(rotated_surf, rect)

class AssetManager:
    """
    Gère le chargement, le cache et la sécurité des ressources.
    Si un fichier est manquant, le jeu utilise un placeholder au lieu de crasher.
    """
    def __init__(self):
        self._images = {}
        self._sounds = {}
        # Surface de remplacement si une image manque (un carré blanc avec bordure)
        self._placeholder_img = pygame.Surface((350, 350))
        self._placeholder_img.fill(blanc)
        pygame.draw.rect(self._placeholder_img, bleu_roi, self._placeholder_img.get_rect(), 5)

    def get_image(self, filename):
        """Charge une image depuis assets/images/ avec cache et protection contre les chemins DB."""
        if not filename: return self._placeholder_img
        
        # Sanitization : on retire les préfixes 'images/' ou 'sounds/' si présents
        # os.path.basename extrait le nom du fichier peu importe le chemin envoyé
        clean_name = os.path.basename(filename).lower()
        
        if clean_name in self._images:
            return self._images[clean_name]
        
        path = os.path.join("assets", "images", clean_name)
        try:
            if os.path.exists(path):
                img = pygame.image.load(path).convert_alpha()
                self._images[clean_name] = img
                return img
            else:
                # Évite le spam de logs si on tourne en boucle
                if not hasattr(self, "_log_missing"): self._log_missing = set()
                if path not in self._log_missing:
                    print(f"⚠️ Image manquante : {path}")
                    self._log_missing.add(path)
                return self._placeholder_img
        except Exception as e:
            print(f"❌ Erreur image {path} : {e}")
            return self._placeholder_img

    def get_sound(self, filename):
        """Charge un son depuis assets/sounds/ avec cache et protection."""
        if not filename: return None
        
        clean_name = os.path.basename(filename).lower()
        
        if clean_name in self._sounds:
            return self._sounds[clean_name]
        
        path = os.path.join("assets", "sounds", clean_name)
        try:
            if os.path.exists(path):
                sound = pygame.mixer.Sound(path)
                self._sounds[clean_name] = sound
                return sound
            else:
                return None
        except Exception as e:
            print(f"❌ Erreur son {path} : {e}")
            return None

    def preload_assets(self, image_list=None, sound_list=None):
        """Pré-charge une liste de ressources pour éviter les lags en jeu."""
        if image_list:
            for img in image_list:
                self.get_image(img)
        if sound_list:
            for snd in sound_list:
                self.get_sound(snd)
        print(f"📦 Pré-chargement terminé : {len(self._images)} images, {len(self._sounds)} sons en cache.")

    def clear_cache(self):
        """Libère la mémoire en vidant les dictionnaires si nécessaire."""
        self._images.clear()
        self._sounds.clear()
        print("🧹 Cache mémoire vidé.")

class GameApp:
    """
    Cœur de l'application Alphabet Kids.
    Gère la boucle de jeu, les entrées et les changements d'états.
    """
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.screen = pygame.display.set_mode((1240, 960))
        pygame.display.set_caption("Alphabet Kids - Charlène")
        
        # Assets et Données
        self.assets = AssetManager()
        self.db = DBManager()
        self.clock = pygame.time.Clock()
        
        # État du Jeu
        self.etat = GameState.START
        self.current_session_data = []
        self.current_index = 0
        self.running = True
        self.state_start_time = 0
        self.sound_played = False
        self.mode_actuel = None # 'letter' ou 'number'
        
        # Stats et Progrès
        progress = self.db.load_progress()
        self.total_discovered = progress.get("total_discovered", 0)
        self.session_discovered = 0
        self.items_decouverts_session = set() # Pour ne pas compter 2 fois la même lettre
        
        # Particules (Confettis)
        self.confettis = []

        # Polices (Robustesse)
        try:
            self.police_geante = pygame.font.SysFont("Comic Sans MS", 350)
            self.police_moyenne = pygame.font.SysFont("Comic Sans MS", 100)
            self.police_petite = pygame.font.SysFont("Comic Sans MS", 50)
        except:
            self.police_geante = pygame.font.SysFont("Arial", 250)
            self.police_moyenne = pygame.font.SysFont("Arial", 80)
            self.police_petite = pygame.font.SysFont("Arial", 40)

        # On ne charge rien au départ, on attend le choix au menu (START)

    def charger_contenu(self, type_demande):
        """Récupère, filtre et mélange les données pour une SESSION UNIQUE."""
        self.mode_actuel = type_demande
        print(f"🔍 Chargement du mode : {type_demande}...")
        
        db_data = self.db.get_educational_content(content_type=type_demande)
        
        if db_data:
            self.current_session_data = db_data
        else:
            # Fallback local minimal
            if type_demande == "letter":
                self.current_session_data = [
                    {"content": "A", "word": "Avion", "image_url": "avion.png", "sound_url": "avion.mp3"},
                    {"content": "B", "word": "Ballon", "image_url": "ballon.png", "sound_url": "ballon.mp3"}
                ]
            else:
                self.current_session_data = [
                    {"content": "1", "word": "Un", "image_url": "1.png", "sound_url": "1.mp3"},
                    {"content": "2", "word": "Deux", "image_url": "2.png", "sound_url": "2.mp3"}
                ]

        # LOGIQUE DE MÉLANGE UNIQUE (RNG)
        random.shuffle(self.current_session_data)
        print(f"✅ Mode {type_demande} chargé : {len(self.current_session_data)} éléments mélangés pour cette session.")

        # Pré-chargement sélectif (Images seulement pour alphabet)
        sounds = [d.get("sound_url") for d in self.current_session_data if d.get("sound_url")]
        images = []
        if self.mode_actuel == "letter":
            images = [d.get("image_url") for d in self.current_session_data if d.get("image_url")]
        
        self.assets.preload_assets(images, sounds)

        # Initialisation de la session
        self.current_index = 0
        self.session_discovered = 0
        self.items_decouverts_session.clear()
        self.changer_etat(GameState.PLAYING_QUESTION)

    def changer_etat(self, nouvel_etat):
        """Change l'état, réinitialise le timer et le drapeau de son."""
        self.etat = nouvel_etat
        self.state_start_time = pygame.time.get_ticks()
        self.sound_played = False

    def handle_events(self):
        """Gère les entrées clavier pour la navigation et l'interaction."""
        elapsed_time = pygame.time.get_ticks() - self.state_start_time

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                # --- ÉCRAN D'ACCUEIL (MENU) ---
                if self.etat == GameState.START:
                    if event.key == pygame.K_1 or event.key == pygame.K_KP1:
                        self.charger_contenu("letter")
                    elif event.key == pygame.K_2 or event.key == pygame.K_KP2:
                        self.charger_contenu("number")

                # 1. Barre ESPACE : Rejouer le son
                elif event.key == pygame.K_SPACE:
                    # Si on est dans le jeu (lettre affichée)
                    if self.etat in [GameState.PLAYING_QUESTION, GameState.PLAYING_HINT]:
                        self.sound_played = False
                        # On force le timer pour que update() déclenche le son immédiatement
                        if elapsed_time < DELAY_SOUND:
                            self.state_start_time = pygame.time.get_ticks() - DELAY_SOUND - 1
                    
                    # Si on est sur l'écran d'accueil
                    elif self.etat == GameState.START:
                        self.current_index = 0
                        self.changer_etat(GameState.PLAYING_QUESTION)
                    
                    # Si on est sur l'écran de victoire, on retourne au menu principal
                    elif self.etat == GameState.CELEBRATION:
                        self.etat = GameState.START

                # 2. Flèche DROITE : Suivant
                elif event.key == pygame.K_RIGHT:
                    if self.current_index < len(self.current_session_data) - 1:
                        self.current_index += 1
                        self.changer_etat(GameState.PLAYING_QUESTION)
                    else:
                        self.changer_etat(GameState.CELEBRATION)
                        # On génère les premières particules
                        for _ in range(100):
                            self.confettis.append(ConfettiParticle(random.randint(0, 1240), random.randint(-500, 0)))
                
                # 3. Flèche GAUCHE : Retour (avec sécurité)
                elif event.key == pygame.K_LEFT:
                    # Sécurité : on n'autorise le retour que si on a "étudié" la lettre au moins 2s
                    if elapsed_time > 2000:
                        if self.current_index > 0:
                            self.current_index -= 1
                            self.changer_etat(GameState.PLAYING_QUESTION)
                        else:
                            # Déjà au début : on retourne au menu pour changer de mode par exemple
                            self.etat = GameState.START
                
                elif event.key == pygame.K_ESCAPE:
                    self.running = False

    def update(self):
        """Machine à états avec cascade temporelle d'indices."""
        if self.etat == GameState.PLAYING_QUESTION:
            elapsed_time = pygame.time.get_ticks() - self.state_start_time
            
            # 1. Déclenchement unique du SON (T+2s)
            if not self.sound_played and elapsed_time > DELAY_SOUND:
                item = self.current_session_data[self.current_index]
                sound_file = item.get("sound_url")
                if sound_file:
                    son = self.assets.get_sound(sound_file)
                    if son: son.play()
                self.sound_played = True

            # 2. Transition vers l'état HINT quand l'image apparaît (T+10s)
            if elapsed_time > DELAY_IMAGE:
                self.etat = GameState.PLAYING_HINT
                
                # INCRA-Savoir : On compte la lettre si c'est une première pour cette session
                current_item_id = self.current_session_data[self.current_index].get("content")
                if current_item_id not in self.items_decouverts_session:
                    self.items_decouverts_session.add(current_item_id)
                    self.session_discovered += 1
                    self.total_discovered += 1
                    self.db.save_progress(self.total_discovered)
                    print(f"📖 Savoir augmenté ! Total : {self.total_discovered}")

        elif self.etat == GameState.CELEBRATION:
            # Animation des confettis
            if len(self.confettis) < 150: # On en rajoute pour la pluie continue
                self.confettis.append(ConfettiParticle(random.randint(0, 1240), -20))
            
            for p in self.confettis[:]:
                p.update()
                if p.y > 1000:
                    self.confettis.remove(p)

    def draw_letter(self, content):
        """Affiche la lettre géante au centre."""
        surface = self.police_geante.render(str(content), True, bleu_roi)
        rect = surface.get_rect(center=(620, 480))
        self.screen.blit(surface, rect)

    def draw_hint(self, word, image_file, elapsed_time):
        """Affiche les indices progressivement selon les paliers atteints."""
        # Palier 2 (T+5s) : Affichage du MOT
        if word and elapsed_time > DELAY_WORD:
            surface_mot = self.police_moyenne.render(word, True, bleu_roi)
            rect_mot = surface_mot.get_rect(centerx=620, bottom=910)
            self.screen.blit(surface_mot, rect_mot)

        # Palier 3 (T+10s) : Affichage de l'IMAGE (Seulement en mode Lettres)
        if self.mode_actuel == "letter" and image_file and elapsed_time > DELAY_IMAGE:
            img = self.assets.get_image(image_file)
            if img:
                img_rect = img.get_rect(center=(620, 200))
                self.screen.blit(img, img_rect)

    def draw(self):
        """Rendu visuel selon l'état actuel."""
        self.screen.fill(fond_rose)
        
        if self.etat == GameState.START:
            titre = self.police_moyenne.render("Menu Charlène", True, bleu_roi)
            self.screen.blit(titre, titre.get_rect(center=(620, 250)))

            opt1 = self.police_moyenne.render("1 - Alphabet (Mélangé)", True, (100, 100, 200))
            self.screen.blit(opt1, opt1.get_rect(center=(620, 450)))

            opt2 = self.police_moyenne.render("2 - Chiffres (Mélangé)", True, (200, 100, 100))
            self.screen.blit(opt2, opt2.get_rect(center=(620, 600)))

            # RECORD
            txt_stats = self.police_petite.render(f"Bravo ! Tu as déjà découvert {self.total_discovered} secrets !", True, bleu_roi)
            self.screen.blit(txt_stats, txt_stats.get_rect(center=(620, 800)))
            
        elif self.etat in [GameState.PLAYING_QUESTION, GameState.PLAYING_HINT]:
            elapsed_time = pygame.time.get_ticks() - self.state_start_time
            item = self.current_session_data[self.current_index]
            self.draw_letter(item.get("content", "?"))
            
            # draw_hint est appelé en continu et gère sa visibilité via elapsed_time
            self.draw_hint(item.get("word"), item.get("image_url"), elapsed_time)
                
        elif self.etat == GameState.CELEBRATION:
            # Pluie de confettis
            for p in self.confettis:
                p.draw(self.screen)
            
            surface = self.police_geante.render("BRAVO !", True, (255, 0, 100))
            self.screen.blit(surface, surface.get_rect(center=(620, 400)))

            txt_score = self.police_moyenne.render(f"+{self.session_discovered} aujourd'hui ! Quel score !", True, bleu_roi)
            self.screen.blit(txt_score, txt_score.get_rect(center=(620, 700)))

            txt_retour = self.police_petite.render("Appuie sur ESPACE pour recommencer", True, (100, 100, 100))
            self.screen.blit(txt_retour, txt_retour.get_rect(center=(620, 850)))

        pygame.display.flip()

    def run(self):
        """Boucle principale."""
        print("🚀 Lancement de l'application...")
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)
        pygame.quit()

if __name__ == "__main__":
    app = GameApp()
    app.run()
