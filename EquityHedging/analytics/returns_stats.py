# -*- coding: utf-8 -*-
"""
Created on Tue Oct  1 17:59:28 2019

@author: Powis Forjoe and Maddie Choi
"""


import numpy as np
from ..datamanager import data_manager as dm
from .util import get_pos_neg_df

#TODO: make sharpe (ret/vol) ratio function
#TODO: make calmar (ret/dd) ratio functions
#TODO: make skew function

def get_ann_return(return_series, freq='1M'):
    """
    Return annualized return for a return series.

    Parameters:
    return_series -- return series
    freq -- string ('1D', '1W', '1M')

    Returns:
    Annualized return -- double
    """
    #compute the annualized return
    d = len(return_series)
    return return_series.add(1).prod()**(dm.switch_freq_int(freq)/d)-1

def get_ann_vol(return_series, freq='1M'):
    """
    Return annualized volatility for a return series.

    Parameters:
    return_series -- return series
    freq -- string ('1D', '1W', '1M')
    
    Returns:
    Annualized volatility double
    """
    #compute the annualized volatility
    return np.std(return_series, ddof=1)*np.sqrt(dm.switch_freq_int(freq))

def get_max_dd(price_series):
    """
    Return max draw down for a price series.

    Parameters:
    price_series -- price series
    
    Returns:
    Max draw down -- double
    """
    # We are going to use the length of the series as the window
    window = len(price_series)
    
    # Calculate the max drawdown in the past window periods for each period in the series.
    roll_max = price_series.rolling(window, min_periods=1).max()
    drawdown = price_series/roll_max - 1.0
    return drawdown.min()

def get_max_dd_freq(price_series, freq='1M', max_3m_dd=False):
    """
    Return dict(value and date) of either max 1M dd or max 3M dd

    Parameters:
    price_series -- price series
    freq -- string ('1M', '3M')
    max_3m_dd -- boolean

    Returns:
    Max draw down data-- dict (max_dd(double), index(date))
    """
    return_series = price_series.copy()
    return_series = return_series.resample(freq).ffill()
    int_freq = dm.switch_freq_int(freq)
    if max_3m_dd:
        periods = round((3/12) * int_freq)
        return_series = return_series.pct_change(periods)
    else:
        periods = round((1/12) * int_freq)
        return_series = return_series.pct_change(periods)
    return_series.dropna(inplace=True)
    max_dd_freq = min(return_series)
    index_list = return_series.index[return_series==max_dd_freq].tolist()
    return {'max_dd': max_dd_freq, 'index': index_list[0]}

def get_avg_pos_neg(df_returns, col_name):
    """
    Return Average positve returns/ Average negative returns
    of a strategy(col_name)
    
    Parameters:
    df_returns -- return dataframe
    col_name -- string (column name in dataframe)
    
    Returns:
    avg pos/neg ratio -- double
    """
    pos_ret = get_pos_neg_df(df_returns,col_name,True)
    neg_ret = get_pos_neg_df(df_returns,col_name,False)
    avg_pos = pos_ret[col_name].mean()
    avg_neg = neg_ret[col_name].mean()
    return avg_pos/avg_neg

def get_down_stddev(df_returns, col, freq='1M', target=0):
    """
    Compute annualized downside std dev
    
    Parameters:
    df_returns -- returns dataframe
    col -- string (column name in dataframe)
    freq -- string ('1M', '1W', '1D')
    target -- double
    
    Returns:
    downside deviation -- double
    """
    # Create a downside return column with the negative returns only
    downside_returns = df_returns.loc[df_returns[col] < target]

    # return annualized std dev of downside
    return get_ann_vol(downside_returns[col], freq)

def get_sortino_ratio(df_returns, col, freq='1M', rfr=0, target=0):
    """
    Compute Sortino ratio (ann_ret - rfr) / down_stddev

    Parameters:
    df_returns -- returns dataframe
    col -- string (column name in dataframe)
    freq -- string ('1M', '1W', '1D')
    rfr -- double
    target -- double
    
    Returns:
    sortino_ratio -- double
    """
    # Calculate annulaized return and std dev of downside
    ann_ret = get_ann_return(df_returns[col], freq)
    down_stddev = get_down_stddev(df_returns, col, freq, target)
    
    # Calculate the sortino ratio
    sortino_ratio = (ann_ret - rfr) / down_stddev
    
    return sortino_ratio

def get_ret_vol_ratio(df_strat,col,freq='1M'):
    #ret vol= annual return/annual vol
    #calculate annual return
    ann_ret = get_ann_return(df_strat[col], freq)
    
    #calculate annual vol
    ann_vol = get_ann_vol(df_strat[col], freq)
    
    #calculate ratio
    ret_vol = ann_ret / ann_vol
    return ret_vol

def get_ret_maxdd_ratio(df_strat,df_prices,col,freq='1M'):
    #return max draw down ratio = (annual returns)/ (max draw downs)
    #compute annual returns
    ann_ret = get_ann_return(df_strat[col], freq)
    
    #compute max draw down
    max_dd = get_max_dd(df_prices[col])
    
    #calculate ratio
    ret_maxdd=  ann_ret/abs(max_dd)
    return ret_maxdd
 
def get_skew(df_strat, col):
    #compute skew
     skew= df_strat[col].skew()
     return skew

def get_ret_maxdd_freq_ratio(df_strat,col,price_series,freq,max_1Q_dd=False):
    #calculate annual return
    ann_ret=get_ann_return(df_strat[col], freq)
        
    if max_1Q_dd==False:
        #calculates 1m ret max dd ratio
        #calculate max 1 month draw down
        max_1m_dd=get_max_dd_freq(price_series[col], freq='1M', max_3m_dd=False)['max_dd']
        
        #compute ratio
        ret_maxdd_ratio= ann_ret/max_1m_dd
    else:
        #calculates 3m return max dd ratio
        
        #calculate max 1 month draw down
        max_1m_dd=get_max_dd_freq(price_series[col], freq='1M', max_3m_dd=True)['max_dd']
        
        #compute ratio
        ret_maxdd_ratio= ann_ret/max_1m_dd
    return ret_maxdd_ratio

def get_return_stats(df_returns, freq='1M'):
    """
    Return a dict of return analytics
    
    Parameters:
    df_returns -- dataframe
    freq -- string ('1M', '1W', '1D')
    
    Returns:
    analysis_pack -- dict(key: column name, value: return analytics)
    """
    
    #generate return stats for each strategy
    df_prices = dm.get_prices_df(df_returns)
    analysis_dict = {}
    for col in df_returns.columns:
        df_strat = dm.remove_na(df_returns, col)
        df_prices = dm.get_prices_df(df_strat)
    
        ann_ret = get_ann_return(df_strat[col], freq)
        ann_vol = get_ann_vol(df_strat[col], freq)
        ret_vol = get_ret_vol_ratio(df_strat,col=col,freq=freq)
        max_dd = get_max_dd(df_prices[col])
        ret_dd = get_ret_maxdd_ratio(df_strat,df_prices,col,freq=freq)
        max_1m_dd = get_max_dd_freq(df_prices[col],freq)['max_dd']
        max_1m_date = get_max_dd_freq(df_prices[col],freq)['index']
        ret_1m_dd=get_ret_maxdd_freq_ratio(df_strat, col, df_prices, freq=freq,max_1Q_dd=False)   
        max_1q_dd = get_max_dd_freq(df_prices[col],freq,True)['max_dd']
        max_1q_date = get_max_dd_freq(df_prices[col],freq,True)['index']
        ret_1q_dd=get_ret_maxdd_freq_ratio(df_strat, col, df_prices, freq=freq,max_1Q_dd=True)
        skew=get_skew(df_strat, col)
        avg_pos_neg = get_avg_pos_neg(df_strat, col)
        down_stdev = get_down_stddev(df_strat, col, freq)
        sortino = get_sortino_ratio(df_strat, col, freq)
        analysis_dict[col] = [ann_ret, ann_vol, ret_vol, max_dd, ret_dd,
                             max_1m_dd, max_1m_date,ret_1m_dd, max_1q_dd, max_1q_date, ret_1q_dd,
                             skew, avg_pos_neg, down_stdev, sortino]
        
    return analysis_dict


