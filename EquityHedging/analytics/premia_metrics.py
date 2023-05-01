# -*- coding: utf-8 -*-
"""
Created on Tue Oct  1 17:59:28 2019

@author: Powis Forjoe, Maddie Choi, and Zach Wells
"""

from EquityHedging.datamanager import data_manager as dm
from EquityHedging.analytics.recovery import compute_recovery_pct
from EquityHedging.analytics.util import get_pos_neg_df
from EquityHedging.analytics import  util

PREMIA_METRICS_INDEX = ['Benefit Count','Benefit Median','Benefit Mean','Benefit Cum', 
                       'Correlation to Equity','Correlation to Rates',
                       'Convexity Count','Convexity Median','Convexity Mean','Convexity Cum',
                       'Cost Count','Cost Median','Cost Mean','Cost Cum',
                       'Recovery']

def get_premia_index_list(full_list=True):
    if full_list:
        return PREMIA_METRICS_INDEX
    else:
        return ['Benefit','Correlation to Equity','Correlation to Rates','Convexity','Cost', 'Recovery']
    
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

def get_recovery_stats(df_returns, col_name, freq):
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
    df_prices = dm.get_prices_df(df_returns)
    if dm.switch_freq_int(freq) >= 12:
        recovery = compute_recovery_pct(df_prices[col_name], freq)
    else:
        recovery = 0

        
    return recovery

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

def get_uncorrelation_stats(df_returns, col_name):
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
    
    #get the equity_id and fi_id
    col_list = list(df_returns.columns)
    equity_id = col_list[0]
    fi_id = col_list[1]
    
    #comupte the correlation
    df_corr = df_returns.corr()
    
    #create reliability dictionary
    uncorrelation={'equity': df_corr[equity_id][col_name],
                 'rates': df_corr[fi_id][col_name]}
    
    return uncorrelation

def get_premia_metrics(df_returns, freq="1M", full_list=True):
    """
    Return a dataframe of hedge metrics

    Parameters
    ----------
    df_returns : dataframe
    freq : string, optional
        Frequency. The default is "1M".
    full_list: boolean, optional

    Returns
    -------
    df_hedge_metrics : dataframe
        
    """
    
    #create empty dictionary
    premia_dict = {}
    
    if full_list:
        #loop through columns in df_returns to compute and store the hedge 
        #metrics for each strategy
        for col in df_returns.columns:
            benefit = get_benefit_stats(df_returns, col)
            uncorrelation = get_uncorrelation_stats(df_returns, col)
            convexity = get_convexity_stats(df_returns, col)
            cost = get_cost_stats(df_returns, col)
            recovery = get_recovery_stats(df_returns, col, freq)
            
            premia_dict[col] = [benefit['count'],benefit['median'],benefit['mean'],
                               benefit['cumulative'],uncorrelation['equity'],uncorrelation['rates'],
                               convexity['count'],convexity['median'],convexity['mean'],
                               convexity['cumulative'],cost['count'],cost['median'],cost['mean'], 
                               cost['cumulative'],recovery]
    else:
        for col in df_returns.columns:
            benefit = get_benefit_stats(df_returns, col)
            uncorrelation = get_uncorrelation_stats(df_returns, col)
            convexity = get_convexity_stats(df_returns, col)
            cost = get_cost_stats(df_returns, col)
            recovery = get_recovery_stats(df_returns, col, freq)
            
            premia_dict[col] = [benefit['cumulative'],
                              uncorrelation['equity'],uncorrelation['rates'],
                              convexity['cumulative'], cost['cumulative'], recovery]
    
    #Converts hedge_dict to a data grame
    df_premia_metrics = util.convert_dict_to_df(premia_dict, get_premia_index_list(full_list))
    return df_premia_metrics