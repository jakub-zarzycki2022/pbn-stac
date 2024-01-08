import logging
import math
from collections import defaultdict
import torch

import numpy as np

EPS = 1e-8


class MCTS:
    """
    This class handles the MCTS tree.
    """

    def __init__(self, env, model):
        self.env = env
        self.model = model
        self.cpuct = 1
        self.args = None
        self.Qsa = {}  # stores Q values for s,a (as defined in the paper)
        self.Nsa = defaultdict(int)  # stores #times edge s,a was visited
        self.Ns = {}  # stores #times board s was visited
        self.Ps = {}  # stores initial policy (returned by neural net)

        self.Es = {}  # stores game.getGameEnded ended for board s
        self.Vs = {}  # stores game.getValidMoves for board s

    def get_action_prob(self, state, target, temp=1):
        """
        This function performs numMCTSSims simulations of MCTS starting from
        canonicalBoard.

        Returns:
            probs: a policy vector where the probability of the ith action is
                   proportional to Nsa[(s,a)]**(1./temp)
        """
        for i in range(10):
            self.search(state, target, self.env.horizon)

        s = tuple(state)
        counts = [self.Nsa[(s, a)] for a in range(len(s) + 1)]

        if temp == 0:
            bestAs = np.array(np.argwhere(counts == np.max(counts))).flatten()
            bestA = np.random.choice(bestAs)
            probs = [0] * len(counts)
            probs[bestA] = 1
            return probs

        counts = [x ** (1. / temp) for x in counts]
        counts_sum = float(sum(counts))
        probs = [x / counts_sum for x in counts]
        return probs

    def search(self, state, target, max_depth=10):
        """
        This function performs one iteration of MCTS. It is recursively called
        till a leaf node is found. The action chosen at each node is one that
        has the maximum upper confidence bound as in the paper.

        Once a leaf node is found, the neural network is called to return an
        initial policy P and a value v for the state. This value is propagated
        up the search path. In case the leaf node is a terminal state, the
        outcome is propagated up the search path. The values of Ns, Nsa, Qsa are
        updated.

        NOTE: the return values are the negative of the value of the current
        state. This is done since v is in [-1,1] and if v is the value of a
        state for the current player, then its value is -v for the other player.

        Returns:
            v: the value of the current state
        """

        if max_depth <= 0:
            return -1

        max_depth -= 1

        state = tuple(state)
        target = tuple(target)

        if state == target:
            self.Es[state] = 1
            return 1

        if state not in self.Ps:
            # leaf node
            self.Ps[state], v = self.model.predict(state, target)
            sum_Ps_s = torch.sum(self.Ps[state])
            self.Ps[state] /= sum_Ps_s  # renormalize

            self.Ns[state] = 0
            return v

        cur_best = float('-inf')
        best_act = -1

        # pick the action with the highest upper confidence bound
        for a in range(len(state) + 1):
            if (state, a) in self.Qsa:
                u = self.Qsa[(state, a)] + \
                    self.cpuct * \
                    self.Ps[state][a] * \
                    math.sqrt(self.Ns[state]) / \
                    (1 + self.Nsa[(state, a)])
            else:
                u = self.cpuct * self.Ps[state][a] * math.sqrt(self.Ns[state] + EPS)

            if u > cur_best:
                cur_best = u
                best_act = a

        a = best_act
        next_state = self.env.get_next_state(state, [a])

        if next_state == state:
            max_depth /= 2

        v = self.search(next_state, target, max_depth)

        if next_state == state:
            v *= .9

        if (state, a) in self.Qsa:
            self.Qsa[(state, a)] = (self.Nsa[(state, a)] * self.Qsa[(state, a)] + v) / (self.Nsa[(state, a)] + 1)
            self.Nsa[(state, a)] += 1
        else:
            self.Qsa[(state, a)] = v
            self.Nsa[(state, a)] = 1

        self.Ns[state] += 1
        return v
