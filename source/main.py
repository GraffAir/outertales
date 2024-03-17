#importer les bibliothèques / modules
import pygame
from pygame.locals import*
from pygame import mixer
import map
import player
import rooms
import interface
import sound

#initialiser pygame
pygame.init()
mixer.init()
clock = pygame.time.Clock()
fps = 60

#configurer la fenêtre et la taille des cases
screen = pygame.display.set_mode((1280, 720))   
pygame.display.set_caption("Outer Tales")
tile_size = 40

interface_menu = interface.Menu(screen)

#les variables
#le niveau de pass pour passer les portes
room_badge = 0
#si le jeu est en cours, ou si le joueur est dans le menu, ou s'il regarde un panneau, s'il examine un coffre, ou s'il entre le mot de passe d'un coffre.
game, menu, sign, watch_chest, open_lock_chest, watch_archives  = False, True, False, False, False, False
#compteur pour les panneaux et les coffres quand on les ouvre avec mot de passe, qu'on les regarde de plus pres aussi 
sign_counter = 0
chest_counter = 0
lock_counter = 0
archives_counter = 0
#pour entrer des mots de passe de coffre
try_ = ""

#charger les images

#celle du sol
bg_img = pygame.image.load("images/map/floor.png").convert()
#le fond noir qui vient s'ajouter quand il n'y a pas d'électricité.
black_img = pygame.transform.scale(pygame.image.load("images/map/black.png"), (1280, 720)).convert_alpha()
black_img.fill((255, 255, 255, 175), special_flags=BLEND_RGBA_MULT)


pygame.mixer.music.load("sound.wav")
pygame.mixer.music.set_volume(0.7)
sound_counter = 451

def draw_badge_level(x, y, num):
   """fonction pour afficher le niveau de badge que possède le joueur"""
   screen.blit(pygame.transform.scale(pygame.image.load(f"images/items/level{num}.png"), (220, 140)), (x, y))

#on définit la salle de base et on la dessine
room = rooms.Rooms[rooms.room_y][rooms.room_x]
room_draw = map.Map(room, player.items, rooms.room_num, tile_size)

#on initialise le joueur
player_ = player.Player(1000, 300)
#lancer la boucle du jeu
run = True
while run:
    #régler la clock sur 60 fps
    clock.tick(fps)
    sound_counter += 1
    if sound_counter == 452:
        pygame.mixer.music.play()
        sound_counter = 0
    #si le jeu est en cours
    if game:
        #afficher le menu si le joueur appuie sur ECHAP, et les dialogues
        if pygame.key.get_pressed()[pygame.K_p]:
            sound.dialogues(["On peut faire des tests", "on passe au suivant", "ca marche"], screen)
        if pygame.key.get_pressed()[pygame.K_ESCAPE]:
            game, menu = False, True
        #changer de map si le joueur change de salle
        if room != rooms.Rooms[rooms.room_y][rooms.room_x]:
            room = rooms.Rooms[rooms.room_y][rooms.room_x]
            #changer le numéro de salle
            row_count = 0
            counter = 1
            for row in rooms.Rooms:
                col_count = 0
                for room_ in row:
                    if room_ == rooms.Rooms[rooms.room_y][rooms.room_x]:
                        rooms.room_num = counter
                    counter += 1
                    col_count += 1
                row_count += 1
            #la dessiner maintenant
            room_draw = map.Map(room, player.items, rooms.room_num, tile_size)
            #faire en sorte que la porte qu'on vient de passer reste ouverte
            for exit in map.exits:
                if player_.rect.colliderect(exit.rect.x - 100, exit.rect.y - 100, 200, 200):
                    exit.open, exit.go_back = True, True
                    exit.rect.x, exit.rect.y = exit.end_pos
                    exit.counter = 100
                    if exit.link == 1:
                        room[0][15], room[0][16] = f"{room[0][15][:3]}O", f"{room[0][16][:3]}O"
                        rooms.Rooms[rooms.room_y-1][rooms.room_x][17][15], rooms.Rooms[rooms.room_y-1][rooms.room_x][17][16] = f"{rooms.Rooms[rooms.room_y-1][rooms.room_x][17][15][:3]}O", f"{rooms.Rooms[rooms.room_y-1][rooms.room_x][17][16][:3]}O"
                    elif exit.link == 2:
                        room[17][15], room[17][16] = f"{room[17][15][:3]}O", f"{room[17][16][:3]}O"
                        rooms.Rooms[rooms.room_y+1][rooms.room_x][0][15], rooms.Rooms[rooms.room_y+1][rooms.room_x][0][16] = f"{rooms.Rooms[rooms.room_y+1][rooms.room_x][0][15][:3]}O", f"{rooms.Rooms[rooms.room_y+1][rooms.room_x][0][16][:3]}O"
                    elif exit.link == 3:
                        room[8][0], room[9][0] = f"{room[8][0][:3]}O", f"{room[9][0][:3]}O"
                        rooms.Rooms[rooms.room_y][rooms.room_x-1][8][31], rooms.Rooms[rooms.room_y][rooms.room_x-1][9][31] = f"{rooms.Rooms[rooms.room_y][rooms.room_x-1][8][31][:3]}O", f"{rooms.Rooms[rooms.room_y][rooms.room_x-1][9][31][:3]}O"
                    elif exit.link == 4:
                        room[8][31], room[9][31] = f"{room[8][31][:3]}O", f"{room[9][31][:3]}O"
                        rooms.Rooms[rooms.room_y][rooms.room_x+1][8][0], rooms.Rooms[rooms.room_y][rooms.room_x+1][9][0] = f"{rooms.Rooms[rooms.room_y][rooms.room_x+1][8][0][:3]}O", f"{rooms.Rooms[rooms.room_y][rooms.room_x+1][9][0][:3]}O"

        #afficher le sol
        screen.blit(bg_img, (0, 0))

        #dessine la map
        room_draw.draw(screen)

        #afficher les portes de sortie, et les faire bouger si nécessaire
        for exit in map.exits:
            exit.update(player_, screen)
            for exit_ in map.exits:
                if exit.link == exit_.link:
                    if exit.collisions_counter == exit_.collisions_counter:
                        if exit.open == True:
                            exit_.open = True
        
        #afficher les coffres ouverts et fermés
        for chest in map.chests:
            chest.update(screen, rooms.room_num, game)

        for chest in map.chests_open:
            chest.update(screen, rooms.room_num, game)

        #afficher les items sur la map
        for item in map.items_map:
            item.draw(screen)

        #afficher les panneaux
        for sign in map.signs:
            sign, game = sign.update(screen, sign, game)

        #afficher les props
        for prop in map.props:
            prop.draw(screen)

        for archive in map.archives:
            archive.draw(screen)
            if pygame.key.get_pressed()[pygame.K_e] == False:
                archive.paper_watched_cooldown = True
        
        if map.generator != None:
            map.generator.draw(screen)

        #mettre à jour le joueur    
        player_.update(screen, room_draw, map.items_map, map.exits, map.signs, map.chests, map.chests_open, room_badge, rooms.room_num, rooms.room_x, rooms.room_y, map.electricity, map.props, map.archives, map.generator)
        map.exits, map.items_map, map.chests, map.chests_open, map.archives, room_badge, rooms.room_x, rooms.room_y, open_lock_chest, watch_chest, watch_archives, map.electricity  = player_.replace()

        #si on tente d'ouvrir un coffre vérouillé
        if open_lock_chest:
            game = False
        
        #si on tente de regarder un coffre de plus pres
        if watch_chest:
            game = False

        if watch_archives:
            game = False
            
        #afficher le niveau de badge
        if room_badge > 0:
            draw_badge_level(1000, 500, room_badge)

        #asssombrir l'écran s'il n'y a pas d'electricité
        if map.electricity == False:
            screen.blit(black_img, (0, 0))

    #si le menu est ouvert
    elif menu:
        #dessiner le menu
        start, volume = interface_menu.draw()  
        pygame.mixer.music.set_volume(volume[0])      
        if start:
            menu, game = False, True
        

    #si un panneau est affiché à l'écran
    elif sign:
        #incrémenter le compteur
        sign_counter += 1
        #afficher le fond et les murs, les portes et les items
        screen.blit(bg_img, (0, 0))
        room_draw.draw(screen)

        for exit in map.exits:
            exit.draw(screen)

        for item in map.items_map:
            item.draw(screen)

        for chest in map.chests:
            chest.draw(screen)

        for chest in map.chests_open:
            chest.draw(screen)
            if chest.contenu != "" and chest.item_took == False:
                chest.contenu.draw(screen)
        #afficher le panneau
        for sign in map.signs:
            if sign.draw == True:
                sign.draw_sign(screen)
                #si le joueur réappuie sur E, ou se déplace, si le compteur est suffisement grand, alors enlever le panneau et revenir au jeu
                if pygame.key.get_pressed()[pygame.K_e] or pygame.key.get_pressed()[pygame.K_LEFT] or pygame.key.get_pressed()[pygame.K_RIGHT] or pygame.key.get_pressed()[pygame.K_UP] or pygame.key.get_pressed()[pygame.K_DOWN]:
                    if sign_counter >= 50:
                        sign.draw = False
                        sign, game = False, True
                        sign_counter = 0

    #si le joueur ouvre un coffre verouillé
    elif open_lock_chest:
        lock_counter += 1
        screen.blit(bg_img, (0, 0))
        screen.blit(pygame.image.load("images/password.png"), (140, 110))
        #les valeurs pouvant être rentrés
        vals = [_ for _ in range(0, 10)]
        #si le joueur appuie sur un chiffre, il l'ajoute à l'essai.
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                try:
                    if int(event.dict['unicode']) in vals:
                        try_ = try_ + str(event.dict['unicode'])
                except:
                    pass
        #s'il a commencé a tapper un mot de passe, alors afficher des asterisques
        if len(try_) == 1:
            screen.blit(pygame.image.load("images/aste.png"), (250, 350))
        if len(try_) == 2:
            screen.blit(pygame.image.load("images/aste.png"), (250, 350))
            screen.blit(pygame.image.load("images/aste.png"), (450, 350))
        if len(try_) == 3:
            screen.blit(pygame.image.load("images/aste.png"), (250, 350))
            screen.blit(pygame.image.load("images/aste.png"), (450, 350))
            screen.blit(pygame.image.load("images/aste.png"), (650, 350))
        #si le mot de passe est le bon, ouvrir le coffre et revenir au jeu
        if len(try_) == 4:
            for ch in map.chests:
                if ch.try_open == True:
                    if try_ == ch.code:
                        ch.try_open = False
                        ch.locked = False
                        ch.open = True
                        map.chests.remove(ch)
                        map.chests_open.append(ch)
                        if ch.contenu != "":
                            map.items_map.append(ch.contenu)
                        game = True
                        open_lock_chest = False
                    else:
                        try_ = ""

        if map.electricity == False:
            screen.blit(black_img, (0, 0))

        if pygame.key.get_pressed()[pygame.K_e]:
            if lock_counter >= 15:
                game = True
                open_lock_chest = False
                try_ = ""
                lock_counter = 0
                for ch in map.chests:
                    ch.try_open = False

    #si le joueur observe un coffre de plus pres
    elif watch_chest:
        chest_counter += 1
        screen.blit(bg_img, (0, 0))
        #afficher le fond, le joueur, les portes, les autres coffres, les props
        room_draw.draw(screen)
        for exit in map.exits:
            exit.draw(screen)
        
        for item in map.items_map:
            item.draw(screen)

        for chest in map.chests:
            chest.draw(screen)

        for prop in map.props:
            prop.draw(screen)

        for ch in map.chests_open:
            if ch.room == rooms.room_num and ch.watched == False:
                ch.draw(screen)
                if chest.contenu != "" and chest.item_took == False:
                    chest.contenu.draw(screen)

        player_.draw(screen)
        #si c'est le coffre ouvert, afficher son image
        for ch in map.chests_open:
            if ch.watched == True:
                ch.draw(screen)
                screen.blit(pygame.transform.scale(pygame.image.load(f"images/ref_chest/{ch.ref}.png"), (560, 560)), (360, 80))
                #si le joueur appuie sur E ou se déplace, l'image s'enleve
                if pygame.key.get_pressed()[pygame.K_e] or pygame.key.get_pressed()[pygame.K_UP] or pygame.key.get_pressed()[pygame.K_DOWN] or pygame.key.get_pressed()[pygame.K_LEFT] or pygame.key.get_pressed()[pygame.K_RIGHT]:
                    if chest_counter >= 50:
                        watch_chest, game = False, True
                        chest_counter = 0
                        ch.watched = False

        if map.electricity == False:
            screen.blit(black_img, (0, 0))
    
    elif watch_archives:
        archives_counter += 1
        screen.blit(bg_img, (0, 0))
        #afficher le fond, le joueur, les portes, les autres coffres, les props
        room_draw.draw(screen)

        for exit in map.exits:
            exit.draw(screen)
        
        for item in map.items_map:
            item.draw(screen)

        for chest in map.chests:
            chest.draw(screen)

        for prop in map.props:
            prop.draw(screen)

        for archive in map.archives:
            archive.draw(screen)

        for chest in map.chests_open:
            if chest.room == rooms.room_num:
                chest.draw(screen)
                if chest.contenu != "" and chest.item_took == False:
                    chest.contenu.draw(screen)

        player_.draw(screen)
        #si c'est le coffre ouvert, afficher son image
        for archive in map.archives:
            if archive.paper_watch == True:
                archive.draw_paper(screen)
                #si le joueur appuie sur E ou se déplace, l'image s'enleve
                if pygame.key.get_pressed()[pygame.K_e] or pygame.key.get_pressed()[pygame.K_UP] or pygame.key.get_pressed()[pygame.K_DOWN] or pygame.key.get_pressed()[pygame.K_LEFT] or pygame.key.get_pressed()[pygame.K_RIGHT]:
                    if archives_counter >= 50:
                        watch_archives, game = False, True
                        archives_counter = 0
                        archive.paper_watch = False

        if map.electricity == False:
            screen.blit(black_img, (0, 0))

    #permet de  quitter le jeu
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    #rafrachir l'écran
    pygame.display.update()

pygame.quit()