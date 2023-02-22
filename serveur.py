import socket
import threading
import time

import pygame.time

'''------------------------------------------------VARIABLES GLOBALES------------------------------------------------'''
#  VARIABLES SERVEUR
ADRESSEIPV4 = "172.23.2.26"
PORT = 9954
serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serveur.bind((ADRESSEIPV4, PORT))
serveur.listen()
print(f"Serveur ouvert aux joueurs sur l'adresse : {ADRESSEIPV4}\nEn attente des joueurs...")

# VARIABLES DE STOCKAGE DE DONNEES
donneesrecues1 = 0
donneesrecues2 = 0
scorejoueur_droite = 0
scorejoueur_gauche = 0
SCORE_GAGNANT = 10
# VARIABLES DE TEST
first_player_connected = False
second_player_connected = False
player_1 = True
player_2 = True
game_on = True

# VARIABLES SERVANT A CREER LES RAQUETTES ET LA BALLE
LARGEUR = 1000
HAUTEUR = 700
LARGEUR_RAQUETTE = 10
RAYON_BALLE = 10
'''------------------------------------------------------------------------------------------------------------------'''

'''
Classe : Raquette
Fonctions : init(x, y, largeur, hauteur)

Cette classe permet de créer une raquette virtuellement en précisant ses coordonées (x,y) ainsi que sa largeur et sa hauteur dans les 
paramètres de la fonction init.'''


class Raquette:
    def __init__(self, x, y, largeur, hauteur):
        self.x = self.x_originale = x
        self.y = self.y_originale = y
        self.largeur = largeur
        self.hauteur = hauteur


'''Classe : Balle
Fonctions : init(x, y, rayon)
           mouvement_balle(self)
           reset(self)

Cette classe permet de créer une balle virtuellement en précisant ses coordonées (x,y) ainsi que son rayon dans les 
paramètres de la fonction init(). La fonction mouvement_balle() gère les déplacements de la balle en fonction des données 
envoyees par le serveur et reset() replace la balle au centre.'''


class Balle:
    MAX_VITESSE = 10
    def __init__(self, x, y, rayon):
        self.x = self.x_originale = x
        self.y = self.y_originale = y
        self.rayon = rayon
        self.y_vitesse = 0
        self.x_vitesse = self.MAX_VITESSE

    def mouvement_balle(self):
        self.x += self.x_vitesse
        self.y += self.y_vitesse

    def reset(self):
        self.x = self.x_originale
        self.y = self.y_originale
        self.y_vitesse = 0
        self.x_vitesse *= 1

# CRÉATION VIRTUELLE DE LA BALLE
balle = Balle(LARGEUR // 2, HAUTEUR // 2, RAYON_BALLE)

'''
Fonction : joueur1
Paramètres : clienconnecte

Cette fonction s'occupe du premier joueur connecté. Elle reçoit les données envoyées par le joueur 1 et les envoie au 
joueur2. C'est le premier thread lancé depuis la boucle principale.
'''


def joueur1(clientconnecte):
    global donneesrecues1, donneesrecues2, first_player_connected
    print("Premier joueur connecté !\nEn attente du deuxième joueur...")
    while first_player_connected:
        donneesrecues1 = clientconnecte.recv(128).decode('utf-8')
        donneesenvoyees1 = f"{donneesrecues2},{balle.x},{balle.y},{scorejoueur_droite},{scorejoueur_gauche}"
        if not donneesrecues1:
            first_player_connected = False
        clientconnecte.send(bytes(str(donneesenvoyees1).encode('utf-8')))


'''
Fonction : joueur2
Paramètres : clienconnecte

Cette fonction s'occupe du deuxieme joueur connecté. Elle reçoit les données envoyées par le joueur 2 et les envoie au 
joueur 1. C'est le deuxieme thread lancé depuis la boucle principale.
'''


def joueur2(clientconnecte):
    global donneesrecues2, donneesrecues1, second_player_connected
    print("Deuxième joueur connecté !\nLa partie peut commencer !")
    while second_player_connected:
        donneesrecues2 = clientconnecte.recv(128).decode('utf-8')
        donneesenvoyees2 = f" {donneesrecues1},{balle.x},{balle.y},{scorejoueur_droite},{scorejoueur_gauche}"
        if not donneesrecues2:
            second_player_connected = False
        clientconnecte.send(bytes(str(donneesenvoyees2).encode('utf-8')))


'''
Fonction : collision
Paramètres : balle, donneesrecues, raquette_droite, raquette_gauche

Cette fonction s'occupe du déplacement de la balle lors des collisions avec les deux raquettes ainsi qu'avec les murs du
haut et du bas. Elle prend en paramètres les deux raquettes, la balle et les données envoyées (coordonée y des raquettes)
par les joueurs.
'''


def collision(balle, donneesrecues1, donneesrecues2):
    global raquette_gauche, raquette_droite, vitesse_balle
    donneesrecues2 = str(donneesrecues2)
    donneesrecues2 = donneesrecues2.split(',')
    donneesrecues1 = str(donneesrecues1)
    donneesrecues1 = donneesrecues1.split(',')
    if len(donneesrecues1) == 5:
        taille_raquette = int(donneesrecues1[2])
        if taille_raquette == 2:
            HAUTEUR_RAQUETTE = 100
        elif taille_raquette == 1:
            HAUTEUR_RAQUETTE = 50
        elif taille_raquette == 3:
            HAUTEUR_RAQUETTE = 150

        vitesse_choisie = int(donneesrecues1[3])
        if vitesse_choisie == 1:
            vitesse_balle = 5
        if vitesse_choisie == 2:
            vitesse_balle = 10
        if vitesse_choisie == 3:
            vitesse_balle = 15


        raquette_gauche = Raquette(10, HAUTEUR // 2 - HAUTEUR_RAQUETTE // 2, LARGEUR_RAQUETTE, HAUTEUR_RAQUETTE)
        raquette_droite = Raquette(LARGEUR - 10 - LARGEUR_RAQUETTE, HAUTEUR // 2 - HAUTEUR_RAQUETTE // 2, LARGEUR_RAQUETTE,
                    HAUTEUR_RAQUETTE)
        raquette_gauche.y = int(donneesrecues1[0])
        raquette_droite.y = int(donneesrecues1[1])

        if balle.y + balle.rayon >= HAUTEUR:
            balle.y_vitesse *= -1
        elif balle.y - balle.rayon <= 0:
            balle.y_vitesse *= -1

        if balle.x_vitesse < 0:
            if balle.y >= raquette_gauche.y and balle.y <= raquette_gauche.y + HAUTEUR_RAQUETTE:
                if balle.x - balle.rayon <= raquette_gauche.x + LARGEUR_RAQUETTE:
                    balle.x_vitesse *= -1
                    milieu_y = raquette_gauche.y + raquette_gauche.hauteur // 2
                    difference_en_y = milieu_y - balle.y
                    facteur_reduction = (raquette_gauche.hauteur // 2) // balle.MAX_VITESSE
                    y_vitesse = difference_en_y // facteur_reduction
                    balle.y_vitesse = -1 * y_vitesse

        else:
            if balle.y >= raquette_droite.y and balle.y <= raquette_droite.y + HAUTEUR_RAQUETTE:
                if balle.x + balle.rayon >= raquette_droite.x:
                    balle.x_vitesse *= -1
                    milieu_y = raquette_droite.y + raquette_droite.hauteur // 2
                    difference_en_y = milieu_y - balle.y
                    facteur_reduction = (raquette_droite.hauteur // 2) // balle.MAX_VITESSE
                    y_vitesse = difference_en_y // facteur_reduction
                    balle.y_vitesse = -1 * y_vitesse

'''
Fonction : jeu
Paramètres : Aucun

Cette fonction s'occupe du déplacement de la balle lorsqu'un point est marqué d'un des deux cotés. C'est à l'intérieur de 
cette fonction que l'on fait appel à la fonction collision(...). Elle s'occupe aussi de l'incrémentation du score et du score
finale de fin de partie. 
'''


def jeu():
    global scorejoueur_droite, scorejoueur_gauche, SCORE_GAGNANT
    while game_on:
        balle.mouvement_balle()
        time.sleep(0.01)
        collision(balle, donneesrecues1, donneesrecues2)
        if balle.x < 0:
            scorejoueur_droite += 1
            balle.reset()
        elif balle.x > LARGEUR:
            scorejoueur_gauche += 1
            balle.reset()
        donneesrecues_joueur1 = str(donneesrecues1)
        donneesrecues_joueur1 = donneesrecues_joueur1.split(',')
        donneesrecues_joueur2 = str(donneesrecues2)
        donneesrecues_joueur2 = donneesrecues_joueur2.split(',')
        if len(donneesrecues_joueur2) == 5 and len(donneesrecues_joueur1) == 5:
            score_gagnant1 = int(donneesrecues_joueur1[4])
            score_gagnant2 = int(donneesrecues_joueur2[4])
        if score_gagnant1 == 10 and score_gagnant2 == 10:
            SCORE_GAGNANT = 11
        elif score_gagnant1 == 5 and score_gagnant2 == 5:
            SCORE_GAGNANT = 6
        elif score_gagnant1 == 15 and score_gagnant2 == 15:
            SCORE_GAGNANT = 16
        if scorejoueur_droite == SCORE_GAGNANT:
            scorejoueur_droite = 0
            scorejoueur_gauche = 0
            pygame.time.delay(5000)
        elif scorejoueur_gauche == SCORE_GAGNANT:
            scorejoueur_droite = 0
            scorejoueur_gauche = 0
            pygame.time.delay(5000)
        print(f"Balle({balle.x},{balle.y}) - Raquette de droite : {raquette_droite.y} - Raquette de gauche : {raquette_gauche.y}")
        if len(donneesrecues1) == 0 or len(donneesrecues2) == 0:
            first_player_connected = False
            second_player_connected = False
            boucle_principale()

'''
Boucle principale qui s'occupe d'accepter les connexions au serveur et de lancer chaque thread les uns après les autres.
'''
def boucle_principale():
    global first_player_connected, second_player_connected
    while True:
        clientconnecte, adresseclient = serveur.accept()
        if first_player_connected == False:
            thread1 = threading.Thread(target=joueur1, args=(clientconnecte,))
            first_player_connected = True
            thread1.start()
        elif second_player_connected == False:
            thread2 = threading.Thread(target=joueur2, args=(clientconnecte,))
            second_player_connected = True
            thread2.start()
        if first_player_connected and second_player_connected:
            thread3 = threading.Thread(target=jeu())
            thread3.start()

boucle_principale()