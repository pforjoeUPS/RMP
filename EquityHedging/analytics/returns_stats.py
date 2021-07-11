# -*- coding: utf-8 -*-
"""
Created on Tue Oct  1 17:59:28 2019

@author: Powis Forjoe, Maddie Choi, and Zach Wells
"""


import numpy as np
from ..datamanager import data_manager as dm
from .util import get_pos_neg_df

def get_ann_return(return_series, freq='1M'):
    """
    Return annualized return for a return series.

    Parameters
    ----------
    return_series : series
        returns series.
    freq : string, optional
        frequency. The default is '1M'.

    Returns
    -------
    double
        Annualized return.

    """
    #compute the annualized return
    d = len(return_series)
    return return_series.add(1).prod()**(dm.switch_freq_int(freq)/d)-1

def get_ann_vol(return_series, freq='1M'):
    """
    Return annualized volatility for a return series.

    Parameters
    ----------
    return_series : series
        returns series.
    freq : string, optional
        frequency. The default is '1M'.

    Returns
    -------
    double
        Annualized volatility.

    """
    #compute the annualized volatility
    return np.std(return_series, ddof=1)*np.sqrt(dm.switch_freq_int(freq))

def get_max_dd(price_series):
    """
    Return maximum draw down (Max DD) for a price series.

    Parameters
    ----------
    price_series : series
        price series.

    Returns
    -------
    double
        Max DD.

    """

    #we are going to use the length of the series as the window
    window = len(price_series)
    
    #calculate the max drawdown in the past window periods for each period in the series.
    roll_max = price_series.rolling(window, min_periods=1).max()
    drawdown = price_series/roll_max - 1.0
    
    return drawdown.min()

def get_max_dd_freq(price_series, freq='1M', max_3m_dd=False):
    """
    Return dictionary (value and date) of either Max 1M DD or Max 3M DD

    Parameters
    ----------
    price_series : series
        price series.
    freq : string, optional
        frequency. The default is '1M'.
    max_3m_dd : boolean, optional
        Compute Max 3M DD. The default is False.

    Returns
    -------
    dictionary
    """
    
    #convert price series into returns
    return_series = price_series.copy()
    return_series = return_series.resample(freq).ffill()
    
    #get int frequency
    int_freq = dm.switch_freq_int(freq)
    
    #compute 3M or 1M returns
    if max_3m_dd:
        periods = round((3/12) * int_freq)
        return_series = return_series.pct_change(periods)
    else:
        periods = round((1/12) * int_freq)
        return_series = return_series.pct_change(periods)
    return_series.dropna(inplace=True)
    
    #compute Max 1M/3M DD
    max_dd_freq = min(return_series)
    
    #get Max 1M/3M DD date
    index_list = return_series.index[return_series==max_dd_freq].tolist()
    
    #return dictionary
    return {'max_dd': max_dd_freq, 'index': index_list[0]}

def get_avg_pos_neg(return_series):
    """
    Return Average positve returns/ Average negative returns
    of a strategy

    Parameters
    ----------
    return_series : series
        returns series.

    Returns
    -------
    double
    
    """
    
    #filter positive and negative returns
    pos_ret = get_pos_neg_df(return_series,True)
    neg_ret = get_pos_neg_df(return_series,False)
    
    #compute means
    avg_pos = pos_ret.mean()
    avg_neg = neg_ret.mean()
    
    return avg_pos/avg_neg

def get_down_stddev(return_series, freq='1M', target=0):
    """
    Compute annualized downside std dev

    Parameters
    ----------
    return_series : series
        returns series.
    freq : string, optional
        frequency. The default is '1M'.
    target : int, optional
        The default is 0.

    Returns
    -------
    double
        downside std deviation.

    """
    #create a downside return column with the negative returns only
    downside_returns = return_series.loc[return_series < target]

    #return annualized std dev of downside
    return get_ann_vol(downside_returns, freq)

def get_sortino_ratio(return_series, freq='1M', rfr=0, target=0):
    """
    Compute Sortino ratio

    Parameters
    ----------
    return_series : series
        returns series.
    freq : string, optional
        frequency. The default is '1M'.
    rfr : int, optional
        The default is 0.
    target : int, optional
        The default is 0.
    
    Returns
    -------
    double
        sortino ratio
    """
    
    #calculate annulaized return and std dev of downside
    ann_ret = get_ann_return(return_series, freq)
    down_stddev = get_down_stddev(return_series, freq, target)
    
    #calculate the sortino ratio
    return (ann_ret - rfr) / down_stddev

def get_ret_vol_ratio(return_series,freq='1M'):
    """
    Compute Ret/Vol ratio

    Parameters
    ----------
    return_series : series
        returns series.
    freq : string, optional
        frequency. The default is '1M'.

    Returns
    -------
    double
        ret/vol ratio

    """
    
    #calculate annulaized return and vol
    ann_ret = get_ann_return(return_series, freq)
    ann_vol = get_ann_vol(return_series, freq)
     
    #calculate ratio
    return ann_ret / ann_vol
    
def get_ret_max_dd_ratio(return_series,price_series,freq='1M'):
    """
    Compute Ret/Max DD ratio

    Parameters
    ----------
    return_series : series
        returns series.
    price_series : series
        price series.
    freq : string, optional
        frequency. The default is '1M'.

    Returns
    -------
    double
        ret/Max DD ratio

    """
    #compute annual returns and Max DD
    ann_ret = get_ann_return(return_series, freq)
    max_dd = get_max_dd(price_series)
    
    #calculate ratio
    return ann_ret / abs(max_dd)
 
def get_skew(return_series):
    """
    Compute skew of a return series

    Parameters
    ----------
    return_series : series
        returns series.

    Returns
    -------
    double
        skew.

    """
    return return_series.skew()

def get_ret_max_dd_freq_ratio(return_series, price_series, freq, max_3m_dd=False):
    """
    Compute Ret/Max 1M/3M DD ratio

    Parameters
    ----------
    return_series : series
        returns series.
    price_series : series
        price series.
    freq : string, optional
        frequency. The default is '1M'.
    max_3m_dd : boolean, optional
        Compute Max 3M DD. The default is False.

    Returns
    -------
    double
        ret/Max 1M/3M DD ratio

    """
    #calculate annual return
    ann_ret = get_ann_return(return_series, freq)
    max_freq_dd = get_max_dd_freq(price_series, freq, max_3m_dd)['max_dd']
    
    #compute ratio
    return ann_ret/abs(max_freq_dd)

def get_return_stats(df_returns, freq='1M'):
    """
    Return a dict of return analytics

    Parameters
    ----------
    df_returns : dataframe
        returns dataframe.
    freq : string, optional
        frequency. The default is '1M'.

    Returns
    -------
    analysis_dict : dictionary

    """
    
    #generate return stats for each strategy
    df_prices = dm.get_prices_df(df_returns)
    analysis_dict = {}
    for col in df_returns.columns:
        df_strat = dm.remove_na(df_returns, col)
        df_prices = dm.get_prices_df(df_strat)
    
        ann_ret = get_ann_return(df_strat[col], freq)
        ann_vol = get_ann_vol(df_strat[col], freq)
        ret_vol = get_ret_vol_ratio(df_strat[col],freq)
        max_dd = get_max_dd(df_prices[col])
        ret_dd = get_ret_max_dd_ratio(df_strat[col],df_prices[col],freq)
        max_1m_dd_dict = get_max_dd_freq(df_prices[col],freq)
        ret_1m_dd = get_ret_max_dd_freq_ratio(df_strat[col], df_prices[col],freq,False)   
        max_3m_dd_dict = get_max_dd_freq(df_prices[col],freq,True)
        ret_3m_dd = get_ret_max_dd_freq_ratio(df_strat[col],df_prices[col],freq,True)
        skew = get_skew(df_strat[col])
        avg_pos_neg = get_avg_pos_neg(df_strat[col])
        down_stdev = get_down_stddev(df_strat[col], freq)
        sortino = get_sortino_ratio(df_strat[col], freq)
        analysis_dict[col] = [ann_ret, ann_vol, ret_vol, max_dd, ret_dd,
                             max_1m_dd_dict['max_dd'], max_1m_dd_dict['index'], ret_1m_dd,
                             max_3m_dd_dict['max_dd'], max_3m_dd_dict['index'], ret_3m_dd,
                             skew, avg_pos_neg, down_stdev, sortino]
        
    return analysis_dict


