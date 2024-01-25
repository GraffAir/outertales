#importer les bibliothèques / modules
import pygame
from pygame.locals import*
import pickle
from os import path
import map
import player
import pancarte

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
#les portes de sorties à considérer en collisions, les items au sol et ceux de l'inventaire
exits, items_map, items = [], [], []
#le niveau de pass pour passer les portes
room_badge = 0
#la salle actuelle et son numéro d'identification
room = []
room_num = 1

#charger les images

#celle du sol
bg_img = pygame.transform.scale(pygame.image.load("images/floor.jpg"), (1280, 720))
        

def affichage(x, y, num):
   screen.blit(pygame.image.load(f"images/print_pass{num}.png"), (x, y))

def import_room(num):
    if path.exists(f"rooms/room{num}.bin"):
        pickle_in = open(f"rooms/room{num}.bin", "rb")
        return pickle.load(pickle_in)

#on importe les salles
rooms = [
    [import_room(1), import_room(2)],
    [import_room(3), import_room(4)]
]

#on définit la salle de base et on la dessine
room = rooms[room_y][room_x]
room_draw = map.Map(room, items, room_num, tile_size)
exits, items_map = room_draw.replace()

#on initialise le joueur
player = player.Player(1000, 400)
pan = pancarte.Pancarte("abruaat", 100, 100)

#lancer la boucle du jeu
run = True
while run:
    #régler la clock sur 60 fps
    clock.tick(fps)
    #afficher le sol
    screen.blit(bg_img, (0, 0))

    #changer de map si nécessaire
    if room != rooms[room_y][room_x]:
        pan.draw(screen)
        room = rooms[room_y][room_x]
        #changer le numéro de salle
        row_count = 0
        counter = 1
        for row in rooms:
            col_count = 0
            for room_ in row:
                if room_ == rooms[room_y][room_x]:
                    room_num = counter
                counter += 1
                col_count += 1
            row_count += 1
        #la dessiner maintenant
        room_draw = map.Map(room, items, room_num, tile_size)
        exits, items_map = room_draw.replace()


    #dessine la map
    room_draw.draw(screen)

    #afficher les portes de sortie, et les faire bouger si nécessaire
    for exit in exits:
        exit.update(player)
        exit.draw(screen)
        for exit_ in exits:
            if exit.collisions_counter == exit_.collisions_counter:
                if exit.open == True:
                    if exit.link == exit_.link:
                        exit_.open = True

    #afficher les items
    for item in items_map:
        item.draw(screen)

    #mettre à jour le joueur    
    player.update(screen, room_draw, items, items_map, exits, room_badge, room_x, room_y)
    exits, items_map, items, room_badge, room_x, room_y  = player.replace()

    #afficher le niveau de badge
    if room_badge > 0:
        affichage(1000, 500, room_badge)
    
    #permet de  quitter le jeu
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    #rafrachir l'écran
    pygame.display.update()

pygame.quit()