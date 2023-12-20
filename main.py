#commente le code

# Importation des modules
import pygame
import os
import random

# Initialisation de pygame
LARGEUR = 1700 #largeur de la fenêtre
HAUTEUR = 900 #hauteur de la fenêtre
CARTE_LARGEUR = 1000 #largeur de la carte
CARTE_HAUTEUR = 400 #hauteur de la carte
BACKGROUND_COLOR = (11, 127, 57) #couleur de fond
BLACK = (0, 0, 0) #couleur noir
BLANC = (255, 255, 255) #couleur blanc
ROUGE = (255, 0, 0) #couleur rouge

pygame.init() #initialisation de pygame

# Création de la classe Bouton
class Bouton:
    # Constructeur de la classe Bouton
    def __init__(self, x, y, l, h, text, text_couleur, couleur, couleur_subbriance) -> None: #initialisation des attributs de la classe
        self.x, self.y, self.l, self.h = x, y, l, h 
        self.text, self.text_couleur, self.couleur = text, text_couleur, couleur 
        self.couleur_subbriance = couleur_subbriance  
             
    def dessiner(self, screen, petit=False): 
        """ 
    Fonction qui dessine le bouton
    parametre 
    ----------
    screen : pygame.Surface
        La surface sur laquelle dessiner le bouton
    petit : bool, optional
        Si le bouton est petit ou non, par défaut False 
    retourne
    -------
    None
    """
        position_souris = pygame.mouse.get_pos() 
        couleur = self.couleur_subbriance if self.x < position_souris[0] < self.x + self.l and self.y < position_souris[1] < self.y + self.h else self.couleur 
        pygame.draw.rect(screen, couleur, (self.x, self.y, self.l, self.h)) #dessine le bouton
        font_size = 36 if petit else 56 #taille de la police
        font = pygame.font.SysFont(None, font_size) #police
        text_surface = font.render(self.text, 1, self.text_couleur) #texte
        text_rect = text_surface.get_rect(center=(self.x + self.l / 2, self.y + self.h / 2)) #position du texte
        screen.blit(text_surface, text_rect) #affiche le texte

    
    def est_clique(self, position_souris):
        ''' 
            Fonction qui vérifie si le bouton est cliqué
            parametre
            ----------
            position_souris : tuple
            La position de la souris
            retourne
            -------
            bool
            True si le bouton est cliqué, False sinon
                   '''
        return self.x < position_souris[0] < self.x + self.l and self.y < position_souris[1] < self.y + self.h #vérifie si le bouton est cliqué
    
# Création de la classe Carte
class Card:
    # Attribut de classe
    SCALE_FACTOR = 0.5

    # Constructeur de la classe Carte
    def __init__(self, suit, value):
        self.suit, self.value = suit, value #initialisation des attributs de la classe
        self.image = pygame.image.load(f"images/{self.suit}_{self.value}.png")
        self.image = pygame.transform.scale(self.image,
                                            (int(self.image.get_width() * self.SCALE_FACTOR),
                                             int(self.image.get_height() * self.SCALE_FACTOR)))
        self.back_image = pygame.image.load("images/back.png")
        self.back_image = pygame.transform.scale(self.back_image,
                                                 (int(self.back_image.get_width() * self.SCALE_FACTOR),
                                                  int(self.back_image.get_height() * self.SCALE_FACTOR)))
        self.face_up = True

  
    def flip(self):
        '''
    Fonction qui retourne la carte
    parametre
    ----------
    None
    retourne
    -------
    None'''

        self.face_up = not self.face_up #retourne la carte

# Création de la classe Deck
class Deck:
    # Constructeur de la classe Deck
    def __init__(self):
        self.cutting_card_draw = False
        self.cards = [Card(suit, value) for _ in range(6) for suit in ["S", "H", 'C', 'D'] for value in range(1, 14)]
        self.deal_sound = pygame.mixer.Sound("sounds/deal.mp3")
        self.cutting_card_image = pygame.image.load("images/R_0.png")
        self.cutting_card_image = pygame.transform.scale(self.cutting_card_image,
                                                         (int(self.cutting_card_image.get_width() * Card.SCALE_FACTOR),
                                                          int(self.cutting_card_image.get_height() * Card.SCALE_FACTOR)))

    
    def shuffle(self):
        '''
        Fonction qui mélange le deck
        parametre
        ----------
        None
        retourne
        -------
        None
        '''
        random.shuffle(self.cards) #mélange le deck


    def add_cutting_card(self):
        '''
        Fonction qui ajoute la carte de coupe
        parametre
        ----------
        None
        retourne
        -------
        None
        '''

        index_milieu = round(len(self.cards) // 2) #ajoute la carte de coupe
        self.cards.insert(index_milieu, Card("R", 0)) 

    def deal(self):
        '''
        Fonction qui distribue une carte
        parametre
        ----------
        None
        retourne
        -------
        Card
        La carte distribuée
        '''

        if self.cards: #distribue une carte
            card = self.cards.pop() #retire la carte du deck
            self.deal_sound.play() #joue le son de distribution
            if card.suit == 'R': #si la carte est la carte de coupe
                self.cutting_card_draw = True #la carte de coupe est dessinée
                card = self.cards.pop() #retire la carte du deck
            return card #retourne la carte
        else:
            print("Erreur, plus de cartes dans le deck") 

    def length(self):
        '''
        Fonction qui retourne la longueur du deck
        parametre
        ----------
        None
        retourne
        -------
        int
        La longueur du deck
        '''

        return len(self.cards)  #retourne la longueur du deck

    def dessiner_cutting_card(self, screen):
        '''
        Fonction qui dessine la carte de coupe
        parametre
        ----------
        screen : pygame.Surface
            La surface sur laquelle dessiner la carte de coupe
        retourne
        -------
        None
        '''
        
        if self.cutting_card_draw: #dessine la carte de coupe 
            screen.blit(self.cutting_card_image, (20, 20)) #dessine la carte de coupe

# Création de la classe Hand
class Hand:

    # Constructeur de la classe Hand
    def __init__(self):
        self.cards = [] #initialisation des attributs de la classe

    def add_card(self, card):
        '''
        Fonction qui ajoute une carte à la main
        parametre
        ----------
        card : Card
            La carte à ajouter
            retourne
            -------
            None
            '''
        self.cards.append(card) #ajoute une carte à la main

    def calculer_total(self):
        '''
        Fonction qui calcule le total de la main
        parametre
        ----------
        None
        retourne
        -------
        int
        Le total de la main
        '''

        total, as_count = 0, 0 #calcule le total de la main
        for card in self.cards: #pour chaque carte dans la main
            if card.value == 1 and total <= 10: #si la carte est un as et que le total est inférieur ou égal à 10
                total += 11 
                as_count += 1 
            else:
                total += min(card.value, 10) 
        while total > 21 and as_count != 0: #si le total est supérieur à 21 et qu'il y a des as
            total -= 10
            as_count -= 1 
        return total

    def has_blackjack(self):
        '''
        Fonction qui vérifie si la main a un blackjack
        parametre
        ----------
        None
        retourne
        -------
        bool
        True si la main a un blackjack, False sinon
        '''

        return len(self.cards) == 2 and ( #vérifie si la main a un blackjack
                (self.cards[0].value == 1 and self.cards[1].value in [10, 11, 12, 13]) or #si la première carte est un as et que la deuxième carte est une figure
                (self.cards[1].value == 1 and self.cards[0].value in [10, 11, 12, 13])) #si la deuxième carte est un as et que la première carte est une figure
    
# Création de la classe Player
class Player:
    # Constructeur de la classe Player
    def __init__(self):
        self.hand = Hand()
        self.money = 1000
        self.bet = [50, 0]
        self.has_split = False
        self.has_double = False
        self.hand2 = Hand()
        self.main_gagne = 0
        self.main_perdu = 0

    def dessiner(self, screen, x_offset, y, hand):
        '''
        Fonction qui dessine la main
        parametre
        ----------
        screen : pygame.Surface
            La surface sur laquelle dessiner la main
        x_offset : int
            L'offset en x
        y : int 
            L'offset en y
        hand : Hand
            La main à dessiner
        retourne
        -------
        None
        '''

        for card in hand.cards: #dessine la main
            image_to_draw = card.image if card.face_up else card.back_image #dessine la carte
            screen.blit(image_to_draw, (x_offset, y)) #dessine la carte 
            x_offset += 20 #augmente l'offset en x

    def retourner_carte(self, index):
        '''
        Fonction qui retourne une carte
        parametre
        ----------
        index : int
            L'index de la carte à retourner
        retourne
        -------
        None
        '''

        if index < len(self.hand.cards): #retourne une carte
            self.hand.cards[index].flip() 

    def hit(self, hand, deck):
        '''
        Fonction qui tire une carte
        parametre
        ----------
        hand : Hand
            La main à laquelle ajouter la carte
        deck : Deck
            Le deck duquel tirer la carte
        retourne
        -------
        None
        '''

        card = deck.deal() #tire une carte
        hand.add_card(card)  #ajoute la carte à la main

    def is_busted(self, hand):
        '''
        Fonction qui vérifie si la main est busted
        parametre
        ----------
        hand : Hand
            La main à vérifier
        retourne
        -------
        bool
        True si la main est busted, False sinon
        '''

        return hand.calculer_total() > 21 #vérifie si la main est busted (elle dépasse 21)

# Création de la classe Dealer
class Dealer(Player): # Dealer hérite de Player
    pass # On ne fait rien

# Création de la classe Game
class Game:
    # Constructeur de la classe Game
    def __init__(self):
        self.can_double = False
        self.can_double_hand2 = False
        self.premiere_main_termine = False
        self.can_split = False
        self.game_started = False
        self.player = Player()
        self.dealer = Dealer()
        self.deck = Deck()
        self.deck.shuffle()
        self.deck.add_cutting_card()
        self.screen = pygame.display.set_mode((LARGEUR, HAUTEUR))
        pygame.display.set_caption("Blackjack")
        self.clock = pygame.time.Clock()
        self.message = ""
        self.bouton_tirer = Bouton(LARGEUR - 200, HAUTEUR / 2, 150, 50, "Tirer", BLACK, BLANC, ROUGE)
        self.bouton_recommencer = Bouton(0, HAUTEUR / 2, 300, 50, "Recommencer", BLACK, BLANC, ROUGE)
        self.bouton_commencer = Bouton(0, HAUTEUR / 2, 300, 50, "Commencer", BLACK, BLANC, ROUGE)
        self.bouton_rester = Bouton(LARGEUR - 200, HAUTEUR / 2 - 70, 150, 50, "Rester", BLACK, BLANC, ROUGE)
        self.bouton_doubler = Bouton(LARGEUR - 200, HAUTEUR / 2 + 70, 150, 50, "Doubler", BLACK, BLANC, ROUGE)
        self.bouton_split = Bouton(LARGEUR - 200, HAUTEUR / 2 + 140, 150, 50, "Split", BLACK, BLANC, ROUGE)
        self.bouton_augmenter_mise = Bouton(LARGEUR // 2 - 60, HAUTEUR - 65, 30, 30, "+", BLACK, BLANC, ROUGE)
        self.bouton_diminuer_mise = Bouton(LARGEUR // 2 + 10, HAUTEUR - 65, 30, 30, "-", BLACK, BLANC, ROUGE)
        self.win_sound = pygame.mixer.Sound("sounds/win.mp3")
        self.loose_sound = pygame.mixer.Sound("sounds/loose.mp3")

    def reset(self):
        '''
        Fonction qui reset le jeu
        parametre
        ----------
        None
        retourne
        -------
        None
        '''
        self.game_started = True #reset le jeu
        if self.deck.cutting_card_draw: #si la carte de coupe est dessinée
            self.deck = Deck() #crée un nouveau deck
            self.deck.shuffle() #mélange le deck
            self.deck.add_cutting_card() #ajoute la carte de coupe
        self.player.hand = Hand() #crée une nouvelle main pour le joueur
        self.dealer.hand = Hand() #crée une nouvelle main pour le dealer
        self.player.hand2 = Hand() #crée une nouvelle main pour le joueur (si il a split)
        self.message = ""

    def afficher_message(self, screen, message):
        '''
        Fonction qui affiche un message
        parametre
        ----------
        screen : pygame.Surface
            La surface sur laquelle afficher le message
        message : str
            Le message à afficher
        retourne
        -------
        None
        '''

        font = pygame.font.SysFont(None, 56) #affiche un message
        text_surface = font.render(message, 1, BLACK) 
        text_rectangle = text_surface.get_rect(center=(LARGEUR / 2, HAUTEUR / 2)) 
        screen.blit(text_surface, text_rectangle) 

      
    def dessiner_monaie(self):
        '''
        Fonction qui dessine la monaie
        parametre
        ----------
        None
        retourne
        -------
        None
        '''

        font = pygame.font.SysFont(None, 36) #dessine la monaie
        texte_argent = font.render("Argent : " + str(round(self.player.money)), 1, BLACK) #affiche l'argent
        texte_argent_rect = texte_argent.get_rect(center=(LARGEUR // 2 - 170, HAUTEUR - 40)) #position du texte
        self.screen.blit(texte_argent, texte_argent_rect) #affiche le texte
        texte_mise = font.render("Mise : " + str(round(self.player.bet[0] + self.player.bet[1])), 1, BLACK) #affiche la mise
        texte_mise_rect = texte_mise.get_rect(center=(LARGEUR // 2 - 170, HAUTEUR - 70)) #position du texte
        self.screen.blit(texte_mise, texte_mise_rect) #affiche le texte

        token_50 = pygame.image.load(os.path.join("monaie", "50.png")) #dessine les jetons
        token_100 = pygame.image.load(os.path.join("monaie", "100.png")) #dessine les jetons

    
        token_50 = pygame.transform.scale(token_50, (200, 150)) #redimensionne les jetons
        token_100 = pygame.transform.scale(token_100, (200, 150)) #redimensionne les jetons

        x_offset = LARGEUR // 2 + 230  
        y_offset = HAUTEUR -500

   
        total_100 = self.player.bet[0] // 100  #si la mise est supérieure à 100
   
        for _ in range(int(total_100)): #si la mise est supérieure à 100 
            self.screen.blit(token_100, (x_offset, y_offset))  #dessine les jetons de 100
            x_offset += 20

   
        for _ in range(int(self.player.bet[0] % 100) // 50): #si la mise est supérieure à 50 et inférieure à 100
            self.screen.blit(token_50, (x_offset, y_offset)) #dessine les jetons de 50 
            x_offset += 20 

        


    def perdre(self):
        '''
        Fonction qui perd
        parametre
        ----------
        None
        retourne
        -------
        None
        '''
        self.message = "Perdu !" 
        self.game_started = False #si le joueur perd
        self.loose_sound.play() #joue le son de perte

    def gagner(self):
        '''
        Fonction qui gagne
        parametre
        ----------
        None
        retourne
        -------
        None
        '''
        self.message = "Gagné !" 
        self.player.money += 2 * self.player.bet[0] #si le joueur gagne
        self.game_started = False 
        self.win_sound.play() #joue le son de victoire

    def egalite(self):
        '''
        Fonction qui fait une égalité
        parametre
        ----------
        None
        retourne
        -------
        None
        '''

        self.message = "Egalité"
        self.player.money += self.player.bet[0] #si il y a égalité
        self.game_started = False 
        self.win_sound.play() #joue le son d'égalité

    def comparer_mains(self):
        '''
        Fonction qui compare les mains
        parametre
        ----------
        None
        retourne
        -------
        None
        '''

        self.dealer.retourner_carte(0) #compare les mains
        while self.dealer.hand.calculer_total() < 17: #si le total du dealer est inférieur à 17
            self.dealer.hit(self.dealer.hand, self.deck) #le dealer tire une carte
        if self.dealer.hand.has_blackjack(): #si le dealer a un blackjack
            self.perdre() #le joueur perd
            return
        if self.player.has_split: #si le joueur a split
            for bet, hand in zip(self.player.bet, [self.player.hand, self.player.hand2]): #pour chaque main
                if self.dealer.hand.calculer_total() <= 21 and hand.calculer_total() < self.dealer.hand.calculer_total() or self.player.is_busted(hand): #si le dealer a un meilleur score ou si le joueur a dépassé 21
                    self.player.main_perdu += 1 #le joueur perd
                elif self.dealer.hand.calculer_total() > 21 or (self.dealer.hand.calculer_total() < hand.calculer_total()) and not self.player.is_busted(hand): #si le dealer a un moins bon score ou si le joueur a un meilleur score
                    self.player.money += 2 * bet #le joueur gagne
                    self.player.main_gagne += 1 #le joueur gagne
                else:
                    self.player.money += bet #si il y a égalité

            if self.player.main_gagne > self.player.main_perdu: #si le joueur a gagné
                self.message = "Gagné !"
                self.game_started = False
                self.win_sound.play()
            elif self.player.main_gagne < self.player.main_perdu: #si le joueur a perdu
                self.message = "Perdu !"
                self.game_started = False
                self.loose_sound.play()
            else: #si il y a égalité
                self.message = "Egalité"
                self.game_started = False
                self.win_sound.play()

        else: #si le joueur n'a pas split
            if self.dealer.hand.calculer_total() <= 21 and self.player.hand.calculer_total() < self.dealer.hand.calculer_total(): #si le dealer a un meilleur score ou si le joueur a dépassé 21
                self.perdre() #le joueur perd
            elif self.dealer.hand.calculer_total() > 21 or ( 
                    self.dealer.hand.calculer_total() < self.player.hand.calculer_total()): #si le dealer a un moins bon score ou si le joueur a un meilleur score
                self.gagner() #le joueur gagne
            else: #si il y a égalité
                self.egalite() #le joueur fait une égalité

        if self.player.has_double: #si le joueur a doublé
            self.player.bet[0] /= 2 #la mise est divisée par 2

        self.player.bet[1] = 0 #la mise de la deuxième main est remise à 0

    def start(self):
        '''
        Fonction qui démarre le jeu
        parametre
        ----------
        None
        retourne
        -------
        None
        '''

        self.game_started = True #démarre le jeu
        self.can_split = False 
        self.player.bet[1] = 0 #la mise de la deuxième main est remise à 0
        self.player.main_gagne = 0 #le nombre de mains gagnées est remis à 0
        self.player.main_perdu = 0 #le nombre de mains perdues est remis à 0
        self.player.has_double = False #
        self.player.has_split = False 
        self.premiere_main_termine = False 
        self.player.has_split = False 
        self.player.hand.add_card(self.deck.deal()) #le joueur tire une carte
        self.dealer.hand.add_card(self.deck.deal()) #le dealer tire une carte
        self.player.hand.add_card(self.deck.deal()) #le joueur tire une carte
        self.dealer.hand.add_card(self.deck.deal()) #le dealer tire une carte
        self.player.money -= self.player.bet[0] #l'argent du joueur est diminué de la mise
        if self.player.money >= self.player.bet[0]: #si le joueur a assez d'argent
            self.can_double = True #le joueur peut doubler
        self.deck.deal_sound.set_volume(1) #le volume du son de distribution est à 1
        if self.player.hand.has_blackjack() and self.dealer.hand.has_blackjack(): #si le joueur et le dealer ont un blackjack
            self.egalite() #si le joueur et le dealer ont un blackjack
            self.win_sound.play() #joue le son d'égalité
        elif self.player.hand.has_blackjack(): #si le joueur a un blackjack
            self.message = "BlackJack" #affiche le message
            self.win_sound.play() #joue le son de victoire
            self.player.money += self.player.bet[0] * 2.5 #le joueur gagne
            self.game_started = False 
        elif self.dealer.hand.has_blackjack(): #si le dealer a un blackjack
            if self.dealer.hand.cards[1].value == 1: #si la deuxième carte du dealer est un as
               
                if not self.player.hand.has_blackjack(): #si le joueur n'a pas un blackjack
                    self.perdre() #le joueur perd
                else:
                    self.egalite() #si le joueur a un blackjack
                self.win_sound.play() #joue le son de victoire
                self.game_started = False 
                self.dealer.retourner_carte(0) #retourne la carte du dealer
            else:
                self.perdre() #le joueur perd
        else:
            self.dealer.retourner_carte(0) #retourne la carte du dealer

        if self.player.hand.cards[0].value == self.player.hand.cards[1].value or (
                self.player.hand.cards[0].value >= 10 and self.player.hand.cards[1].value >= 10) and self.player.money >= self.player.bet[0]: #si les deux premières cartes du joueur ont la même valeur ou si les deux premières cartes du joueur sont des figures
            self.can_split = True #le joueur peut split

        return

    def play(self):
        '''
        Fonction qui lance le jeu
        parametre
        ----------
        None
        retourne
        -------
        None
        '''

        running = True

        while running: #boucle principale
            for event in pygame.event.get():
                if event.type == pygame.QUIT: 
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: #si le bouton gauche de la souris est cliqué

                    if self.bouton_split.est_clique(pygame.mouse.get_pos()) and self.can_split and self.player.money >= self.player.bet[0]:  #si le bouton split est cliqué
                        self.player.money -= self.player.bet[0] 
                        self.player.bet[1] = self.player.bet[0] 
                        self.player.has_split = True 
                        self.can_split = False
                        self.player.hand2.add_card(self.player.hand.cards.pop(1))
                        self.player.hand.add_card(self.deck.deal())
                        self.player.hand2.add_card(self.deck.deal())

                    if self.bouton_tirer.est_clique(pygame.mouse.get_pos()) and not self.message: #si le bouton tirer est cliqué
                        self.can_double = False
                        self.can_split = False
                        if not self.premiere_main_termine: 
                            self.player.hit(self.player.hand, self.deck)
                            if self.player.is_busted(self.player.hand):
                                self.loose_sound.play()
                                if self.player.has_split:
                                    self.premiere_main_termine = True
                                else:
                                    self.message = "Bust (Tu as depassé 21)"
                                    self.game_started = False
                            elif self.player.hand.calculer_total() == 21:
                                if self.player.has_split:
                                    self.premiere_main_termine = True
                                else:
                                    self.comparer_mains()
                        elif self.premiere_main_termine == True:
                            self.player.hit(self.player.hand2, self.deck)
                            if self.player.is_busted(self.player.hand2):
                                self.loose_sound.play()
                                self.comparer_mains()

                    if not self.message and self.bouton_commencer.est_clique(pygame.mouse.get_pos()) and not self.game_started:
                        self.start()

                    if self.bouton_rester.est_clique(pygame.mouse.get_pos()) and not self.message:

                        if not self.player.has_split or self.premiere_main_termine == True:
                            self.comparer_mains()
                        else:
                            self.premiere_main_termine = True

                    if self.bouton_doubler.est_clique(pygame.mouse.get_pos()) and not self.player.hand.calculer_total() >= 21 and not self.message and self.can_double:
                        self.player.money -= self.player.bet[0]
                        self.player.bet[0] *= 2
                        self.player.hit(self.player.hand, self.deck)
                        self.player.has_double = True
                        if self.player.is_busted(self.player.hand):
                            self.message = "Bust !"
                            self.loose_sound.play()
                            self.game_started = False
                        elif not self.player.has_split:
                            self.comparer_mains()
                        else:
                            self.premiere_main_termine = True

                    if self.message and self.bouton_recommencer.est_clique(pygame.mouse.get_pos()) and self.player.money > 0 and self.player.money >= self.player.bet[0]:
                        self.reset() 
                        self.start() 

                    if not self.game_started: #si le jeu n'a pas commencé
                        if self.bouton_augmenter_mise.est_clique(pygame.mouse.get_pos()): #si le bouton est cliqué
                            if self.player.money >= self.player.bet[0] + 50: #si le joueur a assez d'argent
                                self.player.bet[0] += 50 #augmente la mise
                            else:
                                self.player.bet[0] = self.player.money #la mise est égale à l'argent du joueur
                        if self.bouton_diminuer_mise.est_clique(pygame.mouse.get_pos()): #si le bouton est cliqué
                            if self.player.bet[0] >= 50: #si la mise est supérieure à 50
                                self.player.bet[0] -= 50 #diminue la mise
                            else: #si la mise est inférieure à 50
                                self.player.bet[0] = 0  #la mise est égale à 0
                        

            self.screen.fill(BACKGROUND_COLOR) #remplit la fenêtre avec la couleur de fond
            self.dessiner_monaie() #dessine la monaie
          

            if not self.game_started: #dessine les boutons
                self.bouton_commencer.dessiner(self.screen)

            if self.game_started: #dessine les boutons
                self.bouton_tirer.dessiner(self.screen)
                self.bouton_rester.dessiner(self.screen)
                if self.can_double: #dessine les boutons
                    self.bouton_doubler.dessiner(self.screen) 
                if self.can_split and self.player.money >= self.player.bet[1]:
                    self.bouton_split.dessiner(self.screen)

            if not self.game_started: #dessine les boutons
                self.bouton_augmenter_mise.dessiner(self.screen)
                self.bouton_diminuer_mise.dessiner(self.screen)
          


            self.dealer.dessiner(self.screen, (LARGEUR - CARTE_LARGEUR - 15) // 2, 15, self.dealer.hand) #dessine la main du dealer

            if self.message: #affiche le message
                self.afficher_message(self.screen, self.message) 
                self.bouton_recommencer.dessiner(self.screen) 

            if not self.player.has_split: #dessine la main du joueur
                self.player.dessiner(self.screen, (LARGEUR - CARTE_LARGEUR - 15) // 2, HAUTEUR - CARTE_HAUTEUR - 15,
                                     self.player.hand)
            elif self.player.has_split: #dessine les deux mains du joueur
                self.player.dessiner(self.screen, (LARGEUR - CARTE_LARGEUR - 15) // 3 * 2,
                                     HAUTEUR - CARTE_HAUTEUR - 15, self.player.hand)
                self.player.dessiner(self.screen, (LARGEUR - CARTE_LARGEUR - 15) // 3, HAUTEUR - CARTE_HAUTEUR - 15,
                                     self.player.hand2)

            self.deck.dessiner_cutting_card(self.screen) #dessine la carte de coupe
          
            pygame.display.flip()
            self.clock.tick(60)


game = Game()
game.play()
