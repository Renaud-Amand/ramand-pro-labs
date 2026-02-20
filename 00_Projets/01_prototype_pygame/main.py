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

class LogicManager:
    """
    Gère la logique métier, les états du jeu et la progression.
    """
    def __init__(self, db: DBManager, assets: 'AssetManager') -> None:
        """
        Initialise le gestionnaire de logique.
        
        Args:
            db: Instance de gestion de la base de données.
            assets: Instance de gestion des ressources.
        """
        self.db = db
        self.assets = assets
        self.etat = GameState.SPLASH
        self.temps_debut_etat = pygame.time.get_ticks()
        
        # Données session
        self.donnees_session: List[Dict] = []
        self.index_actuel: int = 0
        self.mode_actuel: Optional[str] = None
        self.son_joue: bool = False
        
        # Statistiques
        progres = self.db.load_progress()
        self.total_decouvertes: int = progres.get("total_discovered", 0)
        self.session_decouvertes: int = 0
        self.vus_session: Set[str] = set()
        
        # Effets
        self.confettis: List[ConfettiParticle] = []
        self.bravo_joue: bool = False

    def changer_etat(self, nouvel_etat: GameState) -> None:
        """
        Change l'état du jeu et réinitialise les paramètres temporels associés.
        
        Args:
            nouvel_etat: Le nouvel état à appliquer.
        """
        self.etat = nouvel_etat
        self.temps_debut_etat = pygame.time.get_ticks()
        self.son_joue = False
        if nouvel_etat != GameState.CELEBRATION:
            self.bravo_joue = False

    def charger_contenu(self, type_demande: str) -> None:
        """
        Charge et valide le contenu éducatif depuis la base de données.
        
        Args:
            type_demande: Type de contenu ('letter' ou 'number').
        """
        print(f"📂 Requête contenu : {type_demande}")
        raw_data = self.db.get_educational_content(type_demande)

        if not raw_data or len(raw_data) < 1:
            print("🚨 ÉCHEC CRITIQUE : Utilisation du mode secours.")
            self.db.status = 'critical'
            raw_data = [
                {"content": "A", "word": "Avion", "type": "letter", "image_url": "", "sound_url": ""},
                {"content": "B", "word": "Ballon", "type": "letter", "image_url": "", "sound_url": ""},
                {"content": "C", "word": "Chat", "type": "letter", "image_url": "", "sound_url": ""},
            ]

        random.shuffle(raw_data)
        self.donnees_session = raw_data
        self.mode_actuel = type_demande
        self.index_actuel = 0
        self.session_decouvertes = 0
        self.vus_session.clear()

        # Pré-chargement
        sons = [d.get("sound_url") for d in raw_data if d.get("sound_url")]
        imgs = [d.get("image_url") for d in raw_data if d.get("image_url")] if type_demande == "letter" else []
        self.assets.precharger(imgs, sons)

        self.changer_etat(GameState.PLAYING_QUESTION)

    def mettre_a_jour(self) -> None:
        """
        Gère l'évolution temporelle de la logique du jeu (timers, confettis).
        """
        maintenant = pygame.time.get_ticks()
        ecoule = maintenant - self.temps_debut_etat
        
        if self.etat == GameState.SPLASH:
            if ecoule > Config.DELAI_SPLASH:
                self.changer_etat(GameState.START)

        elif self.etat == GameState.PLAYING_QUESTION:
            if not self.son_joue and ecoule > Config.DELAI_SON:
                self._jouer_son_courant()
                self.son_joue = True

            if ecoule > Config.DELAI_IMAGE:
                self.etat = GameState.PLAYING_HINT
                self._enregistrer_decouverte()

        elif self.etat == GameState.CELEBRATION:
            self._animer_confettis()

    def _jouer_son_courant(self) -> None:
        """Joue le son de l'élément actuellement affiché."""
        item = self.donnees_session[self.index_actuel]
        son = self.assets.get_son(item.get("sound_url"))
        if son: son.play()

    def _enregistrer_decouverte(self) -> None:
        """Enregistre un nouvel élément découvert dans la progression."""
        identifiant = self.donnees_session[self.index_actuel].get("content")
        if identifiant not in self.vus_session:
            self.vus_session.add(identifiant)
            self.session_decouvertes += 1
            self.total_decouvertes += 1
            self.db.save_progress(self.total_decouvertes)

    def _animer_confettis(self) -> None:
        """Gère la physique et le cycle de vie des confettis."""
        if len(self.confettis) < 200:
            self.confettis.append(ConfettiParticle(random.randint(0, Config.LARGEUR_ECRAN), -20))
        
        for p in self.confettis[:]:
            p.update()
            if p.y > Config.HAUTEUR_ECRAN + 50:
                self.confettis.remove(p)

    def lancer_celebration(self) -> None:
        """Initialise la phase de célébration."""
        self.changer_etat(GameState.CELEBRATION)
        self.confettis = [
            ConfettiParticle(random.randint(0, Config.LARGEUR_ECRAN), random.randint(-800, 0)) 
            for _ in range(160)
        ]

class BaseRenderer:
    """Classe de base pour les moteurs de rendu contenant les utilitaires communs."""
    def __init__(self, screen: pygame.Surface) -> None:
        self.screen = screen
        self._configurer_polices()

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

    def _dessiner_texte(self, texte: str, font: pygame.font.Font, couleur: Tuple, 
                        centre: Tuple, contour: Optional[Tuple] = None, epaisseur: int = 5) -> None:
        """Affiche un texte avec un contour optionnel."""
        if contour:
            for dx, dy in [(-1,-1), (-1,1), (1,-1), (1,1), (0,-1), (0,1), (-1,0), (1,0)]:
                s = font.render(str(texte), True, contour)
                r = s.get_rect(center=(centre[0] + dx * epaisseur, centre[1] + dy * epaisseur))
                self.screen.blit(s, r)
        s = font.render(str(texte), True, couleur)
        r = s.get_rect(center=centre)
        self.screen.blit(s, r)

class MenuRenderer(BaseRenderer):
    """
    Gère le rendu visuel des écrans de démarrage et de menu.
    """
    def __init__(self, screen: pygame.Surface) -> None:
        super().__init__(screen)
        self._titre_cache = None

    def dessiner_splash(self, temps_debut: int) -> None:
        """Affiche l'écran de chargement animé."""
        if not self._titre_cache:
            self._titre_cache = self._generer_titre_stylise("Charlène")
        
        r = self._titre_cache.get_rect(center=(Config.LARGEUR_ECRAN // 2, Config.HAUTEUR_ECRAN // 2 - 80))
        self.screen.blit(self._titre_cache, r)
        
        self._dessiner_texte("Chargement...", self.font_petite, Config.GRIS_TEXTE, 
                            (Config.LARGEUR_ECRAN // 2, Config.HAUTEUR_ECRAN * 0.78))
        self._afficher_barre_chargement(temps_debut)

    def _afficher_barre_chargement(self, temps_debut: int) -> None:
        """Dessine la barre de progression du splash."""
        prog = min((pygame.time.get_ticks() - temps_debut) / Config.DELAI_SPLASH, 1.0)
        bw, bh = 800, 45
        bx, by = (Config.LARGEUR_ECRAN - bw) // 2, Config.HAUTEUR_ECRAN * 0.85
        pygame.draw.rect(self.screen, Config.BLANC, (bx, by, bw, bh), 5, border_radius=22)
        if prog > 0.02:
            pygame.draw.rect(self.screen, Config.BLANC, (bx + 10, by + 10, (bw - 20) * prog, bh - 20), border_radius=15)

    def dessiner_menu(self, total_decouvertes: int, db_status: str) -> None:
        """Affiche le menu principal et les statistiques."""
        self._dessiner_texte("Menu Charlène", self.font_moyenne, Config.BLEU_ROI, 
                            (Config.LARGEUR_ECRAN // 2, Config.HAUTEUR_ECRAN * 0.2))
        self._afficher_options_menu()
        self._afficher_stats(total_decouvertes)
        self._afficher_alerte_db(db_status)

    def _afficher_options_menu(self) -> None:
        """Dessine les boutons de sélection du mode."""
        options = [("1 - Alphabet", (100, 100, 200), 0.45), ("2 - Chiffres", (200, 100, 100), 0.6)]
        for texte, couleur, y_ratio in options:
            self._dessiner_texte(texte, self.font_moyenne, couleur, 
                                (Config.LARGEUR_ECRAN // 2, Config.HAUTEUR_ECRAN * y_ratio))

    def _afficher_stats(self, total: int) -> None:
        """Affiche le compteur de savoirs récoltés."""
        txt = f"Savoirs récoltés : {total}"
        self._dessiner_texte(txt, self.font_petite, Config.BLEU_ROI, 
                            (Config.LARGEUR_ECRAN // 2, Config.HAUTEUR_ECRAN * 0.85))

    def _afficher_alerte_db(self, status: str) -> None:
        """Affiche un indicateur visuel si la DB est hors-ligne."""
        if status in ['offline', 'critical']:
            m = "Mode Secours 🚩" if status == 'offline' else "Mode Secours Critique 🚨"
            c = (170, 0, 0) if status == 'offline' else Config.ROUGE_ALERTE
            surf = self.font_petite.render(m, True, c)
            self.screen.blit(surf, (Config.LARGEUR_ECRAN - surf.get_width() - 30, Config.HAUTEUR_ECRAN - surf.get_height() - 30))

    def _generer_titre_stylise(self, texte: str) -> pygame.Surface:
        """Crée une surface de titre avec des couleurs vives et un effet sticker."""
        couleurs = [(230,80,150), (255,160,60), (160,100,200), (80,180,230), (255,210,50), (144,238,144)]
        lettres = [self.font_titre.render(c, True, couleurs[i % len(couleurs)]) for i, c in enumerate(texte)]
        l_totale = sum(l.get_width() - 20 for l in lettres)
        h_max = max(l.get_height() for l in lettres)
        
        surf = pygame.Surface((l_totale + 50, h_max + 50), pygame.SRCALPHA)
        x = 25
        for i, l in enumerate(lettres):
            char = texte[i]
            for dx, dy in [(-5,-5), (5,-5), (-5,5), (5,5), (0,-7), (0,7), (-7,0), (7,0)]:
                sticker = self.font_titre.render(char, True, Config.BLANC)
                surf.blit(sticker, (x + dx, 25 + dy))
            surf.blit(l, (x, 25))
            x += l.get_width() - 20
        return surf

class GameRenderer(BaseRenderer):
    """
    Gère le rendu visuel des phases de jeu et de célébration.
    """
    def dessiner_jeu(self, item: Dict, etat: GameState) -> None:
        """Affiche l'élément éducatif et l'indice si nécessaire."""
        self._afficher_lettre_centrale(item.get("content", "?"))
        if etat == GameState.PLAYING_HINT:
            self._afficher_bandeau_indice(item.get("word", ""))

    def _afficher_lettre_centrale(self, contenu: str) -> None:
        """Affiche le caractère principal au centre de l'écran."""
        self._dessiner_texte(contenu, self.font_geante, Config.NOIR, 
                            (Config.LARGEUR_ECRAN // 2, Config.HAUTEUR_ECRAN // 2), 
                            contour=Config.BLANC, epaisseur=8)

    def _afficher_bandeau_indice(self, mot: str) -> None:
        """Affiche le mot associé au caractère en bas de l'écran."""
        bh = int(Config.HAUTEUR_ECRAN * 0.13)
        bandeau = pygame.Surface((Config.LARGEUR_ECRAN, bh))
        bandeau.fill(Config.NOIR)
        bandeau.set_alpha(150)
        self.screen.blit(bandeau, (0, Config.HAUTEUR_ECRAN - bh))
        self._dessiner_texte(mot, self.font_moyenne, Config.BLANC, 
                            (Config.LARGEUR_ECRAN // 2, Config.HAUTEUR_ECRAN - (bh // 2)))

    def dessiner_victoire(self, confettis: List[ConfettiParticle], decouvertes: int) -> None:
        """Affiche l'écran de célébration final."""
        for p in confettis: p.draw(self.screen)
        
        f_win = pygame.font.SysFont("Comic Sans MS", int(Config.HAUTEUR_ECRAN * 0.38))
        self._dessiner_texte("BRAVO !", f_win, (255, 0, 100), (Config.LARGEUR_ECRAN // 2, Config.HAUTEUR_ECRAN * 0.38))
        
        txt = f"+{decouvertes} savoirs découverts !"
        self._dessiner_texte(txt, self.font_moyenne, Config.BLEU_ROI, 
                            (Config.LARGEUR_ECRAN // 2, Config.HAUTEUR_ECRAN * 0.76))
        
        self._dessiner_texte("Appuie sur ESPACE", self.font_petite, (120, 120, 120), 
                            (Config.LARGEUR_ECRAN // 2, Config.HAUTEUR_ECRAN * 0.94))

class GameApp:
    """
    Chef d'orchestre de l'application.
    Coordonne la logique, le rendu et les entrées utilisateur.
    """
    def __init__(self) -> None:
        """Initialise pygame, les managers et les moteurs de rendu."""
        pygame.init()
        pygame.mixer.init()
        
        self.screen = pygame.display.set_mode(
            (Config.LARGEUR_ECRAN, Config.HAUTEUR_ECRAN),
            pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.NOFRAME
        )
        pygame.display.set_caption("Alphabet Kids - Prototype V1")

        # Initialisation composants
        self.assets = AssetManager()
        self.db = DBManager()
        self.clock = pygame.time.Clock()
        
        # Managers
        self.logic = LogicManager(self.db, self.assets)
        self.menu_renderer = MenuRenderer(self.screen)
        self.game_renderer = GameRenderer(self.screen)

        # Cache d'arrière-plan
        self.fond_degrade = pygame.Surface((Config.LARGEUR_ECRAN, Config.HAUTEUR_ECRAN))
        self._creer_degrade_vertical(self.fond_degrade, Config.BLEU_CIEL, Config.ROSE_PASTEL)
        self.fond_jeu_actuel: Optional[pygame.Surface] = None
        
        # Audio
        self.son_bravo = self.assets.get_son("assets/sounds/effects/fireworks.mp3")
        self.en_cours: bool = True

    def _creer_degrade_vertical(self, surface: pygame.Surface, haut: Tuple, bas: Tuple) -> None:
        """Remplit une surface avec un dégradé de couleurs vertical."""
        h, w = surface.get_height(), surface.get_width()
        for y in range(h):
            r = haut[0] + (bas[0] - haut[0]) * y / h
            g = haut[1] + (bas[1] - haut[1]) * y / h
            b = haut[2] + (bas[2] - haut[2]) * y / h
            pygame.draw.line(surface, (int(r), int(g), int(b)), (0, y), (w, y))

    def _preparer_fond_dynamique(self, image_nom: Optional[str]) -> None:
        """Crée un arrière-plan thématique flou pour la question actuelle."""
        if not image_nom or self.logic.mode_actuel != "letter":
            self.fond_jeu_actuel = None
            return

        image = self.assets.get_image(image_nom)
        if not image or image == self.assets._placeholder:
            self.fond_jeu_actuel = None
            return

        fond = pygame.transform.smoothscale(image, (Config.LARGEUR_ECRAN, Config.HAUTEUR_ECRAN))
        facteur = 12
        pete = pygame.transform.smoothscale(fond, (Config.LARGEUR_ECRAN // facteur, Config.HAUTEUR_ECRAN // facteur))
        fond = pygame.transform.smoothscale(pete, (Config.LARGEUR_ECRAN, Config.HAUTEUR_ECRAN))

        filtre = pygame.Surface((Config.LARGEUR_ECRAN, Config.HAUTEUR_ECRAN))
        filtre.fill(Config.NOIR)
        filtre.set_alpha(130)
        fond.blit(filtre, (0, 0))
        self.fond_jeu_actuel = fond.convert()

    def orchestrer_entrees(self) -> None:
        """Traite les événements pygame et les touches pressées."""
        maintenant = pygame.time.get_ticks()
        ecoule = maintenant - self.logic.temps_debut_etat

        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                self.en_cours = False

            elif event.type == pygame.KEYDOWN:
                if self.logic.etat == GameState.START:
                    if event.key in [pygame.K_1, pygame.K_KP1]:
                        self.logic.charger_contenu("letter")
                        self._actualiser_fond()
                    elif event.key in [pygame.K_2, pygame.K_KP2]:
                        self.logic.charger_contenu("number")
                        self._actualiser_fond()

                elif event.key == pygame.K_SPACE:
                    if self.logic.etat in [GameState.PLAYING_QUESTION, GameState.PLAYING_HINT]:
                        self.logic.son_joue = False
                        if ecoule < Config.DELAI_SON:
                            self.logic.temps_debut_etat = maintenant - Config.DELAI_SON - 1
                    elif self.logic.etat == GameState.CELEBRATION:
                        self.logic.changer_etat(GameState.START)

                elif event.key == pygame.K_RIGHT:
                    if self.logic.etat in [GameState.PLAYING_QUESTION, GameState.PLAYING_HINT]:
                        if self.logic.index_actuel < len(self.logic.donnees_session) - 1:
                            self.logic.index_actuel += 1
                            self.logic.changer_etat(GameState.PLAYING_QUESTION)
                            self._actualiser_fond()
                        else:
                            self.logic.lancer_celebration()
                            if self.son_bravo: self.son_bravo.play()

                elif event.key == pygame.K_LEFT:
                    if self.logic.etat in [GameState.PLAYING_QUESTION, GameState.PLAYING_HINT] and ecoule > 1000:
                        if self.logic.index_actuel > 0:
                            self.logic.index_actuel -= 1
                            self.logic.changer_etat(GameState.PLAYING_QUESTION)
                            self._actualiser_fond()
                        else:
                            self.logic.changer_etat(GameState.START)

    def _actualiser_fond(self) -> None:
        """Met à jour le cache de l'arrière-plan selon l'élément actuel."""
        if self.logic.etat in [GameState.PLAYING_QUESTION, GameState.PLAYING_HINT]:
            item = self.logic.donnees_session[self.logic.index_actuel]
            self._preparer_fond_dynamique(item.get("image_url"))

    def dessiner(self) -> None:
        """Coordonne le rendu visuel global de l'application."""
        # 1. Fond
        if self.logic.etat in [GameState.SPLASH, GameState.START, GameState.CELEBRATION] or not self.fond_jeu_actuel:
            self.screen.blit(self.fond_degrade, (0, 0))
        else:
            self.screen.blit(self.fond_jeu_actuel, (0, 0))
        
        # 2. Scènes spécifiques
        if self.logic.etat == GameState.SPLASH:
            self.menu_renderer.dessiner_splash(self.logic.temps_debut_etat)
        elif self.logic.etat == GameState.START:
            self.menu_renderer.dessiner_menu(self.logic.total_decouvertes, self.db.status)
        elif self.logic.etat in [GameState.PLAYING_QUESTION, GameState.PLAYING_HINT]:
            self.game_renderer.dessiner_jeu(self.logic.donnees_session[self.logic.index_actuel], self.logic.etat)
        elif self.logic.etat == GameState.CELEBRATION:
            self.game_renderer.dessiner_victoire(self.logic.confettis, self.logic.session_decouvertes)

        pygame.display.flip()

    def lancer(self) -> None:
        """Boucle principale d'exécution."""
        print("🚀 Lancement du Prototype V1 (Session Senior)")
        while self.en_cours:
            self.orchestrer_entrees()
            self.logic.mettre_a_jour()
            self.dessiner()
            self.clock.tick(60)
        pygame.quit()

if __name__ == "__main__":
    app = GameApp()
    app.lancer()
