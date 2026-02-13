# On lance le moteur
import pygame
import sys

pygame.init()

# On crée la fenêtre
screen = pygame.display.set_mode((1240, 960))
pygame.display.set_caption('Jeu Apprentissage Charlène')

# On démarre avec boucle principal
en_marche = True

while en_marche:
    screen.fill((255, 255, 255))
        pygame.draw.rect(screen, (620, 480)) 
    
    pygame.display.flip()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            en_marche = False
                        
# On sort du jeu           
pygame.quit()
sys.exit()




            