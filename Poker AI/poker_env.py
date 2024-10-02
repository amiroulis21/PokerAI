import random
import numpy as np
from main import Game, Hand, Player, Pot
from settings import *


class SimplePokerEnv:
    def __init__(self):
        self.game = Game()
        self.player_hands = [[], []]
        self.current_player = 0
        self.community_cards = []
        self.is_running = False



    def reset(self):
        if not self.is_running:
            self.game.run()
            self.is_running = True
        else:
            self.game.hand.p1.cards.clear()
            self.game.hand.p2.cards.clear()
            self.game.hand.p1.current_bet = 0
            self.game.hand.p2.current_bet = 0
            self.game.hand.p1.total_bet = 0
            self.game.hand.p2.total_bet = 0
            self.game.hand.p1.fold = False
            self.game.hand.p2.fold = False
            self.game.hand.p1.all_in = False
            self.game.hand.p2.all_in = False
            self.game.hand.p1.check = False
            self.game.hand.p2.check = False
            self.game.pot_size.size = 0
            self.game.hand = Hand(self.game.p1, self.game.p2, self.game.pot_size)

        for i in range(2):
            for j in range(2):
                self.player_hands[i][j] = ((value_dict[self.game.hand.dealer.player_list[i].cards[j].data.value] - 2) +
                                           (13 * suit_dict[self.game.hand.dealer.player_list[i].cards[j].data.suit]))


    """
        # Initialize the deck: 52 cards represented by numbers 0-51

        # Deal two cards to each player
        self.player_hands = [self.deal_hand(), self.deal_hand()]
        # Deal five community cards
        self.community_cards = [self.deck.pop() for _ in range(5)]
        # Pot starts at zero
        self.pot = 0
        # Bets made by players
        self.bets = [0, 0]
        # Current player (0 or 1)
        self.current_player = 0
        # Game over flag
        self.done = False
        return self.get_state()
    """

    def deal_hand(self):
        return [self.deck.pop(), self.deck.pop()]

    def get_state(self):
        # For simplicity, state includes:
        # - Current player's hand
        # - Community cards
        # - Pot size
        # - Bets
        # We hide the opponent's hand to simulate incomplete information

        state = {
            'hand': self.player_hands[self.current_player],
            'community': self.game.hand.flop,
            'pot': self.game.pot_size,
            'bets': [self.game.p1.current_bet, self.game.p2.current_bet],
            'current_player': self.current_player
        }
        return state

    def step(self, action):
        # Actions: 0 = Fold, 1 = Check/Call, 2 = Bet/Raise
        if action == 0:
            self.game.fold(self.game.player_list[self.current_player])
        if action == 1:
            # Player checks/calls
            bet_amount = min(self.game.amount_to_call, self.game.player_list[self.current_player].chips)
            if bet_amount > 0:
                self.game.call(self.game.player_list[self.current_player], bet_amount)
            elif bet_amount == 0:
                self.game.check(self.game.player_list[self.current_player])
        elif action == 2:
            # Player bets/raises
            bet_amount = 10
            raise_amount = self.game.amount_to_call + bet_amount# Fixed bet/raise amount
            if self.game.betting_state == 0:
                self.game.bet(self.game.player_list[self.current_player], min(bet_amount,
                                                                    self.game.player_list[self.current_player].chips))
            else:
                self.game.raise_bet(self.game.player_list[self.current_player], min(raise_amount,
                                                                    self.game.player_list[self.current_player].chips))
        else:
            raise ValueError("Invalid action")

        if self.game.hand.dealer.round == 2:
            for i in range(3):
                self.community_cards[i] = (
                            (value_dict[self.game.hand.dealer.flop.cards[i].data.value] - 2) +
                            (13 * suit_dict[self.game.hand.dealer.flop.cards[i].data.suit]))





        # Switch to the other player
        self.current_player = 1 - self.current_player

        # If both players have acted, end the game
        if self.bets[0] == self.bets[1]:
            self.done = True
            reward = self.calculate_rewards()
            next_state = None
        else:
            reward = [0, 0]  # No immediate reward
            next_state = self.get_state()

        return next_state, reward, self.done

    def calculate_rewards(self):
        # Simple hand evaluation: sum of card ranks
        # In a real game, you'd use proper hand rankings
        player_scores = []
        for i in range(2):
            hand = self.player_hands[i] + self.community_cards
            ranks = [card % 13 for card in hand]
            score = sum(ranks)
            player_scores.append(score)

        if player_scores[0] > player_scores[1]:
            # Player 0 wins
            return [self.pot / 2, -self.pot / 2]
        elif player_scores[0] < player_scores[1]:
            # Player 1 wins
            return [-self.pot / 2, self.pot / 2]
        else:
            # Tie
            return [0, 0]
