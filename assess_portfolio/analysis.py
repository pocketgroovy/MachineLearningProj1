"""Analyze a portfolio."""
import math
import pandas as pd
import numpy as np
import datetime as dt
from util import get_data, plot_data

# This is the function that will be tested by the autograder
# The student must update this code to properly implement the functionality
def assess_portfolio(sd = dt.datetime(2008,1,1), ed = dt.datetime(2009,1,1), \
    syms = ['GOOG','AAPL','GLD','XOM'], \
    allocs=[0.1,0.2,0.3,0.4], \
    sv=1000000, rfr=0.0, sf=252.0, \
    gen_plot=False):

    # Read in adjusted closing prices for given symbols, date range
    dates = pd.date_range(sd, ed)
    prices_all = get_data(syms, dates)  # automatically adds SPY
    prices_all.fillna(method="ffill",inplace=True)
    prices_all.fillna(method="bfill",inplace=True)
    prices = prices_all[syms]  # only portfolio symbols
    prices_SPY = prices_all['SPY']  # only SPY, for comparison later

    # Get daily portfolio value
    port_val = compute_portfolio_values(prices, allocs, sv) # add code here to compute daily portfolio values

    # Get portfolio statistics (note: std_daily_ret = volatility)
    cr, adr, sddr, sr = compute_portfolio_stats(port_val, allocs, rfr, sf)   #[ 0.25, 0.001, 0.0005, 2.1] # add code here to compute stats

    # Compare daily portfolio value with SPY using a normalized plot
    if gen_plot:
        # add code to plot here
        df_temp = pd.concat([port_val, prices_SPY], keys=['Portfolio', 'SPY'], axis=1)
        plot_data(df_temp)
        pass

    # Add code here to properly compute end value
    ev = port_val[-1]
    return cr, adr, sddr, sr, ev

def compute_portfolio_values(df, allocs=[0.1,0.2,0.3,0.4], sv=1000000):
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

def test_code():
    # This code WILL NOT be tested by the auto grader
    # It is only here to help you set up and test your code

    # Define input parameters
    # Note that ALL of these values will be set to different values by
    # the autograder!
    start_date = dt.datetime(2009,1,1)
    end_date = dt.datetime(2010,1,1)
    symbols = ['GOOG', 'AAPL', 'GLD', 'XOM']
    allocations = [0.2, 0.3, 0.4, 0.1]
    start_val = 1000000
    risk_free_rate = 0.0
    sample_freq = 252

    # Assess the portfolio
    cr, adr, sddr, sr, ev = assess_portfolio(sd = start_date, ed = end_date,\
        syms = symbols, \
        allocs = allocations,\
        sv = start_val, \
        gen_plot = False)

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
    test_code()
