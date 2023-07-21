from model import *
from collections import deque
import numpy as np
import torch
from position import Position


AGENT_HYPERPARAMS = {
    'replay_buffer_size': 100,
    'depth': 3,
}


class Agent:

    def __init__(self):
        self.model = DNN()
        self.n_games = 0
        self.epsilon = 1
        self.buffer = deque(maxlen=AGENT_HYPERPARAMS["replay_buffer_size"])
        self.trainer = None

    def _q_search(self, position):
        # todo
        pass

    def _minimax_search(self, position, depth):
        # todo
        # if position is won for the moving side :
        # return 1
        # else if position is won for the non - moving side :
        # return -1
        # else if position is drawn :
        # return 0
        # if depth == 0:
        # return evaluate ( position )
        return self, position, depth

    def get_action(self, position, state):
        # searched = {position: state}
        move = self._minimax_search(state, AGENT_HYPERPARAMS['depth'])
        return move

    def remember(self, state, action, reward, next_state, done):
        self.buffer.append((state, action, reward, next_state, done))

    def train(self, state, reward, next_state, done):
        self.trainer.train(state, reward, next_state, done)


def train():
    agent = Agent()
    position = Position()
    position.display()
    state = torch.from_numpy(np.array(position.get_state()).astype(np.float32))
    i = 1
    print("="*20)
    print(f"playing game: {i}")
    while True:
        action = agent.get_action(position, state)
        position = position.apply_move(action)
        next_state = position.get_state()

        # todo: add a method to Position class to get reward and done
        done = False
        reward = 0

        agent.train(state, reward, next_state, done)

        if done:
            position = Position()
            state = torch.from_numpy(np.array(position.get_state()).astype(np.float32))
            i += 1
            print(f"playing game: {i}")
        else:
            state = next_state

        if i % 100 == 1:
            print("> saving model")
            agent.model.save()
            print("> analyzing performance")
            # todo: figure out and use STS
            print(">> scored x out of y")
            print("="*20)


if __name__ == '__main__':
    train()
