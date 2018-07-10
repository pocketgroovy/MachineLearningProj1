"""
template for generating data to fool learners (c) 2016 Tucker Balch
"""

import numpy as np

# this function should return a dataset (X and Y) that will work
# better for linear regression than decision trees
def best4DT(seed=1489683273):
    np.random.seed(seed)
    X = np.random.random(size = (100,500))*20-10
    Y = X[:, 0] + X[:,1]*2
    return X, Y

def best4LinReg(seed=1489683273):
    np.random.seed(seed)
    X = np.random.random(size = (10,2))*20-10
    Y = X[:, 0] + X[:,1]*2
    return X, Y

def author():
    return 'ymiyamoto3' #Change this to your user ID

if __name__=="__main__":
    print "they call me Tim."
