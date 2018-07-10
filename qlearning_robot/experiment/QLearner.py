"""
Template for implementing QLearner  (c) 2015 Tucker Balch
"""

import numpy as np
import random as rand
import random as rndm
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
        # initilize Q table [[(floats)num_actions]] x 100  ie.  100 rows x 4 columns
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
        self.FILL_VALUE = 0.0001
        self.T_table = np.full(shape=(self.num_states, self.num_actions, self.num_states), fill_value=self.FILL_VALUE, dtype=float)
        self.T_c_table = np.full(shape=(self.num_states, self.num_actions, self.num_states), fill_value=self.FILL_VALUE,
                                 dtype=float)
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

    # def query(self,s_prime,r):
    #     """
    #     @summary: Update the Q table and return an action
    #     @param s_prime: The new state
    #     @param r: The ne state
    #     @returns: The selected action
    #     """
    #     state = self.s
    #     action = self.a
    #
    #     # self.q_tables[state][action] = (1 - self.alpha) * self.q_tables[state][action]\
    #     #                           + self.alpha * (r + self.gamma * self.q_tables[s_prime, np.argmax(self.q_tables[s_prime, :])])
    #
    #
    #     if self.dyna > 0:
    #         self.T_table[state, action]= [state, action ,[2,1]]
    #
    #         p = r + self.gamma * self.q_tables[s_prime, np.argmax(self.q_tables[s_prime, :])]
    #
    #         q = Q.Queue()
    #         if p > 0:
    #             q.put((p, (state, action)))
    #         index = 0
    #
    #         while index < self.dyna and q.qsize() > 0:
    #             p, q_item = q.get()
    #             state = q_item[0]
    #             action = q_item[1]
    #             r = self.T_table[state][action][s_prime]
    #             self.q_tables[state][action] = (1 - self.alpha) * self.q_tables[state][action] \
    #                                            + self.alpha * (r + self.gamma *
    #                                                            self.q_tables[s_prime, np.argmax(self.q_tables[s_prime, :])])
    #             s_prime = state
    #             # np.argmax(self.T_table[:]np)
    #             #
    #             index +=1
    #
    #     # roll dice
    #     # if random_num < rar, roll dice again to choose action
    #     # else get all column(action) values for s_prime and use highest value action
    #     random_num = rand.uniform(0, 1)
    #     if random_num <= self.rar:
    #         action = rand.randint(0, self.num_actions-1)
    #     else:
    #         action = np.argmax(self.q_tables[s_prime, :])
    #     self.rar = self.rar * self.radr
    #
    #     self.s = s_prime
    #     self.a = action
    #     if self.verbose: print "s =", s_prime,"a =",action,"r =",r
    #     return action

    # def query(self, s_prime, r):
    #     """
    #     @summary: Update the Q table and return an action
    #     @param s_prime: The new state
    #     @param r: The ne state
    #     @returns: The selected action
    #     """
    #     state = self.s
    #     action = self.a
    #
    #     prev_reward = self.q_tables[state, action]
    #     reward = \
    #         (1 - self.alpha) * self.q_tables[state, action] \
    #         + self.alpha * (r + self.gamma * self.q_tables[s_prime, np.argmax(self.q_tables[s_prime, :])])
    #     self.q_tables[state, action] = reward
    #
    #     # the model is used to back track the path. only update the model if the reward is higher than last one
    #     if reward > prev_reward:
    #         self.model[s_prime] = state, action
    #
    #     # p is indicating the reward which will be above 0 if reached the goal
    #     p = r + self.gamma * self.q_tables[s_prime, np.argmax(self.q_tables[s_prime, :])]
    #
    #     # store rewards for the state and action pair
    #     self.R_table[state, action] = (1 - self.alpha) * self.R_table[state, action] + self.alpha * r
    #
    #     # start hallucination when it reached the goal for dyna
    #     if self.dyna > 0 and p > 0:
    #         q = Q.Queue()
    #         q.put((p, state))
    #         index = 0
    #         while index < self.dyna and q.qsize() > 0:
    #             p, state = q.get()
    #             s_prime_h = state
    #             if s_prime_h in self.model:
    #                 prev = self.model[s_prime_h]
    #                 self.model.pop(s_prime_h)
    #                 state = prev[0]
    #                 action =prev[1]
    #                 r = self.R_table[state, action]
    #                 p = r + self.gamma * self.q_tables[s_prime_h, np.argmax(self.q_tables[s_prime_h, :])]
    #                 if p > 0:
    #                     q.put((p, (state, action)))
    #
    #                 self.q_tables[state, action] = (1 - self.alpha) * self.q_tables[state, action]\
    #                               + self.alpha * (r + self.gamma * self.q_tables[s_prime_h, np.argmax(self.q_tables[s_prime_h, :])])
    #             index += 1
    #
    #     random_num = rand.uniform(0, 1)
    #     if random_num <= self.rar:
    #         action = rand.randint(0, self.num_actions - 1)
    #     else:
    #         action = np.argmax(self.q_tables[s_prime, :])
    #     self.rar = self.rar * self.radr
    #
    #     self.s = s_prime
    #     self.a = action
    #     if self.verbose: print "s =", s_prime, "a =", action, "r =", r
    #     return action

    def query(self,s_prime,r):
        """
        @summary: Update the Q table and return an action
        @param s_prime: The new state
        @param r: The ne state
        @returns: The selected action
        """
        state = self.s
        action = self.a

        self.q_tables[state, action] = \
            (1 - self.alpha) * self.q_tables[state, action] \
            + self.alpha * (r + self.gamma * self.q_tables[s_prime, np.argmax(self.q_tables[s_prime, :])])

        random_num = rand.uniform(0, 1)
        if random_num <= self.rar:
            action = rand.randint(0, self.num_actions-1)
        else:
            action = np.argmax(self.q_tables[s_prime, :])
        self.rar = self.rar * self.radr

        p = r + self.gamma * self.q_tables[s_prime, np.argmax(self.q_tables[s_prime, :])]
        self.s = s_prime
        self.a = action

        # count occurrence
        self.T_c_table[state, action, s_prime] = self.T_c_table[state, action, s_prime] + 1
        # sum of the s, a combination
        sum_T = self.T_c_table[state, action, :].sum()
        # probability table
        self.T_table[state, action, :] = self.T_c_table[state, action, :] / sum_T
        # reward table
        self.R_table[state, action] = (1 - self.alpha) * self.R_table[state, action] + self.alpha * r

        if p > 0:
            index = 0
            while index < self.dyna:
                # find s candidate for random choice
                # visited = np.where(np.any(self.T_c_table[:] > 1, axis=0))
                # s_candidates = np.concatenate(visited)
                # s = np.random.choice(s_candidates)
                s = rand.randint(0, self.num_states - 1)
                # randomly choose action
                a = rand.randint(0, self.num_actions-1)
                # a = np.argmax(self.R_table[state, :])
                # reward according to the pair
                r = self.R_table[s, a]
                s_prime = np.random.multinomial(1, self.T_table[s, a, :]).max()
                # s_prime = rand.randint(0, self.num_states-1)
                # self.q_tables = self.update_q_table(q_tables=self.q_tables, state=s, action=a, s_prime=s_prime, r=r)
                self.q_tables[s, a] = \
                    (1 - self.alpha) * self.q_tables[s, a] \
                    + self.alpha * (r + self.gamma * self.q_tables[s_prime, np.argmax(self.q_tables[s_prime, :])])
                index +=1




        if self.verbose: print "s =", s_prime,"a =",action,"r =",r
        return action


    def author(self):
        return 'ymiyamoto3'



if __name__=="__main__":
    print "Remember Q from Star Trek? Well, this isn't him"
