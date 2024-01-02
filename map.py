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
        wall_img = pygame.image.load("images/wall.png")

        #pour modifier les valeurs
        self.exits = exits
        self.items_map = items_map
    
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
                elif str(tile)[0] == 'E':
                    #si c'est une sortie vers le bas ou la droite, il faut léger décallage pour afficher la porte
                    # if str(tile)[0] == 'X':
                    #     exit = Exit(col_count * tile_size + tile_size - 4, row_count * tile_size, tile, tile_size)
                    # elif str(tile)[0] == 'Y':
                    #     exit = Exit(col_count * tile_size, row_count * tile_size + tile_size - 4, tile, tile_size)
                    # else:
                    #     exit = Exit(col_count * tile_size, row_count * tile_size, tile, tile_size)
                    if row_count == 0:
                        exit = Exit(col_count * tile_size, row_count * tile_size, f'y{tile[1]}')
                    elif row_count == 17:
                        exit = Exit(col_count * tile_size, row_count * tile_size + tile_size - 4, f'Y{tile[1]}')
                    elif col_count == 0:
                        exit = Exit(col_count * tile_size, row_count * tile_size, f'x{tile[1]}')
                    elif col_count == 31:
                        exit = Exit(col_count * tile_size + tile_size - 4, row_count * tile_size, f'X{tile[1]}')
                    self.exits.append(exit)
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
    def __init__(self, x, y, val):
        img = pygame.image.load("images/exit.png")
        #en fonction de si la porte est à droite et à gauche ou en haut et en bas, la porte est un rectangle plus long en longueur ou en hauteur
        if val[0] in ["X", "x"]:
            self.image = pygame.transform.scale(img, (4, 40))
        elif val[0] in ['Y', 'y']:
            self.image = pygame.transform.scale(img, (40, 4))
        #les coordonnées
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        #la valeur d'une porte c'est un x ou y qui dit vers ou mène la porte, et un 1 chiffre qui indique quel niveau de pass il faut pour la franchir
        self.value = val
        
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
        self.rect.x = x
        self.rect.y = y

        #sa valeur (ex : un pass de niveau 3)
        self.value = image1[1:]
        #la salle dans laquelle il à été pris
        self.room = room

    def draw(self, screen):
        """dessiner l'item"""
        screen.blit(self.image, self.rect)