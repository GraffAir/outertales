#importer les bibliothèques / modules
import pygame
from pygame.locals import*
import pickle
from os import path
import map
import player

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
room_x = 0
room_y = 0
#les portes de sorties à considérer en collisions
exits = []
#les items actuellement au sol
items_map = []
#les items détenus par le joueur
items = []
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
player = player.Player(40, 40)

#lancer la boucle du jeu
run = True
while run:
    #régler la clock sur 60 fps
    clock.tick(60)

    #changer de map si nécessaire
    if room != rooms[room_y][room_x]:
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

    #afficher le sol
    screen.blit(bg_img, (0, 0))

    #dessine la map
    room_draw.draw(screen)

    #afficher les portes de sortie
    for exit in exits:
        exit.update()
        exit.draw(screen)

    #afficher les items
    for item in items_map:
        item.draw(screen)

    #mettre à jour le joueur    
    player.update(screen, room_draw, items, items_map, exits, room_badge, room_x, room_y)
    exits, items_map, items, room_badge, room_x, room_y  = player.replace()

    if room_badge > 0:
        affichage(1000, 500, room_badge)
    
    #permet de  quitter le jeu
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    #rafrachir l'écran
    pygame.display.update()

pygame.quit()