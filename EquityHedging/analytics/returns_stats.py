# -*- coding: utf-8 -*-
"""
Created on Tue Oct  1 17:59:28 2019

@author: Powis Forjoe, Maddie Choi, and Zach Wells
"""


import numpy as np
from ..datamanager import data_manager as dm
from EquityHedging.analytics import  util


RETURNS_STATS_INDEX = ['Annualized Ret', 'Equity Alpha', 'Equity Beta','Equity Bull Beta','Equity Bear Beta', 'Median Period Return',
                       'Avg. Period Return','Avg. Period Up Return', 'Avg. Period Down Return',
                       'Avg Pos Ret/Avg Neg Ret','Best Period', 'Worst Period','% Positive Periods',
                       '% Negative Periods','Annualized Vol','Upside Deviation','Downside Deviation',
                       'Upside to Downside Deviation Ratio','Skewness', 'Kurtosis',
                       'Max DD','Ret/Vol', 'Sortino Ratio','Ret/Max DD']
RETURNS_STATS_FI_INDEX = ['Annualized Ret', 'Equity Alpha',  'FI Alpha', 'Equity Beta','Equity Bull Beta','Equity Bear Beta','FI Beta','FI Bull Beta','FI Bear Beta','Median Period Return',
                       'Avg. Period Return','Avg. Period Up Return', 'Avg. Period Down Return',
                       'Avg Pos Ret/Avg Neg Ret','Best Period', 'Worst Period','% Positive Periods',
                       '% Negative Periods','Annualized Vol','Upside Deviation','Downside Deviation',
                       'Upside to Downside Deviation Ratio','Skewness', 'Kurtosis',
                       'Max DD','Ret/Vol', 'Sortino Ratio','Ret/Max DD']

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

def get_mkt_series(freq='1M',mkt='SPTR'):
    
    mkt_dict = dm.get_equity_hedge_returns(equity='SPTR',only_equity=True)
    mkt_df = mkt_dict[dm.switch_freq_string(freq)]
    return mkt_df[mkt]
    
def get_beta(return_series, mkt_series, freq = '1M'):
    
    return return_series.cov(mkt_series)/mkt_series.var()

def get_alpha(return_series, mkt_series, freq = '1M', rfr = 0.0):
    beta = get_beta(return_series,mkt_series, freq)
    mkt_ret = get_ann_return(mkt_series, freq)
    port_ret = get_ann_return(return_series, freq)
    return port_ret - (rfr +  beta*(mkt_ret - rfr))

                             
    
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

def get_avg_pos_neg(return_series, pos=True):
    """
    Average positve returns/ Average negative returns
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
    pos_neg_series = util.get_pos_neg_df(return_series,pos)
    
    return pos_neg_series.mean()
    
def get_avg_pos_neg_ratio(return_series):
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
    #compute means
    avg_pos = get_avg_pos_neg(return_series)
    avg_neg = get_avg_pos_neg(return_series, False)
    
    return avg_pos/abs(avg_neg)

def get_pct_pos_neg_periods(return_series, pos=True):
    pos_neg_series = util.get_pos_neg_df(return_series,pos)
    return len(pos_neg_series) / len(return_series)

def get_updown_dev(return_series, freq='1M', target=0, up = False):
    """
    Compute annualized upside/downside dev

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
        upside / downside std deviation.

    """
    #create a upside/downside return column with the positive/negative returns only
    up_down_series = return_series >= target if up else return_series < target
    
    up_down_side_returns = return_series.loc[up_down_series]

    #return annualized std dev of downside
    return get_ann_vol(up_down_side_returns, freq)

def get_up_down_dev_ratio(return_series, freq='M', target = 0):
    return get_updown_dev(return_series, freq, target,True)/get_updown_dev(return_series,freq, target)

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
    down_stddev = get_updown_dev(return_series, freq, target)
    
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

def get_kurtosis(return_series):
    """
    Compute kurtosis of a return series

    Parameters
    ----------
    return_series : series
        returns series.

    Returns
    -------
    double
        kurtosis.

    """
    return return_series.kurtosis()
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

def get_cum_ret(return_series):
    return return_series.add(1).prod(axis=0) - 1

def get_return_stats(df_returns, freq='1M',mkt='SPTR', rfr=0.0, include_fi=True):
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
    df_returns_stats : dataframe

    """
    
    #generate return stats for each strategy
    # df_prices = dm.get_prices_df(df_returns)
    returns_stats_dict = {}
    # mkt_strat = df_returns[df_returns.columns[0]]
    # if include_fi:
    #     fi_mkt_strat = df_returns[df_returns.columns[1]]
    mkt_list = [df_returns.columns[0]]
    if include_fi:
        mkt_list.append(df_returns.columns[1])
    for col in list(df_returns.columns)[2:]:
        df_strat = dm.remove_na(df_returns, col)
        df_prices = dm.get_prices_df(df_strat)
        temp_df = df_returns[mkt_list + [col]].copy()
        temp_df.dropna(inplace=True)
        mkt_strat = temp_df[mkt_list[0]]
        eq_u_df = (temp_df[mkt_strat > 0])
        eq_d_df = (temp_df[ mkt_strat <= 0])
        
        ann_ret = get_ann_return(df_strat[col], freq)
        alpha = 0 if col == mkt_list[0] else get_alpha(df_strat[col],mkt_strat,freq,rfr)
        beta = 1 if col == mkt_list[0] else get_beta(df_strat[col],mkt_strat,freq)
        bull_beta = 1 if col == mkt_list[0] else get_beta(eq_u_df[col],eq_u_df[mkt_list[0]],freq)
        bear_beta = 1 if col == mkt_list[0] else  get_beta(eq_d_df[col],eq_d_df[mkt_list[0]],freq)
        if include_fi:
            fi_mkt_strat = temp_df[mkt_list[1]]
            fi_u_df = (temp_df[fi_mkt_strat > 0])
            fi_d_df = (temp_df[fi_mkt_strat <= 0])
            alpha_fi = 0 if col == mkt_list[1] else get_alpha(df_strat[col],fi_mkt_strat,freq,rfr)
            beta_fi = 1 if col == mkt_list[1] else get_beta(df_strat[col],fi_mkt_strat,freq)
            fi_bull_beta = 1 if col == mkt_list[1] else get_beta(fi_u_df[col],fi_u_df[mkt_list[1]],freq)
            fi_bear_beta = 1 if col == mkt_list[1] else get_beta(fi_d_df[col],fi_d_df[mkt_list[1]],freq)
            
        med_ret = df_strat[col].median()
        avg_ret = df_strat[col].mean()
        avg_up_ret = get_avg_pos_neg(df_strat[col])
        avg_down_ret = get_avg_pos_neg(df_strat[col],False)
        avg_pos_neg = get_avg_pos_neg_ratio(df_strat[col])
        best_period = df_strat[col].max()
        worst_period = df_strat[col].min()
        pct_pos_periods = get_pct_pos_neg_periods(df_strat[col])
        pct_neg_periods = get_pct_pos_neg_periods(df_strat[col], False)
        ann_vol = get_ann_vol(df_strat[col], freq)
        up_dev = get_updown_dev(df_strat[col], freq,up=True)
        down_dev = get_updown_dev(df_strat[col], freq)
        updev_downdev_ratio = get_up_down_dev_ratio(df_strat[col],freq)
        skew = get_skew(df_strat[col])
        kurt = get_kurtosis(df_strat[col])
        max_dd = get_max_dd(df_prices[col])
        ret_vol = get_ret_vol_ratio(df_strat[col],freq)
        sortino = get_sortino_ratio(df_strat[col], freq)
        ret_dd = get_ret_max_dd_ratio(df_strat[col],df_prices[col],freq)
        returns_stats_dict[col] = [ann_ret, alpha, beta, bull_beta, bear_beta, med_ret, avg_ret, avg_up_ret, avg_down_ret,
                                   avg_pos_neg, best_period, worst_period, pct_pos_periods,
                                   pct_neg_periods, ann_vol, up_dev, down_dev, updev_downdev_ratio,
                                   skew, kurt, max_dd,ret_vol,sortino, ret_dd]
        if include_fi:
            returns_stats_dict[col] = [ann_ret, alpha, alpha_fi, beta, bull_beta, bear_beta, beta_fi, fi_bull_beta, fi_bear_beta, 
                                       med_ret, avg_ret, avg_up_ret, avg_down_ret,
                                       avg_pos_neg, best_period, worst_period, pct_pos_periods,
                                       pct_neg_periods, ann_vol, up_dev, down_dev, updev_downdev_ratio,
                                       skew, kurt, max_dd,ret_vol,sortino, ret_dd]
    #Converts hedge_dict to a data grame
    if include_fi:
        df_returns_stats = util.convert_dict_to_df(returns_stats_dict, RETURNS_STATS_FI_INDEX)
    else:
        df_returns_stats = util.convert_dict_to_df(returns_stats_dict, RETURNS_STATS_INDEX)
    return df_returns_stats


                       