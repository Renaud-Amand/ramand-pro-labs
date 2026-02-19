import pygame
import os
import random
from enum import Enum, auto
from db_manager import DBManager

# --- CONFIGURATION ÉCRAN ---
SCREEN_WIDTH  = 1920
SCREEN_HEIGHT = 1080

# --- CONFIGURATION DES DÉLAIS (ms) ---
DELAY_SOUND = 2000    # T+2s : Son de la lettre
DELAY_WORD  = 5000    # T+5s : Apparition du mot
DELAY_IMAGE = 10000   # T+10s : Apparition de l'image

# --- CONSTANTES VISUELLES ---
fond_rose = (255, 240, 245)
bleu_roi = (65, 105, 225)
blanc = (255, 255, 255)
gris_ombre = (100, 100, 100)

# --- COULEURS DÉGRADÉ ---
couleur_bleu_ciel = (160, 210, 255)
couleur_rose_pastel = (255, 190, 210)

class GameState(Enum):
    """
    Définit les différents états possibles de l'application.
    Utiliser un Enum permet d'éviter les erreurs de frappe et rend le code plus lisible.
    """
    SPLASH            = auto() # Écran de démarrage
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
        
        # Performance : On pré-rend une surface pour éviter de le faire dans draw()
        self.base_surf = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        self.base_surf.fill(self.color)

    def update(self):
        self.y += self.speed_y
        self.x += self.speed_x
        self.rotation += self.rot_speed

    def draw(self, screen):
        # Optimisation : On n'affiche que si c'est visible à l'écran
        if -50 < self.x < SCREEN_WIDTH + 50 and -50 < self.y < SCREEN_HEIGHT + 50:
            rotated_surf = pygame.transform.rotate(self.base_surf, self.rotation)
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
        
        # 1. On tente d'abord d'utiliser le chemin tel quel (depuis la DB)
        # On vérifie si c'est un chemin qui existe
        if os.path.exists(filename):
            path = filename
            clean_name = filename.lower()
        else:
            # 2. Fallback historique : on cherche dans assets/sounds/ via le basename
            clean_name = os.path.basename(filename).lower()
            path = os.path.join("assets", "sounds", clean_name)
        
        if clean_name in self._sounds:
            return self._sounds[clean_name]
        
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
        # Full HD avec optimisation matérielle et mode sans bordure (NOFRAME)
        self.screen = pygame.display.set_mode(
            (SCREEN_WIDTH, SCREEN_HEIGHT), 
            pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.NOFRAME
        )
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
        
        # Pré-rendu du dégradé (Optimisation Performance : évite de le dessiner pixel par pixel chaque frame)
        self.gradient_bg = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.draw_vertical_gradient(self.gradient_bg, couleur_bleu_ciel, couleur_rose_pastel)
        self.gradient_bg = self.gradient_bg.convert()

        # Particules (Confettis) et Sons Spéciaux
        self.confettis = []
        self.celebration_sound = self.assets.get_sound("assets/sounds/effects/fireworks.mp3")
        self.fireworks_played = False

        # Arrière-plan Immersif
        self.current_background = None

        # Polices Dynamiques (Ratio de SCREEN_HEIGHT)
        h = SCREEN_HEIGHT
        try:
            self.police_geante = pygame.font.SysFont("Comic Sans MS", int(h * 0.7))
            self.police_titre  = pygame.font.SysFont("Comic Sans MS", int(h * 0.4))
            self.police_moyenne = pygame.font.SysFont("Comic Sans MS", int(h * 0.12))
            self.police_petite = pygame.font.SysFont("Comic Sans MS", int(h * 0.05))
        except:
            self.police_geante = pygame.font.SysFont("Arial", int(h * 0.5))
            self.police_titre  = pygame.font.SysFont("Arial", int(h * 0.3))
            self.police_moyenne = pygame.font.SysFont("Arial", int(h * 0.10))
            self.police_petite = pygame.font.SysFont("Arial", int(h * 0.04))

        # État initial : Splash Screen
        self.changer_etat(GameState.SPLASH)

    def charger_contenu(self, type_demande):
        """Récupère, filtre et mélange les données pour une SESSION UNIQUE."""
        print(f"🔍 Chargement du mode : {type_demande}...")
        data = self.db.get_educational_content(type_demande)
        
        if not data:
            print(f"⚠️ Aucun contenu trouvé pour {type_demande} !")
            self.current_session_data = []
            return

        # LOGIQUE DE MÉLANGE UNIQUE (RNG)
        random.shuffle(data)
        self.current_session_data = data
        self.mode_actuel = type_demande
        self.current_index = 0
        
        print(f"✅ Mode {type_demande} chargé : {len(self.current_session_data)} éléments mélangés pour cette session.")

        # Pré-chargement sélectif (Images seulement pour alphabet)
        sounds = [d.get("sound_url") for d in self.current_session_data if d.get("sound_url")]
        images = []
        if self.mode_actuel == "letter":
            images = [d.get("image_url") for d in self.current_session_data if d.get("image_url")]
        
        self.assets.preload_assets(images, sounds)

        # Initialisation de la session
        self.session_discovered = 0
        self.items_decouverts_session.clear()
        
        # Préparer le premier arrière-plan
        if len(self.current_session_data) > 0:
            item = self.current_session_data[self.current_index]
            self.preparer_arriere_plan(item.get("image_url"))
            
        self.changer_etat(GameState.PLAYING_QUESTION)

    def changer_etat(self, nouvel_etat):
        """Change l'état, réinitialise le timer et gère les ressources de l'état."""
        self.etat = nouvel_etat
        self.state_start_time = pygame.time.get_ticks()
        self.sound_played = False
        
        # Reset celebration sound trigger
        if nouvel_etat != GameState.CELEBRATION:
            self.fireworks_played = False

        # Préparation du background si on change d'élément (PLAYING_QUESTION)
        if nouvel_etat == GameState.PLAYING_QUESTION:
            item = self.current_session_data[self.current_index]
            self.preparer_arriere_plan(item.get("image_url"))

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
                        for _ in range(150):
                            self.confettis.append(ConfettiParticle(random.randint(0, SCREEN_WIDTH), random.randint(-800, 0)))
                
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
        """Mise à jour de la logique du jeu."""
        if self.etat == GameState.SPLASH:
            # Transition automatique après 3 secondes (3000ms)
            if pygame.time.get_ticks() - self.state_start_time > 3000:
                self.changer_etat(GameState.START)
        
        elif self.etat == GameState.PLAYING_QUESTION:
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
            if len(self.confettis) < 200: # Plus de particules pour 1080p
                self.confettis.append(ConfettiParticle(random.randint(0, SCREEN_WIDTH), -20))
            
            # Son de feu d'artifice unique
            if not self.fireworks_played:
                if self.celebration_sound:
                    self.celebration_sound.play()
                self.fireworks_played = True

            for p in self.confettis[:]:
                p.update()
                if p.y > SCREEN_HEIGHT + 50:
                    self.confettis.remove(p)

    def preparer_arriere_plan(self, image_file):
        """Prépare une version floutée et sombre de l'image de fond (une seule fois)."""
        if not image_file or self.mode_actuel != "letter":
            self.current_background = None
            return

        img = self.assets.get_image(image_file)
        if not img or img == self.assets._placeholder_img:
            self.current_background = None
            return

        # 1. Mise à l'échelle pour couvrir l'écran (Scale to Fill)
        bg = pygame.transform.smoothscale(img, (SCREEN_WIDTH, SCREEN_HEIGHT))
        
        # 2. Effet de flou (Technique rapide : Scale down puis scale up)
        blur_factor = 10
        small = pygame.transform.smoothscale(bg, (SCREEN_WIDTH // blur_factor, SCREEN_HEIGHT // blur_factor))
        bg = pygame.transform.smoothscale(small, (SCREEN_WIDTH, SCREEN_HEIGHT))

        # 3. Assombrissement (Overlay noir 50%)
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(120) # ~50% d'opacité
        bg.blit(overlay, (0, 0))

        # 4. Optimisation finale : On convertit pour le format d'affichage (Ultra-important pour la vitesse de blit)
        self.current_background = bg.convert()

    def draw_text_flat(self, text, font, color, center_pos, outline_color=None, outline_width=5):
        """Affiche un texte net. Si outline_color est fourni, dessine un contour."""
        if outline_color:
            # Dessin du contour par décalage (8 directions pour un effet gras et complet)
            for dx, dy in [(-1, -1), (-1, 1), (1, -1), (1, 1), (0, -1), (0, 1), (-1, 0), (1, 0)]:
                # On multiplie par outline_width pour bien voir le halo
                off_surface = font.render(str(text), True, outline_color)
                off_rect = off_surface.get_rect(center=(center_pos[0] + dx * outline_width, center_pos[1] + dy * outline_width))
                self.screen.blit(off_surface, off_rect)

        # Dessin du texte principal
        text_surface = font.render(str(text), True, color)
        text_rect = text_surface.get_rect(center=center_pos)
        self.screen.blit(text_surface, text_rect)

    def draw_letter(self, content):
        """Affiche la lettre géante noire avec un halo blanc pour le contraste."""
        self.draw_text_flat(content, self.police_geante, (0, 0, 0), (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), outline_color=blanc, outline_width=6)

    def draw_hint(self, word, elapsed_time):
        """Affiche le mot en bas sur un bandeau plus fin et élégant."""
        if word and elapsed_time > DELAY_WORD:
            # Bandeau de lisibilité plus fin (12% de la hauteur)
            banner_h = int(SCREEN_HEIGHT * 0.12)
            banner_surf = pygame.Surface((SCREEN_WIDTH, banner_h))
            banner_surf.fill((0, 0, 0))
            banner_surf.set_alpha(120)
            self.screen.blit(banner_surf, (0, SCREEN_HEIGHT - banner_h))

            # Texte du mot centré dans le bandeau
            self.draw_text_flat(word, self.police_moyenne, blanc, (SCREEN_WIDTH // 2, SCREEN_HEIGHT - (banner_h // 2)))

    def draw_vertical_gradient(self, surface, color_top, color_bottom):
        """Dessine un dégradé vertical sur la surface donnée."""
        h = surface.get_height()
        w = surface.get_width()
        for y in range(h):
            # Mixage linéaire des couleurs
            r = color_top[0] + (color_bottom[0] - color_top[0]) * y / h
            g = color_top[1] + (color_bottom[1] - color_top[1]) * y / h
            b = color_top[2] + (color_bottom[2] - color_top[2]) * y / h
            pygame.draw.line(surface, (int(r), int(g), int(b)), (0, y), (w, y))

    def draw_stylized_title(self, text, center_pos):
        """Affichage du titre 'Charlène' avec des lettres multicolores et un effet bulle."""
        # Couleurs inspirées de l'image de référence (Pastels vibrants)
        colors = [
            (230, 80, 150),  # Rose/Magenta
            (255, 160, 60),  # Orange
            (160, 100, 200), # Violet
            (80, 180, 230),  # Bleu ciel
            (255, 210, 50),  # Jaune
            (230, 80, 150),  # Rose
            (144, 238, 144), # Vert clair
            (255, 127, 80)   # Corail
        ]
        
        # On découpe le texte pour dessiner chaque lettre séparément
        total_w = 0
        surfaces = []
        for i, char in enumerate(text):
            color = colors[i % len(colors)]
            # On utilise la police_titre pour un meilleur ajustement
            char_surf = self.police_titre.render(char, True, color)
            surfaces.append(char_surf)
            total_w += char_surf.get_width() - 15 # Léger chevauchement
        
        # Dessin centré
        curr_x = center_pos[0] - total_w // 2
        for char_surf in surfaces:
            # 1. Contour blanc épais (effet stickers)
            rect = char_surf.get_rect(center=(curr_x + char_surf.get_width() // 2, center_pos[1]))
            # On dessine le contour
            for dx, dy in [(-4,-4), (4,-4), (-4,4), (4,4), (0,-6), (0,6), (-6,0), (6,0)]:
                self.screen.blit(self.police_titre.render(text[surfaces.index(char_surf)], True, blanc), (rect.x + dx, rect.y + dy))
            
            # 2. Lettre colorée
            self.screen.blit(char_surf, rect)
            curr_x += char_surf.get_width() - 15

    def draw(self):
        """Rendu visuel optimisé."""
        # 1. Dessiner le Fond (Couche la plus basse)
        if self.etat in [GameState.SPLASH, GameState.START, GameState.CELEBRATION]:
            self.screen.blit(self.gradient_bg, (0, 0))
        elif self.current_background:
            self.screen.blit(self.current_background, (0, 0))
        else:
            self.screen.fill(fond_rose)
        
        if self.etat == GameState.SPLASH:
            # 1. Titre stylisé 'Charlène'
            self.draw_stylized_title("Charlène", (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
            
            # 2. Texte 'Chargement...'
            self.draw_text_flat("Chargement...", self.police_petite, (80, 80, 80), (SCREEN_WIDTH // 2, SCREEN_HEIGHT * 0.78))
            
            # 3. Barre de progression dynamique (White Glossy style)
            elapsed = pygame.time.get_ticks() - self.state_start_time
            progress = min(elapsed / 3000, 1.0)
            
            bar_w, bar_h = 700, 40
            bar_x = (SCREEN_WIDTH - bar_w) // 2
            bar_y = SCREEN_HEIGHT * 0.85
            
            # Contour et fond
            pygame.draw.rect(self.screen, blanc, (bar_x, bar_y, bar_w, bar_h), 4, border_radius=20)
            # Remplissage
            if progress > 0.02:
                pygame.draw.rect(self.screen, blanc, (bar_x + 8, bar_y + 8, (bar_w - 16) * progress, bar_h - 16), border_radius=15)

        elif self.etat == GameState.START:
            self.draw_text_flat("Menu Charlène", self.police_moyenne, bleu_roi, (SCREEN_WIDTH // 2, SCREEN_HEIGHT * 0.2))
            
            # Espacement aéré entre les options
            self.draw_text_flat("1 - Alphabet (Mélangé)", self.police_moyenne, (100, 100, 200), (SCREEN_WIDTH // 2, SCREEN_HEIGHT * 0.45))
            self.draw_text_flat("2 - Chiffres (Mélangé)", self.police_moyenne, (200, 100, 100), (SCREEN_WIDTH // 2, SCREEN_HEIGHT * 0.6))

            txt_stats = f"Bravo ! Tu as déjà découvert {self.total_discovered} secrets !"
            self.draw_text_flat(txt_stats, self.police_petite, bleu_roi, (SCREEN_WIDTH // 2, SCREEN_HEIGHT * 0.85))
            
        elif self.etat in [GameState.PLAYING_QUESTION, GameState.PLAYING_HINT]:
            elapsed_time = pygame.time.get_ticks() - self.state_start_time
            item = self.current_session_data[self.current_index]
            
            # La lettre est toujours là
            self.draw_letter(item.get("content", "?"))
            
            # L'indice (mot + bandeau) apparaît selon le timer
            self.draw_hint(item.get("word"), elapsed_time)
                
        elif self.etat == GameState.CELEBRATION:
            # Pluie de confettis
            for p in self.confettis:
                p.draw(self.screen)
            
            # Texte de victoire équilibré
            # On utilise une taille intermédiaire pour "BRAVO!" (environ 30% de la hauteur)
            font_bravo = pygame.font.SysFont("Comic Sans MS", int(SCREEN_HEIGHT * 0.35))
            self.draw_text_flat("BRAVO !", font_bravo, (255, 0, 100), (SCREEN_WIDTH // 2, SCREEN_HEIGHT * 0.35))

            # Score descendu vers le bas
            txt_score = f"+{self.session_discovered} aujourd'hui ! Quel score !"
            self.draw_text_flat(txt_score, self.police_moyenne, bleu_roi, (SCREEN_WIDTH // 2, SCREEN_HEIGHT * 0.75))

            # Instruction de retour tout en bas
            self.draw_text_flat("Appuie sur ESPACE pour recommencer", self.police_petite, (100, 100, 100), (SCREEN_WIDTH // 2, SCREEN_HEIGHT * 0.94))

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
