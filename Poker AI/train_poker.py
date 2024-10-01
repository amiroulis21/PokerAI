from poker_env import SimplePokerEnv
from dqn import DQNAgent
import numpy as np
import torch


def preprocess_state(state):
    # Convert state dictionary to a flat numpy array
    hand = state['hand']
    community = state['community']
    pot = [state['pot']]
    bets = state['bets']
    current_player = [state['current_player']]

    # Normalize the card values (0-51) to a range [0, 1]
    hand = np.array(hand) / 51.0
    community = np.array(community + [0] * (5 - len(community))) / 51.0  # Pad to 5 cards

    # Normalize pot and bets
    pot = np.array(pot) / 100.0
    bets = np.array(bets) / 100.0

    state_vector = np.concatenate([hand, community, pot, bets, current_player])
    return state_vector


def train_agents(episodes=1000):
    env = SimplePokerEnv()
    input_size = 2 + 5 + 1 + 2 + 1  # hand(2) + community(5) + pot(1) + bets(2) + current_player(1)
    hidden_size = 128
    action_size = 3  # Actions: Fold, Check/Call, Bet/Raise

    agent0 = DQNAgent(input_size, hidden_size, action_size)
    agent1 = DQNAgent(input_size, hidden_size, action_size)

    for episode in range(episodes):
        state = env.reset()
        done = False
        while not done:
            current_player = state['current_player']
            state_vector = preprocess_state(state)
            if current_player == 0:
                action = agent0.act(state_vector)
            else:
                action = agent1.act(state_vector)

            next_state, reward, done = env.step(action)

            if done:
                next_state_vector = None
            else:
                next_state_vector = preprocess_state(next_state)

            # Agents store experiences and learn
            if current_player == 0:
                agent0.remember(state_vector, action, reward[0], next_state_vector, done)
                agent0.replay()
            else:
                agent1.remember(state_vector, action, reward[1], next_state_vector, done)
                agent1.replay()

            state = next_state if next_state is not None else state

        # Update target networks periodically
        if episode % 10 == 0:
            agent0.update_target_model()
            agent1.update_target_model()

        if episode % 100 == 0:
            print(f"Episode {episode}, Epsilon {agent0.epsilon}")

    # Save models
    torch.save(agent0.model.state_dict(), 'agent0_model.pth')
    torch.save(agent1.model.state_dict(), 'agent1_model.pth')


if __name__ == '__main__':
    train_agents(episodes=1000)
