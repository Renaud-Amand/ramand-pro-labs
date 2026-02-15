import pygame
import sys
import os
import random

pygame.init()
pygame.mixer.init()

# 1. Configuration de l'écran et des polices
screen = pygame.display.set_mode((1240, 960))
pygame.display.set_caption("Jeu Apprentissage Charlène")

# Correction du nom de la police (sans l'espace à la fin)
ma_police = pygame.font.SysFont("Comic Sans MS", 350)
petite_police = pygame.font.SysFont("Comic Sans MS", 100)

screen_rect = screen.get_rect()
hauteur = screen_rect.height

alphabet = [
    ("A", "Avion"),
    ("B", "Ballon"),
    ("C", "Chat"),
    ("D", "Dauphin"),
    ("E", "Etoile"),
    ("F", "Fleur"),
    ("G", "Gourde"),
    ("H", "Hibou"),
    ("I", "Ile"),
    ("J", "Jardin"),
    ("K", "Kangourou"),
    ("L", "Lion"),
    ("M", "Maison"),
    ("N", "Nuage"),
    ("O", "Oiseau"),
    ("P", "Poisson"),
    ("Q", "Quille"),
    ("R", "Robot"),
    ("S", "Soleil"),
    ("T", "Tortue"),
    ("U", "Univers"),
    ("V", "Velo"),
    ("W", "Wagon"),
    ("X", "Xylophone"),
    ("Y", "Yaourt"),
    ("Z", "Zebre"),
]

# Initialisation des confettis sur toute la largeur (1240)
confettis = []
for i in range(70):
    confettis.append(
        [
            random.randint(0, 1240),
            random.randint(-400, 0),
            (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)),
            random.randint(2, 5),
        ]
    )

# Variables de contrôle
en_marche = True
fete_active = False
compteur_fete = 0
index = 0

# Couleurs
BLEU_ROI = (65, 105, 225)
BEIGE_DOUX = (245, 245, 220)
ROSE = (255, 240, 245)
BLANC = (255, 255, 255)

# --- BOUCLE PRINCIPALE ---
while en_marche:
    screen.fill(ROSE)

    if index < len(alphabet):
        # --- MODE APPRENTISSAGE ---
        lettre, objet = alphabet[index]

        # Dessin de l'image et de sa pastille
        chemin_image = f"images/{objet}.png"
        if os.path.exists(chemin_image):
            image_brute = pygame.image.load(chemin_image).convert_alpha()
            image_dessin = pygame.transform.scale(image_brute, (350, 350))
            rect_image = image_dessin.get_rect(
                centerx=screen_rect.centerx, centery=hauteur * 0.25
            )

            # La pastille blanche
            pygame.draw.circle(
                screen, BLANC, rect_image.center, 200
            )  # Un peu plus grand (200)
            screen.blit(image_dessin, rect_image)

        # Dessin de la lettre
        image_lettre = ma_police.render(lettre, True, BLEU_ROI)
        rect_lettre = image_lettre.get_rect(
            centerx=screen_rect.centerx, centery=screen_rect.centery + 50
        )
        screen.blit(image_lettre, rect_lettre)

        # Dessin du mot
        image_objet = petite_police.render(objet, True, BLEU_ROI)
        rect_objet = image_objet.get_rect(
            centerx=screen_rect.centerx, bottom=screen_rect.bottom - 40
        )
        screen.blit(image_objet, rect_objet)

    else:
        # --- MODE RÉCOMPENSE ---
        texte_bravo = ma_police.render("Bravo !", True, (255, 0, 100))
        rect_bravo = texte_bravo.get_rect(
            center=(screen_rect.centerx, screen_rect.centery)
        )
        screen.blit(texte_bravo, rect_bravo)

        texte_info = petite_police.render("Appuie pour recommencer", True, (0, 0, 0))
        rect_info = texte_info.get_rect(
            center=(screen_rect.centerx, screen_rect.centery + 300)
        )
        screen.blit(texte_info, rect_info)

    # Gestion des confettis (toujours devant)
    if fete_active:
        for c in confettis:
            c[1] += c[3]
            pygame.draw.rect(screen, c[2], (c[0], c[1], 12, 12))
            if c[1] > 960:
                c[1] = random.randint(-100, -10)
                c[0] = random.randint(0, 1240)

    pygame.display.flip()

    # --- GESTION DES ÉVÉNEMENTS ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            en_marche = False

        elif event.type == pygame.KEYDOWN:
            index += 1
            if index == len(alphabet):
                fete_active = True
                compteur_fete = 0
            elif index > len(alphabet):
                index = 0
                fete_active = False

pygame.quit()
sys.exit()
