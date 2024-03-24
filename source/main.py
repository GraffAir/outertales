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
pygame.display.set_caption("Outer Tale")
pygame.display.set_icon(pygame.image.load("images/logo.png"))
tile_size = 40

#les variables
#le menu
interface_menu = interface.Menu(screen)
#le niveau de pass pour passer les portes
room_badge = 0
#si le jeu est en cours, ou si le joueur est dans le menu, ou s'il regarde un panneau, s'il examine un coffre, ou s'il entre le mot de passe d'un coffre, s'il regarde une archive, si cest la fin
game, menu, sign, watch_chest, open_lock_chest, watch_archives, end1, end2  = False, True, False, False, False, False, False, False
#compteur pour les panneaux et les coffres quand on les ouvre avec mot de passe, qu'on les regarde de plus pres aussi , quand on regarde une archive, quand on dévérouille un coffre, et quand la fin arrive
sign_counter, chest_counter, lock_counter, archives_counter, unlock_counter, outro_counter = 0, 0, 0, 0, 0, 0
#pour entrer des mots de passe de coffre
try_ = ""
vals = [_ for _ in range(0, 10)]
#pour les dialogues qui apparaissent à certains moments
start_speak, door_speak, end_revelation, end_revelation_already, end_dilemma, end_dilemma_already = False, False, False, False, False, False
not_enough_badge_speak = False
#charger les images

#celle du sol
bg_img = pygame.image.load("images/map/floor.png").convert()
#le fond noir qui vient s'ajouter quand il n'y a pas d'électricité.
black_img = pygame.transform.scale(pygame.image.load("images/map/black.png"), (1280, 720)).convert_alpha()
black_img.fill((255, 255, 255, 175), special_flags=BLEND_RGBA_MULT)
#celles quand on rentre un mot de passe
password_img = pygame.transform.scale(pygame.image.load("images/password.png"), (1000, 500)).convert()
password_img1 = pygame.transform.scale(pygame.image.load("images/password_1.png"), (1000, 500)).convert()
password_img2 = pygame.transform.scale(pygame.image.load("images/password_2.png"), (1000, 500)).convert()
password_img3 = pygame.transform.scale(pygame.image.load("images/password_3.png"), (1000, 500)).convert()
password_img4 = pygame.transform.scale(pygame.image.load("images/password_4.png"), (1000, 500)).convert()
password_img_g = pygame.transform.scale(pygame.image.load("images/password_good.png"), (1000, 500)).convert()

#charger le fond sonore
pygame.mixer.music.load("sound.wav")
pygame.mixer.music.set_volume(0.7)
#le compteur pour remettre la musique quand c'est fini
sound_counter = 451

def draw_badge_level(x, y, num):
   """fonction pour afficher le niveau de badge que possède le joueur"""
   screen.blit(pygame.transform.scale(pygame.image.load(f"images/items/level{num}.png"), (220, 140)), (x, y))

   
def text(text, col=(255, 255, 255), pol="Arial"):
    """fonction pour afficher du texte"""
    return pygame.font.SysFont(pol, 35, True).render(f"{text}", False, col)

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
    #la musique
    sound_counter += 1
    if sound_counter == 452:
        pygame.mixer.music.play()
        sound_counter = 0   
    #si le jeu est en cours
    if game:
        #afficher le menu si le joueur appuie sur ECHAP, et les dialogues
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

            #si on est dans la salle de controle, on apprend ce qu'il s'est passé
            if rooms.room_num == 14:
                if end_revelation == False:
                    if end_revelation_already == False:
                        end_revelation = True
            
            #si on est dans la baie de lancement, on a le choix final
            if rooms.room_num == 5:
                if end_dilemma == False:
                    if end_dilemma_already == False:
                        if end_revelation_already:
                            end_dilemma = True
            
            if rooms.room_num == 16:
                bg_img = pygame.transform.scale(pygame.image.load("images/map/floor_labyrinthe.png"), (1280, 720)).convert()
            else:
                bg_img = pygame.transform.scale(pygame.image.load("images/map/floor.png"), (1280, 720)).convert()

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

        #mettre à jour le joueur    
        player_.update(screen, room_draw, map.items_map, map.exits, map.signs, map.chests, map.chests_open, room_badge, rooms.room_num, rooms.room_x, rooms.room_y, map.electricity, map.props, map.archives, map.generator, map.ship, end_revelation_already, map.chair)
        map.exits, map.items_map, map.chests, map.chests_open, map.archives, room_badge, rooms.room_x, rooms.room_y, open_lock_chest, watch_chest, watch_archives, map.electricity, door_speak, not_enough_badge_speak  = player_.replace()

        #dessine la map
        room_draw.draw(screen)

        #afficher les props
        for prop in map.props:
            prop.draw(screen)

        #afficher les archives
        for archive in map.archives:
            archive.draw(screen)
        
        #s'il existe, afficher le generateur
        if map.generator != None:
            map.generator.draw(screen)

        #s'il existe, afficher le vaisseau pour s'enfuir
        if map.ship != None:
            map.ship.draw(screen)
            if map.ship.isCollide:
                end1, game = True, False

        #si elle existe, afficher la chaise à la fin
        if map.chair != None:
            map.chair.draw(screen)
            if map.chair.isCollide:
                end2, game = True, False

        #si on tente d'ouvrir un coffre vérouillé
        if open_lock_chest:
            game = False
        
        #si on tente de regarder un coffre de plus pres
        if watch_chest:
            game = False

        #si on regarde une archive
        if watch_archives:
            game = False
            
        #si la fin du vaisseau arrive
        if end1:
            game = False

        #si la fin de l'attente arrive
        if end2:
            game = False

        #afficher le niveau de badge
        if room_badge > 0:
            draw_badge_level(1000, 500, room_badge)

        #asssombrir l'écran s'il n'y a pas d'electricité
        if map.electricity == False:
            screen.blit(black_img, (0, 0))

        #afficher le dialogue de départ
        if start_speak == False:
            sound.dialogues(["-Que se passe t-il alors ?", "-Pourquoi suis-je dans ce vaisseau abandonné ? ", "-Je ne me souviens de rien...", "En plus la lumière à l'air éteinte..."], screen)
            start_speak = True
        
        #si une porte est fermé et qu'on essaie de l'ouvrir sans rien
        if door_speak == True:
            sound.dialogues([("La porte ne veut pas s'ouvrir, l'electricité à l'air coupée. Il n'y aurait pas", "quelque chose pour forcer la porte ?")], screen)
            door_speak = False

        if not_enough_badge_speak == True:
            sound.dialogues(["Niveau de carte suplémentaire recquis"], screen)
            not_enough_badge_speak = False

        #la revelation que c'est le personnage qui a fait ca
        if end_revelation == True:
            sound.dialogues(["-Ne bouge pas !", "-Qui êtes vous", "-Tu es là pour terminer le travail, cest ca ?", "-Mais de quoi parlez vous ?", ("-Tu ne te souviens pas ? C'est toi qui a tué tout le monde, allez vas y,", "prend ma vie si tu n'a donc pas de coeur !")], screen)
            end_revelation = False
            end_revelation_already = True

        #le dilemme de fin
        if end_dilemma == True:
            sound.dialogues([("En entrant dans la baie de lancement, vous être pris d'un grand remord", "suite à l'annonce que vous avez tué tout le monde"), ("Vous pouvez vous enfuir avec le vaisseau et garder votre peine à tout", "jamais..."), ("Ou vous asseoir sur la chaise et attendre la police pour qu'elle vienne", "vous prendre")], screen)
            end_dilemma = False
            end_dilemma_already = True

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
        if lock_counter <= 14:
            lock_counter += 1
        #dessiner le fond
        screen.blit(bg_img, (0, 0))
        #pour detecter si le joueur appuie sur les touche du clavier
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.dict["unicode"] == "\x08":
                    try_ = try_[0:(len(try_)-1)]
                try:
                    if int(event.dict['unicode']) in vals:
                        try_ = try_ + str(event.dict['unicode'])
                except:
                    pass

        #s'il a commencé a tapper un mot de passe, alors changer l'image
        if try_ == "":
            screen.blit(password_img, (140, 110))
        elif len(try_) == 1:
            screen.blit(password_img1, (140, 110))
        elif len(try_) == 2:
            screen.blit(password_img2, (140, 110))
        elif len(try_) == 3:
            screen.blit(password_img3, (140, 110))
        elif len(try_) == 4:
            screen.blit(password_img4, (140, 110))
        
        #si le mot de passe est le bon, ouvrir le coffre et revenir au jeu
        if len(try_) == 4:
            for ch in map.chests:
                if ch.try_open == True:
                    if try_ == ch.code:
                        screen.blit(password_img_g, (140, 110))
                        unlock_counter += 1
                        if unlock_counter == 15:
                            ch.try_open = False
                            ch.locked = False
                            ch.open = True
                            map.chests.remove(ch)
                            map.chests_open.append(ch)
                            if ch.contenu != "":
                                map.items_map.append(ch.contenu)
                            game = True
                            open_lock_chest = False
                            unlock_counter = 0
                            try_ = ""
                    else:
                        try_ = ""

        #s'il n'y a pas d'electricité
        if map.electricity == False:
            screen.blit(black_img, (0, 0))

        #pouvoir sortir de ca
        if pygame.key.get_pressed()[pygame.K_e]:
            if lock_counter == 15:
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
                screen.blit(pygame.transform.scale(pygame.image.load(f"images/box_open.png"), (560, 560)), (360, 80))
                screen.blit(pygame.transform.scale(text("appuyer sur E pour revenir au jeu", (0, 0, 0), "Comic Sans MS"), (300, 40)).convert_alpha(), (940, 40))
                screen.blit(text(f"{ch.ref}", (0, 0, 0), "Comic Sans MS"), (1280/2-text(f"{ch.ref}", (0, 0, 0), "Comic Sans MS").get_rect().width/2, 90))
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

    #si la fin du vaisseau arrive
    elif end1:
        pygame.draw.rect(screen, (0, 0 ,0), pygame.Rect(0, 0, 1280, 720))
        if outro_counter < 300:
            outro_counter += 1
        if 0 < outro_counter < 150:
            screen.blit(text("Vous vous enfuyez avec le vaisseau"), (640 - text("Vous vous enfuyez avec le vaisseau").get_rect().width/2, 720*1/4 - text("Vous vous enfuyez avec le vaisseau").get_rect().height))
        if  150 <= outro_counter < 300:
            screen.blit(text("Vous mourrez de faim au bout de 48H"), (640 - text("Vous mourrez de faim au bout de 48H").get_rect().width/2, 720*2/4 - text("Vous mourrez de faim au bout de 48H").get_rect().height))
        if outro_counter == 300:
            screen.blit(text("GAME OVER", (255, 0, 0)), (640 - text("GAME OVER").get_rect().width/2, 720*3/4 - text("GAME OVER").get_rect().height))

    #si la fin où le personnage choisit d'attendre la police
    elif end2:
        pygame.draw.rect(screen, (0, 0 ,0), pygame.Rect(0, 0, 1280, 720))
        if outro_counter < 300:
            outro_counter += 1
        if 0 < outro_counter < 150:
            screen.blit(text("La police vient vous chercher 2 jours plus tard"), (640 - text("La police vient vous chercher 2 jours plus tard").get_rect().width/2, 720*1/4 - text("La police vient vous chercher 2 jours plus tard").get_rect().height))
        if  150 <= outro_counter < 300:
            screen.blit(text("Vous eccopez d'une peine de 15 ans de prison"), (640 - text("Vous eccopez d'une peine de 15 ans de prison").get_rect().width/2, 720*2/4 - text("Vous eccopez d'une peine de 15 ans de prison").get_rect().height))
        if outro_counter == 300:
            screen.blit(text("THE END", (255, 0, 0)), (640 - text("THE END").get_rect().width/2, 720*3/4 - text("THE END").get_rect().height))
            
    #permet de  quitter le jeu
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    #rafrachir l'écran
    pygame.display.update()

pygame.quit()
