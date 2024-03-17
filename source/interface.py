import pygame
pygame.font.init()


SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720
ACCENT_COLOR = (53, 144, 247)
BLACK_COLOR = (0, 0, 0)

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
textbutton_audio_activated = font_button.render("Audio", False, BLACK_COLOR)
textbutton_controles_activated = font_button.render("Contrôles", False, BLACK_COLOR)

def get_absolute(position, size, anchorpoint=(0, 0)):
    relx, rely = position
    relwidth, relheight = size
    width, height = (SCREEN_WIDTH * relwidth), (SCREEN_HEIGHT * relheight)
    absx = SCREEN_WIDTH * relx - width*anchorpoint[0]
    absy = SCREEN_HEIGHT * rely - height*anchorpoint[1]
    assert width < 10000 and height < 10000 and absx <= SCREEN_WIDTH and absy <= SCREEN_HEIGHT, "Absolute Value Out of Range"
    return (absx, absy), (width, height)

class Button:
    """
    Classe ne représentant que le squelette d'un bouton : l'interactivité et la surface (texte ou image) intérieure
    Elle n'est *pas* destinée à être utilisée directement, mais à être héritée dans d'autres classes de boutons.
    """
    def __init__(self, screen, position, size, surface, hoversurface=None):
        self.screen = screen
        self.surface = surface
        # self.hoversurface = pygame.transform.scale(surface, (size[0]*1.2, size[1]*1.2))
        self.hoversurface = hoversurface
        self.rect = self.surface.get_rect()
        self.rect.x, self.rect.y = position
        self.interaction = 0 # 0 = None / 1 = Hover / 2 = Click

    def update(self):
        clicked = False

        #avoir la position de la souris
        pos = pygame.mouse.get_pos()

        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1:
                clicked = self.interaction != 2
                self.interaction = 2
            elif pygame.mouse.get_pressed()[0] == 0:
                self.interaction = 1
        else:
            self.interaction = 0
        
        return clicked

    def draw(self):
        if self.interaction == 1 and self.hoversurface != None:
            self.screen.blit(self.hoversurface, self.rect)
        else:
            self.screen.blit(self.surface, self.rect)       

class RectButton(Button):
    """Classe héritée du Button permettant de créer un bouton aux bordures rectangulaires"""
    def __init__(self, screen, rel_pos, rel_size, surfaces):
        self.hoversurface = surfaces[1]
        
        abs_pos, abs_size = get_absolute(rel_pos, rel_size)
        self.x, self.y = abs_pos
        self.width, self.height = abs_size

        text_absx = self.x+self.width/2-surfaces[0].get_width()/2
        text_absy = self.y+self.height/2-surfaces[0].get_height()/2
        super().__init__(screen, (text_absx, text_absy), abs_size, surfaces[0], surfaces[1])

    def update(self):
        clicked = super().update()
        if self.interaction == 0:
            pygame.draw.rect(self.screen, (53, 144, 247), pygame.Rect(self.x, self.y, self.width, self.height), 3)
        else:
            pygame.draw.rect(self.screen, (53, 144, 247), pygame.Rect(self.x, self.y, self.width, self.height), 0)
        super().draw()
        return clicked

class TextButton(Button):
    """Classe héritée du Button représentant un simple bouton sous forme de texte"""
    def __init__(self, screen, rel_pos, rel_size, surface):
        abs_pos, abs_size = get_absolute(rel_pos, rel_size)
        surface = pygame.transform.scale(surface, abs_size)
        super().__init__(screen, abs_pos, abs_size, surface)
        

class Menu:
    def __init__(self, s):
        self.current_window = "menu" # menu / settings / pause
        self.settings_tab = "audio" # audio / controls
        self.screen = s
        black_img = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        self.black_img = black_img.convert_alpha()

        # On définit les boutons
        self.buttons = {
            'main': {
                'play': TextButton(s, (0.4, 0.5), (0.15, 0.07), textbutton_play),
                'settings': TextButton(s, (0.18, 0.5), (0.13, 0.05), textbutton_settings),
                'quit': TextButton(s, (0.65, 0.5), (0.12, 0.05), textbutton_leave)
            },
            'settings': {
                ## communs
                'tab_controls': RectButton(s, (0.5, 0.2), (0.2, 0.1), [textbutton_controles, textbutton_controles_activated]),
                'tab_audio': RectButton(s, (0.3, 0.2), (0.2, 0.1), [textbutton_audio, textbutton_audio_activated])

                ## onglet : audio
                # TODO 'audio_music': SliderButton(s, pos, size)

                ## onglet : controles
            }
        }



    def draw(self):
        """fonction qui sera appellé à chaque boucle du jeu où le menu est allumé"""
        pass
        if self.current_window == "menu":
            self.screen.blit(menu_bg_img, (0, 0))
            self.screen.blit(text_title, (450, 100))
            
            if self.buttons['main']['settings'].update():
                self.current_window = "settings"

            if self.buttons['main']['quit'].update():
                pygame.quit()
                return
            
            for v in self.buttons['main'].values():
                v.draw()
            
            return self.buttons['main']['play'].update()

        elif self.current_window == "settings":
            self.screen.blit(menu_bg_img, (0, 0))
            self.screen.blit(settings_bg_img, (0, 0))

            if self.buttons['settings']['tab_audio'].update():
                self.settings_tab = 'audio'

            if self.buttons['settings']['tab_controls'].update():
                self.settings_tab = 'controls'
            
        return False
        
        

        
                