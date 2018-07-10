import numpy as np

from BagLearner import BagLearner
from LinRegLearner import LinRegLearner


class InsaneLearner(object):

    def __init__(self, verbose = False):
        self.bags_array = []
        self.num_of_bag = 20
        self.verbose = verbose
        self.num_of_learner = 20
        self.learner = LinRegLearner
        self.boost = False
        for i in range(0, self.num_of_bag):
            self.bags_array.append(BagLearner(learner=self.learner, bags=self.num_of_learner, boost=self.boost))


    def author(self):
        return 'ymiyamoto3'


    def addEvidence(self, trainX, trainY):
        for bag in self.bags_array:
            bag.addEvidence(trainX, trainY)


    def query(self, Xtest):
        my_array = np.empty((len(self.bags_array), Xtest.shape[0]))
        index = 0
        for bag in self.bags_array:
            my_array[index] = bag.query(Xtest)
            index += 1
        predY = my_array.mean(axis=0)
        return predY