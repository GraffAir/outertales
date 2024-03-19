from PIL import Image, ImageFilter, ImageOps, ImageEnhance
import pygame
pygame.font.init()


SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720
ACCENT_COLOR = (186, 231, 255)
BLACK_COLOR = (0, 0, 0)

font_header1 = pygame.font.Font('fonts/LTSoul-Bold.otf', 90)
font_header1_blur = pygame.font.SysFont('Impact', 90)
font_header2 = pygame.font.Font('fonts/LTSoul-Regular.otf', 50)
font_button = pygame.font.Font('fonts/NovaSlim-Regular.ttf', 40)

# on définit les images du menu
menu_bg_img = pygame.transform.scale(pygame.image.load("images/menu/menu_bg.png"), (SCREEN_WIDTH, SCREEN_HEIGHT))
settings_bg_img = pygame.Surface(menu_bg_img.get_size(), 32)
settings_bg_img.set_alpha(200, pygame.RLEACCEL)

# les textes
text_title = font_header1.render("Outertale", True, (255, 255, 255))
textbutton_play = font_header2.render("Jouer", True, ACCENT_COLOR)
textbutton_settings = font_header2.render("Paramètres", True, ACCENT_COLOR)
textbutton_leave = font_header2.render("Quitter", True, ACCENT_COLOR)

# les textes du menu paramètres
textbutton_audio = font_button.render("Audio", True, ACCENT_COLOR)
textbutton_controles = font_button.render("Contrôles", True, ACCENT_COLOR)
textbutton_back = font_button.render("Retour", True, ACCENT_COLOR)

textbutton_audio_activated = font_button.render("Audio", True, BLACK_COLOR)
textbutton_controles_activated = font_button.render("Contrôles", True, BLACK_COLOR)

# créer une variante floue des boutons principaux
def blur_surface(surface):
    pil_string_image = pygame.image.tostring(surface, "RGBA",False)
    result_image = Image.frombytes("RGBA",surface.get_size(),pil_string_image)
    result_image = ImageOps.expand(result_image, border = 20, fill = 0)
    result_image = result_image.filter(ImageFilter.GaussianBlur(radius=10))
    result_image = pygame.image.fromstring(result_image.tobytes("raw", 'RGBA'), result_image.size, 'RGBA')
    return result_image

text_title_blur = blur_surface(text_title)
blurs = {
    'play': blur_surface(textbutton_play),
    'settings': blur_surface(textbutton_settings),
    'quit': blur_surface(textbutton_leave)
}

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
            pygame.draw.rect(self.screen, ACCENT_COLOR, pygame.Rect(self.x, self.y, self.width, self.height), 3)
        else:
            pygame.draw.rect(self.screen, ACCENT_COLOR, pygame.Rect(self.x, self.y, self.width, self.height), 0)
        super().draw()
        return clicked

class TextButton(Button):
    """Classe héritée du Button représentant un simple bouton sous forme de texte"""
    def __init__(self, screen, rel_pos, rel_size, surface, anchorpoint=(0,0)):
        abs_pos, abs_size = get_absolute(rel_pos, rel_size, anchorpoint)
        super().__init__(screen, abs_pos, abs_size, surface)

# Gestion du curseur
bar = pygame.image.load("images/menu/slider/bar.png")
bar_unactive = pygame.image.load("images/menu/slider/bar_deactivated.png")
leftarrow = pygame.image.load("images/menu/slider/leftarrow.png")
leftarrow_unactive = pygame.image.load("images/menu/slider/leftarrow_deactivated.png")
rightarrow = pygame.image.load("images/menu/slider/rightarrow.png")
rightarrow_unactive = pygame.image.load("images/menu/slider/rightarrow_deactivated.png")

class SliderButton:
    """Classe représentant un curseur permettant de choisir un paramètre défini"""
    def __init__(self, screen, rel_pos, rel_size, intermediary_steps, padding):
        """
        intermediary_steps: le nombre de barres entre les deux flèches
        """
        abs_pos, abs_size = get_absolute(rel_pos, rel_size)
        self.x, self.y = abs_pos
        self.width, self.height = abs_size

        self.max_step = intermediary_steps + 2
        self.step = self.max_step//2

        step_width = self.width/self.max_step

        self.interaction = 0
        
        self.sub_button = Button(screen, abs_pos, (step_width, self.height), pygame.transform.scale(leftarrow, (step_width, self.height)))
        self.add_button = Button(screen, (self.x+ step_width * (intermediary_steps+1) - 2*padding, self.y), (step_width, self.height), pygame.transform.scale(rightarrow, (step_width-padding, self.height)))

        self.buttons = [(self.sub_button, leftarrow, leftarrow_unactive)]
        for i in range(intermediary_steps):
            button = Button(screen, (self.x + step_width * (i + 1) - 2*padding, self.y), (step_width-padding, self.height), bar)
            self.buttons.append((button, bar, bar_unactive))
        self.buttons.append((self.add_button, rightarrow, rightarrow_unactive))


    def update(self):
        for b in self.buttons:
            if b[0].update():
                self.step = self.buttons.index(b)
                return True
        return False

    def draw(self):
        for i in range(len(self.buttons)):
            button = self.buttons[i]
            if i <= self.step:
                button[0].surface = button[1]
            else:
                button[0].surface = button[2]
            
            button[0].draw()
        

class Menu:
    def __init__(self, s):
        self.current_window = "menu" # menu / settings / pause
        self.settings_tab = "audio" # audio / controls
        self.screen = s
        black_img = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        self.black_img = black_img.convert_alpha()
        self.counter = 0
        self.volume = [0.5, 0.5]

        # On définit les boutons
        self.buttons = {
            'main': {
                'play': TextButton(s, (0.1, 0.25), (0.12, 0.05), textbutton_play),
                'settings': TextButton(s, (0.1, 0.35), (0.12, 0.05), textbutton_settings),
                'quit': TextButton(s, (0.1, 0.45), (0.12, 0.05), textbutton_leave),
            },
            'settings': {
                ## communs
                'tab_controls': RectButton(s, (0.5, 0.2), (0.2, 0.1), [textbutton_controles, textbutton_controles_activated]),
                'tab_audio': RectButton(s, (0.3, 0.2), (0.2, 0.1), [textbutton_audio, textbutton_audio_activated]),
                'back': TextButton(s, (0.7, 0.2), (0.2, 0.1), textbutton_back, (0.5, 0.8)),

                ## onglet : audio
                'audio_music': SliderButton(s, (0.2, 0.4), (0.3, 0.05), 3, 5),
                'audio_sfx': SliderButton(s, (0.2, 0.6), (0.3, 0.05), 3, 5)

                ## onglet : controles
            }
        }



    def draw(self):
        """fonction qui sera appellé à chaque boucle du jeu où le menu est allumé"""
        self.counter += 1
        if self.counter > 500:
            self.counter = 0
        text_title_blur.set_alpha(abs(self.counter - 250)*255/500)

        title_x, title_y = get_absolute((0.1, 0.1), (0, 0))[0]
        if self.current_window == "menu":
            self.screen.blit(menu_bg_img, (0, 0))
            self.screen.blit(text_title, (title_x, title_y))
            self.screen.blit(text_title_blur, (title_x-20, title_y-20))
            
            
            if self.buttons['main']['settings'].update():
                self.current_window = "settings"

            if self.buttons['main']['quit'].update():
                pygame.quit()
                return

            for k, v in self.buttons['main'].items():
                if v.interaction == 1:
                    self.screen.blit(blurs[k], (v.rect.x-20, v.rect.y-20))
                v.draw()
            
            return self.buttons['main']['play'].update(), self.volume

        elif self.current_window == "settings":
            self.screen.blit(menu_bg_img, (0, 0))
            self.screen.blit(settings_bg_img, (0, 0))
            self.buttons['settings']['back'].draw()
            
            if self.buttons['settings']['back'].update():
                self.current_window = 'menu'

            if self.settings_tab == 'audio':
                audio_music = self.buttons['settings']['audio_music']
                audio_sfx = self.buttons['settings']['audio_sfx']
                if audio_music.update():
                    self.volume[0] = audio_music.step/audio_music.max_step
                
                if audio_sfx.update():
                    self.volume[1] = audio_sfx.step/audio_sfx.max_step

                audio_music.draw()
                audio_sfx.draw()

            if self.buttons['settings']['tab_audio'].update():
                self.settings_tab = 'audio'
                
            if self.buttons['settings']['tab_controls'].update():
                self.settings_tab = 'controls'
            
        return False, self.volume
        
        

        
                