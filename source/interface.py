import pygame
pygame.font.init()

font_header1 = pygame.font.SysFont('Courier New', 70, bold=True)
font_header2 = pygame.font.SysFont('Courier New', 50)

# on définit les images du menu
play_btn_img = pygame.image.load("images/menu/play_btn.jpg")
menu_bg_img = pygame.transform.scale(pygame.image.load("images/menu/menu_bg.png"), (1280, 720))

# les textes
text_title = font_header1.render("Outertale", False, (255, 255, 255))
textbutton_play = font_header2.render("Jouer", False, (255, 255, 255))

class Button:
    def __init__(self, x, y, img, size):
        self.image = pygame.transform.scale(img, size)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.clicked = False

    def draw(self, screen):
        action = False

        #avoir la position de la souris
        pos = pygame.mouse.get_pos()

        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                action = True
                self.clicked = True

        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False

        screen.blit(self.image, self.rect)

        return action

# on définit les bouttons
play_btn = Button(100, 200, textbutton_play, (30 * 6, 30 * 2))

def draw_menu(screen):
    """fonction qui sera appellé à chaque boucle du jeu où le menu est allumé"""
    screen.blit(menu_bg_img, (0, 0))
    screen.blit(text_title, (100, 100))
    return play_btn.draw(screen)
            