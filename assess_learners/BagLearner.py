import numpy as np

class BagLearner(object):
    def __init__(self, learner, kwargs = {}, bags = 20, boost = False, verbose = False):
        self.learner_array = []
        for i in range(0, bags):
            self.learner_array.append(learner(**kwargs))
        self.kwargs = kwargs
        self.verbose = verbose
        self.bags = bags


    def addEvidence(self, dataX, dataY):
        for learner in self.learner_array:
            rand_indicex = np.random.randint(dataX.shape[0], size=dataX.shape[0])
            rand_dataX = dataX[rand_indicex]
            rand_dataY = dataY[rand_indicex]
            learner.addEvidence(rand_dataX, rand_dataY)


    def query(self, Xtest):
        if len(self.learner_array) == 1:
            return self.query_for_one(Xtest)
        result_array = np.empty((len(self.learner_array), Xtest.shape[0]))
        index = 0
        for learner in self.learner_array:
            result_array[index] = learner.query(Xtest)
            index += 1
        predY = result_array.mean(axis=0)
        return predY


    def query_for_one(self, Xtest):
        return self.learner_array[0].query(Xtest)

    def author(self):
        return 'ymiyamoto3'