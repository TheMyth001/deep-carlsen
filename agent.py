from chess import *
from model import *
from collections import deque
import random
import torch
import torch.nn as nn
import torch.optim as optim
from plot import plot


AGENT_HYPERPARAMS = {
    'depth': 5,
    'lr': 0.5,
    'lambda': 0.7,
    'gamma': 0.99,
    'loss': nn.MSELoss()
}


class Agent:
    def __init__(self):
        self.model = DNN()
        self.episodes = 0
        self.epsilon = 0.75
        self.gamma = AGENT_HYPERPARAMS['gamma']
        self.lamda = AGENT_HYPERPARAMS['lambda']
        self.loss = AGENT_HYPERPARAMS['loss']
        self.optimizer = optim.AdamW(self.model.parameters(), lr=AGENT_HYPERPARAMS['lr'])

    def _q_search(self, board):
        # todo
        pass

    def _minimax_search_alpha_beta(self, board, depth, alpha, beta):
        # todo: add move ordering
        side = board.side_to_move
        if depth == 0:
            with torch.no_grad():
                return None, self.model(board.get_state(side)).item() * (1 - 2*side)

        if side == 0:
            # white to move, wants to maximize evaluation.
            best_score = -2.0
            best_move = None
            legals = board.legal_moves(side)
            for move in legals:
                next_board, reward, done = board.apply_move(move)
                if done:
                    if reward == 1:
                        return move, 1.0
                    else:
                        score = 0.0
                else:
                    score = self._minimax_search_alpha_beta(next_board, depth-1, alpha, beta)[1]
                if score > best_score:
                    best_score = score
                    best_move = move
                alpha = max(alpha, score)
                if beta <= alpha:
                    break
            return best_move, best_score

        else:
            # black to move, wants to minimize evaluation.
            best_score = 2.0
            best_move = None
            legals = board.legal_moves(side)
            for move in legals:
                next_board, reward, done = board.apply_move(move)
                if done:
                    if reward == 1:
                        return move, -1.0
                    else:
                        score = 0.0
                else:
                    score = self._minimax_search_alpha_beta(next_board, depth-1, alpha, beta)[1]
                if score < best_score:
                    best_score = score
                    best_move = move
                beta = min(beta, score)
                if beta <= alpha:
                    break
            return best_move, best_score

    def get_action(self, board, greedy=True):
        if greedy and random.random() < self.epsilon:
            move = random.choice(board.legal_moves(board.side_to_move))
            return move, None
        else:
            best_move, evaluation = self._minimax_search_alpha_beta(board, AGENT_HYPERPARAMS['depth'], -2.0, 2.0)
            return best_move, evaluation

    def train(self, states, rewards, next_states, eligibilities, done, losses):
        with torch.no_grad():
            if done:
                td_pred = rewards[-1] - self.model(states[-1])
            else:
                td_pred = rewards[-1] + self.gamma * self.model(next_states[-1]) - self.model(states[-1])

        if states[-1] in eligibilities:
            eligibilities[states[-1]] += 1
        else:
            eligibilities[states[-1]] = 1

        for idx in range(len(states)):
            pred = self.model(states[idx])
            self.optimizer.zero_grad()
            loss = self.loss(td_pred, pred)
            if idx == len(states) - 1:
                losses.append(loss.detach().item())
            loss.backward()
            self.optimizer.step()
            eligibilities[states[-1]] = self.gamma*self.lamda*eligibilities[states[-1]]

    def analyze_performance(self):
        # todo: figure out
        pass


def train():

    agent = Agent()
    losses = deque(maxlen=100)

    while True:

        if agent.episodes % 100 == 0:
            agent.analyze_performance()
            agent.model.save(f'model{int(agent.episodes/100)}.pth')

        board = Board()
        agent.episodes += 1

        states = []
        rewards = []
        next_states = []
        eligibilities = {}

        while True:

            if agent.episodes % 10 == 1:
                board.display()

            states.append(board.get_state(board.side_to_move))
            action, score = agent.get_action(board)
            board, reward, done = board.apply_move(action)
            next_states.append(board.get_state(1 - board.side_to_move))
            rewards.append(reward)

            agent.train(states, rewards, next_states, eligibilities, done, losses)

            if done:
                plot(losses, agent.episodes)
                agent.episodes += 1
                agent.epsilon = 0.75 / int(1 + agent.episodes/200)
                break
                

if __name__ == '__main__':
    train()
