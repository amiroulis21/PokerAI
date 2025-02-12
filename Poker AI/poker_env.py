import random
import numpy as np
from game import Game, Hand, Player, Pot
from settings import *

ILLEGAL_PENALTY = -2000 #-2000
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
        self.game.amount_to_call = 0
        self.game.hand = Hand(self.game.p1, self.game.p2, self.game.pot_size)
        self.player_hands = [[0, 0], [0, 0]]
        self.current_player = 0
        self.community_cards = []
        self.phase = 0  # 0 -> pre-flop, 1 -> post-flop
        self.last_actions = [None, None]
        self.done = False
        self.dealt_hole_cards = False
        self.illegal_actions = [3]
        self.penalty = 0


    def display_player_hand(self, player=Player):
        print(f"Player {player.id} Cards: {player.cards[0].id}, "
              f"{player.cards[1].id}")

    def display_community_cards(self):
        print(f"Flop: {self.game.hand.flop.cards[0].id} , {self.game.hand.flop.cards[1].id}, "
              f"{self.game.hand.flop.cards[2].id}")

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
            'last_actions': self.last_actions,

        }
        return state
    def replace_action(self, action):
        #print(f"P{self.current_player + 1} tries to use {action}")
        #self.penalty = ILLEGAL_PENALTY
        if self.illegal_actions.__contains__(2) and self.illegal_actions.__contains__(3):
            self.penalty = ILLEGAL_PENALTY
            return 1
        if action == 3:
            #self.penalty = ILLEGAL_PENALTY
            return 2
        if action == 2:
            #self.penalty = ILLEGAL_PENALTY
            return 3
        return action

    def step(self, action, is_player):
        self.penalty = 0
        if action not in [0, 1, 2, 3]:
            raise ValueError("Invalid action")
        if action in self.illegal_actions:
            action = self.replace_action(action)
        # Actions: 0 = Fold, 1 = Check/Call, 2 = Bet, 3 = Raise
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
                #if self.game.player_list[self.current_player].all_in:
                    #do stuff
            elif self.game.amount_to_call == 0:
                self.game.check(self.game.player_list[self.current_player])
            self.illegal_actions = [3]

            if self.game.p1.all_in or self.game.p2.all_in:
                self.illegal_actions = [0, 1, 2, 3]


        elif action == 2:
            bet_amount = 20
            if is_player:
                bet_amount = int(input("Type bet amount: "))
            self.game.bet(self.game.player_list[self.current_player], min(bet_amount,
                                                        min(self.game.player_list[self.current_player].chips,
                                                            self.game.player_list[1 - self.current_player].chips)))
            self.illegal_actions = [2]
            if (self.game.player_list[self.current_player].current_bet == self.game.player_list[1 - self.current_player].chips) or self.game.player_list[self.current_player].all_in:
                self.illegal_actions.append(3)


        elif action == 3:
            raise_amount = self.game.amount_to_call * 2
            if is_player:
                raise_amount = int(input("Type amount you want to raise to: "))
            if ((self.game.player_list[1 - self.current_player].current_bet + self.game.player_list[1 - self.current_player].chips) -
                (self.game.player_list[self.current_player].current_bet + raise_amount)) < 0:
                raise_amount = self.game.amount_to_call + self.game.player_list[1 - self.current_player].chips
            self.game.raise_bet(self.game.player_list[self.current_player], min(raise_amount,
                                                                                self.game.player_list[
                                                                            self.current_player].chips))

            self.illegal_actions = [2]
            if (self.game.player_list[self.current_player].total_bet == (self.game.player_list[1 - self.current_player].chips +
                    self.game.player_list[1 - self.current_player].total_bet)) or self.game.player_list[self.current_player].all_in:
                self.illegal_actions.append(3)
            if self.game.p1.all_in and self.game.p2.all_in:
                self.illegal_actions = [0, 1, 2, 3]



        self.last_actions[self.current_player] = action
        if self.is_betting_round_over():
            if self.phase == 0:
                self.game.hand.dealer.deal_flop()
                self.phase = 1
                for i in range(3):
                    self.community_cards.append(
                            (value_dict[str(self.game.hand.dealer.flop.cards[i].data.value)] - 2) +
                            (13 * suit_dict[self.game.hand.dealer.flop.cards[i].data.suit]))
                self.display_community_cards()
                self.game.p1.current_bet = 0
                self.game.p2.current_bet = 0
                self.last_actions = [None, None]
                self.current_player = 0
            else:
                self.done = True
                reward = self.calculate_rewards()
                next_state = None
                return next_state, reward, self.done
        else:
            self.current_player = 1 - self.current_player

        reward = [0, 0]
        reward[self.current_player] += self.penalty
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
            return [self.game.pot_size.size / 2, -self.game.pot_size.size / 2]
        elif self.game.hand.dealer.determined_winner == "Player 2":
            return [-self.game.pot_size.size / 2, self.game.pot_size.size / 2]
        else:
            return [0, 0]


    def is_game_over(self):
        if self.game.hand.dealer.overall_winner is not None:
            return True
        return False

    def resolve_game(self):
        if self.phase == 0:
            self.game.hand.dealer.deal_flop()
            self.phase = 1
            for i in range(3):
                self.community_cards.append(
                    (value_dict[str(self.game.hand.dealer.flop.cards[i].data.value)] - 2) +
                    (13 * suit_dict[self.game.hand.dealer.flop.cards[i].data.suit]))
            self.display_community_cards()
            self.game.p1.current_bet = 0
            self.game.p2.current_bet = 0
            self.last_actions = [None, None]
        self.done = True
        reward = self.calculate_rewards()
        next_state = None
        return next_state, reward, self.done