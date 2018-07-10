"""MC2-P1: Market simulator."""
# Yoshi Miyamoto ymiyamoto3


import datetime as dt

import pandas as pd

from util import get_data


def compute_portvals(df_data, start_val = 1000000, commission=9.95, impact=0.005):
    # this is the function the autograder will call to test your code
    # NOTE: orders_file may be a string, or it may be a file object. Your
    # code should work correctly with either input
    # TODO: Your code here
    df_data_copy = df_data.copy() # create a copy to keep the transaction count to apply impact and commissions
    df_data.loc[df_data['Order'] == 'SELL', 'Shares'] = df_data.loc[df_data['Order'] == 'SELL', 'Shares'] * -1 # modify 'SELL' order to negative numbers
    df_data_copy.loc[df_data['Order'] == 'SELL', 'Shares'] = df_data_copy.loc[df_data['Order'] == 'SELL', 'Shares'] * -1 # modify 'SELL' order to negative numbers

    df_data.reset_index(inplace=True)  # make 'Date as a column so it can be used for sorting
    df_data.sort_values(by=['Date', 'Symbol'], inplace=True)
    df_data.reset_index(drop=True, inplace=True)  # reorganize the index numbers before the action below

    # combine the same symbol action into one row
    for index, row in df_data.iterrows():
        if index != 0:
            if df_data.ix[index, 'Date'] == df_data.ix[index-1, 'Date']:
                if df_data.ix[index, 'Symbol'] == df_data.ix[index-1, 'Symbol']:
                    df_data.ix[index, 'Shares'] = df_data.ix[index, 'Shares'] + df_data.ix[index-1, 'Shares']
                    df_data.drop(index-1, inplace=True)

    df_data = df_data.set_index('Date')  # reset 'Date' as index
    dates, syms = get_dates_and_symbols(df_data)
    df_prices = get_adj_close_prices(dates, syms)
    add_cash_column(df_prices)

    df_trade = create_trade_df(df_data, df_prices, dates, syms)

    df_holdings = create_holding_df(df_prices,df_trade, start_val)

    df_values = df_prices * df_holdings

    df_port_val = df_values.sum(axis=1)

    # apply impact and commissions
    for index, row in df_data_copy.iterrows():
        if row['Order'] == 'BUY':
            df_port_val[row['Date']:] = df_port_val[row['Date']:] - (((df_prices.ix[row['Date'], row['Symbol']] * row['Shares']) * impact) + commission)
        if row['Order'] == 'SELL':
            df_port_val[row['Date']:] = df_port_val[row['Date']:] + (((df_prices.ix[row['Date'], row['Symbol']] * row['Shares']) * impact) - commission)
    return df_port_val


def get_dates_and_symbols(df):
    sd = df.index.values[0]  # start date
    ed = df.index.values[-1]  # end date
    dates = pd.date_range(sd, ed)
    syms = list(df['Symbol'].unique())  # list up all symbols
    return dates, syms


def get_adj_close_prices(dates, syms):
    prices_all = get_data(syms, dates)  # automatically adds SPY
    prices_all.fillna(method="ffill",inplace=True)
    prices_all.fillna(method="bfill",inplace=True)
    return prices_all[syms]


def add_cash_column(df):
    df['Cash'] = pd.Series(1.0, index=df.index)


def create_trade_df(df, prices, dates, syms):
    trade = pd.DataFrame(index=dates,columns=syms)
    for sym in syms:
        trade[sym] = df.loc[df['Symbol'] == sym, 'Shares']

    trade.fillna(0, inplace=True)
    add_cash_column(trade)
    totals = prices.ix[:, :-1] * trade.ix[:,:-1]
    trade['Cash']= totals.sum(axis=1) * -1
    return trade.dropna()


def create_holding_df(prices, trade, sv):
    holdings = create_empty_df(prices)
    holdings.ix[0, 'Cash'] = trade.ix[0, 'Cash'] + sv
    for i in range(1, len(holdings)):
        holdings.ix[i,'Cash'] = trade.ix[i, 'Cash'] + holdings.ix[i-1,'Cash']
    holdings.ix[:, :-1] = trade.ix[:,:-1].cumsum()
    return holdings


def create_empty_df(df):
    empty_df = pd.DataFrame.from_items([ (name, pd.Series(data=None, dtype=series.dtype))
                                         for name, series in df.iteritems()]).reindex(index=df.index).fillna(0)
    return empty_df


def author():
    return 'ymiyamoto3'


def test_code():
    # this is a helper function you can use to test your code
    # note that during autograding his function will not be called.
    # Define input parameters

    of = "./orders/orders2.csv"
    # of = "./orders/ordertest2.csv"
    sv = 1000000

    # Process orders
    df_data = pd.DataFrame()
    portvals = compute_portvals(df_data, start_val = sv)
    if isinstance(portvals, pd.DataFrame):
        portvals = portvals[portvals.columns[0]] # just get the first column
    else:
        "warning, code did not return a DataFrame"
    
    # Get portfolio stats
    # Here we just fake the data. you should use your code from previous assignments.
    start_date = dt.datetime(2008,1,1)
    end_date = dt.datetime(2008,6,1)
    cum_ret, avg_daily_ret, std_daily_ret, sharpe_ratio = [0.2,0.01,0.02,1.5]
    cum_ret_SPY, avg_daily_ret_SPY, std_daily_ret_SPY, sharpe_ratio_SPY = [0.2,0.01,0.02,1.5]

    # Compare portfolio against $SPX
    print "Date Range: {} to {}".format(start_date, end_date)
    print
    print "Sharpe Ratio of Fund: {}".format(sharpe_ratio)
    print "Sharpe Ratio of SPY : {}".format(sharpe_ratio_SPY)
    print
    print "Cumulative Return of Fund: {}".format(cum_ret)
    print "Cumulative Return of SPY : {}".format(cum_ret_SPY)
    print
    print "Standard Deviation of Fund: {}".format(std_daily_ret)
    print "Standard Deviation of SPY : {}".format(std_daily_ret_SPY)
    print
    print "Average Daily Return of Fund: {}".format(avg_daily_ret)
    print "Average Daily Return of SPY : {}".format(avg_daily_ret_SPY)
    print
    print "Final Portfolio Value: {}".format(portvals[-1])


if __name__ == "__main__":
    test_code()
