from poker_env import SimplePokerEnv
from dqn import DQNAgent
from settings import *
import numpy as np
import torch
import pygame, pygame_widgets


def preprocess_state(state):
    # Convert state dictionary to a flat numpy array
    hand = state['hand']
    community = state['community']
    pot = [state['pot']]
    bets = state['bets']
    current_player = [state['current_player']]
    chip_stacks = state['chip_stacks']
    phase = [state['phase']]
    last_actions = state['last_actions']


    # Normalize the card values (0-51) to a range [0, 1]
    hand = np.array(hand) / 51.0
    community = np.array(community + [0] * (3 - len(community))) / 51.0

    # Normalize pot and bets
    pot = np.array(pot) / 100.0
    bets = np.array(bets) / 100.0
    chip_stacks = np.array(chip_stacks) / 1000.0

    # Convert last actions (None to -1, 0: Fold, 1: Check/Call, 2: Bet/Raise)
    action_mapping = {None: -1, 0: 0, 1: 1, 2: 2, 3: 3}
    last_actions = [action_mapping[a] for a in last_actions]


    state_vector = np.concatenate([hand, community, pot, bets, chip_stacks, current_player, phase, last_actions])
    return state_vector


def train_agents(episodes=1000):
    env = SimplePokerEnv()

    input_size = 14
    hidden_size = 128
    action_size = 4  # Actions: Fold, Check/Call, Bet, Raise

    agent0 = DQNAgent(input_size, hidden_size, action_size)
    agent1 = DQNAgent(input_size, hidden_size, action_size)

    for episode in range(episodes):
        env.reset()
        env.game.hand.dealer.deal_hole_cards()
        env.deal_hand()
        env.game.ante_up()
        #env.game.hand.update()
        done = False

        state = env.get_state()

        while not done:

            current_player = state['current_player']
            state_vector = preprocess_state(state)
            #Loop act and step
            #step returns illegal action, big negative reward
            next_state = []
            if not env.illegal_actions.__contains__(1):
                if current_player == 0:
                    action = agent0.act(state_vector)
                else:
                    action = agent1.act(state_vector)

                next_state, reward, done = env.step(action, False)
            else:
                next_state, reward, done = env.resolve_game()
            #keep tally of reward
            #print(f"Reward:{reward}")
            #if action was illegal
            #next_state = state

            if done:
                next_state_vector = None
            else:
                check = 1
                next_state_vector = preprocess_state(next_state)

            # Agents store experiences and learn
            if current_player == 0:
                agent0.remember(state_vector, action, reward[0], next_state_vector, done)
                agent0.replay()
            else:
                agent1.remember(state_vector, action, reward[1], next_state_vector, done)
                agent1.replay()

            state = next_state if next_state is not None else state

            if env.is_game_over():
                done = True
                env.game.p1.chips = 1000
                env.game.p2.chips = 1000
            #env.game.screen.fill(BG_COLOR)
            #env.game.hand.update()
            #pygame.display.update()
            #env.game.clock.tick(FPS)

        # Update target networks periodically
        if episode % 10 == 0:
            agent0.update_target_model()
            agent1.update_target_model()

        if episode % 100 == 0:
            print(f"Episode {episode}, Epsilon {agent0.epsilon}")




    # Save models
    torch.save(agent0.model.state_dict(), 'agent0_model_%d.pth'%episodes)
    torch.save(agent1.model.state_dict(), 'agent1_model_%d.pth'%episodes)
    #self.agent.model.load_state_dict(torch.load('agent1_model.pth'))


if __name__ == '__main__':
    train_agents(episodes=1000)
