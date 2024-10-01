
import random
import numpy as np
from main import Game, Player, Pot


class SimplePokerEnv:
    def __init__(self):
        game = Game()
        self.player_hands = [game.p1.cards, game.p2.cards]


    def reset(self):
        game.hand.p1.cards.clear()
        game.hand.p2.cards.clear()
        game.hand.p1.current_bet = 0
        game.hand.p2.current_bet = 0
        game.hand.p1.total_bet = 0
        game.hand.p2.total_bet = 0
        game.hand.p1.fold = False
        game.hand.p2.fold = False
        game.hand.p1.all_in = False
        game.hand.p2.all_in = False
        game.hand.p1.check = False
        game.hand.p2.check = False
        game.pot_size.size = 0

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
            'community': self.community_cards,
            'pot': self.pot,
            'bets': self.bets.copy(),
            'current_player': self.current_player
        }
        return state

    def step(self, action):
        # Actions: 0 = Check/Call, 1 = Bet/Raise
        if action == 0:
            # Player checks/calls
            bet_amount = self.bets[1 - self.current_player] - self.bets[self.current_player]
            self.bets[self.current_player] += bet_amount
            self.pot += bet_amount
        elif action == 1:
            # Player bets/raises
            bet_amount = 10  # Fixed bet/raise amount
            self.bets[self.current_player] += bet_amount
            self.pot += bet_amount
        else:
            raise ValueError("Invalid action")

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






