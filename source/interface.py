import pygame
pygame.font.init()


SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720
ACCENT_COLOR = (53, 144, 247)

font_header1 = pygame.font.Font('fonts/LTSoul-Bold.otf', 90)
font_header2 = pygame.font.SysFont('LTSoul-Regular', 50)
font_button = pygame.font.SysFont('LTSoul-Regular', 50)

# on définit les images du menu
menu_bg_img = pygame.transform.scale(pygame.image.load("images/menu/menu_bg.png"), (SCREEN_WIDTH, SCREEN_HEIGHT))
settings_bg_img = pygame.Surface(menu_bg_img.get_size(), 32)
settings_bg_img.set_alpha(200, pygame.RLEACCEL)

# les textes
text_title = font_header1.render("Outertale", False, (255, 255, 255))
textbutton_play = font_header2.render("Jouer", False, (255, 255, 255))
textbutton_settings = font_header2.render("Paramètres", False, (255, 255, 255))
textbutton_leave = font_header2.render("Quitter", False, (255, 255, 255))


# les textes du menu paramètres
textbutton_audio = font_button.render("Audio", False, ACCENT_COLOR)
textbutton_controles = font_button.render("Contrôles", False, ACCENT_COLOR)

def get_absolute(position, size, anchorpoint=(0, 0)):
    relx, rely = position
    relwidth, relheight = size
    width, height = (SCREEN_WIDTH * relwidth), (SCREEN_HEIGHT * relheight)
    absx = SCREEN_WIDTH * relx - width*anchorpoint[0]
    absy = SCREEN_HEIGHT * rely - height*anchorpoint[1]
    assert width < 10000 and height < 10000 and absx <= SCREEN_WIDTH and absy <= SCREEN_HEIGHT, "Absolute Value Out of Range"
    return (absx, absy), (width, height)

class Button:
    def __init__(self, pos, img, rel_size, anchorpoint=(0,0)):

        abs_pos, size = get_absolute(pos, rel_size, anchorpoint)
        absx, absy = abs_pos

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
    
play_btn = Button((0.4, 0.5), textbutton_play, (0.15, 0.07), (0, 1))
settings_btn = Button((0.18, 0.5), textbutton_settings, (0.13, 0.05), (0, 1))
leave_btn = Button((0.65, 0.5), textbutton_leave, (0.12, 0.05), (0, 1))
    


class Menu:
    def __init__(self, screen):
        self.current_window = "menu" # menu / settings / pause
        self.screen = screen
        black_img = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        self.black_img = black_img.convert_alpha()

    def draw(self):
        """fonction qui sera appellé à chaque boucle du jeu où le menu est allumé"""
        pass
        if self.current_window == "menu":
            self.screen.blit(menu_bg_img, (0, 0))
            self.screen.blit(text_title, (450, 100))
            if settings_btn.draw(self.screen):
                self.current_window = "settings"

            if leave_btn.draw(self.screen):
                pygame.quit()
            
            return play_btn.draw(self.screen)

        elif self.current_window == "settings":
            self.screen.blit(menu_bg_img, (0, 0))
            self.screen.blit(settings_bg_img, (0, 0))

            def textButton(x, y, width, height, surface):
                (absx, absy), (abswidth, absheight) = get_absolute((x, y), (width, height))
                pygame.draw.rect(self.screen, (53, 144, 247), pygame.Rect(absx, absy, abswidth, absheight), 3)
                
                self.screen.blit(surface, (absx+abswidth/2-surface.get_width()/2, absy+absheight/2-surface.get_height()/2)) 
                
            
            textButton(0.3, 0.2, 0.2, 0.1, textbutton_audio)
            textButton(0.5, 0.2, 0.2, 0.1, textbutton_controles)





            return False
        
        

        
                