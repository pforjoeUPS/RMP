# -*- coding: utf-8 -*-
"""
Created on Tue Oct  1 17:59:28 2019

@author: Powis Forjoe, Maddie Choi, and Zach Wells
"""


import numpy as np
from ..datamanager import data_manager as dm
from .import  util


#TODO: Clean this and merge
RETURNS_STATS_INDEX = ['Annualized Return', 'Equity Alpha', 'Equity Beta','Equity Bull Beta',
                       'Equity Bear Beta', 'Median Period Return','Avg. Period Return',
                       'Avg. Period Up Return', 'Avg. Period Down Return','Avg Pos Return/Avg Neg Return',
                       'Best Period', 'Worst Period','% Positive Periods','% Negative Periods',
                       'Annualized Vol','Upside Deviation','Downside Deviation',
                       'Upside to Downside Deviation Ratio','Skewness', 'Kurtosis',
                       'Max DD','Return/Volatility', 'Sortino Ratio','Return/Max DD']

RETURNS_STATS_BMK_INDEX = ['Annualized Return', 'Excess Return (Ann)','Equity Alpha', 'Equity Beta','Equity Bull Beta',
                           'Equity Bear Beta', 'Bmk Beta','Median Period Return','Avg. Period Return',
                           'Avg. Period Up Return', 'Avg. Period Down Return','Avg Pos Return/Avg Neg Return',
                           'Best Period', 'Worst Period','% Positive Periods','% Negative Periods',
                           'Annualized Vol','Tracking Error','Upside Deviation','Downside Deviation',
                           'Upside to Downside Deviation Ratio','Skewness', 'Kurtosis',
                           'Max DD','Return/Volatility', 'IR','Sortino Ratio','Return/Max DD']

RETURNS_STATS_FI_INDEX = ['Annualized Return', 'Equity Alpha',  'FI Alpha', 'Equity Beta',
                          'Equity Bull Beta','Equity Bear Beta','FI Beta','FI Bull Beta',
                          'FI Bear Beta','Median Period Return','Avg. Period Return',
                          'Avg. Period Up Return', 'Avg. Period Down Return',
                          'Avg Pos Return/Avg Neg Return','Best Period', 'Worst Period',
                          '% Positive Periods','% Negative Periods','Annualized Vol',
                          'Upside Deviation','Downside Deviation','Upside to Downside Deviation Ratio',
                          'Skewness', 'Kurtosis','Max DD','Return/Volatility', 'Sortino Ratio','Return/Max DD']

RETURNS_STATS_FI_BMK_INDEX = ['Annualized Return', 'Excess Return (Ann)','Equity Alpha',  'FI Alpha', 'Equity Beta',
                              'Equity Bull Beta','Equity Bear Beta','FI Beta','FI Bull Beta',
                              'FI Bear Beta','Bmk Beta','Median Period Return','Avg. Period Return',
                              'Avg. Period Up Return', 'Avg. Period Down Return',
                              'Avg Pos Return/Avg Neg Return','Best Period', 'Worst Period',
                              '% Positive Periods','% Negative Periods','Annualized Vol','Tracking Error',
                              'Upside Deviation','Downside Deviation',
                              'Upside to Downside Deviation Ratio','Skewness', 'Kurtosis','Max DD',
                              'Return/Volatility', 'IR','Sortino Ratio','Return/Max DD']

def get_comp_returns(return_series):
    return return_series.add(1).prod()-1

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

#TODO: review this method, delete if no longer needed
def get_mkt_series(freq='1M',mkt='SPTR'):
    mkt_dict = dm.get_equity_hedge_returns(equity='SPTR',only_equity=True)
    mkt_df = mkt_dict[dm.switch_freq_string(freq)]
    return mkt_df[mkt]
    
def get_beta(return_series, mkt_series):
    return return_series.cov(mkt_series)/mkt_series.var()

def get_alpha(return_series, mkt_series, freq = '1M', rfr = 0.0):
    beta = get_beta(return_series,mkt_series)
    mkt_ret = get_ann_return(mkt_series, freq)
    port_ret = get_ann_return(return_series, freq)
    return port_ret - (rfr +  beta*(mkt_ret - rfr))                            

def get_up_down_capture_ratio(return_series, mkt_series, upside=True):
    mkt_cap = util.get_pos_neg_df(mkt_series, pos=upside)
    ret_cap = dm.merge_data_frames(mkt_cap, return_series, True)[return_series.name]
    return get_comp_returns(ret_cap)/get_comp_returns(mkt_cap)    

def get_max_dd(return_series):
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
    price_series = dm.get_price_series(return_series)
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
    max_dd_freq = return_series.min()
    
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
    
    try:
        return avg_pos/abs(avg_neg)
    except ZeroDivisionError:
        return float('inf')

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

def get_sharpe_ratio(return_series,freq='1M',rfr=0.0):
    """
    Compute Return/Vol ratio

    Parameters
    ----------
    return_series : series
        returns series.
    freq : string, optional
        frequency. The default is '1M'.

    Returns
    -------
    double
        Return/vol ratio

    """
    
    #calculate annulaized return and vol
    ann_ret = get_ann_return(return_series, freq)
    ann_vol = get_ann_vol(return_series, freq)
     
    #calculate ratio
    return (ann_ret - rfr) / ann_vol
    
def get_ret_max_dd_ratio(return_series,freq='1M'):
    """
    Compute Return/Max DD ratio

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
        Return/Max DD ratio

    """
    #compute annual returns and Max DD
    ann_ret = get_ann_return(return_series, freq)
    max_dd = get_max_dd(return_series)
    
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

def get_median(return_series):
    """
    Compute median of a return series

    Parameters
    ----------
    return_series : series
        returns series.

    Returns
    -------
    double
        skew.

    """
    return return_series.median()

def get_mean(return_series):
    """
    Compute mean of a return series

    Parameters
    ----------
    return_series : series
        returns series.

    Returns
    -------
    double
        kurtosis.

    """
    return return_series.mean()

def get_max(return_series):
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
    return return_series.max()

def get_min(return_series):
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
    return return_series.min()

def get_ret_max_dd_freq_ratio(return_series, price_series, freq, max_3m_dd=False):
    """
    Compute Return/Max 1M/3M DD ratio

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
        Return/Max 1M/3M DD ratio

    """
    #calculate annual return
    ann_ret = get_ann_return(return_series, freq)
    max_freq_dd = get_max_dd_freq(price_series, freq, max_3m_dd)['max_dd']
    
    #compute ratio
    return ann_ret/abs(max_freq_dd)

def get_cum_ret(return_series):
    return return_series.add(1).prod(axis=0) - 1

def get_port_analytics(return_series, freq = '1M',rfr=0.0, target=0.0):
    ann_ret = get_ann_return(return_series, freq)
    med_ret = get_median(return_series)
    avg_ret = get_mean(return_series)
    avg_up_ret = get_avg_pos_neg(return_series)
    avg_down_ret = get_avg_pos_neg(return_series,False)
    avg_pos_neg = get_avg_pos_neg_ratio(return_series)
    best_period = get_max(return_series)
    worst_period = get_min(return_series)
    pct_pos_periods = get_pct_pos_neg_periods(return_series)
    pct_neg_periods = get_pct_pos_neg_periods(return_series, False)
    ann_vol = get_ann_vol(return_series, freq)
    up_dev = get_updown_dev(return_series, freq,up=True)
    down_dev = get_updown_dev(return_series, freq)
    up_down_dev_ratio = get_up_down_dev_ratio(return_series,freq)
    skew = get_skew(return_series)
    kurt = get_kurtosis(return_series)
    max_dd = get_max_dd(return_series)
    ret_vol = get_sharpe_ratio(return_series,freq)
    sortino = get_sortino_ratio(return_series, freq)
    ret_dd = get_ret_max_dd_ratio(return_series,freq)
    return {'ann_ret': ann_ret, 'median_ret': med_ret, 'avg_ret': avg_ret, 
            'avg_pos_ret': avg_up_ret, 'avg_neg_ret': avg_down_ret, 
            'avg_pos_neg_ret': avg_pos_neg, 'best_period': best_period,
            'worst_period': worst_period, 'pct_pos_periods': pct_pos_periods,
            'pct_neg_periods': pct_neg_periods, 'ann_vol': ann_vol,
            'up_dev': up_dev,'down_dev': down_dev,'up_down_dev': up_down_dev_ratio,
            'vol_down_dev':ann_vol/down_dev, 'skew': skew, 'kurt':kurt,
            'max_dd': max_dd, 'ret_vol': ret_vol, 'sortino':sortino, 'ret_dd':ret_dd}

def get_active_analytics(return_series, bmk_series=dm.pd.Series(dtype='float64'), freq='1M', empty=False):
    empty_analytics = {'bmk_name':None, 'bmk_beta': None, 'excess_ret': None,
                       'te': None, 'dwnside_te': None, 'te_dwnside_te': None, 'ir': None, 'ir_asym': None}
    if empty:
        return empty_analytics
    else:
        try:
            bmk_name = bmk_series.name
            df_port_bmk = dm.merge_data_frames(return_series,bmk_series)
            df_port_bmk.columns = ['port', 'bmk']
            df_port_bmk['active'] = df_port_bmk['port'] - df_port_bmk['bmk']
            beta_bmk = get_beta(df_port_bmk['port'],df_port_bmk['bmk'])
            excess_ret = get_ann_return(df_port_bmk['port'], freq) - get_ann_return(df_port_bmk['bmk'], freq)
            te = get_ann_vol(df_port_bmk['active'], freq)
            dwnside_te = get_updown_dev(df_port_bmk['active'], freq)
            ir = None if te == 0.0 else excess_ret/te
            ir_asym = None if dwnside_te == 0.0 else excess_ret/dwnside_te
            return {'bmk_name':bmk_name, 'bmk_beta': beta_bmk, 'excess_ret': excess_ret, 
                    'te': te, 'dwnside_te': dwnside_te, 'te_dwnside_te':te/dwnside_te,'ir': ir, 'ir_asym': ir_asym}
        except KeyError:
            print('Skipping active stats for {}.'.format(return_series.name))
            return empty_analytics

#TODO: delete if no longer needed
def get_return_stats_1(df_returns, 
                     # df_bmk = dm.pd.DataFrame(),
                     freq='1M',rfr=0.0, include_fi=True, include_bmk=False):
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
    skip = 1
    if include_fi and include_bmk:
        mkt_list.append(df_returns.columns[1])
        mkt_list.append(df_returns.columns[2])
        skip += 2
    elif include_fi or include_bmk:
        mkt_list.append(df_returns.columns[1])
        skip += 1
    for col in list(df_returns.columns)[skip:]:
        df_strat = dm.remove_na(df_returns, col)[col]
        # if df_bmk.empty:
        #     df_strat = dm.remove_na(df_returns, col)[col]
        # else:
        #     df_port_bmk = dm.merge_data_frames(df_returns[[col]], df_bmk[[col]])
        #     df_port_bmk.columns = ['port', 'bmk']
        #     df_port_bmk['active'] = df_port_bmk['port'] - df_port_bmk['bmk']
        #     df_port_bmk.dropna(inplace=True)
            
        #     df_strat = df_port_bmk['port']
        #     df_strat_b = df_port_bmk['bmk']
        #     df_strat_a = df_port_bmk['active']
            
        price_series = dm.get_price_series(df_strat)
        temp_df = df_returns[mkt_list + [col]].copy()
        temp_df.dropna(inplace=True)
        mkt_strat = temp_df[mkt_list[0]]
        eq_u_df = (temp_df[mkt_strat > 0])
        eq_d_df = (temp_df[ mkt_strat <= 0])
        
        ann_ret = get_ann_return(df_strat, freq)
        alpha = 0 if col == mkt_list[0] else get_alpha(df_strat,mkt_strat,freq,rfr)
        beta = 1 if col == mkt_list[0] else get_beta(df_strat,mkt_strat)
        bull_beta = 1 if col == mkt_list[0] else get_beta(eq_u_df[col],eq_u_df[mkt_list[0]])
        bear_beta = 1 if col == mkt_list[0] else  get_beta(eq_d_df[col],eq_d_df[mkt_list[0]])
        if include_fi:
            fi_mkt_strat = temp_df[mkt_list[1]]
            fi_u_df = (temp_df[fi_mkt_strat > 0])
            fi_d_df = (temp_df[fi_mkt_strat <= 0])
            alpha_fi = 0 if col == mkt_list[1] else get_alpha(df_strat,fi_mkt_strat,freq,rfr)
            beta_fi = 1 if col == mkt_list[1] else get_beta(df_strat,fi_mkt_strat)
            fi_bull_beta = 1 if col == mkt_list[1] else get_beta(fi_u_df[col],fi_u_df[mkt_list[1]])
            fi_bear_beta = 1 if col == mkt_list[1] else get_beta(fi_d_df[col],fi_d_df[mkt_list[1]])
        if include_fi and include_bmk:
            bmk_strat = temp_df[mkt_list[2]]
            beta_bmk = 1 if col == mkt_list[2] else get_beta(df_strat,bmk_strat)
            active_strat = None if col == mkt_list[2] else df_strat - bmk_strat
            excess_ret = 0 if col == mkt_list[2] else ann_ret - get_ann_return(bmk_strat, freq)
            te = None if col == mkt_list[2] else get_ann_vol(active_strat, freq)
            ir = None if col == mkt_list[2] else excess_ret/te
        elif include_bmk:
            bmk_strat = temp_df[mkt_list[1]]
            beta_bmk = 1 if col == mkt_list[1] else get_beta(df_strat,bmk_strat)
            active_strat = None if col == mkt_list[1] else df_strat - bmk_strat
            excess_ret = 0 if col == mkt_list[1] else ann_ret - get_ann_return(bmk_strat, freq)
            te = None if col == mkt_list[1] else get_ann_vol(active_strat, freq)
            ir = None if col == mkt_list[1] else excess_ret/te
            
            
        med_ret = df_strat.median()
        avg_ret = df_strat.mean()
        avg_up_ret = get_avg_pos_neg(df_strat)
        avg_down_ret = get_avg_pos_neg(df_strat,False)
        avg_pos_neg = get_avg_pos_neg_ratio(df_strat)
        best_period = df_strat.max()
        worst_period = df_strat.min()
        pct_pos_periods = get_pct_pos_neg_periods(df_strat)
        pct_neg_periods = get_pct_pos_neg_periods(df_strat, False)
        ann_vol = get_ann_vol(df_strat, freq)
        up_dev = get_updown_dev(df_strat, freq,up=True)
        down_dev = get_updown_dev(df_strat, freq)
        updev_downdev_ratio = get_up_down_dev_ratio(df_strat,freq)
        skew = get_skew(df_strat)
        kurt = get_kurtosis(df_strat)
        max_dd = get_max_dd(df_strat)
        ret_vol = get_sharpe_ratio(df_strat,freq)
        sortino = get_sortino_ratio(df_strat, freq)
        ret_dd = get_ret_max_dd_ratio(df_strat,freq)
        
        # if not df_bmk.empty:
        #     ann_ret_b = get_ann_return(df_strat_b, freq)
        #     excess_ret = ann_ret - ann_ret_b
        #     ann_vol_b = get_ann_vol(df_strat_b, freq)
        #     te = get_ann_vol(df_strat_a, freq)
        #     beta_bmk = get_beta(df_strat, df_strat_b)
        #     ir = excess_ret/te
        returns_stats_dict[col] = [ann_ret, alpha, beta, bull_beta, bear_beta, med_ret, avg_ret, avg_up_ret,
                                   avg_down_ret,avg_pos_neg, best_period, worst_period, pct_pos_periods,
                                   pct_neg_periods, ann_vol, up_dev, down_dev, updev_downdev_ratio,
                                   skew, kurt, max_dd,ret_vol,sortino, ret_dd]
        if include_bmk and include_fi:
            returns_stats_dict[col] = [ann_ret, excess_ret, alpha, alpha_fi, beta, bull_beta, bear_beta,
                                       beta_fi, fi_bull_beta, fi_bear_beta, 
                                       beta_bmk,med_ret, avg_ret, avg_up_ret, avg_down_ret,
                                       avg_pos_neg, best_period, worst_period, pct_pos_periods,
                                       pct_neg_periods, ann_vol, te, up_dev, down_dev, updev_downdev_ratio,
                                       skew, kurt, max_dd,ret_vol,ir,sortino, ret_dd]
        elif include_fi:
            returns_stats_dict[col] = [ann_ret, alpha, alpha_fi, beta, bull_beta, bear_beta, beta_fi, fi_bull_beta, fi_bear_beta, 
                                       med_ret, avg_ret, avg_up_ret, avg_down_ret,
                                       avg_pos_neg, best_period, worst_period, pct_pos_periods,
                                       pct_neg_periods, ann_vol, up_dev, down_dev, updev_downdev_ratio,
                                       skew, kurt, max_dd,ret_vol,sortino, ret_dd]
        
        elif include_bmk:
            returns_stats_dict[col] = [ann_ret, excess_ret, alpha, beta, bull_beta, bear_beta,beta_bmk,
                                       med_ret, avg_ret, avg_up_ret, avg_down_ret,
                                       avg_pos_neg, best_period, worst_period, pct_pos_periods,
                                       pct_neg_periods, ann_vol, te, up_dev, down_dev, updev_downdev_ratio,
                                       skew, kurt, max_dd,ret_vol, ir, sortino, ret_dd]
    #Converts hedge_dict to a data grame
    if include_bmk and include_fi:
        df_returns_stats = util.convert_dict_to_df(returns_stats_dict, RETURNS_STATS_FI_BMK_INDEX)
    elif include_fi:
        df_returns_stats = util.convert_dict_to_df(returns_stats_dict, RETURNS_STATS_FI_INDEX)
    elif include_bmk:
        df_returns_stats = util.convert_dict_to_df(returns_stats_dict, RETURNS_STATS_BMK_INDEX)
    else:
        df_returns_stats = util.convert_dict_to_df(returns_stats_dict, RETURNS_STATS_INDEX)
    return df_returns_stats

#TODO: delete if no longer needed
def get_return_stats(df_returns,freq='1M',rfr=0.0, include_fi=True, include_cm=False, include_dxy=False,
                     include_bmk=False,df_bmk = dm.pd.DataFrame(), bmk_dict={}):
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
    skip = 1
    if include_fi:
        mkt_list.append(df_returns.columns[1])
        # mkt_list.append(df_returns.columns[2])
        skip += 1
    for col in list(df_returns.columns)[skip:]:
        df_strat = dm.remove_na(df_returns, col)[col]
        # if df_bmk.empty:
        #     df_strat = dm.remove_na(df_returns, col)[col]
        # else:
        #     df_port_bmk = dm.merge_data_frames(df_returns[[col]], df_bmk[[col]])
        #     df_port_bmk.columns = ['port', 'bmk']
        #     df_port_bmk['active'] = df_port_bmk['port'] - df_port_bmk['bmk']
        #     df_port_bmk.dropna(inplace=True)
            
        #     df_strat = df_port_bmk['port']
        #     df_strat_b = df_port_bmk['bmk']
        #     df_strat_a = df_port_bmk['active']
            
        price_series = dm.get_price_series(df_strat)
        temp_df = df_returns[mkt_list + [col]].copy()
        temp_df.dropna(inplace=True)
        mkt_strat = temp_df[mkt_list[0]]
        eq_u_df = (temp_df[mkt_strat > 0])
        eq_d_df = (temp_df[ mkt_strat <= 0])
        
        ann_ret = get_ann_return(df_strat, freq)
        alpha = 0 if col == mkt_list[0] else get_alpha(df_strat,mkt_strat,freq,rfr)
        beta = 1 if col == mkt_list[0] else get_beta(df_strat,mkt_strat)
        bull_beta = 1 if col == mkt_list[0] else get_beta(eq_u_df[col],eq_u_df[mkt_list[0]])
        bear_beta = 1 if col == mkt_list[0] else  get_beta(eq_d_df[col],eq_d_df[mkt_list[0]])
        if include_fi:
            fi_mkt_strat = temp_df[mkt_list[1]]
            fi_u_df = (temp_df[fi_mkt_strat > 0])
            fi_d_df = (temp_df[fi_mkt_strat <= 0])
            alpha_fi = 0 if col == mkt_list[1] else get_alpha(df_strat,fi_mkt_strat,freq,rfr)
            beta_fi = 1 if col == mkt_list[1] else get_beta(df_strat,fi_mkt_strat)
            fi_bull_beta = 1 if col == mkt_list[1] else get_beta(fi_u_df[col],fi_u_df[mkt_list[1]])
            fi_bear_beta = 1 if col == mkt_list[1] else get_beta(fi_d_df[col],fi_d_df[mkt_list[1]])
        if include_cm:
            cm_mkt_strat = temp_df[mkt_list[1]]
            beta_cm = 1 if col == mkt_list[1] else get_beta(df_strat,cm_mkt_strat)
        if include_dxy:
            dxy_mkt_strat = temp_df[mkt_list[1]]
            beta_dxy = 1 if col == mkt_list[1] else get_beta(df_strat,dxy_mkt_strat)
            
        if include_bmk:
            try:
                bmk_name = bmk_dict[col]
                df_port_bmk = dm.merge_data_frames(df_returns[[col]],df_bmk[[bmk_name]])
                df_port_bmk.columns = ['port', 'bmk']
                df_port_bmk['active'] = df_port_bmk['port'] - df_port_bmk['bmk']
                beta_bmk = get_beta(df_strat,df_port_bmk['bmk'])
                excess_ret = ann_ret - get_ann_return(df_port_bmk['bmk'], freq)
                te = get_ann_vol(df_port_bmk['active'], freq)
                te_asym = get_updown_dev(df_port_bmk['active'], freq)
                ir = None if te == 0.0 else excess_ret/te
                ir_asym = None if te_asym == 0.0 else excess_ret/te_asym
            except KeyError:
                print('Skipping active stats for {}.'.format(col))
                bmk_name=None
                beta_bmk = None
                excess_ret = None
                te = None
                te_asym = None
                ir = None
                ir_asym = None
                pass
            
            
        med_ret = df_strat.median()
        avg_ret = df_strat.mean()
        avg_up_ret = get_avg_pos_neg(df_strat)
        avg_down_ret = get_avg_pos_neg(df_strat,False)
        avg_pos_neg = get_avg_pos_neg_ratio(df_strat)
        best_period = df_strat.max()
        worst_period = df_strat.min()
        pct_pos_periods = get_pct_pos_neg_periods(df_strat)
        pct_neg_periods = get_pct_pos_neg_periods(df_strat, False)
        ann_vol = get_ann_vol(df_strat, freq)
        up_dev = get_updown_dev(df_strat, freq,up=True)
        down_dev = get_updown_dev(df_strat, freq)
        updev_downdev_ratio = get_up_down_dev_ratio(df_strat,freq)
        skew = get_skew(df_strat)
        kurt = get_kurtosis(df_strat)
        max_dd = get_max_dd(df_strat)
        ret_vol = get_sharpe_ratio(df_strat,freq)
        sortino = get_sortino_ratio(df_strat, freq)
        ret_dd = get_ret_max_dd_ratio(df_strat,freq)
        
        # if not df_bmk.empty:
        #     ann_ret_b = get_ann_return(df_strat_b, freq)
        #     excess_ret = ann_ret - ann_ret_b
        #     ann_vol_b = get_ann_vol(df_strat_b, freq)
        #     te = get_ann_vol(df_strat_a, freq)
        #     beta_bmk = get_beta(df_strat, df_strat_b)
        #     ir = excess_ret/te
        returns_stats_dict[col] = [ann_ret, alpha, beta, bull_beta, bear_beta, med_ret, avg_ret, avg_up_ret,
                                   avg_down_ret,avg_pos_neg, best_period, worst_period, pct_pos_periods,
                                   pct_neg_periods, ann_vol, up_dev, down_dev, updev_downdev_ratio,
                                   skew, kurt, max_dd,ret_vol,sortino, ret_dd]
        if include_bmk and include_fi:
            returns_stats_dict[col] = [bmk_name, ann_ret, excess_ret, alpha, alpha_fi, beta, bull_beta, bear_beta,
                                       beta_fi, fi_bull_beta, fi_bear_beta, 
                                       beta_bmk,med_ret, avg_ret, avg_up_ret, avg_down_ret,
                                       avg_pos_neg, best_period, worst_period, pct_pos_periods,
                                       pct_neg_periods, ann_vol, up_dev, down_dev, te,te_asym, updev_downdev_ratio,
                                       skew, kurt, max_dd,ret_vol,sortino, ret_dd,ir,ir_asym]
        elif include_fi:
            returns_stats_dict[col] = [ann_ret, alpha, alpha_fi, beta, bull_beta, bear_beta, beta_fi, fi_bull_beta, fi_bear_beta, 
                                       med_ret, avg_ret, avg_up_ret, avg_down_ret,
                                       avg_pos_neg, best_period, worst_period, pct_pos_periods,
                                       pct_neg_periods, ann_vol, up_dev, down_dev, updev_downdev_ratio,
                                       skew, kurt, max_dd,ret_vol,sortino, ret_dd]
        
        elif include_bmk:
            returns_stats_dict[col] = [bmk_name, ann_ret, excess_ret, alpha, beta, bull_beta, bear_beta,beta_bmk,
                                       med_ret, avg_ret, avg_up_ret, avg_down_ret,
                                       avg_pos_neg, best_period, worst_period, pct_pos_periods,
                                       pct_neg_periods, ann_vol, up_dev, down_dev, te,te_asym, updev_downdev_ratio,
                                       skew, kurt, max_dd,ret_vol, sortino, ret_dd, ir,ir_asym]
    #Converts hedge_dict to a data grame
    rs_bmk_index = ['Bmk Name','Annualized Return', 'Excess Return (Ann)','Equity Alpha', 'Equity Beta','Equity Bull Beta',
                               'Equity Bear Beta', 'Bmk Beta','Median Period Return','Avg. Period Return',
                               'Avg. Period Up Return', 'Avg. Period Down Return','Avg Pos Return/Avg Neg Return',
                               'Best Period', 'Worst Period','% Positive Periods','% Negative Periods',
                               'Annualized Vol','Upside Deviation','Downside Deviation','Tracking Error (TE)','Asymmetric TE',
                               'Upside to Downside Deviation Ratio','Skewness', 'Kurtosis',
                               'Max DD','Return/Volatility','Sortino Ratio','Return/Max DD', 'Information Ratio (IR)','Asymmetric IR']
    rs_fi_bmk_index = ['Bmk Name','Annualized Return', 'Excess Return (Ann)','Equity Alpha',  'FI Alpha', 'Equity Beta',
                                  'Equity Bull Beta','Equity Bear Beta','FI Beta','FI Bull Beta',
                                  'FI Bear Beta','Bmk Beta','Median Period Return','Avg. Period Return',
                                  'Avg. Period Up Return', 'Avg. Period Down Return',
                                  'Avg Pos Return/Avg Neg Return','Best Period', 'Worst Period',
                                  '% Positive Periods','% Negative Periods','Annualized Vol','Upside Deviation',
                                  'Downside Deviation','Tracking Error (TE)','Asymmetric TE','Upside to Downside Deviation Ratio',
                                  'Skewness', 'Kurtosis','Max DD','Return/Volatility','Sortino Ratio','Return/Max DD', 'Informatio Ratio (IR)','Asymmetric IR']

    if include_bmk and include_fi:
        df_returns_stats = util.convert_dict_to_df(returns_stats_dict, rs_fi_bmk_index)
    elif include_fi:
        df_returns_stats = util.convert_dict_to_df(returns_stats_dict, RETURNS_STATS_FI_INDEX)
    elif include_bmk:
        df_returns_stats = util.convert_dict_to_df(returns_stats_dict, rs_bmk_index)
    else:
        df_returns_stats = util.convert_dict_to_df(returns_stats_dict, RETURNS_STATS_INDEX)
    return df_returns_stats

#TODO: delete if no longer needed
def get_ret_stats(df_returns,freq='1M',rfr=0.0, include_fi=True, include_cm=False, include_dxy=False,
                     include_bmk=False,df_bmk = dm.pd.DataFrame(), bmk_dict={}):
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
    returns_stats_dict = {}
    mkt_list = [df_returns.columns[0]]
    skip = 1
    if include_fi:
        mkt_list.append(df_returns.columns[1])
        skip += 1
    for col in list(df_returns.columns)[skip:]:
        df_strat = dm.remove_na(df_returns, col)[col]
            
        price_series = dm.get_price_series(df_strat)
        temp_df = df_returns[mkt_list + [col]].copy()
        temp_df.dropna(inplace=True)
        mkt_strat = temp_df[mkt_list[0]]
        eq_u_df = (temp_df[mkt_strat > 0])
        eq_d_df = (temp_df[ mkt_strat <= 0])
        
        ann_ret = get_ann_return(df_strat, freq)
        alpha = 0 if col == mkt_list[0] else get_alpha(df_strat,mkt_strat,freq,rfr)
        beta = 1 if col == mkt_list[0] else get_beta(df_strat,mkt_strat)
        bull_beta = 1 if col == mkt_list[0] else get_beta(eq_u_df[col],eq_u_df[mkt_list[0]])
        bear_beta = 1 if col == mkt_list[0] else  get_beta(eq_d_df[col],eq_d_df[mkt_list[0]])
        if include_fi:
            fi_mkt_strat = temp_df[mkt_list[1]]
            fi_u_df = (temp_df[fi_mkt_strat > 0])
            fi_d_df = (temp_df[fi_mkt_strat <= 0])
            alpha_fi = 0 if col == mkt_list[1] else get_alpha(df_strat,fi_mkt_strat,freq,rfr)
            beta_fi = 1 if col == mkt_list[1] else get_beta(df_strat,fi_mkt_strat)
            fi_bull_beta = 1 if col == mkt_list[1] else get_beta(fi_u_df[col],fi_u_df[mkt_list[1]])
            fi_bear_beta = 1 if col == mkt_list[1] else get_beta(fi_d_df[col],fi_d_df[mkt_list[1]])
        else:
            alpha_fi = None
            beta_fi = None
            fi_bull_beta = None
            fi_bear_beta = None
        if include_cm:
            cm_mkt_strat = temp_df[mkt_list[1]]
            beta_cm = 1 if col == mkt_list[1] else get_beta(df_strat,cm_mkt_strat)
        if include_dxy:
            dxy_mkt_strat = temp_df[mkt_list[1]]
            beta_dxy = 1 if col == mkt_list[1] else get_beta(df_strat,dxy_mkt_strat)
            
        if include_bmk:
            try:
                bmk_name = bmk_dict[col]
                df_port_bmk = dm.merge_data_frames(df_returns[[col]],df_bmk[[bmk_name]])
                df_port_bmk.columns = ['port', 'bmk']
                df_port_bmk['active'] = df_port_bmk['port'] - df_port_bmk['bmk']
                beta_bmk = get_beta(df_strat,df_port_bmk['bmk'])
                excess_ret = ann_ret - get_ann_return(df_port_bmk['bmk'], freq)
                te = get_ann_vol(df_port_bmk['active'], freq)
                te_asym = get_updown_dev(df_port_bmk['active'], freq)
                ir = None if te == 0.0 else excess_ret/te
                ir_asym = None if te_asym == 0.0 else excess_ret/te_asym
            except KeyError:
                print('Skipping active stats for {}.'.format(col))
                bmk_name=None
                beta_bmk = None
                excess_ret = None
                te = None
                te_asym = None
                ir = None
                ir_asym = None
                pass
        else:
            bmk_name=None
            beta_bmk = None
            excess_ret = None
            te = None
            te_asym = None
            ir = None
            ir_asym = None
            
            
        med_ret = df_strat.median()
        avg_ret = df_strat.mean()
        avg_up_ret = get_avg_pos_neg(df_strat)
        avg_down_ret = get_avg_pos_neg(df_strat,False)
        avg_pos_neg = get_avg_pos_neg_ratio(df_strat)
        best_period = df_strat.max()
        worst_period = df_strat.min()
        pct_pos_periods = get_pct_pos_neg_periods(df_strat)
        pct_neg_periods = get_pct_pos_neg_periods(df_strat, False)
        ann_vol = get_ann_vol(df_strat, freq)
        up_dev = get_updown_dev(df_strat, freq,up=True)
        down_dev = get_updown_dev(df_strat, freq)
        updev_downdev_ratio = get_up_down_dev_ratio(df_strat,freq)
        skew = get_skew(df_strat)
        kurt = get_kurtosis(df_strat)
        max_dd = get_max_dd(df_strat)
        ret_vol = get_sharpe_ratio(df_strat,freq)
        sortino = get_sortino_ratio(df_strat, freq)
        ret_dd = get_ret_max_dd_ratio(df_strat,freq)
        
        # if not df_bmk.empty:
        #     ann_ret_b = get_ann_return(df_strat_b, freq)
        #     excess_ret = ann_ret - ann_ret_b
        #     ann_vol_b = get_ann_vol(df_strat_b, freq)
        #     te = get_ann_vol(df_strat_a, freq)
        #     beta_bmk = get_beta(df_strat, df_strat_b)
        #     ir = excess_ret/te
        returns_stats_dict[col] = [bmk_name, ann_ret, excess_ret, alpha, alpha_fi, beta, bull_beta, bear_beta,
                                   beta_fi, fi_bull_beta, fi_bear_beta, 
                                   beta_bmk,med_ret, avg_ret, avg_up_ret, avg_down_ret,
                                   avg_pos_neg, best_period, worst_period, pct_pos_periods,
                                   pct_neg_periods, ann_vol, up_dev, down_dev, te,te_asym, updev_downdev_ratio,
                                   skew, kurt, max_dd,ret_vol,sortino, ret_dd,ir,ir_asym]
        # if include_bmk and include_fi:
        #     returns_stats_dict[col] = [bmk_name, ann_ret, excess_ret, alpha, alpha_fi, beta, bull_beta, bear_beta,
        #                                beta_fi, fi_bull_beta, fi_bear_beta, 
        #                                beta_bmk,med_ret, avg_ret, avg_up_ret, avg_down_ret,
        #                                avg_pos_neg, best_period, worst_period, pct_pos_periods,
        #                                pct_neg_periods, ann_vol, up_dev, down_dev, te,te_asym, updev_downdev_ratio,
        #                                skew, kurt, max_dd,ret_vol,sortino, ret_dd,ir,ir_asym]
        # elif include_fi:
        #     returns_stats_dict[col] = [ann_ret, alpha, alpha_fi, beta, bull_beta, bear_beta, beta_fi, fi_bull_beta, fi_bear_beta, 
        #                                med_ret, avg_ret, avg_up_ret, avg_down_ret,
        #                                avg_pos_neg, best_period, worst_period, pct_pos_periods,
        #                                pct_neg_periods, ann_vol, up_dev, down_dev, updev_downdev_ratio,
        #                                skew, kurt, max_dd,ret_vol,sortino, ret_dd]
        
        # elif include_bmk:
        #     returns_stats_dict[col] = [bmk_name, ann_ret, excess_ret, alpha, beta, bull_beta, bear_beta,beta_bmk,
        #                                med_ret, avg_ret, avg_up_ret, avg_down_ret,
        #                                avg_pos_neg, best_period, worst_period, pct_pos_periods,
        #                                pct_neg_periods, ann_vol, up_dev, down_dev, te,te_asym, updev_downdev_ratio,
        #                                skew, kurt, max_dd,ret_vol, sortino, ret_dd, ir,ir_asym]
    #Converts hedge_dict to a data grame
    # rs_bmk_index = ['Bmk Name','Annualized Return', 'Excess Return (Ann)','Equity Alpha', 'Equity Beta','Equity Bull Beta',
    #                            'Equity Bear Beta', 'Bmk Beta','Median Period Return','Avg. Period Return',
    #                            'Avg. Period Up Return', 'Avg. Period Down Return','Avg Pos Return/Avg Neg Return',
    #                            'Best Period', 'Worst Period','% Positive Periods','% Negative Periods',
    #                            'Annualized Vol','Upside Deviation','Downside Deviation','Tracking Error (TE)','Asymmetric TE',
    #                            'Upside to Downside Deviation Ratio','Skewness', 'Kurtosis',
    #                            'Max DD','Return/Volatility','Sortino Ratio','Return/Max DD', 'Information Ratio (IR)','Asymmetric IR']
    rs_fi_bmk_index = ['Bmk Name','Annualized Return', 'Excess Return (Ann)','Equity Alpha',  'FI Alpha', 'Equity Beta',
                                  'Equity Bull Beta','Equity Bear Beta','FI Beta','FI Bull Beta',
                                  'FI Bear Beta','Bmk Beta','Median Period Return','Avg. Period Return',
                                  'Avg. Period Up Return', 'Avg. Period Down Return',
                                  'Avg Pos Return/Avg Neg Return','Best Period', 'Worst Period',
                                  '% Positive Periods','% Negative Periods','Annualized Vol','Upside Deviation',
                                  'Downside Deviation','Tracking Error (TE)','Asymmetric TE','Upside to Downside Deviation Ratio',
                                  'Skewness', 'Kurtosis','Max DD','Return/Volatility','Sortino Ratio','Return/Max DD', 'Informatio Ratio (IR)','Asymmetric IR']
    df_returns_stats = util.convert_dict_to_df(returns_stats_dict, rs_fi_bmk_index)
    if not include_fi:
        df_returns_stats.drop(['FI Alpha','FI Beta','FI Bull Beta','FI Bear Beta'],
                                 axis=0, inplace=True)
    if not include_bmk:
        df_returns_stats.drop(['Bmk Name','Excess Return (Ann)','Bmk Beta','Tracking Error (TE)','Asymmetric TE','Informatio Ratio (IR)','Asymmetric IR'],
                                     axis=0, inplace=True)

    return df_returns_stats

#TODO: review this method, delete if no longer needed
def add_mkt_data(mkt_df,mkt_key, asset_class):
    return mkt_df[[mkt_key[asset_class]]]

#TODO: review this method, delete if no longer needed
def get_mkt_ret_data(mkt_df,mkt_key, bool_dict, main_asset_class = 'Equity'):
    mkt_ret_df = add_mkt_data(mkt_df, mkt_key, main_asset_class)
    for bool_key in bool_dict:
        if bool_dict[bool_key]:
            try:
                mkt_ret_df = dm.merge_data_frames(mkt_ret_df, add_mkt_data(mkt_df, mkt_key, bool_key))
            except KeyError:
                print(f'No {bool_key} market data...')
                bool_dict[bool_key] = False
                pass
    bool_dict[main_asset_class] = True
    return {'mkt_ret_df': mkt_ret_df, 'bool_dict': bool_dict}
                
def get_mkt_analytics(mkt_ret_df, mkt, strat, freq='1M', rfr=0.0, empty=False):    
    empty_analytics = {'alpha':None, 'beta':None, 'up_beta':None, 'dwn_beta':None,
            'corr': None,'up_corr': None,'dwn_corr': None }
    if empty:
        return empty_analytics
    else:
        try:
            mkt_series = mkt_ret_df[mkt]
            return_series = mkt_ret_df[strat]
            mkt_up_df = (mkt_ret_df[mkt_series > 0])
            mkt_dwn_df = (mkt_ret_df[mkt_series <= 0])
            
            mkt_alpha = 0 if strat == mkt else get_alpha(return_series,mkt_series,freq,rfr)
            mkt_beta = 1 if strat == mkt else get_beta(return_series,mkt_series)
            mkt_up_beta = 1 if strat == mkt else get_beta(mkt_up_df[strat],mkt_up_df[mkt])
            mkt_dwn_beta = 1 if strat == mkt else get_beta(mkt_dwn_df[strat],mkt_dwn_df[mkt])
            mkt_corr =  1 if strat == mkt else mkt_series.corr(return_series)
            mkt_up_corr =  1 if strat == mkt else mkt_up_df[mkt].corr(mkt_up_df[strat])
            mkt_dwn_corr = 1 if strat == mkt else mkt_dwn_df[mkt].corr(mkt_dwn_df[strat])
            return {'alpha':mkt_alpha, 'beta':mkt_beta, 'up_beta':mkt_up_beta, 'dwn_beta':mkt_dwn_beta,
                    'corr': mkt_corr, 'up_corr': mkt_up_corr, 'dwn_corr': mkt_dwn_corr }
        except KeyError:
            return empty_analytics

#TODO: review this method, delete if no longer needed
def get_mkt_analytics_list(mkt_analytics):
    mkt_list = []
    for asset_class in mkt_analytics:
        mkt_list = mkt_list + list(mkt_analytics[asset_class].values())
    return mkt_list

#TODO: review this method, delete if no longer needed
def get_mkt_analytics1(return_series,mkt_ret_data,mkt_key,freq='1M',rfr=0.0, empty=False):    
    try:
        mkt_ret_df = dm.merge_data_frames(mkt_ret_data, return_series)
    except AttributeError:
        empty = True
    
    empty_analytics = {'alpha':None, 'beta':None, 'up_beta':None, 'dwn_beta':None,
                        'corr': None,'up_corr': None,'dwn_corr': None }
    mkt_analytics = {}
    for asset in mkt_key:
        if empty:
            mkt_analytics[asset]= empty_analytics
        else:
            try:
                strat = return_series.name
                mkt_id = mkt_key[asset]
                mkt_strat = mkt_ret_df[mkt_id]
                mkt_up_df = (mkt_ret_df[mkt_strat > 0])
                mkt_dwn_df = (mkt_ret_df[mkt_strat <= 0])
                
                mkt_alpha = 0 if strat == mkt_id else get_alpha(return_series,mkt_strat,freq,rfr)
                mkt_beta = 1 if strat == mkt_id else get_beta(return_series,mkt_strat,freq)
                mkt_up_beta = 1 if strat == mkt_id else get_beta(mkt_up_df[strat],mkt_up_df[mkt_id],freq)
                mkt_dwn_beta = 1 if strat == mkt_id else get_beta(mkt_dwn_df[strat],mkt_dwn_df[mkt_id],freq)
                mkt_corr =  1 if strat == mkt_id else mkt_strat.corr(return_series)
                mkt_up_corr =  1 if strat == mkt_id else mkt_up_df[mkt_id].corr(mkt_up_df[strat])
                mkt_dwn_corr = 1 if strat == mkt_id else mkt_dwn_df[mkt_id].corr(mkt_dwn_df[strat])
                mkt_analytics[asset] =  {'alpha':mkt_alpha, 'beta':mkt_beta, 'up_beta':mkt_up_beta, 'dwn_beta':mkt_dwn_beta,
                                        'corr': mkt_corr,'up_corr': mkt_up_corr,'dwn_corr': mkt_dwn_corr }
            except KeyError:
                mkt_analytics[asset] = empty_analytics
    return mkt_analytics
        
#TODO: delete if no longer needed
def get_return_stats1(df_returns, mkt_df, mkt_key, main_asset_class = 'Equity',
                      freq = '1M', rfr = 0.0, include_fi = True, include_cm = False,
                      include_fx = False, include_bmk = False, df_bmk = dm.pd.DataFrame(), bmk_dict={}):
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
    returns_stats_dict = {}
    bool_dict = {'Fixed Income': include_fi, 'Commodities':include_cm, 'FX':include_fx}
    #get mkt data (EQ, FI, CM, FX bmks)
    mkt_ret_data = get_mkt_ret_data(mkt_df, mkt_key, bool_dict)
    mkt_ret_df = mkt_ret_data['mkt_ret_df']
    bool_dict = mkt_ret_data['bool_dict']
    
    for col in df_returns:
        df_strat = dm.remove_na(df_returns, col)[col]
        price_series = dm.get_price_series(df_strat)
        temp_ret_df = dm.merge_data_frames(mkt_ret_df, df_returns[[col]])
        temp_ret_df.dropna(inplace=True)
        
        #compute mkt analytics (alpha, beta, corr)
        mkt_analytics = {}
        for bool_key in bool_dict:
            mkt_analytics[bool_key] = get_mkt_analytics(temp_ret_df, mkt_key[bool_key], df_strat, freq, rfr)



        ann_ret = get_ann_return(df_strat, freq)
        
        #compute active analytics (bmk beta, excess_ret, TE, IR)
        if include_bmk:
            active_analytics = get_active_analytics(bmk_dict, df_returns, df_bmk, freq, df_strat, ann_ret, col, empty=False)
            
        else:
            active_analytics = get_active_analytics(bmk_dict, df_returns, df_bmk, freq, df_strat, ann_ret, col, empty=True)
            
        med_ret = df_strat.median()
        avg_ret = df_strat.mean()
        avg_up_ret = get_avg_pos_neg(df_strat)
        avg_down_ret = get_avg_pos_neg(df_strat,False)
        avg_pos_neg = get_avg_pos_neg_ratio(df_strat)
        best_period = df_strat.max()
        worst_period = df_strat.min()
        pct_pos_periods = get_pct_pos_neg_periods(df_strat)
        pct_neg_periods = get_pct_pos_neg_periods(df_strat, False)
        ann_vol = get_ann_vol(df_strat, freq)
        up_dev = get_updown_dev(df_strat, freq,up=True)
        down_dev = get_updown_dev(df_strat, freq)
        updev_downdev_ratio = get_up_down_dev_ratio(df_strat,freq)
        skew = get_skew(df_strat)
        kurt = get_kurtosis(df_strat)
        max_dd = get_max_dd(df_strat)
        ret_vol = get_sharpe_ratio(df_strat,freq)
        sortino = get_sortino_ratio(df_strat, freq)
        ret_dd = get_ret_max_dd_ratio(df_strat,freq)
        
        # Make into dict with index and remove keys not needed dependednt on booleans
        analytics_list = [active_analytics['bmk_name'], ann_ret, active_analytics['excess_ret'], 
                                   mkt_analytics['Equity']['alpha'], mkt_analytics['Fixed Income']['alpha'], 
                                   mkt_analytics['Equity']['beta'], mkt_analytics['Equity']['up_beta'], mkt_analytics['Equity']['dwn_beta'],
                                   mkt_analytics['Fixed Income']['beta'], mkt_analytics['Fixed Income']['up_beta'], mkt_analytics['Fixed Income']['dwn_beta'],
                                   mkt_analytics['Commodities']['beta'], mkt_analytics['Commodities']['corr'], mkt_analytics['FX']['beta'], mkt_analytics['FX']['corr'],
                                   active_analytics['bmk_beta'],med_ret, avg_ret, avg_up_ret, avg_down_ret,
                                   avg_pos_neg, best_period, worst_period, pct_pos_periods,
                                   pct_neg_periods, ann_vol, up_dev, down_dev, active_analytics['te'],active_analytics['dwnside_te'], updev_downdev_ratio,
                                   skew, kurt, max_dd,ret_vol,sortino, ret_dd,active_analytics['ir'],active_analytics['ir_asym']]
            
        returns_stats_dict[col] = analytics_list
        
    rs_fi_bmk_index = ['Bmk Name','Annualized Return', 'Excess Return (Ann)','Equity Alpha',  'FI Alpha', 
                       'Equity Beta','Equity Bull Beta','Equity Bear Beta','FI Beta','FI Bull Beta','FI Bear Beta',
                       'CM Beta', 'CM Correlation', 'FX Beta', 'FX Correlation','Bmk Beta','Median Period Return',
                       'Avg. Period Return','Avg. Period Up Return', 'Avg. Period Down Return','Avg Pos Return/Avg Neg Return',
                       'Best Period', 'Worst Period','% Positive Periods','% Negative Periods','Annualized Vol',
                       'Upside Deviation','Downside Deviation','Tracking Error (TE)','Asymmetric TE',
                       'Upside to Downside Deviation Ratio','Skewness', 'Kurtosis','Max DD',
                       'Return/Volatility','Sortino Ratio','Return/Max DD', 'Informatio Ratio (IR)','Asymmetric IR']
    
    df_returns_stats = util.convert_dict_to_df(returns_stats_dict, rs_fi_bmk_index)
    
    if not bool_dict['Equity']:
        df_returns_stats.drop(['Equity Alpha','Equity Beta','Equity Bull Beta','Equity Bear Beta'], inplace = True)
        # rs_fi_bmk_index = [x for x in rs_fi_bmk_index if x not in drop_list]
       
    if not bool_dict['Fixed Income']:
        df_returns_stats.drop(['FI Alpha','FI Beta','FI Bull Beta','FI Bear Beta'], inplace = True)
        # drop_list=['FI Alpha','FI Beta','FI Bull Beta','FI Bear Beta']
        # rs_fi_bmk_index = [x for x in rs_fi_bmk_index if x not in drop_list]
    if not bool_dict['Commodities']:
        df_returns_stats.drop(['CM Beta','CM Correlation'], inplace = True)
        # drop_list = ['CM Beta','CM Correlation']
        # rs_fi_bmk_index = [x for x in rs_fi_bmk_index if x not in drop_list]
    if not bool_dict['FX']:
        df_returns_stats.drop(['FX Beta','FX Correlation'], inplace = True)
        # drop_list=['FX Beta','FX Correlation']
        # rs_fi_bmk_index = [x for x in rs_fi_bmk_index if x not in drop_list]
    if not include_bmk:
        df_returns_stats.drop(['Bmk Name','Excess Return (Ann)','Bmk Beta','Tracking Error (TE)','Asymmetric TE','Informatio Ratio (IR)','Asymmetric IR'], inplace = True)
        # drop_list=['Bmk Name','Excess Return (Ann)','Bmk Beta','Tracking Error (TE)','Asymmetric TE','Informatio Ratio (IR)','Asymmetric IR']
        # rs_fi_bmk_index = [x for x in rs_fi_bmk_index if x not in drop_list]
    # df_returns_stats.dropna(how='all', inplace=True)
    return df_returns_stats

#TODO: delete if no longer needed
def get_return_stats_fi(df_returns, freq='1M'):
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
    for col in list(df_returns.columns):
        df_strat = dm.remove_na(df_returns, col)[col]
        temp_df = df_returns[mkt_list + [col]].copy()
        temp_df.dropna(inplace=True)
        mkt_strat = temp_df[mkt_list[0]]
        active_strat = None if col == mkt_list[0] else df_strat - mkt_strat
        ann_ret = get_ann_return(df_strat, freq)
        excess_ret = None if col == mkt_list[0] else ann_ret - get_ann_return(mkt_strat, freq)
        ann_vol = get_ann_vol(df_strat, freq)
        te = None if col == mkt_list[0] else get_ann_vol(active_strat, freq)
        ret_vol = get_sharpe_ratio(df_strat,freq)
        ir = None if col == mkt_list[0] else excess_ret/te
        beta = 1 if col == mkt_list[0] else get_beta(df_strat,mkt_strat)
        up_cap = 1 if col == mkt_list[0] else get_up_down_capture_ratio(df_strat, mkt_strat)
        down_cap = 1 if col == mkt_list[0] else get_up_down_capture_ratio(df_strat, mkt_strat,False)
        best_period = df_strat.max()
        worst_period = df_strat.min()
        pct_pos_periods = get_pct_pos_neg_periods(df_strat)
        pct_neg_periods = get_pct_pos_neg_periods(df_strat, False)
        returns_stats_dict[col] = [ann_ret, excess_ret,ann_vol, te, ret_vol, ir, beta, up_cap, down_cap, best_period, worst_period, pct_pos_periods,
                                   pct_neg_periods]
    index = ['Ann Return', 'Excess Return (Ann)', 'Ann Volatility','Tracking Error','Return/Volatility', 'IR',
                           'Beta','Upside Capture', 'Downside Capture',
                           'Best Period', 'Worst Period','% Positive Periods',
                           '% Negative Periods']
    df_returns_stats = util.convert_dict_to_df(returns_stats_dict, index)
    return df_returns_stats                       