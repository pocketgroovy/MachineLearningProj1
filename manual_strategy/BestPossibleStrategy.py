import datetime as dt
import math

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import marketsimcode as market
from util import get_data


def testPolicy(symbol='JPM', sd=dt.datetime(2010,1,1), ed=dt.datetime(2012,12,31), sv = 100000):
    price_movement = get_price_movement(symbol, sd, ed)
    order_table = pd.DataFrame(columns=['Date','Symbol','Order','Shares'], index=price_movement.index)
    # positive in price_movement = buy in previous day, negative = sell in previous day
    # first day, only allowed for +- 1000 shares holding
    prev = 0
    first_day = False
    for day in price_movement.index:
        shares = 2000
        if price_movement.ix[day, symbol] > 0 and prev < 0:
            order_table.loc[prev_day] = pd.Series({'Date':prev_day, 'Symbol':symbol, 'Order':'BUY', 'Shares':shares})
        elif price_movement.ix[day, symbol] < 0 and prev > 0:
            order_table.loc[prev_day] = pd.Series({'Date':prev_day, 'Symbol':symbol, 'Order':'SELL', 'Shares':shares})
        else:
            if price_movement.ix[day, symbol] < prev and prev == 0:
                if not first_day:
                    shares = 1000
                    first_day = True
                order_table.loc[prev_day] = pd.Series({'Date':prev_day, 'Symbol': symbol, 'Order': 'SELL', 'Shares': shares})
            elif price_movement.ix[day, symbol] > prev and prev == 0:
                if not first_day:
                    shares = 1000
                    first_day = True
                order_table.loc[prev_day] = pd.Series({'Date':prev_day, 'Symbol': symbol, 'Order': 'BUY', 'Shares': shares})
        prev = price_movement.ix[day, symbol]
        prev_day = day

    # insert dummy order for last day if not exist already
    if order_table.ix[-1].isnull().any():
        order_table.loc[ed] = pd.Series({'Date': ed, 'Symbol': symbol, 'Order': 'SELL', 'Shares': shares})

    # reorganize the index numbers to be Date as index
    order_table = reset_index_drop_na(order_table)

    return order_table


def reset_index_drop_na(df):
    df.reset_index(drop=True, inplace=True)
    df.set_index('Date')
    df.dropna(inplace=True)
    return df


def get_price_movement(symbol='JPM', sd=dt.datetime(2010,1,1), ed=dt.datetime(2012,12,31)):
    dates = pd.date_range(sd, ed)
    price = get_data([symbol], dates, addSPY=True, colname='Adj Close')
    price_movement = price.copy()
    price_movement.ix[:,:] = np.nan
    price_movement[1:] = price.diff() # diff between everyday price, positivee for bull, negative for bear, 0 for no movement
    price_movement.ix[0] = 0 # first day
    del price_movement['SPY'] # drop spy
    return price_movement


def get_benchmark_df(symbol, index, ed, shares=1000):
    order_table = pd.DataFrame(columns=['Date','Symbol','Order','Shares'], index=index)
    order_table.iloc[0] = pd.Series({'Date': index[0], 'Symbol':symbol, 'Order':'BUY', 'Shares':shares})
    order_table.loc[ed] = pd.Series({'Date': ed, 'Symbol': symbol, 'Order': 'SELL', 'Shares': shares})
    order_table= reset_index_drop_na(order_table)
    return order_table


def get_sharpe_ratio(daily_ret, sddr, rfr=0.0, sf=252.0):
    drfr = daily_ret - rfr
    sr = math.sqrt(sf) * ((drfr.mean()) / sddr)
    return sr


def plot_2_data(df, df2, title="Best Possible Strategy", xlabel="Date", ylabel="Values", first_color='black',
                second_color='blue', first_label='Best Values', second_label='Benchmark'):
    ax = df.plot(title=title, color=first_color, label=first_label)
    ax = df2.plot(ax=ax, color=second_color, label=second_label)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    plt.legend(loc='upper left')
    plt.show()


def run_strategy():
    sd = dt.datetime(2008,1,1)
    ed = dt.datetime(2009,12,31)
    dates = pd.date_range(sd, ed)
    price = get_data(['JPM'], dates, addSPY=True, colname='Adj Close')

    df_trades = testPolicy(symbol='JPM', sd=sd, ed=ed, sv=100000)
    best_val = market.compute_portvals(df_trades, start_val=100000, commission=0.00, impact=0.00)

    benchmark = get_benchmark_df('JPM', price.index, ed, 1000)
    benchmark_val = market.compute_portvals(benchmark, start_val=100000, commission=0.00, impact=0.00)

    plot_2_data(best_val, benchmark_val, title="Best Possible Strategy", xlabel="Date", ylabel="Values", first_color='black',
                second_color='blue', first_label='Best Values', second_label='Benchmark')

    daily_ret = (best_val / best_val.shift(1)) - 1
    daily_ret_bench = (benchmark_val / benchmark_val.shift(1)) - 1

    std_daily_ret = daily_ret.std()
    std_daily_bench = daily_ret_bench.std()

    sharpe_ratio = get_sharpe_ratio(daily_ret, std_daily_ret, 0.0, 252)
    sharpe_ratio_bench =get_sharpe_ratio(daily_ret_bench, std_daily_bench, 0.0, 252)

    cum_ret = (best_val[-1] / best_val[0]) - 1
    cum_ret_bench = (benchmark_val[-1] / benchmark_val[0]) - 1

    mean_daily_ret = daily_ret.mean()
    mean_daily_ret_bench = daily_ret_bench.mean()

    final_value = best_val.ix[-1]
    final_value_bench = benchmark_val.ix[-1]

    print "Date Range: {} to {}".format(sd, ed)
    print
    print "Sharpe Ratio of Best Portfolio: {}".format(sharpe_ratio)
    print "Sharpe Ratio of Benchmark : {}".format(sharpe_ratio_bench)
    print
    print "Cumulative Return of Best Portfolio : {}".format(cum_ret)
    print "Cumulative Return of Benchmark : {}".format(cum_ret_bench)
    print
    print "Standard Deviation of Best Portfolio : {}".format(std_daily_ret)
    print "Standard Deviation of Benchmark : {}".format(std_daily_bench)
    print
    print "Mean Daily Return of Best Portfolio : {}".format(mean_daily_ret)
    print "Mean Daily Return of Benchmark : {}".format(mean_daily_ret_bench)
    print
    print "Final Portfolio Value of Best Portfolio : {}".format(final_value)
    print "Final Portfolio Value of Benchmark : {}".format(final_value_bench)


if __name__ == "__main__":
    run_strategy()
