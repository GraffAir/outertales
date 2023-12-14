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
screen = pygame.display.set_mode((1280, 720))
pygame.display.set_caption("Outer Tales")
tile_size = 40

class Player(pygame.sprite.Sprite):
    """classe pour gérer le joueur (déplacements, animations, interactions...)"""
    def __init__(self, x, y):
        """choisir l'image du joueur, établir sa position de base..."""
        self.image = pygame.transform.scale(pygame.image.load("personnage.png"), (40, 40))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = 2.5

    def move_left(self):
        """gérer le déplacement vers la gauche"""
        self.dx -= self.speed * 1.2 #on * par 1.2 car sinon, la vitesse est moins rapide que vers la droite
    
    def move_right(self):
        """gérer le déplacement vers la droite"""
        self.dx += self.speed
        
    def move_up(self):
        """gérer le déplacement vers le haut"""
        self.dy -= self.speed * 1.2 #on * par 1.2 car sinon, la vitesse est moins rapide que vers la droite
        
    def move_down(self):
        """gérer le déplacement vers le bas"""
        self.dy += self.speed
        
    def update(self):
        """gérer tous les évènements"""
        self.dx = 0
        self.dy = 0
        key = pygame.key.get_pressed()
        if key[pygame.K_UP] or key[pygame.K_z]:
            self.move_up()
        if key[pygame.K_DOWN] or key[pygame.K_s]:
            self.move_down()
        if key[pygame.K_LEFT] or key[pygame.K_q]:
            self.move_left()
        if key[pygame.K_RIGHT] or key[pygame.K_d]:
            self.move_right()
            
        self.rect.x += self.dx
        self.rect.y += self.dy
        screen.blit(self.image, self.rect)
        
class Map:
    """classe pour pouvoir dessiner la room"""
    def __init__(self, liste):
        """créer une liste contient les images et les coordonnées à dessiner"""
        self.tiles_list = []
        #charger les images des blocs
        mur_img = pygame.image.load("mur.png")
        
        row_count = 0
        for row in liste:
            col_count = 0
            for tile in row:
                if tile == 1:
                    img = pygame.transform.scale(mur_img, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tiles_list.append(tile)
                col_count += 1
            row_count += 1

    def draw(self):
        """méthode pour dessiner cette liste qui contient toutes les coordonnées et les images des blocs à placer"""
        for tile in self.tiles_list:
            screen.blit(tile[0], tile[1])
            
#importer la première room
def import_room(numero):
    """importer le fichier binaire qui contient la liste de la salle"""
    if path.exists(f"room{numero}.bin"):
        pickle_in = open(f"room{numero}.bin", "rb")
        room = pickle.load(pickle_in)
    return Map(room)

bg_img = pygame.transform.scale(pygame.image.load("herbe.jpg"), (1280, 720))
player = Player(50, 50)
player_group = pygame.sprite.Group()

#lancer la boucle du jeu
run = True
while run:
    clock.tick(fps)
    screen.blit(bg_img, (0, 0))
    import_room(1).draw()
    player.update()
    #permet de  quitter le jeu
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
    #rafrachir l'écran
    pygame.display.update()
pygame.quit()