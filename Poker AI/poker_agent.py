import torch
import torch.nn as nn
import torch.optim as optim


class PokerAgent(nn.Module):
    def __init__(self, input_size, hidden_size, output_size):
        super(PokerAgent, self).__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.relu1 = nn.ReLU()
        self.fc2 = nn.Linear(hidden_size, hidden_size)
        self.relu2 = nn.ReLU()
        self.fc3 = nn.Linear(hidden_size, output_size)  # Output layer

    def forward(self, x):
        x = self.fc1(x)
        x = self.relu1(x)
        x = self.fc2(x)
        x = self.relu2(x)
        x = self.fc3(x)
        return x  # Raw scores (we'll apply softmax or other activation later)
