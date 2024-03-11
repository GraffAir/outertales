import pygame

class Player:
    """classe pour gérer le joueur (déplacements, animations, interactions...)"""
    def __init__(self, x, y):
        """choisir l'image du joueur, établir sa position de base..."""
        #définir les listes qui contiennent les images du joueur qu'on va animer
        self.images_walk_right, self.images_walk_left, self.images_walk_up, self.images_walk_down = [], [], [], []

        #pour chaque liste, on a une série d'images, et on va faire en sorte que l'image du joueur varie d'une image à l'autre pour simuler un GIF
        for number in range(1, 4):
            img_right = pygame.transform.scale(pygame.image.load(f"images/player/right{number}.png"), (40, 40)).convert_alpha()
            self.images_walk_right.append(img_right)
            img_left = pygame.transform.scale(pygame.image.load(f"images/player/left{number}.png"), (40, 40)).convert_alpha()
            self.images_walk_left.append(img_left)
            img_up = pygame.transform.scale(pygame.image.load(f"images/player/up{number}.png"), (40, 40)).convert_alpha()
            self.images_walk_up.append(img_up)
            img_down = pygame.transform.scale(pygame.image.load(f"images/player/down{number}.png"), (40, 40)).convert_alpha()
            self.images_walk_down.append(img_down)
        #on définir l'image de départ
        self.image = self.images_walk_right[0]

        #intervalle de temps entre le changement d'images
        self.animation_cooldown = 6
        #un compteur qui va augmenter pour parvenir au cooldown et revenir à 0, et ainsi créer une boucle temporelle
        self.counter = 0
        #l'indice de l'image à afficher
        self.index = 0
        self.direction = 1

        #pouvoir changer les coordonnées
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y

        #la vitesse de déplacement
        self.speed = 4

        #pour les panneaux
        self.sign_counter = 50
        self.chest_counter = 50

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
    
    def collisions(self, instance):
        dx_test, dy_test = self.dx, self.dy
        if instance.colliderect(self.rect.x + self.dx, self.rect.y, self.image.get_width(), self.image.get_height()) == False:
            if instance.colliderect(self.rect.x + self.dx, self.rect.y + self.dy, self.image.get_width(), self.image.get_height()):
                if instance[0] != self.rect.x + instance[2] and instance[1] != self.rect.y - instance[3]:
                    dy_test = 0
        else:
            dx_test = 0
        if instance.colliderect(self.rect.x, self.rect.y + self.dy, self.image.get_width(), self.image.get_height()) == False:
            if instance.colliderect(self.rect.x + self.dx, self.rect.y + self.dy, self.image.get_width(), self.image.get_height()):
                if instance[0] != self.rect.x - instance[2] and instance[1] != self.rect.y + instance[3]:
                    dx_test = 0
        else:
            dy_test = 0
        self.dx, self.dy = dx_test, dy_test

    def collisions_map(self, tile):
        """gérer les collisions avec les blocs"""
        #si le déplacement n'est pas possible car collisions, alors il ne se déplace pas
        self.collisions(tile[1])

    def collisions_exits(self, exit, electricity, screen):
        """gérer les collisions avec les sorties salles pour changer la salle affichée"""
        #s'il y a de l'electricité
        if electricity:
            if exit.rect.colliderect(self.rect.x + self.dx - 40, self.rect.y + self.dy - 40, self.image.get_width() + 80, self.image.get_height() + 80):
                #on vérifie si le joueur à le niveau de pass requis
                if exit.breakable == False and exit.open == False and self.room_badge >= int(exit.value):
                    screen.blit(pygame.transform.scale(pygame.image.load("images/tell.png"), (300, 40)).convert_alpha(), (940, 40))
                if self.room_badge >= int(exit.value) and pygame.key.get_pressed()[pygame.K_e]:
                    #en fonction de ou mène la porte, on attribue des coordonnées au joueur qui sont différentes
                    exit.open = True
                    #si le joueur n'a pas un niveau de pass requis, alors pas de déplacement
                if exit.breakable == True:
                    exit.open = True
        else:
            for item in self.items:
                if item.value == "hammer":
                    if exit.rect.colliderect(self.rect.x + self.dx - 1, self.rect.y + self.dy - 1, self.image.get_width() + 2, self.image.get_height() + 2):
                        if exit.breakable and exit.open == False:
                            screen.blit(pygame.transform.scale(pygame.image.load("images/tell.png"), (300, 40)).convert_alpha(), (940, 40))
                            if pygame.key.get_pressed()[pygame.K_e]:
                                exit.open = True
                                exit.rect.x, exit.rect.y = exit.end_pos

        self.collisions(exit.rect)

    def collisions_items(self, item):
        """les collisions avec les items au sols"""
        #si l'item est ramassé, on l'enleve des items au sols et on le rajoute dans l'inventaire
        if item.chest == True and item.chest_open == True:
            if item.rect.colliderect(self.rect.x - 1, self.rect.y - 9, self.image.get_width() + 2, self.image.get_height() + 18):
                if pygame.key.get_pressed()[pygame.K_e]:
                    self.items.append(item)
                    self.items_map.remove(item)
        else:
            if item.rect.colliderect(self.rect.x, self.rect.y, self.image.get_width(), self.image.get_height()):
                self.items.append(item)
                self.items_map.remove(item)
        
    def collisions_signs(self, sign):
        """les collisisons avec les panneaux"""
        if sign.rect_item.colliderect(self.rect.x + self.dx, self.rect.y + self.dy, self.image.get_width(), self.image.get_height()):
            if self.sign_counter >= 50:
                if pygame.key.get_pressed()[pygame.K_e]:
                    if sign.draw == False:
                        sign.draw = True
                    else:
                        sign.draw = False
                    self.sign_counter = 0
        self.sign_counter += 1
        
    def collisions_chests(self, chest):
        '''les collisions avec les coffres'''
        if chest.rect.colliderect(self.rect.x + self.dx - 1, self.rect.y + self.dy - 1, self.image.get_width() + 2, self.image.get_height() + 2):
            if pygame.key.get_pressed()[pygame.K_e]:
                if chest.open == False:
                    if chest.locked == False:
                        chest.open = True
                        self.chests.remove(chest)
                        self.chests_open.append(chest)
                        if chest.contenu != "":
                            self.items_map.append(chest.contenu)
                    else:
                        self.lock = True
                        chest.try_open = True
                elif chest.open:
                    #si on ouvre le coffre, ajouter l'item dans l'inventaire
                    if chest.room == self.room_num:
                        if chest.item_took == False:
                            if chest.contenu != "":
                                if chest.item_cooldown == True:
                                    chest.contenu.chest_open = True
                                    chest.item_took = True
                            else:
                                chest.item_took = True
                            self.chest_counter = 0
                        else:
                            if self.chest_counter >= 50:
                                if chest.watched_cooldown:
                                    chest.watched = True
                                    self.chest_counter = 0
                                    chest.watched_cooldown = False
        self.chest_counter += 1
        if chest.room == self.room_num:
            self.collisions(chest.rect)

    def collisions_props(self, prop):
        '''les collisions avec les coffres'''
        self.collisions(prop.rect)

    def use_items(self):
        "une fois un item dans l'inventaire, on peut l'utiliser (une clé par exemple augmente le niveau de pass pour les sorties)"
        keys = []
        for item in self.items:
            if item.value[0:3] == "key":
                keys.append(int(item.value[3]))
                self.room_badge = max(keys)

    def change_room(self):
        '''changer la room si le joueur sort des limites'''
        if self.rect.x > 1240:
            self.room_x += 1
            self.rect.x = 40
        elif self.rect.x < 0:
            self.room_x -= 1
            self.rect.x = 1280 - 40 * 2
        elif self.rect.y > 680:
            self.room_y += 1
            self.rect.y = 40
        elif self.rect.y < 0:
            self.room_y -= 1
            self.rect.y = 720 - 40 * 2

    def update(self, screen, room_draw, items, items_map, exits, signs, chests, chests_open, room_badge, room_num, room_x, room_y, electricity, props):
        """gérer tous les évènements"""
        #on crée un objet avec self pour pouvoir changer les variables avec la méthode replace
        self.exits, self.items_map, self.items, self.chests, self.chests_open, self.room_badge, self.room_num, self.room_x, self.room_y = exits, items_map, items, chests, chests_open, room_badge, room_num, room_x, room_y
        self.lock = False
        #les variables qui symbolise le déplacement qui sera réalisé si possible
        self.dx, self.dy = 0, 0
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
        for exit in self.exits:
            self.collisions_exits(exit, electricity, screen)
            for exit_ in self.exits:
                if electricity == False:
                    if exit.link == exit_.link:
                        if (exit.rect.x, exit.rect.y) == exit.end_pos:
                            exit_.rect.x, exit_.rect.y = exit_.end_pos

        #et le collisions avec les items au sol
        for item in self.items_map:
            self.collisions_items(item)

        #les collisions avec les panneaux, les coffres ouverts et fermés
        for sign in signs:
            self.collisions_signs(sign)

        for chest in chests:
            self.collisions_chests(chest)
        
        for chest in chests_open:
            self.collisions_chests(chest)

        for prop in props:
            self.collisions_props(prop)
        
        #on utilise les items
        self.use_items()

        #on fait changer le joueur de room si besoin
        self.change_room()

        #déplacer le joueur et le dessiner
        self.rect.x += self.dx
        self.rect.y += self.dy
        self.draw(screen)

    def draw(self, screen):
        screen.blit(self.image, self.rect)
        
    def replace(self):
        """on change les variables qui ont été modifiés"""
        return self.exits, self.items_map, self.items, self.chests, self.chests_open, self.room_badge, self.room_x, self.room_y
        