# -*- coding: utf-8 -*-
"""
Created on Tue Oct  1 17:59:28 2019

@author: Powis Forjoe
"""

import numpy as np
import pandas as pd

from . import util_new
from ..datamanager import data_manager_new as dm


def get_corr_analysis(df_returns, notional_weights=[], include_eq=False,include_fi=False, weighted=False):
    """
    Returns a dict of correlation matrices: 
        full correlation, when equity up, when equity down

    Parameters
    ----------
    df_returns : dataframe
    notional_weights : list, optional
        The default is [].
    include_fi : boolean, optional
        The default is False.
    weighted : boolean, optional
        The default is False.

    Returns
    -------
    corr_dict : dictionary
        {key: string, value: list[dataframe, string]}

    """

    strategy_returns = df_returns.copy()
    
    #compute weighted hedges returns
    if weighted:
        strategy_returns = util.get_weighted_hedges(strategy_returns, notional_weights, include_fi)

    #get equity value (e.g. 'SPTR', 'M1WD', 'SX5T')
    col_list = list(strategy_returns.columns)
    
    #get returns when equity > 0 and equity < 0
    # equity_up = (strategy_returns[strategy_returns[equity_id] > 0])
    # equity_down = (strategy_returns[strategy_returns[equity_id] < 0])

    corr_dict = {"full": {'corr_df': strategy_returns.corr(),
                          'title': f'Correlation of {len(strategy_returns)} Historical Observations ({get_data_range(strategy_returns)})'}
                 }
    if include_eq:
        equity_id = col_list[0]
        corr_dict["Equity"] = get_conditional_corr(strategy_returns, equity_id)
    
    if include_fi:
        fi_id = col_list[1]
        corr_dict["Fixed Income"] = get_conditional_corr(strategy_returns, fi_id)
                                   
    
    return corr_dict

def get_data_range(df_returns):
    dates = dm.get_min_max_dates(df_returns)
    return str(dates['start']).split()[0] + ' to ' + str(dates['end']).split()[0]

def get_conditional_corr(df_returns, strat_id):
    strat_up = (df_returns[df_returns[strat_id] > 0])
    strat_down = (df_returns[df_returns[strat_id] < 0])
    return {'corr_df': get_up_lwr_corr(strat_up, strat_down),  'title': f'Conditional correlation where {strat_id} > 0 (upper) and < 0 (lower)'}

def get_up_lwr_corr(up_df, lwr_df):
    up_array = np.triu(up_df.corr().values)
    lwr_array = np.tril(lwr_df.corr().values)
    temp_array = up_array + lwr_array
    for i in range(0,len(temp_array)):
        temp_array[i][i] = 1
        
    return pd.DataFrame(temp_array, index=lwr_df.columns, columns=up_df.columns)

def get_title_string(returns_df,strat_id,scenario='full'):
    
    title = 'Correlation of {} Historical Observations ({}) '.format(str(len(returns_df)), get_data_range(returns_df))
    
    if scenario == 'index_up':
        return title + 'where ' + strat_id + ' > 0'
    elif scenario == 'index_down':
        return title + 'where ' + strat_id + ' < 0'
    else:
        return title
#TODO: make flexible to compute corrs w/o weighted strats/hedges
#TODO: add comments
def get_corr_rank_data(df_returns,buckets, notional_weights=[],include_fi=False):
    """
    Creates a dictionary of correlation dataframes ranked based on the
    equity benchmark returns

    Parameters
    ----------
    df_returns : dataframe
    buckets : TYPE
        DESCRIPTION.
    notional_weights : list, optional
        The default is [].
    include_fi : boolean, optional
        The default is False.

    Returns
    -------
    corr_pack : dicitionary
        {key: string, value: list[dataframe, string]}.

    """
    
    strategy_returns = util.get_weighted_hedges(df_returns, notional_weights, include_fi)
    
    #confirm notional weights is correct len
    notional_weights = util.check_notional(strategy_returns, notional_weights)
    
    #create a ranking for the equity index returns
    col_list = list(strategy_returns.columns)
    equity_id = col_list[0]
    strategy_returns['Rank'] = pd.qcut(strategy_returns[equity_id],buckets,
                                        labels=np.arange(0,buckets,1))
    
    #create a list of dataframes with each bucket
    list_df = []
    for rank in range(buckets):
        list_df.append(strategy_returns[df_returns['Rank'] == rank])
    
    #delete bucket column    
    for i in range(buckets):
        del list_df[i]['Rank']
        
    del strategy_returns['Rank']
    
    #create correlation dictionary
    corr_pack = {}
    corr_pack['corr'] = [strategy_returns.corr(), 'Correlation Analysis']
        
    for rank in range(0,len(list_df)):
        key = 'corr_' + str(rank+1)
        title = 'Correlation Analysis for rank ' + str(rank+1)
        min_value = list_df[rank][equity_id].min()
        min_string = "Min = " + "{:.2%}".format(min_value)
        max_value = list_df[rank][equity_id].max()
        max_string = "   Max = " + "{:.2%}".format(max_value)
        mean_value = list_df[rank][equity_id].mean()
        mean_string = "   Mean = " + "{:.2%}".format(mean_value)
        value = title + "   " + min_string + max_string + mean_string
        corr_pack[key] = [list_df[rank].corr(), value]
    
    return corr_pack


def get_rolling_corr_data(df_returns,window=36):
    """
    Get a dictionary contaiing rolling correlations of each strategy in df_returns vs the other strategies

    Parameters
    ----------
    df_returns : TYPE
        DESCRIPTION.
    window : int
        rolling window.

    Returns
    -------
    rolling_corr_dict : Dictionary
        DESCRIPTION.

    """
    rolling_corr_dict = {}
    
    for strat_1 in df_returns:
        #get list w/o strat_1
        temp_strat_list = list(df_returns.columns).copy()
        temp_strat_list.remove(strat_1)
        
        #create a df of rolling correlations to strat_1
        rolling_corr_temp = get_rolling_corr(df_returns[strat_1],df_returns[strat_1], window)
        for strat_2 in temp_strat_list:
            rolling_corr_temp = dm.merge_data_frames(rolling_corr_temp, get_rolling_corr(df_returns[strat_1],df_returns[strat_2], window),False)
        rolling_corr_temp.drop([strat_1], axis=1, inplace=True)
        rolling_corr_dict[strat_1] = rolling_corr_temp
    return rolling_corr_dict
    
def get_rolling_corr(ret_series_1, ret_series_2, window=36):
    """
    Get rolling correlation between 2 return series

    Parameters
    ----------
    ret_series_1 : Series
        returns.
    ret_series_2 : Series
        returns.
    window : int
        rolling window.

    Returns
    -------
    rolling_corr : Dataframe
        correlation Dataframe.

    """
    rolling_corr = pd.DataFrame(ret_series_1.rolling(window).corr(ret_series_2), columns=[ret_series_2.name])
    rolling_corr.dropna(inplace=True)
    return rolling_corr

