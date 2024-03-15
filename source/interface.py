import pygame
pygame.font.init()


SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720

font_header1 = pygame.font.Font('fonts/LTSoul-Bold.otf', 70)
font_header2 = pygame.font.SysFont('Courier New', 50)

# on définit les images du menu
menu_bg_img = pygame.transform.scale(pygame.image.load("images/menu/menu_bg.png"), (SCREEN_WIDTH, SCREEN_HEIGHT))

# les textes
text_title = font_header1.render("Outertale", False, (255, 255, 255))
textbutton_play = font_header2.render("Jouer", False, (255, 255, 255))
textbutton_settings = font_header2.render("Paramètres", False, (255, 255, 255))
textbutton_leave = font_header2.render("Quitter", False, (255, 255, 255))

class Button:
    def __init__(self, relative_pos, img, size):
        relx, rely = relative_pos
        width, height = size
        #1280*relx - width/2

        absx = SCREEN_WIDTH * relx - width/2
        absy = SCREEN_HEIGHT * rely - height/2

        self.image = pygame.transform.scale(img, size)
        self.hoverimage = pygame.transform.scale(img, (size[0]*1.2, size[1]*1.2))
        self.rect = self.image.get_rect()
        self.rect.x = absx
        self.rect.y = absy
        self.clicked = False
        self.hover = False

    def draw(self, screen):
        action = False

        #avoir la position de la souris
        pos = pygame.mouse.get_pos()

        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                action = True
                self.clicked = True
            else:
                self.hover = True
        else:
            self.hover = False

        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False

        if self.hover == True:
            screen.blit(self.hoverimage, self.rect)
        else:
            screen.blit(self.image, self.rect)
        
        return action


# on définit les bouttons
    
play_btn = Button((0.5, 0.5), textbutton_play, (30 * 6, 30 * 2))
settings_btn = Button((0.25, 0.5), textbutton_settings, (30 * 5, 30))
leave_btn = Button((0.75, 0.5), textbutton_leave, (30 * 4, 30))



def draw_menu(screen):
    """fonction qui sera appellé à chaque boucle du jeu où le menu est allumé"""
    screen.blit(menu_bg_img, (0, 0))
    screen.blit(text_title, (490, 100))
    settings_btn.draw(screen)
    leave_btn.draw(screen)
    return play_btn.draw(screen)
            