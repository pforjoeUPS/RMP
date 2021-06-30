# -*- coding: utf-8 -*-
"""
Created on Tue Oct  1 17:59:28 2019

@author: Powis Forjoe and Maddie Choi
"""

from ..datamanager import data_manager as dm
from .decay import get_decay_days
from .util import get_pos_neg_df

def get_benefit_stats(df_returns, col_name):
    """
    Return count, mean and mode of all positive returns
    less than the 98th percentile rank
    
    Parameters:
    df_returns -- return dataframe
    col_name -- string (column name in dataframe)
    
    Returns:
    benefit -- dict(cout(double), mean(double), median(double))
    """
    df_strat = dm.remove_na(df_returns, col_name)
    percentile = df_strat[col_name].quantile(.98)
    
    benefit_index = df_strat.index[df_strat[col_name] < percentile]
    benefit_ret = df_strat.loc[benefit_index]
    pos_ret = get_pos_neg_df(benefit_ret,col_name,True)
    
    #calculate hedge metrics
    benefit_count=pos_ret[col_name].count()
    benefit_mean=pos_ret[col_name].mean()
    benefit_med=pos_ret[col_name].median()
    benefit_cumulative=benefit_count*benefit_mean
    
    #create dictionary
    benefit = {'count':benefit_count, 
               'mean':benefit_mean, 
               'median': benefit_med,
               'cumulative': benefit_cumulative
               }
    return benefit

def get_convexity_stats(df_returns, col_name):
    """
    Return count, mean and mode of all positive returns
    greater than the 98th percentile rank
    
    Parameters:
    df_returns -- return dataframe
    col_name -- string (column name in dataframe)
    
    Returns:
    convexity -- dict(cout(double), mean(double), median(double))
    """
    
    df_strat = dm.remove_na(df_returns, col_name)
    percentile = df_strat[col_name].quantile(.98)
    
    convexity_index = df_strat.index[df_strat[col_name] > percentile]
    convexity_ret = df_strat.loc[convexity_index]
    
    pos_ret = get_pos_neg_df(convexity_ret,col_name,True)
    
    #calculate hedge metrics
    convexity_count=pos_ret[col_name].count()
    convexity_mean=pos_ret[col_name].mean()
    convexity_med=pos_ret[col_name].median()
    convexity_cumulative= convexity_count*convexity_mean
    
    #create convexity dictionary
    convexity = {'count':convexity_count, 
               'mean': convexity_mean , 
               'median': convexity_med,
               'cumulative': convexity_cumulative
               }
    return convexity

def get_decay_stats(df_returns, col_name, freq):
    """
    Return decay stats of returns
    
    Parameters:
    df_returns -- return dataframe
    col_name -- string (column name in dataframe)
    freq
    
    Returns:
    decay -- dict(half(double), quarter(double), tenth(double))
    """
    if dm.switch_freq_int(freq) >= 12:
        decay_half = get_decay_days(df_returns, col_name, freq)
        decay_quarter = get_decay_days(df_returns, col_name, freq, .25)
        decay_tenth = get_decay_days(df_returns, col_name, freq, .10)
    else:
        decay_half = 0
        decay_quarter = 0
        decay_tenth = 0
        
    decay_dict = {'half':decay_half, 
               'quarter':decay_quarter, 
               'tenth':decay_tenth
               }
    return decay_dict

def get_cost_stats(df_returns, col_name):
    """
    Return count, mean and mode of all negative returns
    
    Parameters:
    df_returns -- return dataframe
    col_name -- string (column name in dataframe)
    
    Returns:
    cost -- dict(cout(double), mean(double), median(double))
    """
    
    neg_ret = get_pos_neg_df(df_returns,col_name,False)
    
    #calculate hedge metrics
    cost_count=neg_ret[col_name].count()
    cost_mean=neg_ret[col_name].mean()
    cost_med=neg_ret[col_name].median()
    cost_cumulative= cost_count*cost_mean
    cost = {'count': cost_count , 
               'mean': cost_mean , 
               'median': cost_med,
               'cumulative': cost_cumulative
               }
    return cost

def get_reliability_stats(df_returns, col_name):
    """
    Return correlation of strategy to equity bencmark downside returns
    
    Parameters:
    df_returns -- return dataframe
    col_name -- string (column name in dataframe)
    
    Returns:
    reliability -- dict(cout(double), mean(double), median(double))
    """
    
    
    col_list = list(df_returns.columns)
    equity_id = col_list[0]
    
    equity_down = (df_returns[df_returns[equity_id]<0])
    corr_d = equity_down.corr()
    reliability_d= corr_d[col_name].iloc[0]
    
    equity_up = (df_returns[df_returns[equity_id]>0])
    corr_u = equity_up.corr()
    reliability_u = corr_u[col_name].iloc[0]
    
    reliability={'up': reliability_u,
                 'down':reliability_d}
    
    return reliability

def get_hedge_metrics(df_returns, freq="1M"):
    """
    Return a dict of hedge metrics
    
    Parameters:
    df_returns -- dataframe
    freq -- string ('1M', '1W', '1D')
    
    Returns:
    hedge_dict -- dict(key: column name, value: hedge metrics)
    """
    hedge_dict = {}
    for col in df_returns.columns:
        benefit = get_benefit_stats(df_returns, col)
        reliability = get_reliability_stats(df_returns, col)
        convexity = get_convexity_stats(df_returns, col)
        cost = get_cost_stats(df_returns, col)
        decay = get_decay_stats(df_returns, col, freq)
        
        hedge_dict[col] = [benefit['count'], benefit['median'],
                          benefit['mean'], benefit['cumulative'], reliability['up'],reliability['down'],
                          convexity['count'], convexity['median'],
                          convexity['mean'],convexity['cumulative'], cost['count'],
                          cost['median'], cost['mean'], cost['cumulative'], decay['half'], 
                          decay['quarter'],decay['tenth']]
        
    return hedge_dict