#importer les bibliothèques / modules
import pygame
from pygame.locals import*
import pickle
from os import path
import map
import player
import rooms
import button

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
room_x, room_y = 0, 0
#les portes de sorties à considérer en collisions, les items au sol et ceux de l'inventaire, les coffres ouverts et fermés.
exits, items_map, items, signs, chests, chests_open, props = [], [], [], [], [], [], []
#le niveau de pass pour passer les portes
room_badge = 0
#la salle actuelle et son numéro d'identification
room = []
room_num = 1
#si le jeu est en cours, ou si le joueur est dans le menu, ou s'il regarde un panneau
game, menu, sign  = False, True, False
#compteur pour les panneaux        
sign_counter = 0
electricity = False
lock = False
try_ = ""
lock_ver = False
#charger les images

#celle du sol
bg_img = pygame.image.load("images/map/floor.png")
#celles du menu
play_btn_img = pygame.image.load("images/menu/play_btn.jpg")
menu_bg_img = pygame.transform.scale(pygame.image.load("images/menu/menu_bg.png"), (1280, 720))

def draw_badge_level(x, y, num):
   """fonction pour afficher le niveau de badge que possède le joueur"""
   screen.blit(pygame.transform.scale(pygame.image.load(f"images/items/level{num}.png"), (220, 140)), (x, y))

def import_room(num):
    """fonction pour charger les salles"""
    return rooms.rooms[f"{num}"]

#on importe les salles
Rooms = [
    [import_room("storage"), import_room("cafeteria"), import_room("breakroom"), import_room("dormitory"), import_room("spaceport"), []],
    [[], import_room("kitchen"), import_room("first_garden"), import_room("greenhouse"), import_room("reception"), import_room("cockpit")],
    [[], import_room("control_room"), import_room("generator_room"), import_room("second_garden"), import_room("archives"), []]
]

#on définit la salle de base et on la dessine
room = Rooms[room_y][room_x]
room_draw = map.Map(room, items, chests_open, room_num, tile_size, electricity)
exits, items_map, signs, chests, props = room_draw.replace()

#on initialise le joueur
player = player.Player(1000, 400)

#on définit les bouttons
play_btn = button.Button(1280 // 2 - 3 * tile_size, 720 // 3 - tile_size, play_btn_img)
                       
#lancer la boucle du jeu
run = True
while run:
    #régler la clock sur 60 fps
    clock.tick(fps)

    #si le jeu est en cours
    if game:
        #afficher le menu si le joueur appuie sur ECHAP
        if pygame.key.get_pressed()[pygame.K_ESCAPE]:
            game, menu = False, True
        #changer de map si nécessaire
        if room != Rooms[room_y][room_x]:
            room = Rooms[room_y][room_x]
            #changer le numéro de salle
            row_count = 0
            counter = 1
            for row in Rooms:
                col_count = 0
                for room_ in row:
                    if room_ == Rooms[room_y][room_x]:
                        room_num = counter
                    counter += 1
                    col_count += 1
                row_count += 1
            #la dessiner maintenant
            room_draw = map.Map(room, items, chests_open, room_num, tile_size, electricity)
            exits, items_map, signs, chests, props = room_draw.replace()
            if room_num == 15:
                electricity = True
            #faire en sorte que les portes soit ouvertes à l'entrée dans la salle
            for exit in exits:
                if player.rect.colliderect(exit.rect.x - 100, exit.rect.y - 100, 200, 200):
                    exit.open, exit.go_back = True, True
                    exit.rect.x, exit.rect.y = exit.end_pos
                    exit.counter = 100

            #modifier les portes de la salles, pour faire en sorte que si elles sont ouvertes sans electricité, elles le restent ensuite
            for exit in exits:
                if player.rect.colliderect(exit.rect.x - 100, exit.rect.y - 100, 200, 200):
                    if exit.link == 1:
                        room[0][15], room[0][16] = f"{room[0][15][:3]}O", f"{room[0][16][:3]}O"
                        Rooms[room_y-1][room_x][17][15], Rooms[room_y-1][room_x][17][16] = f"{Rooms[room_y-1][room_x][17][15][:3]}O", f"{Rooms[room_y-1][room_x][17][16][:3]}O"
                    elif exit.link == 2:
                        room[17][15], room[17][16] = f"{room[17][15][:3]}O", f"{room[17][16][:3]}O"
                        Rooms[room_y+1][room_x][0][15], Rooms[room_y+1][room_x][0][16] = f"{Rooms[room_y+1][room_x][0][15][:3]}O", f"{Rooms[room_y+1][room_x][0][16][:3]}O"
                    elif exit.link == 3:
                        room[8][0], room[9][0] = f"{room[8][0][:3]}O", f"{room[9][0][:3]}O"
                        Rooms[room_y][room_x-1][8][31], Rooms[room_y][room_x-1][9][31] = f"{Rooms[room_y][room_x-1][8][31][:3]}O", f"{Rooms[room_y][room_x-1][9][31][:3]}O"
                    elif exit.link == 4:    
                        room[8][31], room[9][31] = f"{room[8][31][:3]}O", f"{room[9][31][:3]}O"
                        Rooms[room_y][room_x+1][8][0], Rooms[room_y][room_x+1][9][0] = f"{Rooms[room_y][room_x+1][8][0][:3]}O", f"{Rooms[room_y][room_x+1][9][0][:3]}O"

        #afficher le sol
        screen.blit(bg_img, (0, 0))

        #dessine la map
        room_draw.draw(screen)

        #afficher les portes de sortie, et les faire bouger si nécessaire
        for exit in exits:
            exit.update(player, screen, electricity)
            for exit_ in exits:
                if exit.link == exit_.link:
                    if exit.collisions_counter == exit_.collisions_counter:
                        if exit.open == True:
                            exit_.open = True
        
        #afficher les coffres ouverts et fermés
        for chest in chests:
            game, lock_ver = chest.update(screen, room_num, game)
            if lock_ver:
                game = False
                lock = True          

        for chest in chests_open:
            game, lock_ver = chest.update(screen, room_num, game)
        
        #afficher les items sur la map
        for item in items_map:
            item.draw(screen)

        #afficher les panneaux
        for sign in signs:
            sign, game = sign.update(screen, sign, game)

        for prop in props:
            prop.draw(screen)

        #mettre à jour le joueur    
        player.update(screen, room_draw, items, items_map, exits, signs, chests, chests_open, room_badge, room_num, room_x, room_y, electricity, props)
        exits, items_map, items, chests, chests_open, room_badge, room_x, room_y  = player.replace()

        #afficher le niveau de badge
        if room_badge > 0:
            draw_badge_level(1000, 500, room_badge)
    
    #si le menu est ouvert
    elif menu:        
        screen.blit(menu_bg_img, (0, 0))
        if play_btn.draw(screen):
            menu, game = False, True

    #si un panneau est affiché à l'écran
    elif sign:
        #incrémenter le compteur
        sign_counter += 1
        #afficher le fond et les murs, les portes et les items
        screen.blit(bg_img, (0, 0))
        room_draw.draw(screen)

        for exit in exits:
            exit.draw(screen)

        for item in items_map:
            item.draw(screen)

        #afficher le panneau
        for sign in signs:
            if sign.draw == True:
                sign.draw_sign(screen)
                #si le joueur réappuie sur E, ou se déplace, si le compteur est suffisement grand, alors enlever le panneau et revenir au jeu
                if pygame.key.get_pressed()[pygame.K_e] or pygame.key.get_pressed()[pygame.K_LEFT] or pygame.key.get_pressed()[pygame.K_RIGHT] or pygame.key.get_pressed()[pygame.K_UP] or pygame.key.get_pressed()[pygame.K_DOWN]:
                    if sign_counter >= 50:
                        sign.draw = False
                        sign, game = False, True
                        sign_counter = 0

    elif lock:
        screen.blit(bg_img, (0, 0))
        screen.blit(pygame.image.load("images/password.png"), (140, 110))
        vals = [_ for _ in range(0, 9)]
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                try:
                    if int(event.dict['unicode']) in vals:
                        try_ = try_ + str(event.dict['unicode'])
                except:
                    pass
        if len(try_) == 1:
            screen.blit(pygame.image.load("images/aste.png"), (250, 350))
        if len(try_) == 2:
            screen.blit(pygame.image.load("images/aste.png"), (250, 350))
            screen.blit(pygame.image.load("images/aste.png"), (450, 350))
        if len(try_) == 3:
            screen.blit(pygame.image.load("images/aste.png"), (250, 350))
            screen.blit(pygame.image.load("images/aste.png"), (450, 350))
            screen.blit(pygame.image.load("images/aste.png"), (650, 350))
        if len(try_) == 4:
            for ch in chests:
                if ch.try_open == True:
                    if try_ == ch.code:
                        ch.try_open = False
                        ch.locked = False
                        ch.open = True
                        chests.remove(ch)
                        chests_open.append(ch)
                        if ch.contenu != "":
                            items_map.append(ch.contenu)
                        game = True
                        lock = False
                    else:
                        try_ = ""

        if pygame.key.get_pressed()[pygame.K_e]:
            game = True
            lock = False
            try_ = ""
            for ch in chests:
                ch.try_open = False
        
    #permet de  quitter le jeu
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    #rafrachir l'écran
    pygame.display.update()

pygame.quit()