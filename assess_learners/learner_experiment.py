"""
Test a learner.  (c) 2015 Tucker Balch
"""

import numpy as np
import math

import time

import DTLearner as dt
import sys
import pandas as pd
from BagLearner import BagLearner
import RTLearner as rt
import util
from util import plot_data

if __name__=="__main__":
    if len(sys.argv) != 2:
        print "Usage: python testlearner.py <filename>"
        sys.exit(1)
    f = util.get_learner_data_file(sys.argv[1])
    data = np.genfromtxt(f, delimiter=',')
    if f.name == 'Data/Istanbul.csv':
        data = data[1:, 1:]
    # compute how much of the data is training and testing
    train_rows = int(0.6* data.shape[0])
    test_rows = data.shape[0] - train_rows

    # separate out training and testing data
    trainX = data[:train_rows,0:-1]
    trainY = data[:train_rows,-1]
    testX = data[train_rows:,0:-1]
    testY = data[train_rows:,-1]

    leafSize = 1
    bags = True
    plot = False
    random = True




    if random:
        bag_sublearner = rt.RTLearner
    else:
        bag_sublearner = dt.DTLearner

    if bags:
        learner = BagLearner(learner=bag_sublearner,kwargs={"leaf_size":leafSize},bags=20,boost=False,verbose=False)
    else:
        if random:
            learner = rt.RTLearner(leaf_size=leafSize)
        else:
            learner = dt.DTLearner(leaf_size=leafSize)


    start_time = time.time()


    learner.addEvidence(trainX, trainY) # train it
    print learner.author()




    # evaluate in sample
    train_predY = learner.query(trainX) # get the predictions
    rmse = math.sqrt(((trainY - train_predY) ** 2).sum()/trainY.shape[0])

    dfTrainPred = pd.DataFrame(train_predY)
    dfTrainY = pd.DataFrame(trainY)


    if plot:
        df_temp = pd.concat([dfTrainPred, dfTrainY], keys=['Prediction', 'Actual'], axis=1)
        if bags:
            plot_data(df_temp, title="Leaf Size = "+ str(leafSize) +", In-Sample, Bag Size = 20", xlabel="Dates", ylabel="Values")
        else:
            plot_data(df_temp, title="Leaf Size = " + str(leafSize) +", In-Sample", xlabel="Dates",
                  ylabel="Values")

    print
    if bags:
        print "Leaf Size " + str(leafSize) + ", Bag Size 20" + ", Learner = " + str(bag_sublearner)
    else:
        print "Leaf Size " + str(leafSize) + ", Learner = " + str(learner)
    print
    print "In sample results"
    print "RMSE: ", rmse
    c = np.corrcoef(train_predY, y=trainY)
    print "corr: ", c[0,1]




    # evaluate out of sample
    test_predY = learner.query(testX) # get the predictions
    rmse = math.sqrt(((testY - test_predY) ** 2).sum()/testY.shape[0])


    dfTestPredY = pd.DataFrame(test_predY)
    dfTestY = pd.DataFrame(testY)

    if plot:
        df_temp = pd.concat([dfTestPredY, dfTestY], keys=['Prediction', 'Actual'], axis=1)
        if bags:
            plot_data(df_temp, title="Leaf Size = "+ str(leafSize) +",Out-Of-Sample, Bag Size = 20", xlabel="Dates", ylabel="Values")
        else:
            plot_data(df_temp, title="Leaf Size = "+ str(leafSize) +",Out-Of-Sample", xlabel="Dates", ylabel="Values")


    print
    print "Out of sample results"
    print "RMSE: ", rmse
    c = np.corrcoef(test_predY, y=testY)
    print "corr: ", c[0,1]

    print("--- %s seconds ---" % (time.time() - start_time))