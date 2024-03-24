import pygame
pygame.font.init()

font_header = pygame.font.SysFont('Courier New', 16)

def text(text):
    return font_header.render(f"{text}", False, (255, 255, 255))

electricity = False
items_map, chests, chests_open, exits, signs, props, archives = [], [], [], [], [], [], []
generator = None
ship = None
chair = None
control_panel = None

class Map:
    """classe pour pouvoir dessiner la salle"""
    def __init__(self, liste, items, room_num, tile_size):
        """créer une liste contient les images et les coordonnées à dessiner"""
        global electricity, items_map, chests, chests_open, exits, signs, props, archives, generator, ship, chair, control_panel
        self.tile_list = []

        #pour les items au sol
        item_already, chest_already = False, False

        #charger les images des blocs
        mur_img = pygame.transform.scale(pygame.image.load("images/map/mur.png"), (tile_size, tile_size)).convert()
        coin_img = pygame.transform.scale(pygame.image.load("images/map/coin.png"), (tile_size, tile_size)).convert()
        bush_img = pygame.transform.scale(pygame.image.load("images/map/bush.png"), (tile_size, tile_size)).convert()
        blood_img = pygame.transform.scale(pygame.image.load("images/map/blood.png"), (tile_size, tile_size)).convert_alpha()
        #glass_img = pygame.transform.scale(pygame.image.load("images/map/glass_wall.png"), (tile_size, tile_size))

        #pour modifier les valeurs, les sorties, les itemms
        exits, items_map, items_verifications, chests_ver, signs, chests, props, archives, generator, ship, chair, control_panel = [], [], [], [], [], [], [], [], None, None, None, None

        #pour les portes de sorties
        exit_dir = 'left'
        x_, y_ = 0, 0
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
                    else:
                        img = pygame.transform.rotate(mur_img, 0)
                    img_rect = img.get_rect()
                    img_rect.x, img_rect.y = col_count * tile_size, row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                elif tile == 2:
                    img = bush_img
                    img_rect = img.get_rect()
                    img_rect.x, img_rect.y = col_count * tile_size, row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                elif tile == 3:
                    img = blood_img
                    img_rect = img.get_rect()
                    img_rect.x, img_rect.y, img_rect.width, img_rect.height = col_count * tile_size, row_count * tile_size, 0, 0
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                #si elle commence par E alors c'est une porte vers une autre salle
                elif str(tile)[0] == "E":
                    x_, y_, link = 0, 0, 0
                    if row_count == 0 or row_count == 17:
                        if col_count == 15:
                            exit_dir = "left"
                        elif col_count == 16:
                            exit_dir = "right"
                    if row_count == 0:
                        y_ = tile_size - 7
                    elif col_count == 0 or col_count == 31:
                        if row_count == 8:
                            exit_dir = "top"
                        elif row_count == 9:
                            exit_dir = "bottom"
                    if col_count == 0:
                        x_ = tile_size - 7
                    if row_count == 0:
                        link = 1
                    elif row_count == 15:
                        link = 2
                    elif col_count == 0:
                        link = 3
                    elif col_count == 31:
                        link = 4
                    exit = Exit(col_count * tile_size + x_, row_count * tile_size + y_, exit_dir, tile[1], link, tile[2], tile[3])
                    exits.append(exit)
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
                        items_map.append(item)
                    item_already = False
                #les panneaux
                elif str(tile)[0] == "S":
                    sign_ = tile
                    x, y = col_count * tile_size, row_count * tile_size
                    sign = Sign(sign_, x, y)
                    signs.append(sign)
                elif str(tile)[0] == "P":
                    prop = Props(col_count * tile_size, row_count * tile_size, tile[1:])
                    props.append(prop)
                    if prop.collision_prop:
                        props.append(prop.collision_prop)
                elif str(tile)[0] == "A":
                    archive = Archive(col_count * tile_size, row_count * tile_size, tile[1:])
                    archives.append(archive)
                elif str(tile)[0] == "G":
                    generator = Generator(col_count * tile_size, row_count * tile_size)
                elif isinstance(tile, tuple):
                    #les coffres
                    if tile[0] == "C":
                        chest = Chest(col_count * tile_size, row_count * tile_size, tile[1], tile[2], room_num, tile[3], tile[4])
                        #créer une liste contenants les coordonnées et la salle de chaque objet DEJA RAMASSE
                        for ch in chests_open:
                            #ajouter les items ramassé qui ne sont pas dans la liste 
                            chests_ver.append([ch.rect.x, ch.rect.y, ch.room])
                            if [chest.rect.x, chest.rect.y, chest.room] == chests_ver[len(chests_ver)-1]:
                                #ajoute 1 au compteur si l'item à déja été pris
                                chest_already = True
                                if ch.item_took == False and ch.contenu != "":
                                    #ch.contenu = Item(col_count * tile_size, row_count * tile_size, tile[2], room_num)
                                    items_map.append(ch.contenu)
                        #pour chaque item sur le sol, il vérifie s'il en existe deja un semblable dans l'inventaire (avec les coordonnées et le numéro de salle : il ne peut y en avoir qu'un qui y correspond, à savoir le même, qui serait deja ramassé)
                        #et s'il n'a pas été ramassé, alors on l'ajoute à la liste des objets au sol à dessiner, et à considérer ses collisions
                        if chest_already == False:
                            chests.append(chest)
                        chest_already = False
                elif str(tile)[0] == "B":
                    ship = Ship(col_count * tile_size, row_count * tile_size)
                elif str(tile)[0] == "Z":
                    chair = Chair(col_count * tile_size, row_count * tile_size)
                elif str(tile)[0] == "F":
                    control_panel = Control(col_count * tile_size, row_count * tile_size)
                col_count += 1
            row_count += 1
    
    def draw(self, screen):
        """méthode pour dessiner cette liste qui contient toutes les coordonnées et les images des blocs à placer"""
        for tile in self.tile_list:
            screen.blit(tile[0], tile[1])

class Exit:
    """classe pour gérer les changements de salle"""
    def __init__(self, x, y, dir, val, link, breakable, open):
        """definir l'image de la porte, sa position, et ses variables"""
        global electricity
        if breakable == "B":
            img = pygame.image.load("images/glass_door.png").convert_alpha()
        elif breakable == "U":
            img = pygame.image.load("images/iron_door.png").convert()
        #on dessine la porte 
        if dir == 'bottom':
            self.image = img
        elif dir == 'top':
            self.image = pygame.transform.rotate(img, 180)
        elif dir == 'left':
            self.image = pygame.transform.rotate(img, 270)
        elif dir == 'right':
            self.image = pygame.transform.rotate(img, 90)
        #les coordonnées
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y
        #la valeur d'une porte c'est un chiffre qui indique quel niveau de pass il faut pour la franchir
        self.value = val
        #pour indiquer vers ou mène la porte, et a quel groupe elle appartient
        self.direction, self.link = dir, link
        #si la porte est cassable ou non avec un marteau
        if breakable == 'B':
            self.breakable = True
        elif breakable == "U":
            self.breakable = False
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
        self.open, self.go_back = False, False
        self.counter, self.collisions_counter = 0, 0
        #si la porte était deja ouverte sans electricité
        if open == "O" and electricity == False:
            self.rect.x, self.rect.y = self.end_pos
            self.open, self.go_back = True, True

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
        self.counter, self.collisions_counter = 0, 0
        self.go_back, self.open = False, False

    def update(self, player, screen):
        """methode pour faire déplacer les portes, et les faire revenir à leurs positions"""
        global electricity
        if electricity:
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

        self.draw(screen)

    def draw(self, screen):
        """dessiner la porte de sortie"""
        screen.blit(self.image, self.rect)

class Item:
    """classe pour gérer les objets au sol récupérable"""
    def __init__(self, x, y, image1, room, chest=False):
        #l'image
        if image1[1:4] == "key":
            img = pygame.transform.scale(pygame.image.load(f"images/items/level{image1[4]}.png"), (40, 25)).convert_alpha()
            y += 7.5
        else:
            img = pygame.transform.scale(pygame.image.load(f"images//items/{image1[1:]}.png"), (40, 40)).convert_alpha()
        self.image = img
        #les coordonnées
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y
        #sa valeur (ex : un pass de niveau 3)
        self.value = image1[1:]
        #la salle dans laquelle il à été pris
        self.room = room
        self.chest = chest
        self.chest_open = False

    def draw(self, screen):
        """dessiner l'item"""
        screen.blit(self.image, self.rect)
    
class Sign:
    def __init__(self, sign, x, y):
        """définir l'image du panneau, sa position, ses variables"""
        self.image_item = pygame.transform.scale(pygame.image.load("images/signs/sign.png"), (40, 40))    
        self.rect_item = self.image_item.get_rect()   
        self.rect_item.x, self.rect_item.y = x, y
        self.image_sign = pygame.transform.scale(pygame.image.load(f"images/signs/sign{sign[1]}.png"), (1000, 500))
        self.rect_sign = self.image_sign.get_rect()
        self.rect_sign.x, self.rect_sign.y = 140, 110
        self.draw = False

    def draw_item(self, screen):
        """dessiner l'item du panneau au sol"""
        screen.blit(self.image_item, self.rect_item)

    def draw_sign(self, screen):
        """dessiner le panneau quand il sera cliqué"""
        screen.blit(self.image_sign, self.rect_sign)

    def update(self, screen, sign, game):
        """mettre à jour, donc dessiner soit l'item, soit le panneau en grand"""
        if self.draw:
            self.draw_sign(screen)
            sign, game = True, False
            return True, False
        else:
            self.draw_item(screen)
        return sign, game

class Chest:
    def __init__(self, x, y, chest, contenu, room_num, locked, ref):
        """définir quel coffre, son contenu, sa position..."""
        self.image_chest = pygame.transform.scale(pygame.image.load(f"images/{chest}.png"), (40, 40)).convert_alpha()
        self.image_chest_open = pygame.transform.scale(pygame.image.load(f"images/{chest}_open.png"), (40, 40)).convert()
        self.rect = self.image_chest.get_rect()
        self.rect.x, self.rect.y = x, y
        if contenu != "":
            self.contenu = Item(x, y, contenu, room_num, True)
        else:
            self.contenu = contenu
        self.open = False
        self.room = room_num
        self.item_took = False
        self.item_cooldown = 0
        self.try_open = None
        self.code = None
        if len(locked) == 4:
            self.locked = True
            self.try_open = False
            self.code = locked
        else:
            self.locked = False
        self.watched = False
        self.ref = ref
        self.watched_cooldown = 0

    def draw(self, screen):
        """dessiner le coffre"""
        screen.blit(self.image_chest, self.rect)
    
    def draw_item(self, screen):
        """dessiner l'item dans le coffre"""
        screen.blit(self.contenu.image, self.contenu.rect)

    def update(self, screen, room_num, game):
        """changer l'image du coffre s'il est ouvert, l'afficher, et affiche l'item si le coffre est ouvert"""
        if self.open:
            self.image_chest = self.image_chest_open
            if self.room == room_num:
                self.draw(screen)
            if pygame.key.get_pressed()[pygame.K_e] == False:
                self.item_cooldown = True
                self.watched_cooldown = True
        else:
            self.draw(screen)
    
class Props:
    def __init__(self, x, y, image, can_collide=True, width=10, height=10):
        self.can_collide = can_collide
        self.collision_prop = None
        if image == "invisible":
            self.image = pygame.image.load(f"images/props/{image}.png").convert_alpha()
            self.image = pygame.transform.scale(self.image, (width, height)).convert_alpha()
        elif image == "bed":
            self.image = pygame.image.load(f"images/props/{image}.png").convert_alpha()
            self.image = pygame.transform.scale(self.image, (80, 120)).convert_alpha()
        elif image[:-1] == "biblio":
            w,h,s = 100, 130, 110
            self.image = pygame.image.load(f"images/props/biblio.png").convert_alpha()
            self.image = pygame.transform.scale(self.image, (w, h)).convert_alpha()
            self.can_collide = False
            self.collision_prop = Props(x, y+s, "invisible", width=w, height=h-s)
        elif image == "gaz":
            self.image = pygame.image.load(f"images/props/{image}.png").convert_alpha()
            self.image = pygame.transform.scale(self.image, (20, 60)).convert_alpha()
        elif image == "couch":
            self.image = pygame.image.load(f"images/props/{image}.png").convert_alpha()
            self.image = pygame.transform.scale(self.image, (130, 40)).convert_alpha()
        elif image == "mur" or image[:-1] == "mur":
            if image == "mur3":
                self.image = pygame.image.load(f"images/props/mur1.png").convert_alpha()
                self.image = pygame.transform.rotate(self.image, -90)
            else:
                self.image = pygame.image.load(f"images/props/{image}.png").convert_alpha()
            self.image = pygame.transform.scale(self.image, (40, 40)).convert_alpha()
        elif image == "coke":
            self.image = pygame.image.load(f"images/props/{image}.png").convert_alpha()
            self.image = pygame.transform.scale(self.image, (10, 20)).convert_alpha()
        elif image == "table":
            self.image = pygame.image.load(f"images/props/{image}.png").convert_alpha()
            self.image = pygame.transform.scale(self.image, (150, 100)).convert_alpha()
        elif image == "fat_table":
            self.image = pygame.image.load(f"images/props/{image}.png").convert_alpha()
            self.image = pygame.transform.scale(self.image, (500, 100)).convert_alpha()
        elif image == 'billard':
            self.image = pygame.image.load(f"images/props/{image}.png").convert()
            self.image = pygame.transform.scale(self.image, (160, 80)).convert_alpha()
            self.image = pygame.transform.rotate(self.image, 90)
        elif image == 'cadaver':
            self.image = pygame.image.load(f"images/props/{image}.png").convert_alpha()
            self.image = pygame.transform.scale(self.image, (80, 40)).convert_alpha()
        elif image == 'end_perso':
            self.image = pygame.image.load(f"images/props/{image}.png").convert_alpha()
            self.image = pygame.transform.scale(self.image, (40, 55)).convert_alpha()
            self.image = pygame.transform.flip(self.image, True, False)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y
        if image == 'cadaver':
            self.isDiscover = True
        else:
            self.isDiscover = False
    
    def draw(self, screen):
        screen.blit(self.image, self.rect)

class Archive:
    def __init__(self, x, y, ref):
        self.image = pygame.transform.scale(pygame.image.load("images/archives/arch.png").convert(), (80, 40))
        self.paper_image = pygame.transform.scale(pygame.image.load(f"images/archives/found.png").convert(), (1000, 500))
        if ref in ["A000-099", "B900-999", "C700-799", "D600-699"]:
            self.paper_image_found = pygame.transform.scale(pygame.image.load(f"images/archives/paper{ref}.png").convert(), (120, 120))
        else:
            self.paper_image_found = pygame.transform.scale(pygame.image.load(f"images/archives/others.png").convert(), (120, 120))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.ref = ref
        self.paper_watch = False
        self.paper_watched_cooldown = True

    def draw(self, screen):
        screen.blit(self.image, self.rect)
        screen.blit(text(self.ref[:4]), (self.rect.x + 20, self.rect.y + 10))

    def draw_paper(self, screen):
        screen.blit(self.paper_image, (140, 60))
        screen.blit(self.paper_image_found, (600, 400))

class Generator:
    def __init__(self, x, y):
        self.image = pygame.transform.scale(pygame.image.load("images/map/generator.png"), (360, 360)).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.actionned = False

    def draw(self, screen):
        screen.blit(self.image, self.rect)

class Ship:
    def __init__(self, x, y):
        self.image = pygame.transform.scale(pygame.image.load("images/map/ship.png"), (120, 120)).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.isCollide = False

    def draw(self, screen):
        screen.blit(self.image, self.rect)

class Chair:
    def __init__(self, x, y):
        self.image = pygame.transform.scale(pygame.image.load("images/map/chair.png"), (40, 40)).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.isCollide = False

    def draw(self, screen):
        screen.blit(self.image, self.rect)

class Control:
    def __init__(self, x, y):
        self.image = pygame.transform.scale(pygame.image.load("images/map/control_panel.png"), (80, 80)).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.isActived = False

    def draw(self, screen):
        screen.blit(self.image, self.rect)