import pygame

items = []
font_header = pygame.font.SysFont('Comic Sans MS', 35, bold=True)

def text(text):
    return font_header.render(f"{text}", False, (0, 0, 0))

class Player:
    """classe pour gérer le joueur (déplacements, animations, interactions...)"""
    def __init__(self, x, y):
        """choisir l'image du joueur, établir sa position de base..."""
        #définir les listes qui contiennent les images du joueur qu'on va animer
        self.images_walk_right, self.images_walk_left, self.images_walk_up, self.images_walk_down = [], [], [], []

        #pour chaque liste, on a une série d'images, et on va faire en sorte que l'image du joueur varie d'une image à l'autre pour simuler un GIF
        for number in range(1, 5):
            img_right = pygame.transform.scale(pygame.image.load(f"images/player/right{number}.png"), (30, 50)).convert_alpha()
            self.images_walk_right.append(img_right)
            img_left = pygame.transform.flip(img_right, True, False)
            self.images_walk_left.append(img_left)
            img_up = pygame.transform.scale(pygame.image.load(f"images/player/up{number}.png"), (30, 50)).convert_alpha()
            self.images_walk_up.append(img_up)
            img_down = pygame.transform.scale(pygame.image.load(f"images/player/down{number}.png"), (30, 50)).convert_alpha()
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

        #des compteurs pour faire en sort qu'on ne puisse re-essayer d'ouvrir un coffre vérouillé tout de suite(cooldown à -1seconde)
        self.sign_counter = 50
        self.chest_counter = 50
        self.lock_cooldown = 15
        self.archive_counter = 15
        self.door_speak_counter = True

        self.door_test = False

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
        """fonction pour gérer les collisions entre le joueur et une autre entité qui sera employé dans tout le code"""
        dx_test, dy_test = self.dx, self.dy
        #cette manière de régler les coliisions empêche certains bugs possibles lorsque l'on essaie d'aller vers la gauche et le haut, ce qui peut faire entrer la hitbox du joueur dans celle des murs par exemple
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
        self.collisions(tile[1])

    def collisions_exits(self, exit, electricity, screen):
        """gérer les collisions avec les sorties salles pour changer la salle affichée"""
        global items
        #s'il y a de l'electricité
        if electricity:
            #si le joueur entre en collisions avec une porte
            if exit.rect.colliderect(self.rect.x + self.dx - 40, self.rect.y + self.dy - 40, self.image.get_width() + 80, self.image.get_height() + 80):
                #on vérifie si le joueur à le niveau de pass requis, que la porte n'est pas cassable, et que la porte est fermée
                if exit.breakable == False and exit.open == False and self.room_badge >= int(exit.value):
                    #on affiche l'image en haut disant "appuyer sur E pour ouvrir la porte"
                    screen.blit(pygame.transform.scale(text("appuyer sur E pour ouvrir la porte"), (300, 40)).convert_alpha(), (940, 40))
                #et si le joueur a le bon niveau de badge et appuie sur E
                if self.room_badge >= int(exit.value) and pygame.key.get_pressed()[pygame.K_e]:
                    #on ouvre la porte
                    exit.open = True
                #si la porte est cassable, alors elle s'ouvre automatiquement sans appuyer sur E
                if exit.breakable == True:
                    exit.open = True
        #s'il n'y a pas d'electricite
        else:
            #on verifie s'il y a un marteau dans les items possédés
            for item in items:
                if item.value == "hammer":
                    #si oui, on verifie les collisions, si la porte est cassable, qu'elle est fermée, on affiche donc "appuyer pour ouvir la porte" 
                    if exit.rect.colliderect(self.rect.x + self.dx - 1, self.rect.y + self.dy - 1, self.image.get_width() + 4, self.image.get_height() + 4):
                        if exit.breakable and exit.open == False:
                            screen.blit(pygame.transform.scale(text("appuyer sur E pour forcer la porte"), (300, 40)).convert_alpha(), (940, 40))
                            #s'il appuye sur E
                            if pygame.key.get_pressed()[pygame.K_e]:
                                #on ouvre la porte, et on la met directement a la posititon de fin, 
                                exit.open = True
                                exit.rect.x, exit.rect.y = exit.end_pos
            if not 'hammer' in [_.value for _ in items]:
                if exit.rect.colliderect(self.rect.x + self.dx - 1, self.rect.y + self.dy - 1, self.image.get_width() + 4, self.image.get_height() + 4):
                    if exit.breakable and exit.open == False:
                        if self.door_speak_counter:
                            #
                            self.door_speak = True
                            self.door_speak_counter = False

        # for exit in self.exits:
        if exit.rect.colliderect(self.rect.x + self.dx - 1, self.rect.y + self.dy - 1, self.image.get_width() + 4, self.image.get_height() + 4):
            self.door_test = True
        if self.door_test == False:
            self.door_speak_counter = True
        else:
            self.door_test = False

        #on verifie ensuite les collisions avec les portes, pour ne pas rentrer dedans
        self.collisions(exit.rect)

    def collisions_items(self, item):
        """les collisions avec les items au sols"""
        global items
        #si l'item est contenu dans un coffre, est que le coffre est ouvert
        if item.chest == True and item.chest_open == True:
            #si le joueur est en collision avec l'objet
            if item.rect.colliderect(self.rect.x - 1, self.rect.y - 9, self.image.get_width() + 4, self.image.get_height() + 20):
                #s'il appuie sur E
                if pygame.key.get_pressed()[pygame.K_e]:
                    #on ajoute l'objet aux objets possédes et on le retire des objets posés sur la map
                    items.append(item)
                    self.items_map.remove(item)
        #si l'objet nest pas dans un coffre
        elif item.chest == False:
            #si on entre en colisions avec
            if item.rect.colliderect(self.rect.x, self.rect.y, self.image.get_width(), self.image.get_height()):
                #on ajoute l'item a l'inventaire, et on l'enleve des objets sur la map
                items.append(item)
                self.items_map.remove(item)
        
    def collisions_signs(self, sign):
        """les collisisons avec les panneaux"""
        #si on entre en collisions avec 
        if sign.rect_item.colliderect(self.rect.x + self.dx, self.rect.y + self.dy, self.image.get_width(), self.image.get_height()):
            #et que cela fait suffisament de temps depuis la derniere fois ou on entré en collions avec un panneau
            if self.sign_counter == 50:
                #si le joueur appuie sur E
                if pygame.key.get_pressed()[pygame.K_e]:
                    #alors la variable du panneau qui indique s'il est dessiné est noté comme True
                    if sign.draw == False:
                        sign.draw = True
                    #on remete le compteur pour les panneaux a 0
                    self.sign_counter = 0
        #on augmente ce compteur s'il n'est pas au dessus de 50, pour eviter une information inutile trop lourde en mémoire
        if self.sign_counter < 50:
            self.sign_counter += 1
        
    def collisions_chests(self, chest, screen):
        '''les collisions avec les coffres'''
        #si le joueur entre en collision avec 
        if pygame.key.get_pressed()[pygame.K_e] == False:
            self.lock_cooldown = True
        if chest.rect.colliderect(self.rect.x + self.dx - 1, self.rect.y + self.dy - 1, self.image.get_width() + 4, self.image.get_height() + 4):
            #s'il appuie sur 
                #si le coffre est fermé
            if chest.open == False:
                    #si le coffre n'est pas vérouillé ou plus vérouillé
                if chest.locked == False:
                    screen.blit(pygame.transform.scale(text("appuyer sur E pour ouvrir le coffre"), (300, 40)).convert_alpha(), (940, 40))
                    if pygame.key.get_pressed()[pygame.K_e]:
                        #le coffre est maintenant ouvert, on le retire de la liste des coffres, et on l'ajoute a la liste des coffres deja ouverts
                        chest.open = True
                        self.chests.remove(chest)
                        self.chests_open.append(chest)
                        #si le contenu du coffre n'est pas vide
                        if chest.contenu != "":
                            #on ajoute l'item a la liste des item posés dans la salle
                            self.items_map.append(chest.contenu)
                    #si le coffre est verouillé
                else:
                    #si cela fait sufisament de temps depuis la derniere fois ou on a essayé d'ouvrir un coffre vérouillé
                    screen.blit(pygame.transform.scale(text("appuyer sur E pour déverrouiller le coffre"), (300, 40)).convert_alpha(), (940, 40))
                    if pygame.key.get_pressed()[pygame.K_e]:
                        if self.lock_cooldown:
                            #on modifie la variable lock, qui sera retourné dans la boucle principale, le cooldown revient a 0, et on tente d'ouvrir le coffre
                            self.lock = True
                            chest.try_open = True
                            self.lock_cooldown = False
                #si jamais le coffre est déja ouvert
            elif chest.open:
                #s'il est dans la bonne salle
                if chest.room == self.room_num:
                    #si le contenu du coffre n'a pas deja ete pris
                    if chest.item_took == False:
                        #si le contenu n'est pas vide
                        if chest.contenu != "":
                            screen.blit(pygame.transform.scale(text("appuyer sur E pour récupérer l'object"), (300, 40)).convert_alpha(), (940, 40))
                            if pygame.key.get_pressed()[pygame.K_e]:
                            #pour qu'on ne puisse pas ouvrir le coffre et prende l'item avec un seul appui sur E
                                if chest.item_cooldown == True:
                                    #on dit a l'item que son coffre est ouvert
                                    chest.contenu.chest_open = True
                                    #et on dit au coffre que son item est pris
                                    chest.item_took = True
                        else:
                        #si le contenu est vide, on dit que son contenu est pris quand meme, pour eviter des erreurs plus tard
                            chest.item_took = True
                        self.chest_counter = 0
                    else:
                        #si le contenu est deja pris
                        if self.chest_counter >= 50:
                            screen.blit(pygame.transform.scale(text("appuyer sur E pour regarder le fond du coffre"), (300, 40)).convert_alpha(), (940, 40))
                            #si ca fait sufisament de temps depuis qu'on a essayé de regardé de plus pres un coffre
                            if pygame.key.get_pressed()[pygame.K_e]:
                                if chest.watched_cooldown:
                                    #le coffre est regarder, le compteur revient a 0, le cooldown pour regarder le coffre est False
                                    chest.watched = True
                                    self.chest_counter = 0
                                    chest.watched_cooldown = False
                                    #on renvoie dans la boucle principale que on regarde un coffre
                                    self.chest = True

        #si les compteur qui indique qu'on a regardé un coffre ou esayé d'en ouvrir un vérouillé sont en dessous de 50, on les augmente
        if self.chest_counter < 50:
            self.chest_counter += 1
        #on verifie les collisions avec le coffre, pour ne pas rentrer dedans
        if chest.room == self.room_num:
            self.collisions(chest.rect)

    def collisions_props(self, prop):
        '''les collisions avec les props'''
        self.collisions(prop.rect)

    def collisions_archives(self, archive):
        """les collisions avec les archives"""
        global items
        #s'il entre en collision avec l'archive
        if archive.rect.colliderect(self.rect.x + self.dx - 1, self.rect.y + self.dy - 1, self.image.get_width() + 4, self.image.get_height() + 4):
            #s'il appuie sur E
            if pygame.key.get_pressed()[pygame.K_e]:
                #si le papier n'est pas en train d'être regardé
                if archive.paper_watch == False:
                    #si cela fait suffisament de temps depuis qu'on a regardé la note d'une archive
                    if self.archive_counter == 15:
                        #si cest possible de regarder la note
                        if archive.paper_watched_cooldown:
                            #alors on envoie dans la boucle principale que l'on regarde la note d'une archive
                            archive.paper_watch = True
                            self.archive = True
                            self.archive_counter = 0
                            archive.paper_watched_cooldown = False

        #incrémenter le compteur quand on regarde une archive
        if self.archive_counter < 15:
            self.archive_counter += 1
        #les collisions pour pas rentrer dedans
        self.collisions(archive.rect)

    def collisions_generator(self, generator, screen):
        if generator.rect.colliderect(self.rect.x + self.dx - 1, self.rect.y + self.dy - 1, self.image.get_width() + 4, self.image.get_height() + 4):
            if self.electricity == False:
                if generator.actionned == False:
                    screen.blit(pygame.transform.scale(text("appuyer sur E pour rallumer le génerateur"), (300, 40)).convert_alpha(), (940, 40))
                    if pygame.key.get_pressed()[pygame.K_e]:
                        generator.actionned = True
                        self.electricity = True
        self.collisions(generator.rect)

    def collisions_ship(self, ship, screen):
        if self.end_speak == True:
            if ship.rect.colliderect(self.rect.x + self.dx - 1, self.rect.y + self.dy - 1, self.image.get_width() + 4, self.image.get_height() + 4):
                screen.blit(pygame.transform.scale(text("appuyer sur E pour aller dans le vaisseau"), (300, 40)).convert_alpha(), (940, 40))
                if pygame.key.get_pressed()[pygame.K_e]:
                    self.end = True

        self.collisions(ship.rect)
    def use_items(self):
        "une fois un item dans l'inventaire, on peut l'utiliser (une clé par exemple augmente le niveau de pass pour les sorties)"
        global items
        keys = []
        for item in items:
            #on regarde parmi les badge celui qui est le plus gros est on le définit comme le niveau de badge
            if item.value[0:3] == "key":
                keys.append(int(item.value[3]))
                self.room_badge = max(keys)

    def change_room(self):
        '''changer la salle si le joueur sort des limites'''
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

    def update(self, screen, room_draw, items_map, exits, signs, chests, chests_open, room_badge, room_num, room_x, room_y, electricity, props, archives, generator, ship, end_speak):
        """gérer tous les évènements"""
        global items
        #on crée un objet avec self pour pouvoir changer les variables avec la méthode replace et les utiliser dans les autres methodes
        self.exits, self.items_map, self.chests, self.chests_open, self.archives, self.room_badge, self.room_num, self.room_x, self.room_y, self.electricity = exits, items_map, chests, chests_open, archives, room_badge, room_num, room_x, room_y, electricity
        #valeur renvoyé dans la boucle principale pour indique sui on ouvre un coffre vérouillé, ou si on regarde un coffre de plus pres
        self.lock, self.chest, self.archive = False, False, False
        self.door_speak = False
        self.end_speak = end_speak
        self.end = False
        #les variables qui symbolise le déplacement qui sera réalisé si possible
        self.dx, self.dy = 0, 0
        #on vérifie s'il appuie sur les touches de déplacements, et si oui on fait le deplaceement en question, et on change l'animation
        key = pygame.key.get_pressed()
        if key[pygame.K_UP] and key[pygame.K_RIGHT]:
            self.move_right()
            self.move_up()
        elif key[pygame.K_UP] and key[pygame.K_LEFT]:
            self.move_left()
            self.move_up()
        elif key[pygame.K_UP] and key[pygame.K_DOWN]:
            self.direction = 2
            self.counter += 1
            self.change_animation()
        elif key[pygame.K_RIGHT] and key[pygame.K_LEFT]:
            self.direction = 1
            self.counter += 1
            self.change_animation()
        elif key[pygame.K_RIGHT] and key[pygame.K_DOWN]:
            self.move_right()
            self.move_down()
        elif key[pygame.K_DOWN] and key[pygame.K_LEFT]:
            self.move_left()
            self.move_down()
        elif key[pygame.K_UP]:
            self.move_up()
        elif key[pygame.K_DOWN]:
            self.move_down()
        elif key[pygame.K_RIGHT]:
            self.move_right()
        elif key[pygame.K_LEFT]:
            self.move_left()
        #si le joueur ne se deplace pas, on laisse l'image en question
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
            
        #les collisions avec la map
        for tile in room_draw.tile_list:
            self.collisions_map(tile)
        
        #gérer les collisions avec les portes de sorties, et si l'une s'ouvre sans electricité, sa moitié le doit aussi
        for exit in self.exits:
            self.collisions_exits(exit, electricity, screen)
            for exit_ in self.exits:
                if electricity == False:
                    if exit.link == exit_.link:
                        if (exit.rect.x, exit.rect.y) == exit.end_pos:
                            exit_.rect.x, exit_.rect.y = exit_.end_pos

        #et les collisions avec les items au sol
        for item in self.items_map:
            self.collisions_items(item)

        #les collisions avec les panneaux
        for sign in signs:
            self.collisions_signs(sign)

        #les collisison avec les coffres
        for chest in chests:
            self.collisions_chests(chest, screen)
        
        #les collisions avec les coffres ouverts
        for chest in chests_open:
            self.collisions_chests(chest, screen)

        #les collisions avec les props
        for prop in props:
            self.collisions_props(prop)

        for archive in archives:
            self.collisions_archives(archive)

        if generator != None:
            self.collisions_generator(generator, screen)

        if ship != None:
            self.collisions_ship(ship, screen)
        
        #on utilise les items
        self.use_items()

        #on fait changer le joueur de room si besoin
        self.change_room()

        #déplacer le joueur et le dessiner
        self.rect.x += self.dx
        self.rect.y += self.dy
        self.draw(screen)

    def draw(self, screen):
        """methode pour dessiner le joueur"""
        screen.blit(self.image, self.rect)
        
    def replace(self):
        """on change les variables qui ont été modifiés"""
        return self.exits, self.items_map, self.chests, self.chests_open, self.archives, self.room_badge, self.room_x, self.room_y, self.lock, self.chest, self.archive, self.electricity, self.door_speak, self.end
        