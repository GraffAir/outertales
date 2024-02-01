import pygame

class Player:
    """classe pour gérer le joueur (déplacements, animations, interactions...)"""
    def __init__(self, x, y):
        """choisir l'image du joueur, établir sa position de base..."""
        #définir les listes qui contiennent les images du joueur qu'on va animer
        self.images_walk_right, self.images_walk_left, self.images_walk_up, self.images_walk_down = [], [], [], []

        #pour chaque liste, on a une série d'images, et on va faire en sorte que l'image du joueur varie d'une image à l'autre pour simuler un GIF
        for number in range(1, 5):
            img_right = pygame.transform.scale(pygame.image.load(f"images/player/player{number}.png"), (40, 40))
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
        self.rect.x, self.rect.y = x, y

        #la vitesse de déplacement
        self.speed = 4

        #pour les panneaux
        self.sign_counter = 100

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
        dx_test, dy_test = self.dx, self.dy
        if tile[1].colliderect(self.rect.x + self.dx, self.rect.y, self.image.get_width(), self.image.get_height()) == False:
            if tile[1].colliderect(self.rect.x + self.dx, self.rect.y + self.dy, self.image.get_width(), self.image.get_height()):
                if tile[1][0] != self.rect.x + 40 and tile[1][1] != self.rect.y - 40:
                    dy_test = 0
        else:
            dx_test = 0
        if tile[1].colliderect(self.rect.x, self.rect.y + self.dy, self.image.get_width(), self.image.get_height()) == False:
            if tile[1].colliderect(self.rect.x + self.dx, self.rect.y + self.dy, self.image.get_width(), self.image.get_height()):
                if tile[1][0] != self.rect.x - 40 and tile[1][1] != self.rect.y + 40:
                    dx_test = 0
        else:
            dy_test = 0
        self.dx, self.dy = dx_test, dy_test


    def collisions_exits(self, exit):
        """gérer les collisions avec les sorties salles pour changer la salle affichée"""
        if exit.rect.colliderect(self.rect.x + self.dx, self.rect.y + self.dy, self.image.get_width(), self.image.get_height()):
            #on vérifie si le joueur à le niveau de pass requis
            if self.room_badge >= int(exit.value) and pygame.key.get_pressed()[pygame.K_e]:
                #en fonction de ou mène la porte, on attribue des coordonnées au joueur qui sont différentes
                exit.open = True
                #si le joueur n'a pas un niveau de pass requis, alors pas de déplacement
        dx_test, dy_test = self.dx, self.dy
        if exit.rect.colliderect(self.rect.x + self.dx, self.rect.y, self.image.get_width(), self.image.get_height()) == False:
            if exit.rect.colliderect(self.rect.x + self.dx, self.rect.y + self.dy, self.image.get_width(), self.image.get_height()):
                if exit.rect.x != self.rect.x + 40 and exit.rect.y != self.rect.y - 40:
                    dy_test = 0
        else:
            dx_test = 0
        if exit.rect.colliderect(self.rect.x, self.rect.y + self.dy, self.image.get_width(), self.image.get_height()) == False:
            if exit.rect.colliderect(self.rect.x + self.dx, self.rect.y + self.dy, self.image.get_width(), self.image.get_height()):
                if exit.rect.x != self.rect.x - 40 and exit.rect.y != self.rect.y + 40:
                    dx_test = 0
        else:
            dy_test = 0
        self.dx, self.dy = dx_test, dy_test

    def collisions_items(self, item):
        """les collisions avec les items au sols"""
        #si l'item est ramassé, on l'enleve des items au sols et on le rajoute dans l'inventaire
        if item.rect.colliderect(self.rect.x, self.rect.y, self.image.get_width(), self.image.get_height()):
            self.items.append(item)
            self.items_map.remove(item)
        
    def collisions_signs(self, sign):

        # dx_test, dy_test = self.dx, self.dy
        # if sign.rect.colliderect(self.rect.x + self.dx, self.rect.y, self.image.get_width(), self.image.get_height()) == False:
        #     if sign.rect.colliderect(self.rect.x + self.dx, self.rect.y + self.dy, self.image.get_width(), self.image.get_height()):
        #         if sign.rect.x != self.rect.x + 40 and sign.rect.y != self.rect.y - 40:
        #             dy_test = 0
        # else:
        #     dx_test = 0
        # if sign.rect.colliderect(self.rect.x, self.rect.y + self.dy, self.image.get_width(), self.image.get_height()) == False:
        #     if sign.rect.colliderect(self.rect.x + self.dx, self.rect.y + self.dy, self.image.get_width(), self.image.get_height()):
        #         if sign.rect.x != self.rect.x - 40 and sign.rect.y != self.rect.y + 40:
        #             dx_test = 0
        # else:
        #     dy_test = 0
        # self.dx, self.dy = dx_test, dy_test

        if sign.rect.colliderect(self.rect.x + self.dx, self.rect.y + self.dy, self.image.get_width(), self.image.get_height()):
            if self.sign_counter >= 50:
                if pygame.key.get_pressed()[pygame.K_e]:
                    if sign.draw == False:
                        sign.draw = True
                    else:
                        sign.draw = False
                    self.sign_counter = 0
        self.sign_counter += 1

    def use_items(self):
        "une fois un item dans l'inventaire, on peut l'utiliser (une clé par exemple augmente le niveau de pass pour les sorties)"
        keys = []

        for item in self.items:
            if item.value[0:3] == "key":
                keys.append(int(item.value[3]))
                self.room_badge = max(keys)

    def update(self, screen, room_draw, items, items_map, exits, signs, room_badge, room_x, room_y):
        """gérer tous les évènements"""
        #on crée un objet avec self pour pouvoir changer les variables avec la méthode replace
        self.exits, self.items_map, self.items, self.signs, self.room_badge, self.room_x, self.room_y = exits, items_map, items, signs, room_badge, room_x, room_y

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
            self.collisions_exits(exit)

        #et le collisions avec les items au sol
        for item in self.items_map:
            self.collisions_items(item)

        for sign in signs:
            self.collisions_signs(sign)
        
        #on utilise les items
        self.use_items()

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

        #déplacer le joueur et le dessiner
        self.rect.x += self.dx
        self.rect.y += self.dy
        screen.blit(self.image, self.rect)

    def replace(self):
        """on change les variables qui ont été modifiés"""
        return self.exits, self.items_map, self.items, self.room_badge, self.room_x, self.room_y