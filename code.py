#importer les bibliothèques / modules
import pygame
from pygame.locals import*
import pickle
from os import path
#initialiser pygame
pygame.init()
clock = pygame.time.Clock()
fps = 60
#configurer la fenêtre et la taille des cases
fenetre = pygame.display.set_mode((1280, 720))
pygame.display.set_caption("Outer Tales")
taille_case = 40

class Joueur(pygame.sprite.Sprite):
    """classe pour gérer le joueur (déplacements, animations, interactions...)"""
    def __init__(self, x, y):
        """choisir l'image du joueur, établir sa position de base..."""
        self.image = pygame.transform.scale(pygame.image.load("personnage.png"), (40, 40))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
    
    def deplacements(self):
        """gérer ses déplacements ainsi que les animations"""
        dx = 0
        dy = 0
        vitesse = 2.5
        
        key = pygame.key.get_pressed()
        if key[pygame.K_UP] or key[pygame.K_z]:
            dy -= vitesse * 1.2 #on * par 1.2 car sinon, la vitesse est moins rapide que vers le bas
        if key[pygame.K_DOWN] or key[pygame.K_s]:
            dy += vitesse
        if key[pygame.K_LEFT] or key[pygame.K_q]:
            dx -= vitesse * 1.2 #on * par 1.2 car sinon, la vitesse est moins rapide que vers la droite
        if key[pygame.K_RIGHT] or key[pygame.K_d]:
            dx += vitesse

        self.rect.y += dy
        self.rect.x += dx
        
        fenetre.blit(self.image, self.rect)
        
class Map:
    """classe pour pouvoir dessiner la salle"""
    def __init__(self, liste):
        """créer une liste contient les images et les coordonnées à dessiner"""
        self.liste_cases = []
        #charger les images des blocs
        mur_img = pygame.image.load("mur.png")
        
        lignes_count = 0
        for lignes in liste:
            col_count = 0
            for case in lignes:
                if case == 1:
                    img = pygame.transform.scale(mur_img, (taille_case, taille_case))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * taille_case
                    img_rect.y = lignes_count * taille_case
                    case = (img, img_rect)
                    self.liste_cases.append(case)
                col_count += 1
            lignes_count += 1

    def draw(self):
        """méthode pour dessiner cette liste qui contient toutes les coordonnées et les images des blocs à placer"""
        for case in self.liste_cases:
            fenetre.blit(case[0], case[1])
            
#importer la première salle
def import_salle(numero):
    """importer le fichier binaire qui contient la liste de la salle"""
    if path.exists(f"salle{numero}.bin"):
        pickle_in = open(f"salle{numero}.bin", "rb")
        salle = pickle.load(pickle_in)
    return Map(salle)

bg_img = pygame.transform.scale(pygame.image.load("herbe.jpg"), (1280, 720))
joueur = Joueur(50, 50)
joueur_group = pygame.sprite.Group()

#lancer la boucle du jeu
run = True
while run:
    clock.tick(fps)
    fenetre.blit(bg_img, (0, 0))
    import_salle(1).draw()
    joueur.deplacements()
    #joueur_group.draw(fenetre)
    #permet de  quitter le jeu
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
    #rafrachir l'écran
    pygame.display.update()

pygame.quit()