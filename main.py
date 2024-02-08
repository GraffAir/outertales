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
exits, items_map, items, signs, chests, chests_open = [], [], [], [], [],[]
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

#charger les images

#celle du sol
bg_img = pygame.transform.scale(pygame.image.load("images/map/floor.png"), (1280, 720))

def draw_badge_level(x, y, num):
   """fonction pour afficher le niveau de badge que possède le joueur"""
   screen.blit(pygame.image.load(f"images/print_pass{num}.png"), (x, y))

def import_room(num):
    """fonction pour charger les salles"""
    # if path.exists(f"rooms/room{num}.bin"):
    #     pickle_in = open(f"rooms/room{num}.bin", "rb")
    #     return pickle.load(pickle_in)
    return rooms.rooms[f"{num}"]

#on importe les salles
Rooms = [
    [import_room(1), import_room(2)],
    [import_room(3), import_room(4)]
]

#on définit la salle de base et on la dessine
room = Rooms[room_y][room_x]
room_draw = map.Map(room, items, chests_open, room_num, tile_size)
exits, items_map, signs, chests = room_draw.replace()

#on initialise le joueur
player = player.Player(1000, 400)

#on définit les bouttons
play_btn = button.Button(1280 // 2 - 3 * tile_size, 720 // 3 - tile_size, pygame.image.load("images/menu/play_btn.jpg"))
                       
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
            room_draw = map.Map(room, items, chests_open, room_num, tile_size)
            exits, items_map, signs, chests = room_draw.replace()
            #faire en sorte que les portes soit ouvertes à l'entrée dans la salle
            for exit in exits:
                if player.rect.colliderect(exit.rect.x - 100, exit.rect.y - 100, 200, 200):
                    exit.open, exit.go_back = True, True
                    if exit.direction == "top":
                        exit.rect.y -= 40
                    elif exit.direction == "bottom":
                        exit.rect.y += 40
                    elif exit.direction == "left":
                        exit.rect.x -= 40
                    elif exit.direction == "right":
                        exit.rect.x += 40
                    exit.counter = 100

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
            chest.update(screen, room_num)
            
        for chest in chests_open:
            chest.update(screen, room_num)
        
        #afficher les items sur la map
        for item in items_map:
            item.draw(screen)

        #afficher les panneaux
        for sign in signs:
            sign, game = sign.update(screen, sign, game)

        #mettre à jour le joueur    
        player.update(screen, room_draw, items, items_map, exits, signs, chests, chests_open, room_badge, room_x, room_y, electricity)
        exits, items_map, items, chests, chests_open, room_badge, room_x, room_y  = player.replace()

        #afficher le niveau de badge
        if room_badge > 0:
            draw_badge_level(1000, 500, room_badge)
    
    #si le menu est ouvert
    elif menu:        
        screen.blit(pygame.transform.scale(pygame.image.load("images/menu/menu_bg.jpg"), (1280, 720)), (0, 0))
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

    #permet de  quitter le jeu
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    #rafrachir l'écran
    pygame.display.update()

pygame.quit()