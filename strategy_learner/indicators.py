# Yoshi Miyamoto ymiyamoto3


import datetime as dt

import matplotlib.pyplot as plt
import pandas as pd

from util import get_data


def indicators(symbol, start_date, end_date, plot=True):
    dates = pd.date_range(start_date, end_date)
    bollinger_lookback = 200
    momentum_lookback = 50
    sma_lookback = 241

    all_price_df = get_data([symbol], dates, addSPY=True, colname='Adj Close')
    price_df = all_price_df[[symbol]]
    price_df.columns = ['Price']
    normed_price_df = normalize_data(price_df)

    # momentum
    momentum = create_momentum_df(price_df,momentum_lookback)
    if plot:
        momentum_x = momentum.plot()
        normed_price_df.plot(title='Momentum', ax=momentum_x, label='Price')
        plt.legend()

    # sma
    sma_df = create_sma_df(price_df, sma_lookback)
    sma_df.fillna(method="bfill",inplace=True)
    normed_sma_df = normalize_data(sma_df)
    price_sma_df = get_price_sma_ratio(sma_df, price_df)
    if plot:
        sma_x = normed_sma_df.plot()
        price_sma_x = price_sma_df.plot(ax=sma_x)
        normed_price_df.plot(title='Price/SMA', ax=price_sma_x)
        plt.legend(loc='best',bbox_to_anchor=(0.5, 0.5))

    # Bollinger Band
    top_band, bottom_band = create_bollinger_bands_df(normed_price_df, bollinger_lookback, normed_sma_df)
    if plot:
        sma_df_x = normed_sma_df.plot()
        bottom_band_ax = bottom_band.plot(ax=sma_df_x)
        top_band_ax = top_band.plot(ax=bottom_band_ax)
        normed_price_df.plot(title='Bollinger Bands', ax=top_band_ax)
        plt.legend(loc='lower right')

    # volatility
    volatility = create_volatility_df(price_df)

    if plot:
        volatility_ax = volatility.plot()
        normed_price_df.plot(title='Volatility', ax=volatility_ax)
        plt.legend(loc='center right')
        plt.show()

    return normed_price_df, price_sma_df, top_band, bottom_band, volatility, momentum



def create_momentum_df(price, n_day):
    momentum = (price / price.shift(n_day)) # don't deduct 1 to match with normalized price in graph
    momentum.columns = ['Momentum']
    momentum.fillna(method="bfill", inplace=True)
    return momentum


def create_sma_df(price, lookback):
    sma = price.rolling(window=lookback, min_periods=lookback).mean()
    sma.columns = ['SMA']
    sma.fillna(method="bfill", inplace=True)
    return sma


def get_price_sma_ratio(sma, price):
    sma_price = price.ix[:,'Price'] / sma.ix[:,'SMA']
    sma_price_df = pd.DataFrame(sma_price, columns=['Price/SMA'])
    return sma_price_df


def create_bollinger_bands_df(price, lookback, sma):
    rolling_std = price.rolling(window=lookback, min_periods=lookback).std()
    rolling_std.columns = ['Rolling Std']
    top_band = sma.ix[:,'SMA'] + (2 * rolling_std.ix[:,'Rolling Std'])
    bottom_band = sma.ix[:,'SMA'] - (2 * rolling_std.ix[:,'Rolling Std'])
    top_band_df = pd.DataFrame(top_band, columns=['Top Band'])
    bottom_band_df = pd.DataFrame(bottom_band, columns=['Bottom Band'])
    top_band_df.fillna(method="bfill", inplace=True)
    bottom_band_df.fillna(method="bfill", inplace=True)
    return top_band_df, bottom_band_df


def create_volatility_df(price):
    volatility = price.copy()
    volatility = (volatility / volatility.shift(1)) - 1
    volatility.columns = ['Volatility']
    return volatility


def normalize_data(df):
    return df/df.ix[0, :]


if __name__ == '__main__':
    indicators()
