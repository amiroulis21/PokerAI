import random
import numpy as np
from game import Game, Hand, Player, Pot
from settings import *


class SimplePokerEnv:
    def __init__(self):
        self.game = Game()


    def reset(self):
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
        self.player_hands = [[0, 0], [0, 0]]
        self.current_player = 0
        self.community_cards = []
        self.phase = 0  # 0 -> pre-flop, 1 -> post-flop
        self.last_actions = [None, None]
        self.done = False
        self.dealt_hole_cards = False



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
        for i in range(2):
            for j in range(2):
                #print(f"P{i+1}, Card{j+1}")
                self.player_hands[i][j] = ((value_dict[str(self.game.player_list[i].cards[j].data.value)] - 2) +
                                           (13 * suit_dict[self.game.player_list[i].cards[j].data.suit]))

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
            'pot': self.game.pot_size.size,
            'bets': [self.game.p1.current_bet, self.game.p2.current_bet],
            'chip_stacks': [self.game.p1.chips, self.game.p2.chips],
            'current_player': self.current_player,
            'phase': self.phase,
            'last_actions': self.last_actions
        }
        return state

    def step(self, action):

        if action not in [0, 1, 2]:
            raise ValueError("Invalid action")
        # Actions: 0 = Fold, 1 = Check/Call, 2 = Bet/Raise
        if action == 0:
            self.game.fold(self.game.player_list[self.current_player])
            self.game.hand.dealer.eval_folds()
            reward = [-self.game.player_list[self.current_player].current_bet,
                      self.game.pot_size.size / 2] if self.current_player == 0 else [
                self.game.pot_size.size / 2, -self.game.player_list[1 - self.current_player].current_bet]
            next_state = None
            self.done = True
            return next_state, reward, self.done

        if action == 1:
            # Player checks/calls
            bet_amount = min(self.game.amount_to_call, self.game.player_list[self.current_player].chips)
            if bet_amount > 0:
                self.game.call(self.game.player_list[self.current_player], bet_amount)
            elif self.game.amount_to_call == 0:
                self.game.check(self.game.player_list[self.current_player])



        elif action == 2:
            # Player bets/raises
            bet_amount = 10
            raise_amount = self.game.amount_to_call + bet_amount  # Fixed bet/raise amount
            if self.game.betting_state == 0:
                self.game.bet(self.game.player_list[self.current_player], min(bet_amount,
                                                                              self.game.player_list[
                                                                                  self.current_player].chips))
            else:
                self.game.raise_bet(self.game.player_list[self.current_player], min(raise_amount,
                                                                                    self.game.player_list[
                                                                                  self.current_player].chips))
        self.last_actions[self.current_player] = action
        if self.is_betting_round_over():
            if self.phase == 0:
                self.game.hand.dealer.deal_flop()
                self.phase = 1
                for i in range(3):
                    self.community_cards.append(
                            (value_dict[str(self.game.hand.dealer.flop.cards[i].data.value)] - 2) +
                            (13 * suit_dict[self.game.hand.dealer.flop.cards[i].data.suit]))
                self.game.p1.current_bet = 0
                self.game.p2.current_bet = 0
                self.last_actions = [None, None]
            else:
                self.done = True
                reward = self.calculate_rewards()
                next_state = None
                return next_state, reward, self.done
        # Switch to the other player
        self.current_player = 1 - self.current_player

        reward = [0, 0]
        next_state = self.get_state()
        return next_state, reward, self.done

    def is_betting_round_over(self):
        if self.last_actions[0] is None or self.last_actions[1] is None:
            return False

        if self.game.p1.current_bet == self.game.p2.current_bet:
            return True

        return False

    def calculate_rewards(self):
        # Simple hand evaluation: sum of card ranks
        # In a real game, you'd use proper hand rankings
        eval_cards = ([card_id.id for card_id in self.game.player_list[0].cards] + [card_id.id for card_id in
                                                                                    self.game.hand.dealer.flop.cards] + [
                          card_id.id for card_id in self.game.hand.dealer.flop.cards] +
                      [card_id.id for card_id in self.game.player_list[1].cards])

        self.game.hand.dealer.determined_winner = self.game.hand.dealer.eval_winner(eval_cards)

        if self.game.hand.dealer.determined_winner == "Player 1":
            return [self.game.pot_size.size / 2, -self.game.pot_size.size]
        elif self.game.hand.dealer.determined_winner == "Player 2":
            return [-self.game.pot_size.size / 2, self.game.pot_size.size]
        else:
            return [0, 0]

        """
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
        """

    def is_game_over(self):
        if self.game.hand.dealer.overall_winner is not None:
            return True
        return False
