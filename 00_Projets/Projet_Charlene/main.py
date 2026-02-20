import pygame
import os
import random
from enum import Enum, auto
from typing import List, Dict, Optional, Set, Tuple
from db_manager import DBManager

class Config:
    """
    Configuration centralisée de l'application (Encapsulation).
    Toutes les constantes sont regroupées ici pour éviter les variables globales.
    """
    # Dimensions
    LARGEUR_ECRAN: int = 1920
    HAUTEUR_ECRAN: int = 1080
    
    # Couleurs (Standard Senior : Noms en MAJUSCULES)
    BLANC: Tuple[int, int, int] = (255, 255, 255)
    BLEU_ROI: Tuple[int, int, int] = (65, 105, 225)
    FOND_ROSE: Tuple[int, int, int] = (255, 240, 245)
    BLEU_CIEL: Tuple[int, int, int] = (173, 216, 230)
    ROSE_PASTEL: Tuple[int, int, int] = (255, 182, 193)
    NOIR: Tuple[int, int, int] = (0, 0, 0)
    ROUGE_ALERTE: Tuple[int, int, int] = (255, 0, 0)
    GRIS_TEXTE: Tuple[int, int, int] = (80, 80, 80)
    
    # Délais (ms)
    DELAI_SON: int = 2000    # Temps avant le son automatique
    DELAI_IMAGE: int = 10000 # Temps avant l'indice visuel
    DELAI_SPLASH: int = 3000 # Durée de l'écran de splash

class GameState(Enum):
    """États possibles du cycle de vie du jeu."""
    SPLASH = auto()
    START = auto()
    PLAYING_QUESTION = auto()
    PLAYING_HINT = auto()
    CELEBRATION = auto()


class ConfettiParticle:
    """Représente une particule de confetti pour l'écran de célébration."""
    def __init__(self, x: int, y: int) -> None:
        self.x: int = x
        self.y: int = y
        self.size: int = random.randint(10, 25)
        self.color: Tuple[int, int, int] = (
            random.randint(50, 255), 
            random.randint(50, 255), 
            random.randint(50, 255)
        )
        self.speed: int = random.randint(5, 12)
        self.angle: float = random.uniform(0, 6.28)

    def update(self) -> None:
        """Met à jour la position et la rotation de la particule."""
        self.y += self.speed
        self.x += int(random.uniform(-2, 2))
        self.angle += 0.1

    def draw(self, screen: pygame.Surface) -> None:
        """Dessine la particule avec une légère rotation."""
        p_surf = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        pygame.draw.rect(p_surf, self.color, (0, 0, self.size, self.size))
        rotated = pygame.transform.rotate(p_surf, int(self.angle * 50))
        screen.blit(rotated, (self.x, self.y))

class AssetManager:
    """
    Gestionnaire de ressources (Images/Sons) avec cache et sécurité.
    Implémente un système de fallback (placeholder) pour éviter les crashs.
    """
    def __init__(self) -> None:
        self._images: Dict[str, pygame.Surface] = {}
        self._sons: Dict[str, pygame.mixer.Sound] = {}
        self._manquants: Set[str] = set()
        
        # Création du placeholder (Carré blanc avec bordure)
        self._placeholder = pygame.Surface((350, 350))
        self._placeholder.fill(Config.BLANC)
        pygame.draw.rect(self._placeholder, Config.BLEU_ROI, self._placeholder.get_rect(), 8)

    def get_image(self, nom_fichier: Optional[str]) -> pygame.Surface:
        """Récupère une image du cache ou la charge depuis le disque."""
        if not nom_fichier:
            return self._placeholder

        cle = os.path.basename(nom_fichier).lower()
        if cle in self._images:
            return self._images[cle]

        chemin = os.path.join("assets", "images", cle)
        try:
            if os.path.exists(chemin):
                img = pygame.image.load(chemin).convert_alpha()
                self._images[cle] = img
                return img
            if chemin not in self._manquants:
                print(f"⚠️ Image absente : {chemin}")
                self._manquants.add(chemin)
            return self._placeholder
        except Exception as e:
            print(f"❌ Erreur chargement image {chemin} : {e}")
            return self._placeholder

    def get_son(self, nom_fichier: Optional[str]) -> Optional[pygame.mixer.Sound]:
        """Récupère un son du cache ou le charge depuis le disque."""
        if not nom_fichier:
            return None

        # Gestion hybride : chemin direct ou assets/sounds/
        if os.path.exists(nom_fichier):
            chemin = nom_fichier
            cle = nom_fichier.lower()
        else:
            cle = os.path.basename(nom_fichier).lower()
            chemin = os.path.join("assets", "sounds", cle)

        if cle in self._sons:
            return self._sons[cle]

        try:
            if os.path.exists(chemin):
                son = pygame.mixer.Sound(chemin)
                self._sons[cle] = son
                return son
            return None
        except Exception as e:
            print(f"❌ Erreur chargement son {chemin} : {e}")
            return None

    def precharger(self, images: List[str] = None, sons: List[str] = None) -> None:
        """Pré-charge une liste de ressources et gère la saturation du cache."""
        # Sécurité RAM : Nettoyage si le cache devient trop gros
        if len(self._images) > 200 or len(self._sons) > 200:
            self.nettoyer_cache()

        if images:
            for img in images: self.get_image(img)
        if sons:
            for s in sons: self.get_son(s)
        print(f"📦 Assets en cache : {len(self._images)} images, {len(self._sons)} sons.")

    def nettoyer_cache(self) -> None:
        """Vide le cache manuellement pour libérer de la mémoire."""
        self._images.clear()
        self._sons.clear()
        print("🧹 Mémoire libérée (Cache vidé).")

class GameApp:
    """
    Application principale (Architecte Senior).
    Gère le cycle de vie, les entrées utilisateurs, la logique et le rendu.
    """
    def __init__(self) -> None:
        pygame.init()
        pygame.mixer.init()
        
        # Configuration de la fenêtre
        self.screen = pygame.display.set_mode(
            (Config.LARGEUR_ECRAN, Config.HAUTEUR_ECRAN),
            pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.NOFRAME
        )
        pygame.display.set_caption("Alphabet Kids - Senior Edition")

        # Modules
        self.assets = AssetManager()
        self.db = DBManager()
        self.clock = pygame.time.Clock()

        # État Interne
        self.etat = GameState.START
        self.donnees_session: List[Dict] = []
        self.index_actuel: int = 0
        self.en_cours: bool = True
        self.temps_debut_etat: int = 0
        self.son_joue: bool = False
        self.mode_actuel: Optional[str] = None

        # Statistiques
        progres = self.db.load_progress()
        self.total_decouvertes: int = progres.get("total_discovered", 0)
        self.session_decouvertes: int = 0
        self.vus_session: Set[str] = set()

        # cache Rendu
        self.fond_degrade = pygame.Surface((Config.LARGEUR_ECRAN, Config.HAUTEUR_ECRAN))
        self._creer_degrade_vertical(self.fond_degrade, Config.BLEU_CIEL, Config.ROSE_PASTEL)
        self.fond_degrade = self.fond_degrade.convert()
        
        self._titre_splash_cache: Optional[pygame.Surface] = None
        self.fond_jeu_actuel: Optional[pygame.Surface] = None

        # Effets
        self.confettis: List[ConfettiParticle] = []
        self.son_bravo = self.assets.get_son("assets/sounds/effects/fireworks.mp3")
        self.bravo_joue: bool = False

        # Initialisation
        self._configurer_polices()
        self.changer_etat(GameState.SPLASH)

    def _configurer_polices(self) -> None:
        """Prépare les polices de caractères adaptées à la résolution."""
        h = Config.HAUTEUR_ECRAN
        try:
            self.font_geante = pygame.font.SysFont("Comic Sans MS", int(h * 0.7))
            self.font_titre = pygame.font.SysFont("Comic Sans MS", int(h * 0.4))
            self.font_moyenne = pygame.font.SysFont("Comic Sans MS", int(h * 0.12))
            self.font_petite = pygame.font.SysFont("Comic Sans MS", int(h * 0.05))
        except:
            self.font_geante = pygame.font.SysFont("Arial", int(h * 0.5))
            self.font_titre = pygame.font.SysFont("Arial", int(h * 0.3))
            self.font_moyenne = pygame.font.SysFont("Arial", int(h * 0.10))
            self.font_petite = pygame.font.SysFont("Arial", int(h * 0.04))

    # --- LOGIQUE DE NAVIGATION ---

    def changer_etat(self, nouvel_etat: GameState) -> None:
        """Effectue une transition d'état et réinitialise les timers associés."""
        self.etat = nouvel_etat
        self.temps_debut_etat = pygame.time.get_ticks()
        self.son_joue = False
        
        if nouvel_etat != GameState.CELEBRATION:
            self.bravo_joue = False

        if nouvel_etat == GameState.PLAYING_QUESTION:
            item = self.donnees_session[self.index_actuel]
            self._preparer_fond_dynamique(item.get("image_url"))

    def charger_contenu(self, type_demande: str) -> None:
        """Récupère les données, valide le contenu et pré-charge les ressources."""
        print(f"📂 Requête contenu : {type_demande}")
        raw_data = self.db.get_educational_content(type_demande)

        # SÉCURITÉ ARCHITECTE : Validation immédiate
        if not raw_data or len(raw_data) < 1:
            print("🚨 ÉCHEC CRITIQUE : Aucune donnée reçue. Activation du Plan de Secours.")
            self.db.status = 'critical'
            raw_data = [
                {"content": "A", "word": "Avion", "type": "letter", "image_url": "", "sound_url": ""},
                {"content": "B", "word": "Ballon", "type": "letter", "image_url": "", "sound_url": ""},
                {"content": "C", "word": "Chat", "type": "letter", "image_url": "", "sound_url": ""},
            ]

        # Préparation session
        random.shuffle(raw_data)
        self.donnees_session = raw_data
        self.mode_actuel = type_demande
        self.index_actuel = 0
        self.session_decouvertes = 0
        self.vus_session.clear()

        # Pre-loading intelligent
        sons = [d.get("sound_url") for d in raw_data if d.get("sound_url")]
        imgs = [d.get("image_url") for d in raw_data if d.get("image_url")] if type_demande == "letter" else []
        self.assets.precharger(imgs, sons)

        if len(self.donnees_session) > 0:
            item = self.donnees_session[self.index_actuel]
            self._preparer_fond_dynamique(item.get("image_url"))

        self.changer_etat(GameState.PLAYING_QUESTION)

    def _preparer_fond_dynamique(self, image_nom: Optional[str]) -> None:
        """Crée un arrière-plan flouté et immersif pour l'élément actuel."""
        if not image_nom or self.mode_actuel != "letter":
            self.fond_jeu_actuel = None
            return

        image = self.assets.get_image(image_nom)
        if not image or image == self.assets._placeholder:
            self.fond_jeu_actuel = None
            return

        # Effet : Scale -> Blur (Low Res -> High Res) -> Dim
        fond = pygame.transform.smoothscale(image, (Config.LARGEUR_ECRAN, Config.HAUTEUR_ECRAN))
        facteur = 12
        petite = pygame.transform.smoothscale(fond, (Config.LARGEUR_ECRAN // facteur, Config.HAUTEUR_ECRAN // facteur))
        fond = pygame.transform.smoothscale(petite, (Config.LARGEUR_ECRAN, Config.HAUTEUR_ECRAN))

        filtre = pygame.Surface((Config.LARGEUR_ECRAN, Config.HAUTEUR_ECRAN))
        filtre.fill(Config.NOIR)
        filtre.set_alpha(130)
        fond.blit(filtre, (0, 0))
        self.fond_jeu_actuel = fond.convert()

    # --- ENTRÉES ---

    def orchestrer_entrees(self) -> None:
        """Gère les interactions clavier et la sortie du programme."""
        maintenant = pygame.time.get_ticks()
        ecoule = maintenant - self.temps_debut_etat

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.en_cours = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.en_cours = False
                
                # NAVIGATION MENU
                if self.etat == GameState.START:
                    if event.key in [pygame.K_1, pygame.K_KP1]:
                        self.charger_contenu("letter")
                    elif event.key in [pygame.K_2, pygame.K_KP2]:
                        self.charger_contenu("number")

                # ACTIONS COMMUNES
                elif event.key == pygame.K_SPACE:
                    if self.etat in [GameState.PLAYING_QUESTION, GameState.PLAYING_HINT]:
                        self.son_joue = False
                        if ecoule < Config.DELAI_SON:
                            self.temps_debut_etat = maintenant - Config.DELAI_SON - 1
                    elif self.etat == GameState.CELEBRATION:
                        self.changer_etat(GameState.START)

                elif event.key == pygame.K_RIGHT:
                    if self.etat in [GameState.PLAYING_QUESTION, GameState.PLAYING_HINT]:
                        if self.index_actuel < len(self.donnees_session) - 1:
                            self.index_actuel += 1
                            self.changer_etat(GameState.PLAYING_QUESTION)
                        else:
                            self._lancer_celebration()

                elif event.key == pygame.K_LEFT:
                    if self.etat in [GameState.PLAYING_QUESTION, GameState.PLAYING_HINT] and ecoule > 1500:
                        if self.index_actuel > 0:
                            self.index_actuel -= 1
                            self.changer_etat(GameState.PLAYING_QUESTION)
                        else:
                            self.changer_etat(GameState.START)

    def _lancer_celebration(self) -> None:
        """Initialise la session de fête finale."""
        self.changer_etat(GameState.CELEBRATION)
        for _ in range(160):
            self.confettis.append(ConfettiParticle(random.randint(0, Config.LARGEUR_ECRAN), random.randint(-800, 0)))

    # --- MISE À JOUR LOGIQUE ---

    def mettre_a_jour(self) -> None:
        """Gère l'évolution automatique des états et animations."""
        maintenant = pygame.time.get_ticks()
        
        if self.etat == GameState.SPLASH:
            if maintenant - self.temps_debut_etat > Config.DELAI_SPLASH:
                self.changer_etat(GameState.START)

        elif self.etat == GameState.PLAYING_QUESTION:
            ecoule = maintenant - self.temps_debut_etat
            
            # Son (T+2s)
            if not self.son_joue and ecoule > Config.DELAI_SON:
                self._jouer_son_courant()
                self.son_joue = True

            # Hint (T+10s)
            if ecoule > Config.DELAI_IMAGE:
                self.etat = GameState.PLAYING_HINT
                self._enregistrer_decouverte()

        elif self.etat == GameState.CELEBRATION:
            self._animer_confettis()

    def _jouer_son_courant(self) -> None:
        """Identifie et joue le fichier sonore associé à l'élément actif."""
        item = self.donnees_session[self.index_actuel]
        son = self.assets.get_son(item.get("sound_url"))
        if son: son.play()

    def _enregistrer_decouverte(self) -> None:
        """Incrémente les statistiques globales si l'élément n'a pas été vu cette session."""
        identifiant = self.donnees_session[self.index_actuel].get("content")
        if identifiant not in self.vus_session:
            self.vus_session.add(identifiant)
            self.session_decouvertes += 1
            self.total_decouvertes += 1
            self.db.save_progress(self.total_decouvertes)

    def _animer_confettis(self) -> None:
        """Gère la pluie de confettis et le déclenchement sonore Bravo."""
        if len(self.confettis) < 200:
            self.confettis.append(ConfettiParticle(random.randint(0, Config.LARGEUR_ECRAN), -20))
        
        if not self.bravo_joue and self.son_bravo:
            self.son_bravo.play()
            self.bravo_joue = True

        for p in self.confettis[:]:
            p.update()
            if p.y > Config.HAUTEUR_ECRAN + 50:
                self.confettis.remove(p)

    # --- RENDU ---

    def _creer_degrade_vertical(self, surface: pygame.Surface, haut: Tuple, bas: Tuple) -> None:
        """Remplit une surface avec un dégradé de couleurs vertical."""
        h, w = surface.get_height(), surface.get_width()
        for y in range(h):
            r = haut[0] + (bas[0] - haut[0]) * y / h
            g = haut[1] + (bas[1] - haut[1]) * y / h
            b = haut[2] + (bas[2] - haut[2]) * y / h
            pygame.draw.line(surface, (int(r), int(g), int(b)), (0, y), (w, y))

    def _dessiner_texte(self, texte: str, font: pygame.font.Font, couleur: Tuple, 
                       centre: Tuple, contour: Optional[Tuple] = None, epaisseur: int = 5) -> None:
        """Affiche un texte avec ou sans contour (DRY helper)."""
        texte_s = str(texte)
        if contour:
            for dx, dy in [(-1,-1), (-1,1), (1,-1), (1,1), (0,-1), (0,1), (-1,0), (1,0)]:
                s = font.render(texte_s, True, contour)
                r = s.get_rect(center=(centre[0] + dx * epaisseur, centre[1] + dy * epaisseur))
                self.screen.blit(s, r)

        s = font.render(texte_s, True, couleur)
        r = s.get_rect(center=centre)
        self.screen.blit(s, r)

    def _pre_rendu_titre(self, texte: str) -> pygame.Surface:
        """Génère une surface composite riche pour le titre de l'application."""
        couleurs = [(230,80,150), (255,160,60), (160,100,200), (80,180,230), (255,210,50), (144,238,144)]
        lettres = []
        l_totale, h_max = 0, 0
        
        for i, char in enumerate(texte):
            c = couleurs[i % len(couleurs)]
            s = self.font_titre.render(char, True, c)
            lettres.append(s)
            l_totale += s.get_width() - 20
            h_max = max(h_max, s.get_height())

        finale = pygame.Surface((l_totale + 50, h_max + 50), pygame.SRCALPHA)
        x_actuel = 25
        for i, s_lettre in enumerate(lettres):
            char = texte[i]
            # Contour Sticker
            for dx, dy in [(-5,-5), (5,-5), (-5,5), (5,5), (0,-7), (0,7), (-7,0), (7,0)]:
                sticker = self.font_titre.render(char, True, Config.BLANC)
                finale.blit(sticker, (x_actuel + dx, 25 + dy))
            finale.blit(s_lettre, (x_actuel, 25))
            x_actuel += s_lettre.get_width() - 20
        return finale

    def dessiner(self) -> None:
        """Gère tout l'affichage visuel en fonction de l'état actuel."""
        # 1. Background
        if self.etat in [GameState.SPLASH, GameState.START, GameState.CELEBRATION]:
            self.screen.blit(self.fond_degrade, (0, 0))
        elif self.fond_jeu_actuel:
            self.screen.blit(self.fond_jeu_actuel, (0, 0))
        else:
            self.screen.fill(Config.FOND_ROSE)
        
        # 2. Scènes
        if self.etat == GameState.SPLASH:
            self._dessiner_splash()
        elif self.etat == GameState.START:
            self._dessiner_menu()
        elif self.etat in [GameState.PLAYING_QUESTION, GameState.PLAYING_HINT]:
            self._dessiner_jeu()
        elif self.etat == GameState.CELEBRATION:
            self._dessiner_victoire()

        pygame.display.flip()

    def _dessiner_splash(self) -> None:
        """Affiche le splash screen avec titre animé et barre de chargement."""
        if not self._titre_splash_cache:
            self._titre_splash_cache = self._pre_rendu_titre("Charlène")
        
        r = self._titre_splash_cache.get_rect(center=(Config.LARGEUR_ECRAN // 2, Config.HAUTEUR_ECRAN // 2 - 80))
        self.screen.blit(self._titre_splash_cache, r)
        
        self._dessiner_texte("Chargement...", self.font_petite, Config.GRIS_TEXTE, 
                            (Config.LARGEUR_ECRAN // 2, Config.HAUTEUR_ECRAN * 0.78))
        
        # Barre Senior
        prog = min((pygame.time.get_ticks() - self.temps_debut_etat) / Config.DELAI_SPLASH, 1.0)
        bw, bh = 800, 45
        bx, by = (Config.LARGEUR_ECRAN - bw) // 2, Config.HAUTEUR_ECRAN * 0.85
        pygame.draw.rect(self.screen, Config.BLANC, (bx, by, bw, bh), 5, border_radius=22)
        if prog > 0.02:
            pygame.draw.rect(self.screen, Config.BLANC, (bx + 10, by + 10, (bw - 20) * prog, bh - 20), border_radius=15)

    def _dessiner_menu(self) -> None:
        """Affiche le menu de sélection et les statistiques globales."""
        self._dessiner_texte("Menu Charlène", self.font_moyenne, Config.BLEU_ROI, 
                            (Config.LARGEUR_ECRAN // 2, Config.HAUTEUR_ECRAN * 0.2))
        
        couleurs_menu = [(100, 100, 200), (200, 100, 100)]
        off_y = [0.45, 0.6]
        options = ["1 - Alphabet", "2 - Chiffres"]
        
        for i, text in enumerate(options):
            self._dessiner_texte(text, self.font_moyenne, couleurs_menu[i], 
                                (Config.LARGEUR_ECRAN // 2, Config.HAUTEUR_ECRAN * off_y[i]))

        lab = f"Savoirs récoltés : {self.total_decouvertes}"
        self._dessiner_texte(lab, self.font_petite, Config.BLEU_ROI, 
                            (Config.LARGEUR_ECRAN // 2, Config.HAUTEUR_ECRAN * 0.85))

        # Indicateur Unique (Source : self.db.status)
        if self.db.status in ['offline', 'critical']:
            m = "Mode Secours 🚩" if self.db.status == 'offline' else "Mode Secours Critique 🚨"
            c = (170, 0, 0) if self.db.status == 'offline' else Config.ROUGE_ALERTE
            surf = self.font_petite.render(m, True, c)
            self.screen.blit(surf, (Config.LARGEUR_ECRAN - surf.get_width() - 30, Config.HAUTEUR_ECRAN - surf.get_height() - 30))

    def _dessiner_jeu(self) -> None:
        """Affiche la lettre ou le chiffre ainsi que l'indice bandeau."""
        item = self.donnees_session[self.index_actuel]
        self._dessiner_texte(item.get("content", "?"), self.font_geante, Config.NOIR, 
                            (Config.LARGEUR_ECRAN // 2, Config.HAUTEUR_ECRAN // 2), 
                            contour=Config.BLANC, epaisseur=8)
        
        if self.etat == GameState.PLAYING_HINT:
            mot = item.get("word", "")
            bh = int(Config.HAUTEUR_ECRAN * 0.13)
            bandeau = pygame.Surface((Config.LARGEUR_ECRAN, bh))
            bandeau.fill(Config.NOIR)
            bandeau.set_alpha(150)
            self.screen.blit(bandeau, (0, Config.HAUTEUR_ECRAN - bh))
            self._dessiner_texte(mot, self.font_moyenne, Config.BLANC, 
                                (Config.LARGEUR_ECRAN // 2, Config.HAUTEUR_ECRAN - (bh // 2)))

    def _dessiner_victoire(self) -> None:
        """Affiche l'écran de fin de session avec les confettis."""
        for c in self.confettis: c.draw(self.screen)
        
        f_win = pygame.font.SysFont("Comic Sans MS", int(Config.HAUTEUR_ECRAN * 0.38))
        self._dessiner_texte("BRAVO !", f_win, (255, 0, 100), (Config.LARGEUR_ECRAN // 2, Config.HAUTEUR_ECRAN * 0.38))
        
        txt = f"+{self.session_decouvertes} savoirs découverts !"
        self._dessiner_texte(txt, self.font_moyenne, Config.BLEU_ROI, 
                            (Config.LARGEUR_ECRAN // 2, Config.HAUTEUR_ECRAN * 0.76))
        
        self._dessiner_texte("Appuie sur ESPACE", self.font_petite, (120, 120, 120), 
                            (Config.LARGEUR_ECRAN // 2, Config.HAUTEUR_ECRAN * 0.94))

    def lancer(self) -> None:
        """Démarre la boucle principale du programme."""
        print("🏛️ Architecture Senior prête.")
        while self.en_cours:
            self.orchestrer_entrees()
            self.mettre_a_jour()
            self.dessiner()
            self.clock.tick(60)
        pygame.quit()

if __name__ == "__main__":
    app = GameApp()
    app.lancer()
