import pygame

class Pancarte:
    def __init__(self, img, x, y):
        self.image = pygame.image.load(f"images/sign/{img}.png")
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def draw(self, screen):
        #if pygame.key.get_pressed()[pygame.K_f] == False:
        screen.blit(self.image, self.rect)
        #else:
           # screen.blit(self.image, (1300, 800))
