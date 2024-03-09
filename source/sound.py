
def subTitles(texte, police='Arial', couleur=(0,0,0) , x, y):
    """
    fonction qui permet d'afficher le texte les parametres sont : texte, police, coleur, x, y
    """
    text_font = pygame.font.SysFont(police, 30)
    img = text_font.render(texte, True, couleur)
    screen.blit(img(x,y))