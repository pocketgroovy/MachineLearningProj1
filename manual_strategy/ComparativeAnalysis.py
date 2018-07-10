import datetime as dt

import pandas as pd

import ManualStrategy as manual
import marketsimcode as market
from util import get_data


def run_strategy():
    sd = dt.datetime(2010,1,1)
    ed = dt.datetime(2011,12,31)
    dates = pd.date_range(sd, ed)
    price = get_data(['JPM'], dates, addSPY=True, colname='Adj Close')

    df_trades = manual.testPolicy(symbol='JPM', sd=sd, ed=ed, sv=100000)
    long_entry = df_trades.ix[df_trades.ix[:,'Order'].values == 'BUY']
    short_entry = df_trades.ix[df_trades.ix[:,'Order'].values == 'SELL']

    manual_val = market.compute_portvals(df_trades, start_val=100000, commission=9.95, impact=0.005)

    benchmark = manual.get_benchmark_df('JPM', price.index, ed, 1000)
    benchmark_val = market.compute_portvals(benchmark, start_val=100000, commission=9.95, impact=0.005)

    manual.plot_2_data(manual_val, benchmark_val, long_entry, short_entry, title="Manual Strategy/Out Sample", xlabel="Date", ylabel="Values",
                first_color='black', second_color='blue', first_label='Rule Based Values', second_label='Benchmark', legend_loc='lower left')

    daily_ret = (manual_val / manual_val.shift(1)) - 1
    daily_ret_bench = (benchmark_val / benchmark_val.shift(1)) - 1

    std_daily_ret = daily_ret.std()
    std_daily_bench = daily_ret_bench.std()

    sharpe_ratio = manual.get_sharpe_ratio(daily_ret, std_daily_ret, 0.0, 252)
    sharpe_ratio_bench =manual.get_sharpe_ratio(daily_ret_bench, std_daily_bench, 0.0, 252)

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
