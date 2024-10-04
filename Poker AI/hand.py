import itertools, os, pygame, random
from cards import *
from settings import *

# Audio
"""pygame.mixer.init()
audio_files = os.listdir(GAME_AUDIO_DIR)
wav_files = [file for file in audio_files if file.endswith('.wav')]
num_channels = len(wav_files)
pygame.mixer.set_num_channels(num_channels)
channels = [pygame.mixer.Channel(i) for i in range(num_channels)]
"""


class Hand:
    def __init__(self, p1, p2, pot_size):
        self.display_surface = pygame.display.get_surface()
        self.winner = None
        self.font = pygame.font.Font(GAME_FONT, 120)
        self.win_rotation_angle = random.uniform(-10, 10)
        self.p1 = p1
        self.p2 = p2
        self.pot_size = pot_size
        self.flop = Flop()
        self.player_list = [self.p1, self.p2]
        self.dealer = Dealer(self.player_list, self.flop, self.pot_size)
        self.p1.can_bet = True

    def render_cards(self):
        # Draw cards at current positions
        for player in self.player_list:
            for card in player.cards:
                self.display_surface.blit(card.card_surf, card.start_position)
        for card in self.flop.cards:
            self.display_surface.blit(card.card_surf, card.position)

    def render_round_winner(self):
        if self.dealer.determined_winner is not None:
            # Set the text and color based on the winner
            if self.dealer.determined_winner == "Player 1":
                text = "Player 1 Wins the Pot!"
                text_color = (115, 235, 0)  # Blue
            elif self.dealer.determined_winner == "Player 2":
                text = "Player 2 Wins the Pot!"
                text_color = (135, 206, 235)  # Green
            elif self.dealer.determined_winner == "Tie":
                text = "Split Pot!"
                text_color = (255, 192, 203)  # Pink

            coordinates = (300, 100)
            # Winner text
            text_surface = self.font.render(text, True, text_color)
            text_rect = text_surface.get_rect()
            text_rect.topleft = coordinates
            rotated_surface = pygame.transform.rotate(text_surface, self.win_rotation_angle)
            rotated_rect = rotated_surface.get_rect(center=text_rect.center)
            self.display_surface.blit(rotated_surface, rotated_rect)

    def render_overall_winner(self):
        if self.dealer.overall_winner is not None:
            if self.dealer.overall_winner == "Player 1":
                text = "Player 1 Wins the Game"
                text_color = (115, 235, 0)
            elif self.dealer.overall_winner == "Player 2":
                text = "Player 2 Wins the Game"
                text_color = (135, 206, 235)

            coordinates = (300, 100)
            # Winner text
            text_surface = self.font.render(text, True, text_color)
            text_rect = text_surface.get_rect()
            text_rect.topleft = coordinates
            rotated_surface = pygame.transform.rotate(text_surface, self.win_rotation_angle)
            rotated_rect = rotated_surface.get_rect(center=text_rect.center)
            self.display_surface.blit(rotated_surface, rotated_rect)

    def update(self):
        #self.dealer.update()
        self.render_cards()
        self.render_overall_winner()
        if self.dealer.overall_winner is None:
            self.render_round_winner()


class Dealer():
    def __init__(self, players, flop, pot_size):
        self.determined_winner = None
        self.overall_winner = None
        self.players_list = players
        self.num_players = len(players)
        self.current_player_index = 0
        self.current_flop_index = 0
        self.printed_flop = False
        self.deck = self.generate_deck()
        random.shuffle(self.deck)
        self.animating_card = None
        self.can_deal = True
        self.can_deal_flop = False
        self.last_dealt_card_time = None
        self.last_dealt_flop_time = None
        self.dealt_cards = 0
        self.flop = flop
        self.pot_size = pot_size
        self.audio_channel = 0
        self.round = 1

    """ def card_audio(self):
        random_wav = random.choice(wav_files)
        wav_file_path = os.path.join(GAME_AUDIO_DIR, random_wav)
        sound = pygame.mixer.Sound(wav_file_path)
        channels[self.audio_channel].play(sound)
        self.audio_channel += 1
        """

    def generate_deck(self):
        fresh_deck = []
        for cv in cardvalues:
            for cs in cardsuits:
                fresh_deck.append(Card(cv, cs))
        return fresh_deck

    def cooldowns(self):
        # Need to use delta time
        current_time = pygame.time.get_ticks()
        #print(self.last_dealt_card_time)
        #print(current_time)
        #print(self.last_dealt_card_time and current_time)
        if self.last_dealt_card_time and current_time - 200 > self.last_dealt_card_time:
            print("can_deal")
            self.can_deal = True

        if self.last_dealt_flop_time and \
                current_time - random.randint(120, 200) > self.last_dealt_flop_time:
            self.can_deal_flop = True

    def animate_hole_card(self, card):
        current_time = pygame.time.get_ticks()
        elapsed_time = current_time - self.last_dealt_card_time

        current_card = card
        animation_duration = 200

        if elapsed_time < animation_duration:
            # Calculate the increment for each frame to move the card and update position
            x_orig, y_orig = current_card.orig_position
            x_final, y_final = current_card.position
            elapsed_ratio = elapsed_time / animation_duration
            x_change = x_orig + (x_final - x_orig) * elapsed_ratio
            y_change = y_orig + (y_final - y_orig) * elapsed_ratio
            current_card.start_position = (x_change, y_change)
        else:
            card.animation_complete = True

    def deal_hole_cards(self):
        for i in range(4):
            current_player = self.players_list[self.current_player_index]
            current_player.cards.append(self.deck[-1])
            self.dealt_cards = self.update_dealt_card_count()
            # Remove dealt card from deck; change player index; prompt card dealing cooldown
            self.deck.pop(-1)
            self.current_player_index = (self.current_player_index + 1) % self.num_players

    def deal_flop(self):
        # Set flop card locations

        while self.dealt_cards - (self.num_players * 2) < 3:
            self.flop.cards.append(self.deck[-1])
            self.deck.pop(-1)
            self.last_dealt_flop_time = pygame.time.get_ticks()
            self.dealt_cards += 1

        # Print length of deck after card is dealt for troubleshooting
        # print(f"{len(self.deck)} cards left in deck; {self.update_dealt_card_count()} dealt.")

    # Hand-ranking algorithm reference in README.md
    def eval_hand(self, hand):
        # Return ranking followed by tie-break information.
        # 8. Straight Flush
        # 7. Four of a Kind
        # 6. Full House
        # 5. Flush
        # 4. Straight
        # 3. Three of a Kind
        # 2. Two pair
        # 1. One pair
        # 0. High card

        values = sorted([c[0] for c in hand], reverse=True)
        suits = [c[1] for c in hand]
        straight = (values == list(range(values[0], values[0] - 5, -1)) or values == [14, 5, 4, 3, 2])
        flush = all(s == suits[0] for s in suits)

        if straight and flush: return 8, values[1]
        if flush: return 5, values
        if straight: return 4, values[1]

        trips = []
        pairs = []
        for v, group in itertools.groupby(values):
            count = sum(1 for _ in group)
            if count == 4:
                return 7, v, values
            elif count == 3:
                trips.append(v)
            elif count == 2:
                pairs.append(v)

        if trips: return (6 if pairs else 3), trips, pairs, values
        return len(pairs), pairs, values

    def eval_winner(self, hand_to_eval):
        eval_cards = [(value_dict[x[0]], x[1]) for x in hand_to_eval]
        if self.eval_hand(eval_cards[:5]) > self.eval_hand(eval_cards[5:]):
            print(f"P1 WIN: {self.eval_hand(eval_cards[:5])}")
            self.players_list[0].chips += self.pot_size.size

            print(f"P1 {self.players_list[0].chips}")
            print(f"P2 {self.players_list[1].chips}")
            self.overall_winner = self.eval_overall_winner()
            return "Player 1"
        elif self.eval_hand(eval_cards[:5]) < self.eval_hand(eval_cards[5:]):
            print(f"P2 WIN: {self.eval_hand(eval_cards[5:])}")
            self.players_list[1].chips += self.pot_size.size

            print(f"P1 {self.players_list[0].chips}")
            print(f"P2 {self.players_list[1].chips}")
            self.overall_winner = self.eval_overall_winner()
            return "Player 2"
        else:
            print("SPLIT")
            self.players_list[0].chips += self.pot_size.size / 2
            self.players_list[1].chips += self.pot_size.size / 2
            print(f"P1 {self.players_list[0].chips}")
            print(f"P2 {self.players_list[1].chips}")
            return "Tie"

    def eval_folds(self):
        if self.players_list[0].fold or self.players_list[1].fold:
            if self.players_list[0].fold:
                self.determined_winner = "Player 2"
                self.players_list[1].chips += self.pot_size.size
                print("P2 WIN")
            elif self.players_list[1].fold:
                self.determined_winner = "Player 1"
                self.players_list[0].chips += self.pot_size.size
                print("P1 WIN")
            print(f"P1 {self.players_list[0].chips}")
            print(f"P2 {self.players_list[1].chips}")

    def eval_overall_winner(self):
        if self.players_list[0].chips == 0:
            return "Player 2"
        elif self.players_list[1].chips == 0:
            return "Player 1"
        return None

    # Print to console
    def print_hands(self):
        for i in range(len(self.players_list)):
            print(f"P{i + 1}: {[card.id for card in self.players_list[i].cards]}")
        print(f"FL: {[card.id for card in self.flop.cards]}")

    # Getter for number of dealt cards
    def update_dealt_card_count(self):
        total_card_count = 0
        for player in self.players_list:
            total_card_count += len(player.cards)
        total_card_count += len(self.flop.cards)
        return total_card_count

    def update(self):
        self.dealt_cards = self.update_dealt_card_count()
        self.cooldowns()

        if self.dealt_cards < (self.num_players * 2):
            self.deal_hole_cards()

        if self.animating_card:
            self.animate_hole_card(self.animating_card)

        if self.determined_winner is None:
            self.eval_folds()

        # Deal flop after hole cards are dealt and animations are done and bets are in
        if self.dealt_cards == (self.num_players * 2) and (
                not self.animating_card or self.animating_card.animation_complete):
            if self.players_list[0].current_bet == self.players_list[1].current_bet and (
                    self.players_list[0].current_bet != 0 or self.players_list[0].all_in or self.players_list[
                1].all_in or (
                            self.players_list[0].check and self.players_list[1].check)):
                self.can_deal_flop = True

        if self.dealt_cards < (self.num_players * 2) + 3 and self.can_deal_flop:
            self.deal_flop()
            self.players_list[0].check = False
            self.players_list[1].check = False
            #print(self.dealt_cards)

        if self.dealt_cards == (self.num_players * 2) + 3 and self.round == 1:
            self.players_list[0].current_bet = 0
            self.players_list[1].current_bet = 0
            print(f"P1 reset bet {self.players_list[0].current_bet}")
            print(f"P2 reset bet {self.players_list[1].current_bet}")
            self.players_list[0].can_bet = True
            self.round += 1
        # Print hand data to console
        if not self.printed_flop and self.dealt_cards == (self.num_players * 2) + 3:
            self.print_hands()
            self.printed_flop = True

        if self.dealt_cards == ((self.num_players * 2) + 3) and (
                self.players_list[0].current_bet == self.players_list[1].current_bet) and (
                self.players_list[0].current_bet != 0 or self.players_list[0].all_in or self.players_list[1].all_in or (
                self.players_list[0].check and self.players_list[1].check)) and self.determined_winner is None:
            eval_cards = [card_id.id for card_id in self.players_list[0].cards] + [card_id.id for card_id in
                                                                                   self.flop.cards] + [card_id.id for
                                                                                                       card_id in
                                                                                                       self.flop.cards] + [
                             card_id.id for card_id in self.players_list[1].cards]
            self.determined_winner = self.eval_winner(eval_cards)
            if self.players_list[0].chips == 0:
                self.overall_winner = "Player 2"
            elif self.players_list[1].chips == 0:
                self.overall_winner = "Player 1"
