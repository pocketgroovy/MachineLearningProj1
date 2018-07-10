# Yoshi Miyamoto ymiyamoto3


import datetime as dt
import math

import matplotlib.pyplot as plt
import pandas as pd

from util import get_data
from StrategyLearner import StrategyLearner
import ManualStrategy as manual
import marketsimcode as market


def testManualPolicy(symbol, sd, ed, sv=100000):
    return manual.testPolicy(symbol, sd, ed, sv)


def reset_index_drop_na(df):
    df.dropna(inplace=True)
    df.reset_index(drop=True, inplace=True)
    df.set_index('Date')
    return df


def get_benchmark_df(symbol, index, ed, shares=1000):
    order_table = pd.DataFrame(columns=['Date', 'Symbol', 'Order', 'Shares'], index=index)
    order_table.iloc[0] = pd.Series({'Date': index[0], 'Symbol': symbol, 'Order': 'BUY', 'Shares': shares})
    order_table.ix[-1] = pd.Series(
        {'Date': order_table.index[-1], 'Symbol': symbol, 'Order': 'SELL', 'Shares': shares})
    order_table = reset_index_drop_na(order_table)
    return order_table


def get_sharpe_ratio(daily_ret, sddr, rfr=0.0, sf=252.0):
    drfr = daily_ret - rfr
    sr = math.sqrt(sf) * ((drfr.mean()) / sddr)
    return sr


def plot_3_data(learn_val, manual_val, benchmark_val, title="Manual Strategy/Learner Strategy", \
                xlabel="Date", ylabel="Values", first_color='black', second_color='blue', third_color='green', \
                first_label='Leaner Based Values', second_label='Manual Based Value', third_label='Benchmark', \
                legend_loc='upper left'):
    ax = learn_val.plot(title=title, color=first_color, label=first_label)
    ax = manual_val.plot(ax=ax, color=second_color, label=second_label)
    ax = benchmark_val.plot(ax=ax, color=third_color, label=third_label)

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    plt.legend(loc=legend_loc)
    plt.show()


def get_order_df(symbol, trades):
    orders_df = pd.DataFrame(columns=['Shares','Order','Symbol'])
    for row_idx in trades.index:
        nshares = trades.loc[row_idx][0]
        if nshares == 0:
            continue
        order = 'SELL' if nshares < 0 else 'BUY'
        new_row = pd.DataFrame([[row_idx, abs(nshares),order,symbol],],columns=['Date', 'Shares','Order','Symbol'],index=[row_idx,])
        orders_df = orders_df.append(new_row)
    return orders_df


def run_strategy():
    sd = dt.datetime(2008,1,1)
    ed = dt.datetime(2009,12,31)
    dates = pd.date_range(sd, ed)
    price = get_data(['JPM'], dates, addSPY=True, colname='Adj Close')

    commision = 0
    impact = 0

    learner = StrategyLearner(verbose=False, impact=impact)
    learner.addEvidence(symbol='JPM', sd=sd, ed=ed, sv=100000)
    trades = learner.testPolicy(symbol='JPM', sd=sd, ed=ed, sv=100000)

    df_learner_trades = get_order_df('JPM',trades)

    df_manual_trades = testManualPolicy(symbol='JPM', sd=sd, ed=ed, sv=100000)

    learn_val = market.compute_portvals(df_learner_trades, start_val=100000, commission=commision, impact=impact)
    learn_val_normalized = learn_val[:]/learn_val[0]

    manual_val = market.compute_portvals(df_manual_trades, start_val=100000, commission=commision, impact=impact)
    manual_val_normalized = manual_val[:]/manual_val[0]

    benchmark = get_benchmark_df('JPM', price.index, ed, 1000)
    benchmark_val = market.compute_portvals(benchmark, start_val=100000, commission=commision, impact=impact)
    benchmark_val_normalized = benchmark_val[:]/benchmark_val[0]

    plot_3_data(learn_val_normalized, manual_val_normalized, benchmark_val_normalized, title="Manual Strategy/Learner Strategy", \
                xlabel="Date", ylabel="Values", first_color='black', second_color='blue',  third_color='green', \
                first_label='Leaner Based Values', second_label='Manual Based Value', third_label='Benchmark', \
                legend_loc='upper left')

    daily_ret_learner = (learn_val / learn_val.shift(1)) - 1
    daily_ret_manual = (manual_val / manual_val.shift(1)) - 1
    daily_ret_bench = (benchmark_val / benchmark_val.shift(1)) - 1

    std_daily_ret_learner = daily_ret_learner.std()
    std_daily_ret_manual = daily_ret_manual.std()
    std_daily_bench = daily_ret_bench.std()

    sharpe_ratio_learner = get_sharpe_ratio(daily_ret_learner, std_daily_ret_learner, 0.0, 252)
    sharpe_ratio_manual = get_sharpe_ratio(daily_ret_manual, std_daily_ret_manual, 0.0, 252)
    sharpe_ratio_bench =get_sharpe_ratio(daily_ret_bench, std_daily_bench, 0.0, 252)

    cum_ret_learner = (learn_val[-1] / learn_val[0]) - 1
    cum_ret_manual = (manual_val[-1] / manual_val[0]) - 1
    cum_ret_bench = (benchmark_val[-1] / benchmark_val[0]) - 1

    mean_daily_ret_learner = daily_ret_learner.mean()
    mean_daily_ret_manual = daily_ret_manual.mean()
    mean_daily_ret_bench = daily_ret_bench.mean()

    final_value_learner = learn_val.ix[-1]
    final_value_manual = manual_val.ix[-1]
    final_value_bench = benchmark_val.ix[-1]

    print "Date Range: {} to {}".format(sd, ed)
    print
    print "Sharpe Ratio of Learner Portfolio: {}".format(sharpe_ratio_learner)
    print "Sharpe Ratio of Manual Portfolio: {}".format(sharpe_ratio_manual)
    print "Sharpe Ratio of Benchmark : {}".format(sharpe_ratio_bench)
    print
    print "Cumulative Return of Learner Portfolio : {}".format(cum_ret_learner)
    print "Cumulative Return of Manual Portfolio : {}".format(cum_ret_manual)
    print "Cumulative Return of Benchmark : {}".format(cum_ret_bench)
    print
    print "Standard Deviation of Learner Portfolio : {}".format(std_daily_ret_learner)
    print "Standard Deviation of Manual Portfolio : {}".format(std_daily_ret_manual)
    print "Standard Deviation of Benchmark : {}".format(std_daily_bench)
    print
    print "Mean Daily Return of Learner Portfolio : {}".format(mean_daily_ret_learner)
    print "Mean Daily Return of Manual Portfolio : {}".format(mean_daily_ret_manual)
    print "Mean Daily Return of Benchmark : {}".format(mean_daily_ret_bench)
    print
    print "Final Portfolio Value of Learner Portfolio : {}".format(final_value_learner)
    print "Final Portfolio Value of Manual Portfolio : {}".format(final_value_manual)
    print "Final Portfolio Value of Benchmark : {}".format(final_value_bench)


if __name__ == "__main__":
    run_strategy()
