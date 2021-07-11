# -*- coding: utf-8 -*-
"""
Created on Tue Oct  1 17:59:28 2019

@author: Powis Forjoe, Maddie Choi, and Zach Wells
"""

from ..datamanager import data_manager as dm
from .decay import get_decay_days
from .util import get_pos_neg_df

def get_benefit_stats(df_returns, col_name):
    """
    Return count, mean, mode and cumulative of all positive returns
    less than the 98th percentile rank

    Parameters
    ----------
    df_returns : dataframe
    col_name : string
        strategy name in df_returns.

    Returns
    -------
    benefit : dictionary
        {count: double, mean: double, median: double, cumulative: double}

    """
    
    #create a dataframe containing only the col_name strategy
    df_strat = dm.remove_na(df_returns, col_name)
    
    #compute the 98th percentile
    percentile = df_strat[col_name].quantile(.98)
    
    #get the all data that is less than the 98th percentile
    benefit_index = df_strat.index[df_strat[col_name] < percentile]
    benefit_ret = df_strat.loc[benefit_index]
    
    #filter out negative returns
    pos_ret = get_pos_neg_df(benefit_ret[col_name],True)
    
    #calculate hedge metrics
    benefit_count = pos_ret.count()
    benefit_mean = pos_ret.mean()
    benefit_med = pos_ret.median()
    benefit_cum = benefit_count*benefit_mean
    
    #create dictionary
    benefit = {'count': benefit_count, 
               'mean': benefit_mean, 
               'median': benefit_med,
               'cumulative': benefit_cum
               }
    return benefit

def get_convexity_stats(df_returns, col_name):
    """
    Return count, mean, mode and cumulative of all positive returns
    greater than the 98th percentile rank

    Parameters
    ----------
    df_returns : dataframe
    col_name : string
        strategy name in df_returns.

    Returns
    -------
    convexity : dictionary
        {count: double, mean: double, median: double, cumulative: double}
    """
    
    #create a dataframe containing only the col_name strategy
    df_strat = dm.remove_na(df_returns, col_name)
    
    #compute the 98th percentile
    percentile = df_strat[col_name].quantile(.98)
    
    #get the all data that is greater than the 98th percentile
    convexity_index = df_strat.index[df_strat[col_name] > percentile]
    convexity_ret = df_strat.loc[convexity_index]
    
    #may not need this line since all the data may be positive already
    pos_ret = get_pos_neg_df(convexity_ret[col_name],True)
    
    #calculate hedge metrics
    convexity_count = pos_ret.count()
    convexity_mean = pos_ret.mean()
    convexity_med = pos_ret.median()
    convexity_cum = convexity_count*convexity_mean
    
    #create convexity dictionary
    convexity = {'count': convexity_count, 
                 'mean': convexity_mean , 
                 'median': convexity_med,
                 'cumulative': convexity_cum
                 }
    return convexity

def get_decay_stats(df_returns, col_name, freq):
    """
    Return decay stats of returns

    Parameters
    ----------
    df_returns : dataframe
    col_name : string
        strategy name in df_returns.
    freq : string
        frequency.

    Returns
    -------
    decay_dict : dictionary
        {key: decay_percent, value: int)

    """
    
    #Compute decay values only if data is daily or weekly
    if dm.switch_freq_int(freq) >= 12:
        decay_half = get_decay_days(df_returns, col_name, freq)
        decay_quarter = get_decay_days(df_returns, col_name, freq, .25)
        decay_tenth = get_decay_days(df_returns, col_name, freq, .10)
    else:
        decay_half = 0
        decay_quarter = 0
        decay_tenth = 0
        
    #create decay dictionary
    decay_dict = {'half':decay_half, 
               'quarter':decay_quarter, 
               'tenth':decay_tenth
               }
    
    return decay_dict

def get_cost_stats(df_returns, col_name):
    """
    Return count, mean, mode and cumulative of all negative returns

    Parameters
    ----------
    df_returns : dataframe
    col_name : string
        strategy name in df_returns.

    Returns
    -------
    cost : dictionary
        {count: double, mean: double, median: double, cumulative: double}

    """
    
    #filter out positive returns
    neg_ret = get_pos_neg_df(df_returns[col_name] ,False)
    
    #calculate hedge metrics
    cost_count = neg_ret.count()
    cost_mean = neg_ret.mean()
    cost_med = neg_ret.median()
    cost_cum = cost_count*cost_mean
    
    #create cost dictionary
    cost = {'count': cost_count , 
            'mean': cost_mean , 
            'median': cost_med,
            'cumulative': cost_cum
            }
    
    return cost

def get_reliability_stats(df_returns, col_name):
    """
    Return correlation of strategy to equity bencmark downside returns and upside returns
    
    Parameters
    ----------
    df_returns : dataframe
    col_name : string
        strategy name in df_returns.
        
    Returns
    -------
    reliability : dictionary
        dict{down(double), up(double)}.

    """
    
    #get the equity_id
    col_list = list(df_returns.columns)
    equity_id = col_list[0]
    
    #create dataframe containing only data when equity_id < 0
    equity_down = (df_returns[df_returns[equity_id] < 0])
    
    #comupte the correlation and get the reliability stat for the col_name strategy
    corr_d = equity_down.corr()
    reliability_d= corr_d[col_name].iloc[0]
    
    #create dataframe containing only data when equity_id > 0
    equity_up = (df_returns[df_returns[equity_id] > 0])
    
    #comupte the correlation and get the reliability stat for the col_name strategy
    corr_u = equity_up.corr()
    reliability_u = corr_u[col_name].iloc[0]
    
    #create reliability dictionary
    reliability={'down': reliability_d,
                 'up':reliability_u}
    
    return reliability

def get_hedge_metrics(df_returns, freq="1M"):
    """
    Return a dict of hedge metrics

    Parameters
    ----------
    df_returns : dataframe
    freq : string, optional
        Frequency. The default is "1M".

    Returns
    -------
    hedge_dict : dictionary
        {key: column name, value: hedge metrics}

    """
    
    #create empty dictionary
    hedge_dict = {}
    
    #loop through columns in df_returns to compute and store the hedge metrics for each strategy
    for col in df_returns.columns:
        benefit = get_benefit_stats(df_returns, col)
        reliability = get_reliability_stats(df_returns, col)
        convexity = get_convexity_stats(df_returns, col)
        cost = get_cost_stats(df_returns, col)
        decay = get_decay_stats(df_returns, col, freq)
        
        hedge_dict[col] = [benefit['count'], benefit['median'],
                          benefit['mean'], benefit['cumulative'],
                          reliability['down'],reliability['up'],
                          convexity['count'], convexity['median'],
                          convexity['mean'],convexity['cumulative'], cost['count'],
                          cost['median'], cost['mean'], cost['cumulative'], decay['half'], 
                          decay['quarter'],decay['tenth']]
        
    return hedge_dict