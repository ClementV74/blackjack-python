import pygame
import os
import random

LARGEUR = 1700
HAUTEUR = 900
CARTE_LARGEUR = 1000
CARTE_HAUTEUR = 400
BACKGROUND_COLOR = (11, 127, 57)
BLACK = (0, 0, 0)
BLANC = (255, 255, 255)
ROUGE = (255, 0, 0)

pygame.init()

class Bouton:
    def __init__(self, x, y, l, h, text, text_couleur, couleur, couleur_subbriance) -> None:
        self.x, self.y, self.l, self.h = x, y, l, h
        self.text, self.text_couleur, self.couleur = text, text_couleur, couleur
        self.couleur_subbriance = couleur_subbriance

    def dessiner(self, screen, petit=False):
        position_souris = pygame.mouse.get_pos()
        couleur = self.couleur_subbriance if self.x < position_souris[0] < self.x + self.l and self.y < position_souris[1] < self.y + self.h else self.couleur
        pygame.draw.rect(screen, couleur, (self.x, self.y, self.l, self.h))
        font_size = 36 if petit else 56
        font = pygame.font.SysFont(None, font_size)
        text_surface = font.render(self.text, 1, self.text_couleur)
        text_rect = text_surface.get_rect(center=(self.x + self.l / 2, self.y + self.h / 2))
        screen.blit(text_surface, text_rect)

    def est_clique(self, position_souris):
        return self.x < position_souris[0] < self.x + self.l and self.y < position_souris[1] < self.y + self.h

class Card:
    SCALE_FACTOR = 0.5

    def __init__(self, suit, value):
        self.suit, self.value = suit, value
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
        self.face_up = not self.face_up


class Deck:
    def __init__(self):
        self.cutting_card_draw = False
        self.cards = [Card(suit, value) for _ in range(6) for suit in ["S", "H", 'C', 'D'] for value in range(1, 14)]
        self.deal_sound = pygame.mixer.Sound("sounds/deal.mp3")
        self.cutting_card_image = pygame.image.load("images/R_0.png")
        self.cutting_card_image = pygame.transform.scale(self.cutting_card_image,
                                                         (int(self.cutting_card_image.get_width() * Card.SCALE_FACTOR),
                                                          int(self.cutting_card_image.get_height() * Card.SCALE_FACTOR)))

    def shuffle(self):
        random.shuffle(self.cards)

    def add_cutting_card(self):
        index_milieu = round(len(self.cards) // 2)
        self.cards.insert(index_milieu, Card("R", 0))

    def deal(self):
        if self.cards:
            card = self.cards.pop()
            self.deal_sound.play()
            if card.suit == 'R':
                self.cutting_card_draw = True
                card = self.cards.pop()
            return card
        else:
            print("Erreur, plus de cartes dans le deck")

    def length(self):
        return len(self.cards)

    def dessiner_cutting_card(self, screen):
        if self.cutting_card_draw:
            screen.blit(self.cutting_card_image, (20, 20))

class Hand:
    def __init__(self):
        self.cards = []

    def add_card(self, card):
        self.cards.append(card)

    def calculer_total(self):
        total, as_count = 0, 0
        for card in self.cards:
            if card.value == 1 and total <= 10:
                total += 11
                as_count += 1
            else:
                total += min(card.value, 10)
        while total > 21 and as_count != 0:
            total -= 10
            as_count -= 1
        return total

    def has_blackjack(self):
        return len(self.cards) == 2 and (
                (self.cards[0].value == 1 and self.cards[1].value in [10, 11, 12, 13]) or
                (self.cards[1].value == 1 and self.cards[0].value in [10, 11, 12, 13]))
    
class Player:
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
        for card in hand.cards:
            image_to_draw = card.image if card.face_up else card.back_image
            screen.blit(image_to_draw, (x_offset, y))
            x_offset += 20

    def retourner_carte(self, index):
        if index < len(self.hand.cards):
            self.hand.cards[index].flip()

    def hit(self, hand, deck):
        card = deck.deal()
        hand.add_card(card)

    def is_busted(self, hand):
        return hand.calculer_total() > 21


class Dealer(Player):
    pass


class Game:
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
        self.game_started = True
        if self.deck.cutting_card_draw:
            self.deck = Deck()
            self.deck.shuffle()
            self.deck.add_cutting_card()
        self.player.hand = Hand()
        self.dealer.hand = Hand()
        self.player.hand2 = Hand()
        self.message = ""

    def afficher_message(self, screen, message):
        font = pygame.font.SysFont(None, 56)
        text_surface = font.render(message, 1, BLACK)
        text_rectangle = text_surface.get_rect(center=(LARGEUR / 2, HAUTEUR / 2))
        screen.blit(text_surface, text_rectangle)

    def dessiner_monaie(self):
        font = pygame.font.SysFont(None, 36)
        texte_argent = font.render("Argent : " + str(round(self.player.money)), 1, BLACK)
        texte_argent_rect = texte_argent.get_rect(center=(LARGEUR // 2 - 170, HAUTEUR - 10))
        self.screen.blit(texte_argent, texte_argent_rect)
        texte_mise = font.render("Mise : " + str(round(self.player.bet[0] + self.player.bet[1])), 1, BLACK)
        texte_mise_rect = texte_mise.get_rect(center=(LARGEUR // 2 - 170, HAUTEUR - 50))
        self.screen.blit(texte_mise, texte_mise_rect)
      
    def dessiner_monaie(self):
        font = pygame.font.SysFont(None, 36)
        texte_argent = font.render("Argent : " + str(round(self.player.money)), 1, BLACK)
        texte_argent_rect = texte_argent.get_rect(center=(LARGEUR // 2 - 170, HAUTEUR - 10))
        self.screen.blit(texte_argent, texte_argent_rect)
        texte_mise = font.render("Mise : " + str(round(self.player.bet[0] + self.player.bet[1])), 1, BLACK)
        texte_mise_rect = texte_mise.get_rect(center=(LARGEUR // 2 - 170, HAUTEUR - 50))
        self.screen.blit(texte_mise, texte_mise_rect)

        token_50 = pygame.image.load(os.path.join("monaie", "50.png"))
        token_100 = pygame.image.load(os.path.join("monaie", "100.png"))

    
        token_50 = pygame.transform.scale(token_50, (200, 150))
        token_100 = pygame.transform.scale(token_100, (200, 150))

        x_offset = LARGEUR // 2 + 230 
        y_offset = HAUTEUR -500

   
        total_100 = self.player.bet[0] // 100
   
        for _ in range(total_100):
            self.screen.blit(token_100, (x_offset, y_offset))
            x_offset += 20

   
        for _ in range((self.player.bet[0] % 100) // 50):
            self.screen.blit(token_50, (x_offset, y_offset))
            x_offset += 20

        x_offset = LARGEUR // 2 + 10
        y_offset = HAUTEUR - 200

    
        total_100 = self.player.bet[1] // 100
   
        for _ in range(total_100):
            self.screen.blit(token_100, (x_offset, y_offset))
            x_offset += 40

   
        for _ in range((self.player.bet[1] % 100) // 50):
            self.screen.blit(token_50, (x_offset, y_offset))
            x_offset += 40
    

    def perdre(self):
        self.message = "Perdu !"
        self.game_started = False
        self.loose_sound.play()

    def gagner(self):
        self.message = "Gagné !"
        self.player.money += 2 * self.player.bet[0]
        self.game_started = False
        self.win_sound.play()

    def egalite(self):
        self.message = "Egalité"
        self.player.money += self.player.bet[0]
        self.game_started = False
        self.win_sound.play()

    def comparer_mains(self):
        self.dealer.retourner_carte(0)
        while self.dealer.hand.calculer_total() < 17:
            self.dealer.hit(self.dealer.hand, self.deck)
        if self.dealer.hand.has_blackjack():
            self.perdre()
            return
        if self.player.has_split:
            for bet, hand in zip(self.player.bet, [self.player.hand, self.player.hand2]):
                if self.dealer.hand.calculer_total() <= 21 and hand.calculer_total() < self.dealer.hand.calculer_total() or self.player.is_busted(
                        hand):
                    self.player.main_perdu += 1
                elif self.dealer.hand.calculer_total() > 21 or (
                        self.dealer.hand.calculer_total() < hand.calculer_total()) and not self.player.is_busted(hand):
                    self.player.money += 2 * bet
                    self.player.main_gagne += 1
                else:
                    self.player.money += bet

            if self.player.main_gagne > self.player.main_perdu:
                self.message = "Gagné !"
                self.game_started = False
                self.win_sound.play()
            elif self.player.main_gagne < self.player.main_perdu:
                self.message = "Perdu !"
                self.game_started = False
                self.loose_sound.play()
            else:
                self.message = "Egalité"
                self.game_started = False
                self.win_sound.play()

        else:
            if self.dealer.hand.calculer_total() <= 21 and self.player.hand.calculer_total() < self.dealer.hand.calculer_total():
                self.perdre()
            elif self.dealer.hand.calculer_total() > 21 or (
                    self.dealer.hand.calculer_total() < self.player.hand.calculer_total()):
                self.gagner()
            else:
                self.egalite()

        if self.player.has_double:
            self.player.bet[0] /= 2

        self.player.bet[1] = 0

    def start(self):
        self.game_started = True
        self.can_split = False
        self.player.bet[1] = 0
        self.player.main_gagne = 0
        self.player.main_perdu = 0
        self.player.has_double = False
        self.player.has_split = False
        self.premiere_main_termine = False
        self.player.has_split = False
        self.player.hand.add_card(self.deck.deal())
        self.dealer.hand.add_card(self.deck.deal())
        self.player.hand.add_card(self.deck.deal())
        self.dealer.hand.add_card(self.deck.deal())
        self.player.money -= self.player.bet[0]
        if self.player.money >= self.player.bet[0]:
            self.can_double = True
        self.deck.deal_sound.set_volume(1)
        if self.player.hand.has_blackjack() and self.dealer.hand.has_blackjack():
            self.egalite()
            self.win_sound.play()
        elif self.player.hand.has_blackjack():
            self.message = "BlackJack"
            self.win_sound.play()
            self.player.money += self.player.bet[0] * 2.5
            self.game_started = False
        elif self.dealer.hand.has_blackjack():
            if self.dealer.hand.cards[1].value == 1:
               
                if not self.player.hand.has_blackjack():
                    self.perdre()
                else:
                    self.egalite()
                self.win_sound.play()
                self.game_started = False
                self.dealer.retourner_carte(0)
            else:
                self.perdre()
        else:
            self.dealer.retourner_carte(0)

        if self.player.hand.cards[0].value == self.player.hand.cards[1].value or (
                self.player.hand.cards[0].value >= 10 and self.player.hand.cards[1].value >= 10) and self.player.money >= self.player.bet[0]:
            self.can_split = True

        return

    def play(self):
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:

                    if self.bouton_split.est_clique(pygame.mouse.get_pos()) and self.can_split and self.player.money >= self.player.bet[0]:
                        self.player.money -= self.player.bet[0]
                        self.player.bet[1] = self.player.bet[0]
                        self.player.has_split = True
                        self.can_split = False
                        self.player.hand2.add_card(self.player.hand.cards.pop(1))
                        self.player.hand.add_card(self.deck.deal())
                        self.player.hand2.add_card(self.deck.deal())

                    if self.bouton_tirer.est_clique(pygame.mouse.get_pos()) and not self.message:
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

                    if not self.game_started:
                        if self.bouton_augmenter_mise.est_clique(pygame.mouse.get_pos()):
                            if self.player.money >= self.player.bet[0] + 50:
                                self.player.bet[0] += 50
                            else:
                                self.player.bet[0] = self.player.money
                        if self.bouton_diminuer_mise.est_clique(pygame.mouse.get_pos()):
                            if self.player.bet[0] >= 50:
                                self.player.bet[0] -= 50
                            else:
                                self.player.bet[0] = 0
                        

            self.screen.fill(BACKGROUND_COLOR)
            self.dessiner_monaie()
          

            if not self.game_started:
                self.bouton_commencer.dessiner(self.screen)

            if self.game_started:
                self.bouton_tirer.dessiner(self.screen)
                self.bouton_rester.dessiner(self.screen)
                if self.can_double:
                    self.bouton_doubler.dessiner(self.screen)
                if self.can_split and self.player.money >= self.player.bet[1]:
                    self.bouton_split.dessiner(self.screen)

            if not self.game_started:
                self.bouton_augmenter_mise.dessiner(self.screen)
                self.bouton_diminuer_mise.dessiner(self.screen)
          


            self.dealer.dessiner(self.screen, (LARGEUR - CARTE_LARGEUR - 15) // 2, 15, self.dealer.hand)

            if self.message:
                self.afficher_message(self.screen, self.message)
                self.bouton_recommencer.dessiner(self.screen)

            if not self.player.has_split:
                self.player.dessiner(self.screen, (LARGEUR - CARTE_LARGEUR - 15) // 2, HAUTEUR - CARTE_HAUTEUR - 15,
                                     self.player.hand)
            elif self.player.has_split:
                self.player.dessiner(self.screen, (LARGEUR - CARTE_LARGEUR - 15) // 3 * 2,
                                     HAUTEUR - CARTE_HAUTEUR - 15, self.player.hand)
                self.player.dessiner(self.screen, (LARGEUR - CARTE_LARGEUR - 15) // 3, HAUTEUR - CARTE_HAUTEUR - 15,
                                     self.player.hand2)

            self.deck.dessiner_cutting_card(self.screen)
          
            pygame.display.flip()
            self.clock.tick(60)


game = Game()
game.play()
