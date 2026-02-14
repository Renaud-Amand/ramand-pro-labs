import pygame
import sys
import os

pygame.init()

# 1. On crée d'abord l'écran et la police
screen = pygame.display.set_mode((1240, 960))
pygame.display.set_caption('Jeu Apprentissage Charlène')
ma_police = pygame.font.SysFont("Arial", 350) # On le met en très gros !
petite_police = pygame.font.SysFont("Arial", 100)
screen_rect = screen.get_rect()
hauteur = screen_rect.height

alphabet = [
    ("A", "Avion"), ("B", "Ballon"), ("C", "Chat"), ("D", "Dauphin"),
    ("E", "Etoile"), ("F", "Fleur"), ("G", "Gourde"), ("H", "Hibou"),
    ("I", "Ile"), ("J", "Jardin"), ("K", "Kangourou"), ("L", "Lion"),
    ("M", "Maison"), ("N", "Nuage"), ("O", "Oiseau"), ("P", "Poisson"),
    ("Q", "Quille"), ("R", "Robot"), ("S", "Soleil"), ("T", "Tortue"),
    ("U", "Univers"), ("V", "Velo"), ("W", "Wagon"), ("X", "Xylophone"),
    ("Y", "Yaourt"), ("Z", "Zebre")
]

index = 0
en_marche = True

while en_marche:
    # A. Le dessin (On efface et on dessine la lettre actuelle)
    screen.fill((255, 255, 255))
    
    lettre, objet = alphabet[index]

    #On définit le chemin de l'image
    chemin_image = f"images/{objet}.png"

    if os.path.exists(chemin_image):
        image_brute = pygame.image.load(chemin_image).convert_alpha()
        image_dessin = pygame.transform.scale(image_brute, (300, 300))
        rect_image = image_dessin.get_rect(centerx=screen_rect.centerx, centery = 180)
        rect_image.centerx = screen_rect.centerx
        rect_image.centery = hauteur * 0.25
        screen.blit(image_dessin, rect_image)
    else:
        pass
        

     # 1. On prépare la lettre (en gros)
    image_lettre = ma_police.render(lettre, True, (0, 0, 0))
    rect_lettre = image_lettre.get_rect()
    rect_lettre.centerx = screen_rect.centerx
    rect_lettre.centery = screen_rect.centery + 50
    screen.blit(image_lettre, rect_lettre) 
    
    image_objet = petite_police.render(objet, True, (50, 50, 50))
    rect_objet = image_objet.get_rect()
    rect_objet.centerx = screen_rect.centerx
    rect_objet.bottom = screen_rect.bottom -40
    screen.blit(image_objet, rect_objet)
    # B. On rafraîchit l'écran
    pygame.display.flip()

    # C. On attend un événement (Clavier ou quitter)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            en_marche = False
            
        elif event.type == pygame.KEYDOWN:
            # On change d'index seulement quand une touche est pressée !
             index = (index + 1) % len(alphabet)
            
pygame.quit()
sys.exit()




            