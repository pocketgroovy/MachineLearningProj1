"""
Template for implementing QLearner  (c) 2015 Tucker Balch
"""

import numpy as np
import random as rand
import Queue as Q

class QLearner(object):

    def __init__(self, \
        num_states=100, \
        num_actions = 4, \
        alpha = 0.2, \
        gamma = 0.9, \
        rar = 0.5, \
        radr = 0.99, \
        dyna = 0, \
        verbose = False):
        self.verbose = verbose
        self.num_actions = num_actions
        self.num_states = num_states
        self.s = 0
        self.a = 0
        self.q_tables = np.zeros(shape=(num_states, num_actions))
        self.alpha = alpha
        self.gamma = gamma
        self.rar = rar
        self.radr = radr
        self.dyna = dyna
        self.model = dict({})

        self.R_table = np.full(shape=(self.num_states, self.num_actions), fill_value=-0.1, dtype=float)

    def querysetstate(self, s):
        """
        @summary: Update the state without updating the Q-table
        @param s: The new state
        @returns: The selected action

        """
        random_num = rand.uniform(0, 1)
        if random_num <= self.rar:
            action = rand.randint(0, self.num_actions-1)
        else:
            action = np.argmax(self.q_tables[s, :])

        self.s = s
        self.a = action
        if self.verbose: print "s =", s,"a =",action
        return action

    def query(self, s_prime, r):
        """
        @summary: Update the Q table and return an action
        @param s_prime: The new state
        @param r: The ne state
        @returns: The selected action
        """
        state = self.s
        action = self.a

        prev_reward = self.q_tables[state, action]
        reward = \
            (1 - self.alpha) * self.q_tables[state, action] \
            + self.alpha * (r + self.gamma * self.q_tables[s_prime, np.argmax(self.q_tables[s_prime, :])])
        self.q_tables[state, action] = reward

        # the model is used to back track the path. only update the model if the reward is higher than last one
        if reward > prev_reward:
            self.model[s_prime] = state, action

        # p is indicating the reward which will be above 0 if reached the goal
        p = r + self.gamma * self.q_tables[s_prime, np.argmax(self.q_tables[s_prime, :])]

        # store rewards for the state and action pair
        self.R_table[state, action] = (1 - self.alpha) * self.R_table[state, action] + self.alpha * r

        # start hallucination when it reached the goal for dyna
        if self.dyna > 0 and p > 0:
            q = Q.Queue()
            q.put((p, state))
            index = 0
            while index < self.dyna and q.qsize() > 0:
                p, state = q.get()
                s_prime_h = state
                if s_prime_h in self.model:
                    prev = self.model[s_prime_h]
                    self.model.pop(s_prime_h)
                    state = prev[0]
                    action =prev[1]
                    r = self.R_table[state, action]
                    p = r + self.gamma * self.q_tables[s_prime_h, np.argmax(self.q_tables[s_prime_h, :])]
                    if p > 0:
                        q.put((p, (state, action)))

                    self.q_tables[state, action] = (1 - self.alpha) * self.q_tables[state, action]\
                                  + self.alpha * (r + self.gamma * self.q_tables[s_prime_h, np.argmax(self.q_tables[s_prime_h, :])])
                index += 1

        random_num = rand.uniform(0, 1)
        if random_num <= self.rar:
            action = rand.randint(0, self.num_actions - 1)
        else:
            action = np.argmax(self.q_tables[s_prime, :])
        self.rar = self.rar * self.radr

        self.s = s_prime
        self.a = action
        if self.verbose: print "s =", s_prime, "a =", action, "r =", r
        return action

    def author(self):
        return 'ymiyamoto3'

if __name__=="__main__":
    print "Remember Q from Star Trek? Well, this isn't him"
