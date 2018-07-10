"""
Template for implementing StrategyLearner  (c) 2016 Tucker Balch
"""
# Yoshi Miyamoto ymiyamoto3

import datetime as dt
import pandas as pd

from BagLearner import BagLearner
from RTLearner import RTLearner
from indicators import indicators


class StrategyLearner(object):

    # constructor
    def __init__(self, N_day=221, YSELL=-0.02, YBUY=0.08, leaf=31, bags=40, verbose=False, impact=0.0):
        self.verbose = verbose
        self.impact = impact
        self.N_day = N_day
        self.YSELL = YSELL
        self.YBUY = YBUY
        self.leaf = leaf
        self.bags = bags

    def addEvidence(self, symbol = "IBM", \
        sd=dt.datetime(2008,1,1), \
        ed=dt.datetime(2009,1,1), \
        sv = 10000):
        # add your code to do learning here
        trainX, normed_price_df = get_standardized_indicator_dataX_and_price(symbol, sd, ed)

        trainY = get_dataY(normed_price_df, self.N_day, self.YSELL, self.YBUY)

        self.learner = BagLearner(learner=RTLearner, kwargs={"leaf_size": self.leaf}, bags=self.bags, boost=False, verbose=False)
        self.learner.addEvidence(trainX.values, trainY.values)


    # this method should use the existing policy and test it against new data
    def testPolicy(self, symbol = "IBM", \
        sd=dt.datetime(2009,1,1), \
        ed=dt.datetime(2010,1,1), \
        sv = 10000):

        testX, normed_price_df = get_standardized_indicator_dataX_and_price(symbol, sd, ed)

        result = self.learner.query(testX.values)

        status_df = pd.DataFrame(data=result, index=normed_price_df.index, columns=['Classified'])

        trades = pd.DataFrame(columns=['Date','Shares'], index=normed_price_df.index)

        first_purchase = True
        prev_order_type = ''
        holding = 0
        for day in trades.ix[:, :].index:
            if first_purchase:
                shares = 1000
            else:
                shares = 2000
            if status_df.ix[day, 'Classified'] < 0 and (holding < 0 or first_purchase) and \
                    (prev_order_type == '' or prev_order_type != 'BUY'):
                trades.loc[day] = pd.Series({'Date': day, 'Shares': shares})
                holding += shares
                first_purchase = False
                prev_order_type = 'BUY'
            elif status_df.ix[day, 'Classified'] > 0 and (holding > 0 or first_purchase) and \
                    (prev_order_type == '' or prev_order_type != 'SELL'):
                trades.loc[day] = pd.Series({'Date': day, 'Shares': -shares})
                holding -= shares
                first_purchase = False
                prev_order_type = 'SELL'

        shares = 2000
        if trades.ix[-1].isnull().any():
            if prev_order_type == 'BUY':
                shares *= -1
            trades.ix[-1] = pd.Series(
                {'Date': trades.index[-1], 'Shares': shares})

        # reorganize the index numbers to make Date as index
        trades = reset_index_drop_na(trades)

        return trades


def get_standardized_indicator_dataX_and_price(symbol, sd, ed):
    normed_price_df, price_sma_df, top_band, bottom_band, volatility, momentum = indicators(symbol, sd, ed, plot=False)

    stdz_sma = (price_sma_df - price_sma_df.mean()) / price_sma_df.std()
    stdz_top_band = (top_band - top_band.mean()) / top_band.std()
    trainX = pd.concat([stdz_sma, stdz_top_band], axis=1)

    stdz_bottom_band = ((bottom_band - bottom_band.mean()) / bottom_band.std())
    trainX = pd.concat([trainX, stdz_bottom_band], axis=1)


    stdz_volatility = ((volatility - volatility.mean()) / volatility.std())
    trainX = pd.concat([trainX, stdz_volatility], axis=1)

    return trainX, normed_price_df


def get_dataY(normed_price_df, N, YSELL, YBUY):
    trainY = (normed_price_df / normed_price_df.shift(N)) - 1.0
    trainY[trainY < YSELL] = -1
    trainY[trainY > YBUY] = 1
    trainY[(trainY >= YSELL) & (trainY <= YBUY)] = 0
    return trainY


def reset_index_drop_na(df):
    df.dropna(inplace=True)
    df.reset_index(drop=True, inplace=True)
    df.set_index('Date', inplace=True)
    return df


if __name__=="__main__":
    print "One does not simply think up a strategy"
