import random
import numpy as np
from collections import deque
from poker_agent import PokerAgent
import torch.optim as optim
import torch
import torch.nn as nn


class DQNAgent:
    def __init__(self, input_size, hidden_size, action_size, lr=0.001, gamma=0.99):
        self.model = PokerAgent(input_size, hidden_size, action_size)
        self.target_model = PokerAgent(input_size, hidden_size, action_size)
        self.update_target_model()
        self.optimizer = optim.Adam(self.model.parameters(), lr=lr)
        self.criteria = nn.MSELoss()
        self.memory = deque(maxlen=10000)
        self.gamma = gamma
        self.batch_size = 64
        self.epsilon = 1.0  # Exploration rate
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
        self.action_size = action_size

    def update_target_model(self):
        self.target_model.load_state_dict(self.model.state_dict())

    def remember(self, state, action, reward, next_state, done):
        # Store experience in memory
        self.memory.append((state, action, reward, next_state, done))

    def act(self, state):
        # Epsilon-greedy action selection
        if np.random.rand() <= self.epsilon:
            return random.randrange(self.action_size)
        state_tensor = torch.FloatTensor(state)
        q_values = self.model(state_tensor)
        return torch.argmax(q_values).item()

    def replay(self):
        if len(self.memory) < self.batch_size:
            return

        minibatch = random.sample(self.memory, self.batch_size)

        # Prepare batches
        states = torch.FloatTensor([m[0] for m in minibatch])
        actions = torch.LongTensor([m[1] for m in minibatch]).unsqueeze(1)
        rewards = torch.FloatTensor([m[2] for m in minibatch])
        next_states = torch.FloatTensor([
            np.zeros_like(m[0]) if m[3] is None else m[3] for m in minibatch
        ])
        dones = torch.FloatTensor([m[4] for m in minibatch])

        rewards = rewards / 1000.0
        #print(f"Reward: {rewards} ")
        # Compute current Q values
        q_values = self.model(states).gather(1, actions)

        # Compute next Q values for all next_states
        next_q_values = self.target_model(next_states).max(1)[0].detach()

        # Zero out next Q values where episodes have ended
        next_q_values = next_q_values * (1 - dones)

        # Compute target Q values
        q_targets = rewards + self.gamma * next_q_values

        # Compute loss
        loss = self.criteria(q_values.squeeze(), q_targets)

        # Optimize the model
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

        # Update exploration rate
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
