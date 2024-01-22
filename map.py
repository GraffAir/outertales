import pygame

class Map:
    """classe pour pouvoir dessiner la salle"""
    def __init__(self, liste, items, room_num, tile_size):
        """créer une liste contient les images et les coordonnées à dessiner"""
        self.tile_list = []
        #pour les portes de sorties
        exits = []

        #pour les items au sol
        items_map = []
        items_verifications = []
        counter = 0

        #charger les images des blocs
        mur_img = pygame.transform.scale(pygame.image.load("images/map/mur.png"), (tile_size, tile_size))
        coin_img = pygame.transform.scale(pygame.image.load("images/map/coin.png"), (tile_size, tile_size))       

        #pour modifier les valeurs
        self.exits, self.items_map = exits, items_map
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
                    x_, y_ = 0, 0
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
                            link = 3
                        elif row_count == 9:
                            exit_dir = "bottom"
                            link = 4
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
                            counter += 1
                    #et s'il n'a pas été ramassé, alors on l'ajoute à la liste des objets au sol à dessiner, et à considérer ses collisions
                    if counter == 0:
                        self.items_map.append(item)
                    counter = 0
                col_count += 1
            row_count += 1
    
    def replace(self):
        """une méthode pour pouvoir remplacer les variables"""
        return self.exits, self.items_map
    
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
            self.image = pygame.transform.scale(img, (4, 40))
        elif dir in ["left", "right"]:
            self.image = pygame.transform.scale(img, (40, 4))
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