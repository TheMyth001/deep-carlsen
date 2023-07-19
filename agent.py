from model import *
from collections import deque
import numpy as np
from position import Position


AGENT_HYPERPARAMS = {
    "replay_buffer_size": 100,
}


class Agent:

    def __init__(self):
        self.n_games = 0
        self.epsilon = 1
        self.buffer = deque(maxlen=AGENT_HYPERPARAMS["replay_buffer_size"])
        self.trainer = None

    def get_action(self, state):
        # todo: implement minimax, alpha beta pruning
        return self, state

    def remember(self, state, action, reward, next_state, done):
        self.buffer.append((state, action, reward, next_state, done))

    def train_short_memory(self, state, action, reward, next_state, done):
        self.trainer.train(state, action, reward, next_state, done)


def train():
    agent = Agent()
    position = Position("1r6/ppp1qkp1/5p1n/3P4/2P1P2p/8/P1P1Q1PP/1R2B1K1 w - - 0 21")
    position.display()
    state = np.array(position.get_state())
    while True:
        # get action
        action = agent.get_action(state)
        # get (s, a, r, s) tuple
        break


if __name__ == '__main__':
    train()
