"""MC1-P2: Optimize a portfolio."""

import math
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import datetime as dt
from util import get_data, plot_data
import scipy.optimize as spo


# This is the function that will be tested by the autograder
# The student must update this code to properly implement the functionality
def optimize_portfolio(sd=dt.datetime(2008,1,1), ed=dt.datetime(2009,1,1), \
    syms=['GOOG','AAPL','GLD','XOM'], gen_plot=False):

    # Read in adjusted closing prices for given symbols, date range
    dates = pd.date_range(sd, ed)
    prices_all = get_data(syms, dates)  # automatically adds SPY
    prices_all.fillna(method="ffill",inplace=True)
    prices_all.fillna(method="bfill",inplace=True)
    prices = prices_all[syms]  # only portfolio symbols
    prices_SPY = prices_all['SPY']  # only SPY, for comparison later

    # find the allocations for the optimal portfolio
    # note that the values here ARE NOT meant to be correct for a test case
    allocs = find_allocations(prices, len(syms)) # add code here to find the allocations

    # Get daily portfolio value
    port_val = compute_portfolio_values(prices, allocs, 1) # add code here to compute daily portfolio values

    cr, adr, sddr, sr = compute_portfolio_stats(port_val) # add code here to compute stats

    # Compare daily portfolio value with SPY using a normalized plot
    if gen_plot:
        # add code to plot here
        prices_SPY = prices_SPY/prices_SPY.ix[0,:]
        df_temp = pd.concat([port_val, prices_SPY], keys=['Portfolio', 'SPY'], axis=1)
        plot_data(df_temp)
        pass

    return allocs, cr, adr, sddr, sr


def min_func_deviation(allocs, prices):
    port_val = compute_portfolio_values(prices, allocs)
    return abs(compute_portfolio_stats(port_val, allocs)[2])  # access volatility


def compute_portfolio_values(df, allocs, sv=1000000):
    normed = df / df.ix[0,:]
    alloced = normed * allocs
    port_val = alloced * sv
    return port_val.sum(axis=1)


def compute_portfolio_stats(prices, allocs=[0.1,0.2,0.3,0.4], rfr=0.0, sf=252.0):
    cr = (prices.ix[-1] / prices.ix[0]) - 1
    daily_ret = get_daily_returns(prices)
    daily_ret = daily_ret.ix[1:] # removed 1st day values which were 0
    adr = daily_ret.mean()
    sddr = daily_ret.std()
    drfr = daily_ret - rfr
    sr = math.sqrt(sf)*((drfr.mean())/sddr)
    return cr, adr, sddr, sr


def get_daily_returns(df):
    df = df / df.shift(1) -1
    df.ix[0] = 0
    return df


def find_allocations(prices, list_size):
    cons = ({'type': 'eq', 'fun': lambda x: np.sum(x) -1}) # add up to 1
    bnds = tuple((0, 1) for x in range(list_size)) # within 0 and 1
    guess = list_size * [1. / list_size, ] # initial value
    opts = spo.minimize(min_func_deviation, guess, args=(prices, ), bounds=bnds, constraints=cons, method='SLSQP', options={'disp': True})
    return opts.x


def test_code():
    # This function WILL NOT be called by the auto grader
    # Do not assume that any variables defined here are available to your function/code
    # It is only here to help you set up and test your code

    # Define input parameters
    # Note that ALL of these values will be set to different values by
    # the autograder!

    # start_date = dt.datetime(2009,1,1)
    # end_date = dt.datetime(2010,1,1)
    start_date = dt.datetime(2008, 6, 1)
    end_date = dt.datetime(2009, 6, 1)
    # symbols = ['GOOG', 'AAPL', 'GLD', 'XOM', 'IBM']
    symbols = ['GLD', 'X', 'IBM']
    # Assess the portfolio
    allocations, cr, adr, sddr, sr = optimize_portfolio(sd = start_date, ed = end_date,\
        syms = symbols, \
        gen_plot = True)

    # Print statistics
    print "Start Date:", start_date
    print "End Date:", end_date
    print "Symbols:", symbols
    print "Allocations:", allocations
    print "Sharpe Ratio:", sr
    print "Volatility (stdev of daily returns):", sddr
    print "Average Daily Return:", adr
    print "Cumulative Return:", cr

if __name__ == "__main__":
    # This code WILL NOT be called by the auto grader
    # Do not assume that it will be called
    test_code()
