import ctypes
import pygame
import pygame_widgets
import sys
import random
from dqn import DQNAgent
import torch
from new_hand import *
from settings import *
from button import *
from pygame_widgets.textbox import TextBox

# Maintain resolution regardless of Windows scaling settings
ctypes.windll.user32.SetProcessDPIAware()

bet_button = Button(390, 1000, 100, 75)
check_button = Button(280, 1000, 100, 75)
call_button = Button(500, 1000, 100, 75)
raise_button = Button(610, 1000, 100, 75)
fold_button = Button(720, 1000, 100, 75)


class Player:
    def __init__(self, id):
        self.cards = []
        self.chips = 1000
        self.current_bet = 0
        self.total_bet = 0
        self.can_bet = False
        self.id = id
        self.fold = False
        self.all_in = False
        self.check = False


class Pot:
    def __init__(self):
        self.size = 0


class Game:

    def __init__(self):

        # General setup
        #pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(TITLE_STRING)
        self.clock = pygame.time.Clock()
        self.p1 = Player(1)
        self.p2 = Player(2)
        self.player_list = [self.p1, self.p2]
        self.pot_size = Pot()
        self.hand = Hand(self.p1, self.p2, self.pot_size)
        self.ante = 5
        self.bet_exists = False
        self.betting_state = 0  # 0 = no one has bet, player bets are equal, or both players are all in, 1 = waiting on player2 to call, -1 = waiting on player1 to call
        self.turn = 1
        self.round = 1# 1 = player1 to act, -1 = player2 to act
        #self.total_current_bet = 0
        self.amount_to_call = 0

        bet_button.setButton('Bet', self.bet)
        check_button.setButton('Check', self.check)
        call_button.setButton('Call', self.call)
        raise_button.setButton('Raise', self.raise_bet)
        fold_button.setButton('Fold', self.fold)
        self.bet_text = TextBox(self.screen, 390, 915, 100, 75, fontSize=40, borderColour=(0, 0, 0),
                                textColour=(0, 0, 0))
        self.raise_text = TextBox(self.screen, 610, 915, 100, 75, fontSize=40, borderColour=(0, 0, 0),
                                  textColour=(0, 0, 0))
        """
               input_size = 13
               hidden_size = 128
               action_size = 4
               self.agent = DQNAgent(input_size, hidden_size, action_size)
               self.agent.model.load_state_dict(torch.load('agent1_model.pth'))
               self.agent.model.eval()
               self.agent.epsilon = 0
        """

    def bet_process(self):
        mousePos = pygame.mouse.get_pos()
        bet_button.buttonSurface.fill(bet_button.fillColors['normal'])
        if bet_button.buttonRect.collidepoint(mousePos):
            bet_button.buttonSurface.fill(bet_button.fillColors['hover'])
            if pygame.mouse.get_pressed(num_buttons=3)[
                0] and self.turn == 1 and self.betting_state == 0 and bet_button.alreadyPressed == False:
                bet_button.buttonSurface.fill(bet_button.fillColors['pressed'])
                bet_button.alreadyPressed = True
                print(self.turn)
                print(self.betting_state)
                if self.bet_text.getText() != None and self.bet_text.getText().isdigit() and self.hand.dealer.determined_winner == None:
                    bet = int(self.bet_text.getText())
                    if bet <= self.hand.p1.chips and bet >= self.ante and bet <= self.hand.p2.chips:
                        bet_button.onclickFunction(self.hand.p1, bet)
                        self.hand.p1.can_bet = False
                        self.betting_state = 1
                        print(self.turn)
                        print(self.betting_state)
            if not pygame.mouse.get_pressed(num_buttons=3)[0]:
                bet_button.alreadyPressed = False
        bet_button.buttonSurface.blit(bet_button.buttonSurf, [
            bet_button.buttonRect.width / 2 - bet_button.buttonSurf.get_rect().width / 2,
            bet_button.buttonRect.height / 2 - bet_button.buttonSurf.get_rect().height / 2
        ])
        self.screen.blit(bet_button.buttonSurface, bet_button.buttonRect)

    def check_process(self):
        mousePos = pygame.mouse.get_pos()
        check_button.buttonSurface.fill(check_button.fillColors['normal'])
        if check_button.buttonRect.collidepoint(mousePos):
            check_button.buttonSurface.fill(check_button.fillColors['hover'])
            if pygame.mouse.get_pressed(num_buttons=3)[0] and check_button.alreadyPressed == False:
                check_button.buttonSurface.fill(check_button.fillColors['pressed'])
                check_button.alreadyPressed = True
                if self.betting_state == 0 and self.turn == 1 and self.hand.dealer.determined_winner == None:
                    check_button.onclickFunction(self.hand.p1)
                    self.hand.p1.can_bet = False
            if not pygame.mouse.get_pressed(num_buttons=3)[0]:
                check_button.alreadyPressed = False
        check_button.buttonSurface.blit(check_button.buttonSurf, [
            check_button.buttonRect.width / 2 - check_button.buttonSurf.get_rect().width / 2,
            check_button.buttonRect.height / 2 - check_button.buttonSurf.get_rect().height / 2
        ])
        self.screen.blit(check_button.buttonSurface, check_button.buttonRect)

    def call_process(self):
        mousePos = pygame.mouse.get_pos()
        call_button.buttonSurface.fill(check_button.fillColors['normal'])
        if call_button.buttonRect.collidepoint(mousePos):
            call_button.buttonSurface.fill(call_button.fillColors['hover'])
            if pygame.mouse.get_pressed(num_buttons=3)[0] and call_button.alreadyPressed == False:
                call_button.buttonSurface.fill(call_button.fillColors['pressed'])
                call_button.alreadyPressed = True
                if self.betting_state == -1 and self.turn == 1 and self.hand.dealer.determined_winner == None:
                    call_button.onclickFunction(self.hand.p1, self.amount_to_call)
                    # self.hand.p1.can_bet = False
            if not pygame.mouse.get_pressed(num_buttons=3)[0]:
                call_button.alreadyPressed = False
        call_button.buttonSurface.blit(call_button.buttonSurf, [
            call_button.buttonRect.width / 2 - call_button.buttonSurf.get_rect().width / 2,
            call_button.buttonRect.height / 2 - call_button.buttonSurf.get_rect().height / 2
        ])
        self.screen.blit(call_button.buttonSurface, call_button.buttonRect)

    def raise_process(self):
        mousePos = pygame.mouse.get_pos()
        raise_button.buttonSurface.fill(raise_button.fillColors['normal'])
        if raise_button.buttonRect.collidepoint(mousePos):
            raise_button.buttonSurface.fill(raise_button.fillColors['hover'])
            if pygame.mouse.get_pressed(num_buttons=3)[
                0] and self.turn == 1 and self.betting_state == -1 and raise_button.alreadyPressed == False:
                raise_button.buttonSurface.fill(raise_button.fillColors['pressed'])
                raise_button.alreadyPressed = True
                print(self.turn)
                print(self.betting_state)
                if self.raise_text.getText() != None and self.raise_text.getText().isdigit() and self.hand.dealer.determined_winner == None:
                    raise_ = int(self.raise_text.getText())
                    if raise_ >= 10 and raise_ > self.hand.p2.current_bet and raise_ < self.hand.p1.chips and raise_ <= self.hand.p2.chips:
                        raise_button.onclickFunction(self.hand.p1, raise_)
                        self.hand.p1.can_bet = False
                        self.betting_state = 1
                        print(self.turn)
                        print(self.betting_state)
            if not pygame.mouse.get_pressed(num_buttons=3)[0]:
                raise_button.alreadyPressed = False
        raise_button.buttonSurface.blit(raise_button.buttonSurf, [
            raise_button.buttonRect.width / 2 - raise_button.buttonSurf.get_rect().width / 2,
            raise_button.buttonRect.height / 2 - raise_button.buttonSurf.get_rect().height / 2
        ])
        self.screen.blit(raise_button.buttonSurface, raise_button.buttonRect)

    def fold_process(self):
        mousePos = pygame.mouse.get_pos()
        fold_button.buttonSurface.fill(fold_button.fillColors['normal'])
        if fold_button.buttonRect.collidepoint(mousePos):
            fold_button.buttonSurface.fill(fold_button.fillColors['hover'])
            if pygame.mouse.get_pressed(num_buttons=3)[
                0] and fold_button.alreadyPressed == False and self.turn == 1 and self.hand.dealer.determined_winner == None:
                fold_button.alreadyPressed = True
                fold_button.onclickFunction(self.hand.p1)
            if not pygame.mouse.get_pressed(num_buttons=3)[0]:
                fold_button.alreadyPressed = False
        fold_button.buttonSurface.blit(fold_button.buttonSurf, [
            fold_button.buttonRect.width / 2 - fold_button.buttonSurf.get_rect().width / 2,
            fold_button.buttonRect.height / 2 - fold_button.buttonSurf.get_rect().height / 2
        ])
        self.screen.blit(fold_button.buttonSurface, fold_button.buttonRect)

    def run(self):
        self.start_time = pygame.time.get_ticks()
        while True:
            self.bet_process()
            self.check_process()
            self.call_process()
            self.raise_process()
            self.fold_process()
            events = pygame.event.get()
            # Handle quit operation
            for event in events:
                if pygame.key.get_pressed()[pygame.K_ESCAPE] or event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if pygame.key.get_pressed()[pygame.K_RIGHT]:
                    if self.hand.dealer.determined_winner != None and self.hand.dealer.overall_winner is None:
                        self.hand.p1.cards.clear()
                        self.hand.p2.cards.clear()
                        self.hand.p1.current_bet = 0
                        self.hand.p2.current_bet = 0
                        self.hand.p1.total_bet = 0
                        self.hand.p2.total_bet = 0
                        self.hand.p1.fold = False
                        self.hand.p2.fold = False
                        self.hand.p1.all_in = False
                        self.hand.p2.all_in = False
                        self.hand.p1.check = False
                        self.hand.p2.check = False
                        self.pot_size.size = 0

                        self.hand = Hand(self.hand.p1, self.hand.p2, self.pot_size)
                if pygame.key.get_pressed()[pygame.K_SPACE]:
                    if self.hand.dealer.overall_winner is not None:
                        self.hand.p1.chips = 1000
                        self.hand.p2.chips = 1000
                        self.hand.p1.cards.clear()
                        self.hand.p2.cards.clear()
                        self.hand.p1.current_bet = 0
                        self.hand.p2.current_bet = 0
                        self.hand.p1.total_bet = 0
                        self.hand.p2.total_bet = 0
                        self.hand.p1.fold = False
                        self.hand.p2.fold = False
                        self.hand.p1.all_in = False
                        self.hand.p2.all_in = False
                        self.hand.p1.check = False
                        self.hand.p2.check = False
                        self.pot_size.size = 0

                        self.hand = Hand(self.hand.p1, self.hand.p2, self.pot_size)

            # Time variables
            self.delta_time = (pygame.time.get_ticks() - self.start_time) / 1000
            self.start_time = pygame.time.get_ticks()
            pygame_widgets.update(events)
            pygame.display.update()
            self.screen.fill(BG_COLOR)

            self.hand.update()
            self.clock.tick(FPS)

            """
                       if self.turn == -1:
                           state = self.extract_state()
                           state_vector = self.preprocess_state(state)
                           state_tensor = torch.FloatTensor(state_vector)

                           with torch.no_grad():
                               action = self.agent.act(state_tensor)

                           self.execute_agent_action(action)

                           # Switch turn
                           self.turn *= -1
                       """

    def ante_up(self):
        self.hand.p1.chips -= self.ante
        self.hand.p1.total_bet += self.ante
        self.hand.p2.chips -= self.ante
        self.hand.p2.total_bet += self.ante
        self.pot_size.size += self.ante * 2
        if self.hand.p1.chips <= 0:
            self.hand.p1.all_in = True
        elif self.hand.p2.chips <= 0:
            self.hand.p2.all_in = True
        print(f"\nROUND {self.round}")
        print("P1 antes 5")
        print("P2 antes 5")
        print(f"P1 {self.hand.p1.chips}")
        print(f"P2 {self.hand.p2.chips}")
        self.round += 1

    def call(self, player=Player, amount=int):
        player.chips -= amount
        player.current_bet += amount
        player.total_bet += amount
        #self.total_current_bet += amount
        self.pot_size.size += amount
        self.bet_exists = False
        self.betting_state = 0
        self.amount_to_call = 0
        if player.chips <= 0:
            player.all_in = True
        print(f"P{player.id} calls")
        print(f"P{player.id} {player.chips}")

    def bet(self, player=Player, amount=int):
        player.chips -= amount
        player.current_bet += amount
        player.total_bet += amount
        self.bet_exists = True
        self.pot_size.size += amount
        print(f"P{player.id} bet {amount}")
        print(f"P{player.id} {player.chips}")
        self.amount_to_call = max(self.p1.current_bet, self.p2.current_bet) - min(self.p1.current_bet,
                                                                                  self.p2.current_bet)
        if player.chips <= 0:
            player.all_in = True
        self.turn *= -1
        #self.call(amount)

    """
        self.hand.p1.chips -= 5
        self.hand.p1.current_bet += 5
        self.hand.p1.total_bet += 5
        self.total_current_bet += 5
        self.pot_size += 5
        self.bet_exists = True
        print(f"P1 bet {self.hand.p1.current_bet}")
        print(f"P1 {self.hand.p1.chips}")
        self.call()
        """

    def raise_bet(self, player=Player, amount=int):
        player.chips -= amount
        player.current_bet += amount
        player.total_bet += amount
        self.bet_exists = True
        self.pot_size.size += amount
        if player.chips <= 0:
            player.all_in = True
        print(f"P{player.id} raises to {player.current_bet}")
        print(f"P{player.id} {player.chips}")
        self.amount_to_call = max(self.p1.current_bet, self.p2.current_bet) - min(self.p1.current_bet,
                                                                                  self.p2.current_bet)
        self.turn *= -1

    def check(self, player=Player):
        print(f"P{player.id} checks")
        self.turn *= -1
        player.check = True

    def fold(self, player=Player):
        print(f"P{player.id} folds")
        player.fold = True




