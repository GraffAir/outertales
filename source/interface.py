import pygame

class Button:
    def __init__(self, x, y, img):
        self.image = pygame.transform.scale(img, (40 * 6, 40 * 2))
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
    
# on définit
# les images du menu
play_btn_img = pygame.image.load("images/menu/play_btn.jpg")
menu_bg_img = pygame.transform.scale(pygame.image.load("images/menu/menu_bg.png"), (1280, 720))

# les bouttons
play_btn = Button(50, 50, play_btn_img)

def draw_menu(screen):
    screen.blit(menu_bg_img, (0, 0))
    return play_btn.draw(screen)
            