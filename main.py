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

#les variables

#pour se réperer dans la liste des salles
room_x = 0
room_y = 0
#les portes de sorties à considérer en collisions
exits = []
#les items actuellement au sol
items_map = []
#les items détenus par le joueur
items = []
#le niveau de pass pour passer les portes
room_badge = 0
#la salle actuelle et son numéro d'identification
room = []
room_num = 1

#charger les images

#celle du sol
bg_img = pygame.transform.scale(pygame.image.load("images/floor.jpg"), (1280, 720))

class Player:
    """classe pour gérer le joueur (déplacements, animations, interactions...)"""
    def __init__(self, x, y):
        """choisir l'image du joueur, établir sa position de base..."""
        #définir les listes qui contiennent les images du joueur qu'on va animer
        self.images_walk_right = []
        self.images_walk_left = []
        self.images_walk_up = []
        self.images_walk_down = []

        #pour chaque liste, on a une série d'images, et on va faire en sorte que l'image du joueur varie d'une image à l'autre pour simuler un GIF
        for number in range(1, 5):
            img_right = pygame.transform.scale(pygame.image.load(f"images/player/player{number}.png"), (tile_size, tile_size))
            self.images_walk_right.append(img_right)
            img_left = pygame.transform.flip(img_right, True, False)
            self.images_walk_left.append(img_left)
            img_up = pygame.transform.rotate(img_right, 90)
            self.images_walk_up.append(img_up)
            img_down = pygame.transform.flip(img_up, False, True)
            self.images_walk_down.append(img_down)
        #on définir l'image de départ
        self.image = self.images_walk_right[0]

        #intervalle de temps entre le changement d'images
        self.animation_cooldown = 5
        #un compteur qui va augmenter pour parvenir au cooldown et revenir à 0, et ainsi créer une boucle temporelle
        self.counter = 0
        #l'indice de l'image à afficher
        self.index = 0
        self.direction = 1

        #pouvoir changer les coordonnées
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        #la vitesse de déplacement
        self.speed = 4

    def move_left(self):
        """gérer le déplacement vers la gauche"""
        self.dx -= self.speed
        self.counter += 1
        self.direction = -1
        
    def move_right(self):
        """gérer le déplacement vers la droite"""
        self.dx += self.speed
        self.counter += 1
        self.direction = 1
        
    def move_up(self):
        """gérer le déplacement vers le haut"""
        self.dy -= self.speed
        self.counter += 1
        self.direction = -2
        
    def move_down(self):
        """gérer le déplacement vers le bas"""
        self.dy += self.speed
        self.counter += 1
        self.direction = 2

    def change_animation(self):
        """changer l'animation selon la direction vers laquelle le joueur se dirige"""
        if self.direction == 1:
            self.image = self.images_walk_right[self.index]
        elif self.direction == -1:
            self.image = self.images_walk_left[self.index]
        elif self.direction == 2:
            self.image = self.images_walk_down[self.index]
        elif self.direction == -2:
            self.image = self.images_walk_up[self.index]

    def collisions_map(self, tile):
        """gérer les collisions avec les blocs"""
        #si le déplacement n'est pas possible car collisions, alors il ne se déplace pas
        if tile[1].colliderect(self.rect.x + self.dx, self.rect.y, self.image.get_width(), self.image.get_height()):
            self.dx = 0
        if tile[1].colliderect(self.rect.x, self.rect.y + self.dy, self.image.get_width(), self.image.get_height()):
            self.dy = 0
    
    def collisions_exits(self, exit):
        """gérer les collisions avec les sorties salles pour changer la salle affichée"""
        global room_x, room_y, room_badge
        if exit.rect.colliderect(self.rect.x + self.dx, self.rect.y + self.dy, self.image.get_width(), self.image.get_height()):
            #on vérifie si le joueur à le niveau de pass recquis
            if room_badge >= int(exit.value[1]):
                #en fonction de ou mène la porte, on attribue des coordonnées au joueur qui sont différentes
                if exit.value[0] == 'X':
                    room_x += 1
                    self.rect.x = 40
                elif exit.value[0] == 'x':
                    room_x -= 1
                    self.rect.x = 1280 - tile_size * 2
                elif exit.value[0] == 'Y':
                    room_y += 1
                    self.rect.y = 40
                elif exit.value[0] == 'y':
                    room_y -= 1
                    self.rect.y = 720 - tile_size * 2
            else:
                #si le joueur n'a pas un niveau de pass recquis, alors pas de déplacement
                if exit.value[0] in ["X", "x"]:
                    self.dx = 0
                elif exit.value[0] in ["Y", 'y']:
                    self.dy = 0

    def collisions_items(self, item):
        """les collisions avec les items au sols"""
        global items, items_map
        #si l'item est ramassé, on l'enleve des items au sols et on le rajoute dans l'inventaire
        if item.rect.colliderect(self.rect.x, self.rect.y, self.image.get_width(), self.image.get_height()):
            items.append(item)
            items_map.remove(item)

    def use_items(self):
        "une fois un item dans l'inventaire, on peut l'utiliser (une clé par exemple augmente le niveau de pass pour les sorties)"
        global items, room_badge
        keys = []

        for item in items:
            if item.value[0:3] == "key":
                keys.append(int(item.value[3]))
                room_badge = max(keys)

    def update(self):
        """gérer tous les évènements"""
        global room
        #les variables qui symbolise le déplacement qui sera réalisé si possible
        self.dx = 0
        self.dy = 0
        #on vérifie s'il appuie sur les touches de déplacements
        key = pygame.key.get_pressed()
        if key[pygame.K_UP]:
            self.move_up()
        if key[pygame.K_LEFT]:
            self.move_left()
        if key[pygame.K_DOWN]:
            self.move_down()
        if key[pygame.K_RIGHT]:
            self.move_right()
        if key[pygame.K_RIGHT] == False and key[pygame.K_LEFT] == False and key[pygame.K_UP] == False and key[pygame.K_DOWN] == False:
            self.index = 0
            self.counter = 0
            self.change_animation()
            
        #le changement d'animation
        if self.counter > self.animation_cooldown:
            self.counter = 0
            self.index += 1
            if self.index >= len(self.images_walk_right):
                self.index = 0
            self.change_animation()
            
        #les collisions  
        for tile in room_draw.tile_list:
            self.collisions_map(tile)
        
        #gérer les collisions avec les portes de sorties
        for exit in exits:
            self.collisions_exits(exit)

        #et le collisions avec les items au sol
        for item in items_map:
            self.collisions_items(item)
        
        #on utilise les items
        self.use_items()

        #déplacer le joueur et le dessiner
        self.rect.x += self.dx
        self.rect.y += self.dy
        screen.blit(self.image, self.rect)
        
class Map:
    """classe pour pouvoir dessiner la room"""
    def __init__(self, liste):
        """créer une liste contient les images et les coordonnées à dessiner"""
        global exits, items_map, items, room_x, room_y, rooms, room, room_num
        self.tile_list = []
        #pour les portes de sorties
        exits = []

        #pour les items au sol
        items_map = []
        items_verifications = []
        counter = 0

        #charger les images des blocs
        wall_img = pygame.image.load("images/wall.png")
    
        #parcourir la liste
        row_count = 0
        for row in liste:
            col_count = 0
            for tile in row:
                #pour chaque case
                #si c'est un 1, alors c'est un mur
                if tile == 1:
                    img = pygame.transform.scale(wall_img, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                #si elle commence par x, X, y ou Y, alors c'est une porte vers une autre salle
                elif str(tile)[0] in ["x", "X", "y", "Y"]:
                    #si c'est une sortie vers le bas ou la droite, il faut léger décallage pour afficher la porte
                    if str(tile)[0] == 'X':
                        exit = Exit(col_count * tile_size + tile_size - 4, row_count * tile_size, tile)
                    elif str(tile)[0] == 'Y':
                        exit = Exit(col_count * tile_size, row_count * tile_size + tile_size - 4, tile)
                    else:
                        exit = Exit(col_count * tile_size, row_count * tile_size, tile)
                    exits.append(exit)
                #si elle commence par un O, c'est un objet ramassable
                elif str(tile)[0] == 'O':
                    item = Item(col_count * tile_size, row_count * tile_size, tile, room_num)
                    #créer une liste contenants les coordonnées et la salle de chaque objet DEJA RAMASSE
                    for it in items:
                        #ajouter les items ramassé qui ne sont pas dans la liste 
                        if [it.rect.x, it.rect.y, it.room] not in items_verifications:
                            items_verifications.append([it.rect.x, it.rect.y, it.room])
                    #pour chaque item sur le sol, il vérifie s'il en existe deja un semblable dans l'inventaire (avec les coordonnées et le numéro de salle : il ne peut y en avoir qu'un qui y correspond, à savoir le même, qui serait deja ramassé)
                    for index in range(len(items_verifications)):
                        if [item.rect.x, item.rect.y, item.room] == items_verifications[index]:
                            #ajoute 1 au compteur si l'item à déja été pris
                            counter += 1
                    #et s'il n'a pas été ramassé, alors on l'ajoute à la liste des objets au sol à dessiner, et à considérer ses collisions
                    if counter == 0:
                        items_map.append(item)
                    counter = 0
                col_count += 1
            row_count += 1

    def draw(self):
        """méthode pour dessiner cette liste qui contient toutes les coordonnées et les images des blocs à placer"""
        for tile in self.tile_list:
            screen.blit(tile[0], tile[1])

class Exit:
    """classe pour gérer les changements de salle"""
    def __init__(self, x, y, val):
        img = pygame.image.load("images/exit.png")
        #en fonction de si la porte est à droite et à gauche ou en haut et en bas, la porte est un rectangle plus long en longueur ou en hauteur
        if val[0] in ["X", "x"]:
            self.image = pygame.transform.scale(img, (4, tile_size))
        elif val[0] in ['Y', 'y']:
            self.image = pygame.transform.scale(img, (tile_size, 4))
        #les coordonnées
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        #la valeur d'une porte c'est un x ou y qui dit vers ou mène la porte, et un 1 chiffre qui indique quel niveau de pass il faut pour la franchir
        self.value = val
        
    def draw(self):
        """dessiner la porte de sortie"""
        screen.blit(self.image, self.rect)

class Item:
    """classe pour gérer les objets au sol récupérable"""
    def __init__(self, x, y, image1, room):
        #l'image
        img = pygame.image.load(f"images/{image1[1:]}.png")
        self.image = pygame.transform.scale(img, (tile_size, tile_size))
        #les coordonnées
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        #sa valeur (ex : un pass de niveau 3)
        self.value = image1[1:]
        #la salle dans laquelle il à été pris
        self.room = room

    def draw(self):
        """dessiner l'item"""
        screen.blit(self.image, self.rect)

def import_rooms():
    """fonction pour importer toutes nos salles"""
    global rooms
    if path.exists(f"rooms/room1.bin"):
        pickle_in = open(f"rooms/room1.bin", "rb")
        room1 = pickle.load(pickle_in)
    if path.exists(f"rooms/room2.bin"):
        pickle_in = open(f"rooms/room2.bin", "rb")
        room2 = pickle.load(pickle_in)
    if path.exists(f"rooms/room3.bin"):
        pickle_in = open(f"rooms/room3.bin", "rb")
        room3 = pickle.load(pickle_in)
    if path.exists(f"rooms/room4.bin"):
        pickle_in = open(f"rooms/room4.bin", "rb")
        room4 = pickle.load(pickle_in)
    rooms = [
    [room1, room2],
    [room3, room4]
    ]

#on importe les salles
import_rooms()

#on définit la salle de base et on la dessine
room = rooms[room_y][room_x]
room_draw = Map(room)

#on initialise le joueur
player = Player(40, 40)

#lancer la boucle du jeu
run = True
while run:
    #régler la clock sur 60 fps
    clock.tick(fps)

    #changer de map si nécessaire
    if room != rooms[room_y][room_x]:
        room = rooms[room_y][room_x]
        #changer le numéro de salle
        row_count = 0
        compter = 1
        for row in rooms:
            col_count = 0
            for rooma in row:
                if rooma == rooms[room_y][room_x]:
                    room_num = compter
                compter += 1
                col_count += 1
            row_count += 1
        #la dessiner maintenant
        room_draw = Map(room)

    #afficher le sol
    screen.blit(bg_img, (0, 0))

    #dessine la map
    room_draw.draw()

    #afficher les portes de sortie
    for exit in exits:
        exit.draw()

    #afficher les items
    for item in items_map:
        item.draw()

    #mettre à jour le joueur
    player.update()
    
    #permet de  quitter le jeu
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    #rafrachir l'écran
    pygame.display.update()

pygame.quit()