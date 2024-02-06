import pygame

class Sign:
    def __init__(self, img, x, y):
        self.image = pygame.image.transform(pygame.image.load(f"images/signs/{img}.png"), (40, 40))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def draw(self, screen):
        screen.blit(self.image, self.rect)