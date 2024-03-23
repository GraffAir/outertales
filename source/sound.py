import pygame


def subTitles(texte, police, couleur, x, y, gras , italic , screen):
    """
    fonction qui permet d'afficher le texte les parametres sont : texte, police, coleur, x, y, gras (True ou False) et italic (True ou False)
    """
    text_font = pygame.font.SysFont(police, 30, bold = gras, italic = italic)
    img = text_font.render(texte, True, couleur)
    screen.blit(img, (x,y))

def dialogues(liste_textes, screen):
    """
    Affiche un dialogue, passes au texte suivant quand p est pressé, les textes viennent d'une liste rentrée en paramètre de la fonction.
    """
    

    for i in range(len(liste_textes)):
        rect = pygame.Surface((980, 100))  # Create a surface for the rectangle
        rect.fill((0, 0, 0))  # Fill the rectangle with the clear color
        screen.blit(rect, (150, 500))  # Blit the rectangle onto the screen at position (0, 0)
        text_font2 = pygame.font.SysFont('Arial', 23, bold = False, italic = True)
        img2 = text_font2.render("Appuyer sur ESPACE pour continuer", True, (0, 0, 0))
        screen.blit(img2, (1280-img2.get_rect().width, 100-img2.get_rect().height))
        subTitles(liste_textes[i], 'Arial', (255, 255, 255), 150, 500, False, True, screen)
        pygame.display.update()  # Update the display after rendering the text
        
        while True:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    break
            else:
                continue
            break