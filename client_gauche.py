__all__ = ['main']

import pygame
import pygame_menu
import socket
from pygame_menu.examples import create_example_window

from random import randrange
from typing import Tuple, Any, Optional, List

pygame.init()

'''------------------------------------------------VARIABLES GLOBALES------------------------------------------------'''
# SERVEUR
ADRESSEIPV4 = "172.23.2.26"
PORT = 9954
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# FENETRE
LARGEUR = 1000
HAUTEUR = 700
FENETRE = pygame.display.set_mode((LARGEUR, HAUTEUR))
FPS = 60
pygame.display.set_caption("Pong")

# COULEURS, SONS ET STYLE D'ECRITURE
BLANC = (255, 255, 255)
NOIR = (0, 0, 0)
ROSE = (253, 108, 158)
ORANGE = (255, 127,0)
JAUNE = (255, 255, 0)
VERT = (0,255,0)
ROUGE = (255,0,0)
BLEU = (0,0,255)

SCORE_FONT = pygame.font.Font("Minecraft.ttf", 32)
SON_BUT = pygame.mixer.Sound('score.wav')
SON_RAQUETTE = pygame.mixer.Sound('pong.wav')
SON_MUR = pygame.mixer.Sound('song_mur.wav')
SON_VICTOIRE = pygame.mixer.Sound('victoire.wav')

# JEU
run = True
player_connected = False
HAUTEUR_RAQUETTE = 100
LARGEUR_RAQUETTE = 10
RAYON_BALLE = 10
SCORE_GAGNANT = 10

# CREATION JEU
clock = pygame.time.Clock()
score_gauche = 0
score_droite = 0

TAILLE = ['NORMALE']
VITESSE = ['NORMALE']
NB_JOUEURS = ['2']
BG_COLOR = ['NOIR']
R_B_COLOR = ['BLANC']
TEXT_COLOR = ['NOIR']
WINNING_SCORE = ['10']
texte_score_color = (255, 255, 255)
background_color = (0, 0, 0)
raquette_balle_color = (255, 255, 255)
winning_score = 10
taille_raquette = 2
FPS = 60
WINDOW_SIZE = (1000, 700)

clock: Optional['pygame.time.Clock'] = None
main_menu: Optional['pygame_menu.Menu'] = None
surface: Optional['pygame.Surface'] = None
'''------------------------------------------------------------------------------------------------------------------'''


class Raquette:
    COULEUR = raquette_balle_color
    VITESSE_RAQUETTE = 9

    def __init__(self, x, y, largeur, hauteur):
        self.x = self.x_originale = x
        self.y = self.y_originale = y
        self.largeur = largeur
        self.hauteur = hauteur

    def dessin(self, fenetre, r_b_color):
        pygame.draw.rect(fenetre, r_b_color, (self.x, self.y, self.largeur, self.hauteur))

    def mouvement(self, up=True):
        if up:
            self.y -= self.VITESSE_RAQUETTE
        else:
            self.y += self.VITESSE_RAQUETTE

    def reset(self):
        self.x = self.x_originale
        self.y = self.y_originale


'''
Classe : Balle
Fonctions : init(x, y, rayon)
           dessin(self, fenetre)
           mouvement_balle(self)
           reset(self)

Cette classe permet de créer une balle en précisant ses coordonées (x,y) ainsi que son rayon dans les 
paramètres de la fonction init. La fonction dessin permet de dessiner la balle, mouvement_balle gère les déplacements de
la balle en fonction des données envoyees par le serveur et reset replace la balle au centre.'''


class Balle:
    MAX_VITESSE = 9

    def __init__(self, x, y, rayon):
        self.x = self.x_originale = x
        self.y = self.y_originale = y
        self.rayon = rayon
        self.x_vitesse = self.MAX_VITESSE
        self.y_vitesse = 0

    def dessin(self, fenetre, r_b_color):
        pygame.draw.circle(fenetre, r_b_color, (self.x, self.y), self.rayon)

    def mouvement_balle(self):
        if len(donneesrecues) == 9:
            self.x = int(donneesrecues[5])
            self.y = int(donneesrecues[6])


# CREATION RAQUETTES ET BALLE
balle = Balle(LARGEUR // 2, HAUTEUR // 2, RAYON_BALLE)

'''
Fonction : dessin
Parametres : fenetre, raquettes, balle, score_gauche, score_droit

Cette fonction s'occupe de dessiner les différents éléments dans la fenêtre de jeu.'''


def dessin(fenetre, raquettes, balle, score_gauche, score_droit):
    fenetre.fill(background_color)

    score_gauche_texte = SCORE_FONT.render(f"{score_gauche}", 1, texte_score_color)
    score_droit_texte = SCORE_FONT.render(f"{score_droit}", 1, texte_score_color)

    fenetre.blit(score_gauche_texte, (LARGEUR // 4 - score_gauche_texte.get_width() // 2, 20))
    fenetre.blit(score_droit_texte, (LARGEUR * (3 / 4) - score_droit_texte.get_width() // 2, 20))

    for raquette in raquettes:
        raquette.dessin(fenetre, raquette_balle_color)

    for i in range(10, HAUTEUR, HAUTEUR // 20):
        if i % 2 == 1:
            continue
        pygame.draw.rect(fenetre, texte_score_color, (LARGEUR // 2 - 5, i, 10, HAUTEUR // 20))
    balle.dessin(fenetre, raquette_balle_color)
    pygame.display.update()


'''
Fonction : mouvement_raquette
Parametres : keys, raquette_gauche, raquette_droite, donneesrecues

Cette fonction s'occupe du déplacement de la raquette de gauche avec les touches s et w.
Le mouvement de la raquette de droite est assuré par le deuxième paramètre envoyee par le serveur.'''


def mouvement_raquette(keys, raquette_gauche, raquette_droite):
    if len(donneesrecues) == 9:
        raquette_droite.y = int(donneesrecues[1])

    if keys[pygame.K_s] and raquette_gauche.y - raquette_gauche.VITESSE_RAQUETTE >= 0:
        raquette_gauche.mouvement(up=True)
    if keys[pygame.K_w] and raquette_gauche.y + raquette_gauche.VITESSE_RAQUETTE + raquette_gauche.hauteur <= HAUTEUR:
        raquette_gauche.mouvement(up=False)


def change_taille_raq(value: Tuple[Any, int], taille: str) -> None:
    """
    Change difficulty of the game.
    :param value: Tuple containing the data of the selected object
    :param difficulty: Optional parameter passed as argument to add_selector
    """
    selected, index = value
    print(f'Taille selectionnée: "{selected}" ({taille}) at index {index}')
    TAILLE[0] = taille


def change_vitesse_balle(value: Tuple[Any, int], vitesse: str) -> None:
    selected, index = value
    print(f'Vitesse Sélectionnée : "{selected}" ({vitesse}) at index {index}')
    VITESSE[0] = vitesse


def change_nbre_joueurs(value: Tuple[Any, int], nbre_joueurs: str) -> None:
    selected, index = value
    print(f'Nombre de joueurs : "{selected}" ({nbre_joueurs}) at index {index}')
    NB_JOUEURS[0] = nbre_joueurs


def change_bg_color(value: Tuple[Any, int], bg_color: str) -> None:
    selected, index = value
    print(f'Bg color : "{selected}" ({bg_color}) at index {index}')
    BG_COLOR[0] = bg_color


def change_r_b_color(value: Tuple[Any, int], r_b_color: str) -> None:
    selected, index = value
    print(f'Couleur raquettes et balle : "{selected}" ({r_b_color}) at index {index}')
    R_B_COLOR[0] = r_b_color


def change_text_color(value: Tuple[Any, int], text_color: str) -> None:
    selected, index = value
    print(f'Couleur score et texte : "{selected}" ({text_color}) at index {index}')
    TEXT_COLOR[0] = text_color

def change_winning_score(value: Tuple[Any, int], winning_score: str) -> None:
    selected, index = value
    print(f'Score gagnant : "{selected}" ({winning_score}) at index {index}')
    WINNING_SCORE[0] = winning_score

def play_function(taille: List, font: 'pygame.font.Font', vitesse: List, winning_score_selected: List,
                  test: bool = False) -> None:
    """
    Main game function.
    :param taille: taille de la raquette
    :param difficulty: Difficulty of the game
    :param font: Pygame font
    :param test: Test method, if ``True`` only one loop is allowed
    """
    assert isinstance(taille, list)
    taille = taille[0]
    assert isinstance(taille, str)

    assert isinstance(vitesse, list)
    vitesse = vitesse[0]
    assert isinstance(vitesse, str)

    assert isinstance(winning_score_selected, list)
    winning_score_selected = winning_score_selected[0]
    assert isinstance(winning_score_selected, str)

    # Define globals
    global main_menu
    global clock
    global taille_raquette
    global vitesse_balle
    global winning_score
    global score_droite
    global score_gauche
    global donneesrecues
    global raquette_gauche
    global raquette_droite

    if taille == 'PETITE':
        taille_raquette = 1
    elif taille == 'NORMALE':
        taille_raquette = 2
    elif taille == 'GRANDE':
        taille_raquette = 3
    else:
        raise ValueError(f'unknown difficulty {taille}')

    if vitesse == 'LENTE':
        vitesse_balle = 1
    elif vitesse == 'NORMALE':
        vitesse_balle = 2
    elif vitesse == 'RAPIDE':
        vitesse_balle = 3

    if winning_score_selected == '5':
        winning_score = 5
    if winning_score_selected == '0':
        winning_score = 10
    if winning_score_selected == '15':
        winning_score = 15


    if taille_raquette == 2:
        raquette_gauche = Raquette(10, HAUTEUR // 2 - HAUTEUR_RAQUETTE // 2, LARGEUR_RAQUETTE, HAUTEUR_RAQUETTE)
    elif taille_raquette == 1:
        raquette_gauche = Raquette(10, HAUTEUR // 2 - HAUTEUR_RAQUETTE // 2, LARGEUR_RAQUETTE, HAUTEUR_RAQUETTE - 50)
    elif taille_raquette == 3:
        raquette_gauche = Raquette(10, HAUTEUR // 2 - HAUTEUR_RAQUETTE // 2, LARGEUR_RAQUETTE, HAUTEUR_RAQUETTE + 50)
    global raquette_droite
    if taille_raquette == 2:
        raquette_droite = Raquette(LARGEUR - 10 - LARGEUR_RAQUETTE, HAUTEUR // 2 - HAUTEUR_RAQUETTE // 2,
                                   LARGEUR_RAQUETTE,
                                   HAUTEUR_RAQUETTE)
    elif taille_raquette == 1:
        raquette_droite = Raquette(LARGEUR - 10 - LARGEUR_RAQUETTE, HAUTEUR // 2 - HAUTEUR_RAQUETTE // 2,
                                   LARGEUR_RAQUETTE,
                                   HAUTEUR_RAQUETTE - 50)
    elif taille_raquette == 3:
        raquette_droite = Raquette(LARGEUR - 10 - LARGEUR_RAQUETTE, HAUTEUR // 2 - HAUTEUR_RAQUETTE // 2,
                                   LARGEUR_RAQUETTE,
                                   HAUTEUR_RAQUETTE + 50)
    # Reset main menu and disable
    # You also can set another menu, like a 'pause menu', or just use the same
    # main_menu as the menu that will check all your input.
    main_menu.disable()
    main_menu.full_reset()

    frame = 0

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((ADRESSEIPV4, PORT))
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()  # si on quitte on sort
                break
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    main_menu.enable()
                    client.close()
                    return
        # Pass events to main_menu
        if main_menu.is_enabled():
            main_menu.update(events)
        client.send(
            bytes(str(f"{raquette_gauche.y},{raquette_droite.y},{taille_raquette},{vitesse_balle},{winning_score}").encode('utf-8')))
        donneesrecues = client.recv(128).decode('utf-8')
        donneesrecues = donneesrecues.split(',')
        clock.tick(FPS)
        print(donneesrecues)
        if len(donneesrecues) == 9:
            score_droite = int(donneesrecues[7])
            score_gauche = int(donneesrecues[8])
            dessin(FENETRE, [raquette_gauche, raquette_droite], balle, score_gauche, score_droite)
        keys = pygame.key.get_pressed()
        mouvement_raquette(keys, raquette_gauche, raquette_droite)
        balle.mouvement_balle()

        gagnant = False
        if score_gauche == winning_score+1:
            SON_VICTOIRE.play()
            gagnant = True
            fenetre_texte = "Joueur de gauche gagne !"
        elif score_droite == winning_score+1:
            SON_VICTOIRE.play()
            gagnant = True
            fenetre_texte = "Joueur de droite gagne !"
        if gagnant:
            texte = SCORE_FONT.render(fenetre_texte, 1, texte_score_color)
            FENETRE.blit(texte, (LARGEUR // 2 - texte.get_width() // 2, HAUTEUR // 2 - texte.get_height() // 2))
            pygame.display.update()
            pygame.time.delay(5000)
            raquette_gauche.reset()
            raquette_droite.reset()
        if test and frame == 2:
            break

def save_data(bg_color: List, r_b_color: List, text_color: List, test: bool = False) -> None:
    assert isinstance(bg_color, list)
    bg_color = bg_color[0]
    assert isinstance(bg_color, str)

    assert isinstance(r_b_color, list)
    r_b_color = r_b_color[0]
    assert isinstance(r_b_color, str)

    assert isinstance(text_color, list)
    text_color = text_color[0]
    assert isinstance(text_color, str)

    global background_color
    global raquette_balle_color
    global texte_score_color

    if bg_color == 'NOIR':
        background_color = NOIR
    if bg_color == 'ROSE':
        background_color = ROSE
    if bg_color == 'VERT':
        background_color = VERT
    if bg_color == 'JAUNE':
        background_color = JAUNE
    if bg_color == 'BLANC':
        background_color = BLANC
    if bg_color == 'ORANGE':
        background_color = ORANGE
    if bg_color == 'ROUGE':
        background_color = ROUGE
    if bg_color == 'BLEU':
        background_color = BLEU

    if r_b_color == 'NOIR':
        raquette_balle_color = NOIR
    if r_b_color == 'ROSE':
        raquette_balle_color = ROSE
    if r_b_color == 'VERT':
        raquette_balle_color = VERT
    if r_b_color == 'JAUNE':
        raquette_balle_color = JAUNE
    if r_b_color == 'BLANC':
        raquette_balle_color = BLANC
    if r_b_color == 'ORANGE':
        raquette_balle_color = ORANGE
    if r_b_color == 'ROUGE':
        raquette_balle_color = ROUGE
    if r_b_color == 'BLEU':
        raquette_balle_color = BLEU

    if text_color == 'NOIR':
        texte_score_color = NOIR
    if text_color == 'ROSE':
        texte_score_color = ROSE
    if text_color == 'VERT':
        texte_score_color = VERT
    if text_color == 'JAUNE':
        texte_score_color = JAUNE
    if text_color == 'BLANC':
        texte_score_color = BLANC
    if text_color == 'ORANGE':
        texte_score_color = ORANGE
    if text_color == 'ROUGE':
        texte_score_color = ROUGE
    if text_color == 'BLEU':
        texte_score_color = BLEU



def main_background() -> None:
    """
    Function used by menus, draw on background while menu is active.
    """
    global surface
    surface.fill((0, 0, 0))


def main(test: bool = False) -> None:
    """
    Main program.
    :param test: Indicate function is being tested
    """

    # -------------------------------------------------------------------------
    # Globals
    # -------------------------------------------------------------------------
    global clock
    global main_menu
    global surface

    # -------------------------------------------------------------------------
    # Create window
    # -------------------------------------------------------------------------
    surface = create_example_window('PONG GAME', WINDOW_SIZE)
    clock = pygame.time.Clock()
    main_theme = pygame_menu.themes.Theme(  # transparent background
        title_background_color=(0, 0, 0),
        title_bar_style=pygame_menu.widgets.MENUBAR_STYLE_NONE,
        widget_padding=25,
        selection_color=((255, 255, 255)),
        widget_font_color=((200, 200, 200)))
    my_image = pygame_menu.baseimage.BaseImage('background.PNG',
                                               drawing_mode=pygame_menu.baseimage.IMAGE_MODE_REPEAT_XY)
    main_theme.background_color = my_image
    # --------------------------------------------------------------------------
    # Create menus: About Menu
    # -------------------------------------------------------------------------
    about_menu = pygame_menu.Menu(
        height=700,
        title='A propos',
        width=1000,
        theme=main_theme
    )
    about_menu.add.label(
        "Ce jeu a été programmé dans le cadre d'un projet de fin d'études\nAuteurs : Etienne PEREZ, Théo Supiot, Loan Germond\n Email : etienne.perez@etud.univ-angers.fr")
    about_menu.add.button('Retourner au menu principal', pygame_menu.events.BACK)
    # --------------------------------------------------------------------------
    # Create menus: Play Menu
    # -------------------------------------------------------------------------
    parametre_menu = pygame_menu.Menu(
        height=700,
        title='Paramètres',
        width=1000,
        theme=main_theme
    )
    parametre_menu.add.selector('Couleur raquettes et balle ',
                                [('Blanc', 'BLANC'), ('Bleu', 'BLEU'), ('Rouge', 'ROUGE'), ('Noir', 'NOIR'),('Rose', 'ROSE'),('Orange','ORANGE'), ('Jaune','JAUNE'),('Vert','VERT')],
                                onchange=change_r_b_color,
                                selector_id='select_ball_raq_color',
                                style_fancy_bgcolor=((0, 0, 0)),
                                style_fancy_arrow_color=((200, 200, 200)),
                                style='fancy')
    parametre_menu.add.selector("Couleur fond d'écran ",
                                [('Noir', 'NOIR'),('Blanc', 'BLANC'), ('Bleu', 'BLEU'), ('Rouge', 'ROUGE'),('Rose', 'ROSE'),('Orange','ORANGE'), ('Jaune','JAUNE'),('Vert','VERT')],
                                onchange=change_bg_color,
                                selector_id='select_bg_color',
                                style_fancy_bgcolor=((0, 0, 0)),
                                style_fancy_arrow_color=((200, 200, 200)),
                                style='fancy')
    parametre_menu.add.selector("Couleur score et texte ",
                                [('Blanc', 'BLANC'),('Noir', 'NOIR'), ('Bleu', 'BLEU'), ('Rouge', 'ROUGE'),('Rose', 'ROSE'),('Orange','ORANGE'), ('Jaune','JAUNE'),('Vert','VERT')],
                                onchange=change_text_color,
                                selector_id='select_text_color',
                                style_fancy_bgcolor=((0, 0, 0)),
                                style_fancy_arrow_color=((200, 200, 200)),
                                style='fancy')
    parametre_menu.add.button('Enregistrer les modifications', save_data,
                              BG_COLOR, R_B_COLOR, TEXT_COLOR)
    parametre_menu.add.button('Retourner au menu principal', pygame_menu.events.BACK)

    # -------------------------------------------------------------------------
    # Create menus: Main
    # -------------------------------------------------------------------------
    main_menu = pygame_menu.Menu(
        height=700,
        theme=main_theme,
        title='Menu Principal',
        width=1000
    )

    main_menu.add.button('Lancer la partie', play_function,
                         TAILLE,
                         pygame.font.Font(pygame_menu.font.FONT_FRANCHISE, 30), VITESSE, NB_JOUEURS)
    main_menu.add.selector('Taille de la raquette ',
                           [('Normale', 'NORMALE'),
                            ('Petite', 'PETITE'),
                            ('Grande', 'GRANDE')],
                           onchange=change_taille_raq,
                           selector_id='select_difficulty',
                           style_fancy_bgcolor=((0, 0, 0)),
                           style_fancy_arrow_color=((200, 200, 200)),
                           style='fancy')
    main_menu.add.selector('Vitesse de la balle',
                           [('Normale', 'NORMALE'),
                            ('Rapide', 'RAPIDE'),
                            ('Lente', 'LENTE')],
                           onchange=change_vitesse_balle,
                           selector_id='select_speed',
                           style_fancy_bgcolor=((0, 0, 0)),
                           style_fancy_arrow_color=((200, 200, 200)),
                           style='fancy')
    main_menu.add.selector('Score gagnant ',
                           [('10', '10'),
                            ('5', '5'),
                            ('15', '15')],
                           onchange=change_winning_score,
                           selector_id='select_winning_score',
                           style_fancy_bgcolor=((0, 0, 0)),
                           style_fancy_arrow_color=((200, 200, 200)),
                           style='fancy')

    main_menu.add.button('Paramètres', parametre_menu)
    main_menu.add.button('A propos', about_menu)
    main_menu.add.button('Quitter', pygame_menu.events.EXIT)

    # -------------------------------------------------------------------------
    # Main loop
    # -------------------------------------------------------------------------
    frame = 0
    while True:

        # Tick
        clock.tick(FPS)
        frame += 1

        # Paint background
        main_background()

        # Application events
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                exit()

        # Main menu
        if main_menu.is_enabled():
            main_menu.mainloop(surface, main_background, disable_loop=test, fps_limit=FPS)

        # Flip surface
        pygame.display.flip()

        # At first loop returns
        if test:
            break


if __name__ == '__main__':
    main()
