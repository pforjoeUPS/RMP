# -*- coding: utf-8 -*-
"""
Created on Thu Apr 22 00:02:00 2021

@author: Powis Forjoe
"""

import pandas as pd
import numpy as np
from ..datamanager.data_manager import get_notional_weights
#from ..import DataManager

def get_pos_neg_df(df_returns, col_name, pos=True):
    """
    Return dataframe with positive/negative returns of col_name as a condition
    
    Parameters:
    df_returns -- return dataframe
    col_name -- string (column name in dataframe)
    pos -- boolean (True for positive returns, False for negative)
    
    Returns:
    return dataframe -- dataframe
    """
    
    ret = df_returns.copy()
    if pos:
        ret_index = ret.index[ret[col_name] > 0]
    else:
        ret_index = ret.index[ret[col_name] < 0]
    ret_df = ret.loc[ret_index]
    return ret_df

def get_rolling_cum(df_returns, interval):
    """
    Get rolling cum returns dataframe
    
    Parameters:
    df_returns -- return dataframe
    interval -- 

    Returns:
    Rolling cum return -- dataframe
    """
    
    rolling_cum_ret = df_returns.copy()
    for col in df_returns.columns:
        rolling_cum_ret[col] = (1+rolling_cum_ret[col]).rolling(window=interval).apply(np.prod, raw=True)-1
    rolling_cum_ret.dropna(inplace=True)
    return rolling_cum_ret

def get_strat_weights(notional_weights, include_fi=False):
    """
    Return weights of each strategy compared to Equity or Equity and FI, if include_fi=True.

    Parameters:
    notional weights -- list
    include_fi -- boolean
    
    Returns:
    strat_weights -- list
    """
    
    #get strategy weights (strat_weights)
    strat_total = 0
    for weight in notional_weights:
        strat_total += weight
    strat_total = strat_total - notional_weights[0]
    if(include_fi):
        strat_total = strat_total - notional_weights[1]
    strat_total
    
    strat_weights = [weight / strat_total for weight in notional_weights]
    strat_weights[0] = 0
    if(include_fi):
        strat_weights[1] = 0
    return strat_weights

def get_weighted_strats_df(df_returns, notional_weights):
    """
    Return dataframe of weighted startegy returns, with and without newest strategy

    Parameters:
    returns_df -- dataframe
    notional weights -- list
    
    Returns:
    df_weighted_strats -- dataframe
    """
    
    #Get weighted strategies (weighted_strats) with and 
    #without new strategy (weighted_strats_old)
    pct_weights = [weight / notional_weights[0] for weight in notional_weights]
    pct_weights
    pct_weights.append(0)
    pct_weights
    
    pct_weights_old = pct_weights.copy()
    pct_weights_old[len(pct_weights_old)-2]=0
    pct_weights_old
    
    df_weighted_strats = df_returns.dot(tuple(pct_weights)).to_frame()
    df_weighted_strats.columns = ['Weighted Strats']
    col_names = [col for col in df_returns]
    wgt_strat_wo_name = 'Weighted Strats w/o ' + col_names[len(col_names)-2]
    df_weighted_strats[wgt_strat_wo_name] = df_returns.dot(tuple(pct_weights_old)).to_frame()
    return df_weighted_strats

def get_pct_weights(notional_weights, include_fi=False):
    """
    Return percentage weights based off of notional weights
    
    Parameters:
    notional_weights -- list
    include_fi -- boolean
    
    Returns:
    pct_weights -- list
    """
    
    total_weight = notional_weights[0] + notional_weights[1] if include_fi else notional_weights[0]
    pct_weights = [weight / total_weight for weight in notional_weights]
    return pct_weights

def get_df_weights(notional_weights, col_list, include_fi=False):
    """
    

    Parameters:
    notional_weights -- list
    col_list -- list
    include_fi -- boolean
    
    Returns:
    d_weights -- list
    """
    
    index_list = ['Notional Weights (Billions)',
                  'Percentage Weights',
                  'Strategy Weights']
    pct_weights = get_pct_weights(notional_weights, include_fi)
    strat_weights = get_strat_weights(notional_weights, include_fi)
    df_weights = pd.DataFrame([notional_weights, pct_weights, strat_weights],
                              index = index_list)
    df_weights.columns = col_list
    return df_weights

def check_notional(df_returns, notional_weights):
    """
    """
    
    #create list of df_returns column names
    col_list = list(df_returns.columns)
    
    #get notional weights for weighted strategy returns if not accurate
    if len(col_list) != len(notional_weights):
        notional_weights = []
        notional_weights = get_notional_weights(df_returns)
    
    return notional_weights

def get_weighted_strats_df_1(df_returns, notional_weights=[], include_fi=False, new_strat=False):
    """
    Return dataframe of weighted startegy returns, with and without newest strategy

    Parameters:
    returns_df -- dataframe
    notional weights -- list
    include_fi -- boolean
    new_strat -- boolean
    
    Returns:
    df_weighted_strats - dataframe
    """
    
    #confirm notional weights is correct len
    notional_weights = check_notional(df_returns, notional_weights)
    
    #Get weighted strategies (weighted_strats) with and 
    #without new strategy (weighted_strats_old)
    pct_weights = get_pct_weights(notional_weights, include_fi)
    df_weighted_strats = df_returns.dot(tuple(pct_weights)).to_frame()
    df_weighted_strats.columns = ['Weighted Strats']
    if new_strat:
        pct_weights_old = pct_weights.copy()
        pct_weights_old[len(pct_weights_old)-1] = 0
        col_names = list(df_returns.columns)
        wgt_strat_wo_name = 'Weighted Strats w/o ' + col_names[len(col_names)-1]
        df_weighted_strats[wgt_strat_wo_name] = df_returns.dot(tuple(pct_weights_old)).to_frame()
    
    return df_weighted_strats

def get_weighted_hedges(df_returns, notional_weights, include_fi=False):
    """
    """
    
    df_weighted_hedges = df_returns.copy()
    strat_weights = get_strat_weights(notional_weights, include_fi)
    df_weighted_hedges['Weighted Hedges'] = df_weighted_hedges.dot(tuple(strat_weights))
    return df_weighted_hedges

def bucket(x):
    """
    """
    
    if x < 1.0:
        return 'Bottom'
    elif x < 2.0 :
        return '2nd'
    elif x < 3.0 :
        return '3rd'
    elif x < 4.0 :
        return '4th'
    else:
        return 'Top'
