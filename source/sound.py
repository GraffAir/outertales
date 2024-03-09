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
    for elem in liste_textes:
        while not pygame.key.get_pressed()[pygame.K_p]:
            subTitles(elem, 'Arial', (0,0,0), 0, 0, False, True, screen)
