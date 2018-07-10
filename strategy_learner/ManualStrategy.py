# Yoshi Miyamoto ymiyamoto3


import datetime as dt
import math

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import marketsimcode as market
from indicators import indicators
from util import get_data


def testPolicy(symbol='JPM', sd=dt.datetime(2010,1,1), ed=dt.datetime(2012,12,31), sv = 100000):
    normed_price_df, price_sma_df, top_band, bottom_band, volatility, momentum = indicators(symbol, sd, ed, plot=False)
    normed_price_df = normed_price_df.ix[sd:]
    price_index = get_price_index(symbol, sd, ed)
    order_table = pd.DataFrame(columns=['Date','Symbol','Order','Shares'], index=price_index.index)
    # positive in price_movement = buy in previous day, negative = sell in previous day
    # first day, only allowed for +- 1000 shares holding
    first_purchase = True
    prev = normed_price_df.ix[0, 'Price']
    prev_day = normed_price_df.index[0]

    sma_overbought = 1.03
    sma_oversold = 1.02

    volat_overbought = 0.11
    volat_oversold = -0.09

    # mom_overbought = 0.004
    # mom_oversold = -0.11
    # order_table, prev_order_type = apply_momentum(oversold=mom_oversold, overbought=mom_overbought,
    #                                               price_df=normed_price_df,
    #                                               momentum_df=momentum, order_table=order_table, symbol=symbol)

    order_table, prev_order_type = apply_bollinger_bands(prev_value=prev, prev_day=prev_day, symbol=symbol,
                                                         price=normed_price_df,
                                                         order_table=order_table, top_band=top_band,
                                                         bottom_band=bottom_band)

    order_table, prev_order_type = apply_price_sma_ratio(oversold=sma_oversold, overbought=sma_overbought,
                                                         order_table=order_table,
                                                         price_sma_df=price_sma_df, symbol=symbol)

    order_table, prev_order_type = apply_volatility(oversold=volat_oversold, overbought=volat_overbought, order_table=order_table,
                                                    volatility_df=volatility, symbol=symbol)

    # insert dummy order for last day if not exist already
    shares = 2000
    if order_table.ix[-1].isnull().any():
        if prev_order_type == 'BUY':
            order_type = 'SELL'
        else:
            order_type = 'BUY'
    else:
        order_type = order_table.ix[ed, 'Order']
        if prev_order_type == order_type:
            if prev_order_type == 'BUY':
                order_type = 'SELL'
            else:
                order_type = 'BUY'

    order_table.ix[-1] = pd.Series({'Date': order_table.index[-1], 'Symbol': symbol, 'Order': order_type, 'Shares': shares})

    # reorganize the index numbers to be Date as index
    order_table = reset_index_drop_na(order_table)

    return order_table


def apply_bollinger_bands(prev_value, prev_day, symbol, price, order_table, top_band, bottom_band):
    first_purchase = True
    prev_order_type = ''
    holding = 0
    for day in order_table.ix[1:,:].index:
        if not order_table.ix[prev_day].isnull().any():
            prev_day_order_type = order_table.ix[prev_day, 'Order']
            if prev_order_type != '' and prev_order_type == prev_day_order_type:
                order_table.ix[prev_day] = np.nan
                prev_value = price.ix[day, 'Price']
                prev_day = day
                continue
            if order_table.ix[prev_day, 'Shares'] == 1000:
                if not first_purchase:
                    order_table.ix[day, 'Shares'] = 2000
                else:
                    first_purchase = False
            if order_table.ix[prev_day, 'Order'] == 'BUY':
                holding = 1000
                prev_order_type = 'BUY'
            elif order_table.ix[prev_day, 'Order'] == 'SELL':
                holding = -1000
                prev_order_type = 'SELL'
            prev_value = price.ix[day, 'Price']
            prev_day = day
            continue
        if first_purchase:
            shares = 1000
        else:
            shares = 2000

        if bottom_band.ix[day, 'Bottom Band'] > price.ix[day, 'Price'] and bottom_band.ix[prev_day, 'Bottom Band'] < prev_value \
                and (holding < 0 or first_purchase) and (prev_order_type == '' or prev_order_type != 'BUY'):
            order_table.loc[prev_day] = pd.Series({'Date':prev_day, 'Symbol':symbol, 'Order':'BUY', 'Shares':shares})
            holding += shares
            first_purchase = False
            prev_order_type = 'BUY'
        elif top_band.ix[day, 'Top Band'] > price.ix[day, 'Price'] and top_band.ix[prev_day, 'Top Band'] < prev_value \
                and (holding > 0 or first_purchase) and (prev_order_type == '' or prev_order_type != 'SELL'):
            order_table.loc[prev_day] = pd.Series({'Date':prev_day, 'Symbol':symbol, 'Order':'SELL', 'Shares':shares})
            holding -= shares
            first_purchase = False
            prev_order_type = 'SELL'
        prev_value = price.ix[day, 'Price']
        prev_day = day
    return order_table, prev_order_type


def apply_price_sma_ratio(oversold, overbought, order_table, price_sma_df, symbol):
    holding = 0
    first_purchase = True
    prev_order_type = ''
    for day in order_table.index:
        if not order_table.ix[day].isnull().any():
            curr_order_type = order_table.ix[day, 'Order']
            if prev_order_type != '' and prev_order_type == curr_order_type:  #if already the same order type exists, cancels it so that previous order will be in effect
                order_table.ix[day] = np.nan
                continue

            if order_table.ix[day, 'Shares'] == 1000:
                if not first_purchase:
                    order_table.ix[day, 'Shares'] = 2000
                else:
                    first_purchase = False
            if order_table.ix[day, 'Order'] == 'BUY':
                holding = 1000
                prev_order_type = 'BUY'

            elif order_table.ix[day, 'Order'] == 'SELL':
                holding = -1000
                prev_order_type = 'SELL'
            continue

        if first_purchase:
            shares = 1000
        else:
            shares = 2000
        if price_sma_df.ix[day, 'Price/SMA'] < oversold and (holding < 0 or first_purchase) and \
                (prev_order_type == '' or prev_order_type != 'BUY'):
            order_table.loc[day] = pd.Series({'Date':day, 'Symbol':symbol, 'Order':'BUY', 'Shares':shares})
            holding += shares
            first_purchase = False
            prev_order_type = 'BUY'
        elif price_sma_df.ix[day, 'Price/SMA'] > overbought and (holding > 0 or first_purchase) and \
                (prev_order_type == '' or prev_order_type != 'SELL'):
            order_table.loc[day] = pd.Series({'Date':day, 'Symbol':symbol, 'Order':'SELL', 'Shares':shares})
            holding -= shares
            first_purchase = False
            prev_order_type = 'SELL'
    return order_table, prev_order_type


def apply_volatility(oversold, overbought, order_table, volatility_df, symbol):
    holding = 0
    first_purchase = True
    prev_order_type = ''
    for day in order_table.index:
        if not order_table.ix[day].isnull().any():
            curr_order_type = order_table.ix[day, 'Order']
            if prev_order_type != '' and prev_order_type == curr_order_type:
                order_table.ix[day] = np.nan
                continue

            if order_table.ix[day, 'Shares'] == 1000:
                if not first_purchase:
                    order_table.ix[day, 'Shares'] = 2000
                else:
                    first_purchase = False
            if order_table.ix[day, 'Order'] == 'BUY':
                holding = 1000
                prev_order_type = 'BUY'

            elif order_table.ix[day, 'Order'] == 'SELL':
                holding = -1000
                prev_order_type = 'SELL'
            continue

        if first_purchase:
            shares = 1000
        else:
            shares = 2000
        if volatility_df.ix[day, 'Volatility'] < oversold and (holding < 0 or first_purchase) and \
                (prev_order_type == '' or prev_order_type != 'BUY'):
            order_table.loc[day] = pd.Series({'Date':day, 'Symbol':symbol, 'Order':'BUY', 'Shares':shares})
            holding += shares
            first_purchase = False
            prev_order_type = 'BUY'
        elif volatility_df.ix[day, 'Volatility'] > overbought and (holding > 0 or first_purchase) and \
                (prev_order_type == '' or prev_order_type != 'SELL'):
            order_table.loc[day] = pd.Series({'Date':day, 'Symbol':symbol, 'Order':'SELL', 'Shares':shares})
            holding -= shares
            first_purchase = False
            prev_order_type = 'SELL'
    return order_table, prev_order_type


def apply_momentum(oversold, overbought, price_df,  momentum_df, order_table, symbol):
    holding = 0
    first_purchase = True
    prev_order_type = ''
    for day in order_table.index:
        if not order_table.ix[day].isnull().any():
            curr_order_type = order_table.ix[day, 'Order']
            if prev_order_type != '' and prev_order_type == curr_order_type:
                order_table.ix[day] = np.nan
                continue

            if order_table.ix[day, 'Shares'] == 1000:
                if not first_purchase:
                    order_table.ix[day, 'Shares'] = 2000
                else:
                    first_purchase = False
            if order_table.ix[day, 'Order'] == 'BUY':
                holding = 1000
                prev_order_type = 'BUY'

            elif order_table.ix[day, 'Order'] == 'SELL':
                holding = -1000
                prev_order_type = 'SELL'
            continue

        if first_purchase:
            shares = 1000
        else:
            shares = 2000
        if (momentum_df.ix[day, 'Momentum'] - price_df.ix[day, 'Price']) < oversold and (holding < 0 or first_purchase) and \
                (prev_order_type == '' or prev_order_type != 'BUY'):
            order_table.loc[day] = pd.Series({'Date':day, 'Symbol':symbol, 'Order':'BUY', 'Shares':shares})
            holding += shares
            first_purchase = False
            prev_order_type = 'BUY'
        elif (momentum_df.ix[day, 'Momentum']- price_df.ix[day, 'Price']) > overbought and (holding > 0 or first_purchase) and \
                (prev_order_type == '' or prev_order_type != 'SELL'):
            order_table.loc[day] = pd.Series({'Date':day, 'Symbol':symbol, 'Order':'SELL', 'Shares':shares})
            holding -= shares
            first_purchase = False
            prev_order_type = 'SELL'
    return order_table, prev_order_type


def get_price_index(symbol='JPM', sd=dt.datetime(2010,1,1), ed=dt.datetime(2012,12,31)):
    dates = pd.date_range(sd, ed)
    price = get_data([symbol], dates, addSPY=True, colname='Adj Close')
    del price['SPY'] # drop spy
    return price


def reset_index_drop_na(df):
    df.dropna(inplace=True)
    df.reset_index(drop=True, inplace=True)
    df.set_index('Date')
    return df


def get_benchmark_df(symbol, index, ed, shares=1000):
    order_table = pd.DataFrame(columns=['Date','Symbol','Order','Shares'], index=index)
    order_table.iloc[0] = pd.Series({'Date': index[0], 'Symbol':symbol, 'Order':'BUY', 'Shares':shares})
    order_table.ix[-1] = pd.Series({'Date': order_table.index[-1], 'Symbol': symbol, 'Order': 'SELL', 'Shares': shares})
    order_table= reset_index_drop_na(order_table)
    return order_table


def get_sharpe_ratio(daily_ret, sddr, rfr=0.0, sf=252.0):
    drfr = daily_ret - rfr
    sr = math.sqrt(sf) * ((drfr.mean()) / sddr)
    return sr


def plot_2_data(df, df2, long_entry, short_entry, title="Manual Strategy", xlabel="Date", ylabel="Values", first_color='black',
                second_color='blue', first_label='Rule Based Values', second_label='Benchmark', legend_loc='upper left'):

    ax = df.plot(title=title, color=first_color, label=first_label)
    ax = df2.plot(ax=ax, color=second_color, label=second_label)
    ymin, ymax = ax.get_ylim()
    ax.vlines(x=long_entry.ix[:,'Date'].values, ymin=ymin, ymax=ymax, color='g', label='Long Entry')
    ax.vlines(x=short_entry.ix[:,'Date'].values, ymin=ymin, ymax=ymax, color='r', label='Short Entry')
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    plt.legend(loc=legend_loc)
    plt.show()


def run_strategy():
    sd = dt.datetime(2008,1,1)
    ed = dt.datetime(2009,12,31)
    dates = pd.date_range(sd, ed)
    price = get_data(['JPM'], dates, addSPY=True, colname='Adj Close')

    df_trades = testPolicy(symbol='JPM', sd=sd, ed=ed, sv=100000)
    long_entry = df_trades.ix[df_trades.ix[:,'Order'].values == 'BUY']
    short_entry = df_trades.ix[df_trades.ix[:,'Order'].values == 'SELL']

    manual_val = market.compute_portvals(df_trades, start_val=100000, commission=9.95, impact=0.005)

    benchmark = get_benchmark_df('JPM', price.index, ed, 1000)
    benchmark_val = market.compute_portvals(benchmark, start_val=100000, commission=9.95, impact=0.005)

    plot_2_data(manual_val, benchmark_val, long_entry, short_entry, title="Manual Strategy", xlabel="Date", ylabel="Values",
                first_color='black', second_color='blue', first_label='Rule Based Values', second_label='Benchmark', legend_loc='upper left')

    daily_ret = (manual_val / manual_val.shift(1)) - 1
    daily_ret_bench = (benchmark_val / benchmark_val.shift(1)) - 1

    std_daily_ret = daily_ret.std()
    std_daily_bench = daily_ret_bench.std()

    sharpe_ratio = get_sharpe_ratio(daily_ret, std_daily_ret, 0.0, 252)
    sharpe_ratio_bench =get_sharpe_ratio(daily_ret_bench, std_daily_bench, 0.0, 252)

    cum_ret = (manual_val[-1] / manual_val[0]) - 1
    cum_ret_bench = (benchmark_val[-1] / benchmark_val[0]) - 1

    mean_daily_ret = daily_ret.mean()
    mean_daily_ret_bench = daily_ret_bench.mean()

    final_value = manual_val.ix[-1]
    final_value_bench = benchmark_val.ix[-1]

    print "Date Range: {} to {}".format(sd, ed)
    print
    print "Sharpe Ratio of Manual Portfolio: {}".format(sharpe_ratio)
    print "Sharpe Ratio of Benchmark : {}".format(sharpe_ratio_bench)
    print
    print "Cumulative Return of Manual Portfolio : {}".format(cum_ret)
    print "Cumulative Return of Benchmark : {}".format(cum_ret_bench)
    print
    print "Standard Deviation of Manual Portfolio : {}".format(std_daily_ret)
    print "Standard Deviation of Benchmark : {}".format(std_daily_bench)
    print
    print "Mean Daily Return of Manual Portfolio : {}".format(mean_daily_ret)
    print "Mean Daily Return of Benchmark : {}".format(mean_daily_ret_bench)
    print
    print "Final Portfolio Value of Manual Portfolio : {}".format(final_value)
    print "Final Portfolio Value of Benchmark : {}".format(final_value_bench)


if __name__ == "__main__":
    run_strategy()
