import pygame

class Map:
    """classe pour pouvoir dessiner la salle"""
    def __init__(self, liste, items, chests, room_num, tile_size):
        """créer une liste contient les images et les coordonnées à dessiner"""
        self.tile_list = []

        #pour les items au sol
        item_already = False
        chest_already = False

        #charger les images des blocs
        mur_img = pygame.transform.scale(pygame.image.load("images/map/mur.png"), (tile_size, tile_size))
        coin_img = pygame.transform.scale(pygame.image.load("images/map/coin.png"), (tile_size, tile_size))

        #pour modifier les valeurs, les sorties, les itemms
        self.exits, self.items_map, items_verifications, chests_ver, self.signs, self.chests = [], [], [], [], [], []

        #pour les portes de sorties
        exit_dir = 'left'
        x_ = 0
        y_ = 0
        #parcourir la liste
        row_count = 0
        for row in liste:
            col_count = 0
            for tile in row:
                #pour chaque case
                #si c'est un 1, alors c'est un mur
                if tile == 1:
                    if row_count == 0 and col_count == 0:
                        img = coin_img
                    elif row_count == 0 and col_count == 31:
                        img = pygame.transform.rotate(coin_img, -90)
                    elif row_count == 17 and col_count == 0:
                        img = pygame.transform.rotate(coin_img, 90)
                    elif row_count == 17 and col_count == 31:
                        img = pygame.transform.rotate(coin_img, 180)
                    elif row_count == 0 and (0 < col_count < 31):
                        img = pygame.transform.rotate(mur_img, 180)
                    elif (0 < row_count < 17) and col_count == 0:
                        img = pygame.transform.rotate(mur_img, -90)
                    elif row_count == 17 and (0 < col_count < 31):
                        img = mur_img
                    elif (0 < row_count < 17) and col_count == 31:
                        img = pygame.transform.rotate(mur_img, 90)
                    img_rect = img.get_rect()
                    img_rect.x, img_rect.y = col_count * tile_size, row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                #si elle commence par x, X, y ou Y, alors c'est une porte vers une autre salle
                elif str(tile)[0] == "E":
                    x_, y_, link = 0, 0, 0
                    if row_count == 0 or row_count == 17:
                        if col_count == 15:
                            exit_dir = "left"
                        elif col_count == 16:
                            exit_dir = "right"
                    if row_count == 0:
                        y_ = tile_size - 4
                    elif col_count == 0 or col_count == 31:
                        if row_count == 8:
                            exit_dir = "top"
                        elif row_count == 9:
                            exit_dir = "bottom"
                    if col_count == 0:
                        x_ = tile_size - 4
                    if row_count == 0:
                        link = 1
                    elif row_count == 15:
                        link = 2
                    elif col_count == 0:
                        link = 3
                    elif col_count == 31:
                        link = 4
                    exit = Exit(col_count * tile_size + x_, row_count * tile_size + y_, exit_dir, tile[1], link)
                    self.exits.append(exit)
                #si elle commence par un O, c'est un objet ramassable
                elif str(tile)[0] == "O":
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
                            item_already = True
                    #et s'il n'a pas été ramassé, alors on l'ajoute à la liste des objets au sol à dessiner, et à considérer ses collisions
                    if item_already == False:
                        self.items_map.append(item)
                    item_already = False
                elif str(tile)[0] == "S":
                    img = pygame.transform.scale(pygame.image.load(f"images/signs/sign{str(tile)[1]}.png"), (1000, 500))       
                    img_rect = img.get_rect()
                    img_rect.x, img_rect.y = col_count * tile_size, row_count * tile_size
                    sign = Sign(img, img_rect.x, img_rect.y)
                    self.signs.append(sign)
                elif isinstance(tile, tuple):
                    if tile [0] == "C":
                        chest = Chest(col_count * tile_size, row_count * tile_size, tile[1], tile[2], room_num)
                        #créer une liste contenants les coordonnées et la salle de chaque objet DEJA RAMASSE
                        for ch in chests:
                            #ajouter les items ramassé qui ne sont pas dans la liste 
                            if [ch.rect.x, ch.rect.y, ch.room] not in chests_ver:
                                chests_ver.append([ch.rect.x, ch.rect.y, ch.room])
                        #pour chaque item sur le sol, il vérifie s'il en existe deja un semblable dans l'inventaire (avec les coordonnées et le numéro de salle : il ne peut y en avoir qu'un qui y correspond, à savoir le même, qui serait deja ramassé)
                        for index in range(len(chests_ver)):
                            if [chest.rect.x, chest.rect.y, chest.room] == chests_ver[index]:
                                #ajoute 1 au compteur si l'item à déja été pris
                                chest_already = True
                        #et s'il n'a pas été ramassé, alors on l'ajoute à la liste des objets au sol à dessiner, et à considérer ses collisions
                        if chest_already == False:
                            self.chests.append(chest)
                        chest_already = False
                col_count += 1
            row_count += 1
    
    def replace(self):
        """une méthode pour pouvoir remplacer les variables"""
        return self.exits, self.items_map, self.signs, self.chests
    
    def draw(self, screen):
        """méthode pour dessiner cette liste qui contient toutes les coordonnées et les images des blocs à placer"""
        for tile in self.tile_list:
            screen.blit(tile[0], tile[1])

class Exit:
    """classe pour gérer les changements de salle"""
    def __init__(self, x, y, dir, val, link):
        img = pygame.image.load("images/exit.png")
        #en fonction de si la porte est à droite et à gauche ou en haut et en bas, la porte est un rectangle plus long en longueur ou en hauteur
        if dir in ["top", "bottom"]: #On répère l'image à dessiner en fonction du point cardinal O, E, S, N
            self.image = pygame.transform.scale(img, (7, 40))
        elif dir in ["left", "right"]:
            self.image = pygame.transform.scale(img, (40, 7))
        #les coordonnées
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y
        #la valeur d'une porte c'est un chiffre qui indique quel niveau de pass il faut pour la franchir
        self.value = val
        #pour indiquer vers ou mène la porte, et a quel groupe elle appartient
        self.direction = dir
        self.link = link
        #définir la position de départ et celle d'arrivée
        self.start_pos = (x, y)
        if self.direction == 'right':
            self.end_pos = (x + 40, y)
        elif self.direction == 'left':
            self.end_pos = (x - 40, y)
        elif self.direction == 'top':
            self.end_pos = (x, y - 40)
        elif self.direction == 'bottom':
            self.end_pos = (x, y + 40)
        #variables pour l'ouverture des portes
        self.open = False
        self.counter = 0
        self.go_back = False
        self.collisions_counter = 0
        
    def open_door(self):
        """ouvrir la porte"""
        if self.direction == 'top':
            self.dy = -1
        elif self.direction == "bottom":
            self.dy = 1
        elif self.direction == "left":
            self.dx = -1
        elif self.direction == "right":
            self.dx = 1

    def close_door(self):
        """fermer la porte"""
        if self.direction == 'top':
            self.dy = 1
        elif self.direction == "bottom":
            self.dy = -1
        elif self.direction == "left":
            self.dx = 1
        elif self.direction == "right":
            self.dx = -1

    def check_collisions_player(self, player):
        """vérifier les colisions avec le joueur"""
        if player.rect.colliderect(self.rect.x + self.dx, self.rect.y + self.dy, self.image.get_width(), self.image.get_height()):
            self.dx, self.dy = 0, 0
            self.collisions_counter += 1

    def reset(self):
        """remettre à 0 certaines variables une fois la porte refermé"""
        self.counter = 0
        self.go_back, self.open = False, False
        self.collisions_counter = 0

    def update(self, player):
        """methode pour faire déplacer les portes, et les faire revenir à leurs positions"""
        self.dx, self.dy = 0, 0

        #ouvrir la porte
        if self.open == True and self.go_back == False:
            self.open_door()

        #déplacer la porte dans l'autre sens, une fois la position de fin atteinte
        if self.end_pos == (self.rect.x + self.dx, self.rect.y + self.dy):
            self.go_back = True

        if self.open == True and self.go_back == True:
            self.counter += 1
            if self.counter >= 150:
                self.close_door()
                self.check_collisions_player(player)

        self.rect.x += self.dx
        self.rect.y += self.dy

        #si la porte est réfermé, remettre à 0 les variables
        if self.start_pos == (self.rect.x, self.rect.y):
            self.reset()

    def draw(self, screen):
        """dessiner la porte de sortie"""
        screen.blit(self.image, self.rect)

class Item:
    """classe pour gérer les objets au sol récupérable"""
    def __init__(self, x, y, image1, room):
        #l'image
        img = pygame.image.load(f"images/{image1[1:]}.png")
        self.image = pygame.transform.scale(img, (40, 40))
        #les coordonnées
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y

        #sa valeur (ex : un pass de niveau 3)
        self.value = image1[1:]
        #la salle dans laquelle il à été pris
        self.room = room

    def draw(self, screen):
        """dessiner l'item"""
        screen.blit(self.image, self.rect)
    
class Sign:
    def __init__(self, img2, x, y):
        self.image = pygame.transform.scale(pygame.image.load("images/signs/sign.png"), (40, 40))    
        self.rect = self.image.get_rect()   
        self.rect.x = x
        self.rect.y = y
        self.image2 = img2
        self.rect2 = self.image2.get_rect()
        self.rect2.x = 140
        self.rect2.y = 110
        self.draw = False

    def draw_item(self, screen):
        screen.blit(self.image, self.rect)

    def draw_(self, screen):
        screen.blit(self.image2, self.rect2)

class Chest:
    def __init__(self, x, y, chest, contenu, room_num):
        self.image = pygame.transform.scale(pygame.image.load(f"images/{chest}.png"), (40, 40))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.contenu = Item(x, y, contenu, room_num)
        self.open = False
        self.room = room_num

    def draw(self, screen):
        screen.blit(self.image, self.rect)
    
    def draw_item(self, screen):
        screen.blit(self.contenu.image, self.contenu.rect)
