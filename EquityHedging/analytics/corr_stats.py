# -*- coding: utf-8 -*-
"""
Created on Tue Oct  1 17:59:28 2019

@author: Powis Forjoe
"""

import pandas as pd
import numpy as np
from ..datamanager.data_manager import get_min_max_dates
from .import util

def get_corr_analysis(df_returns, notional_weights=[], include_fi=False, weighted=False):
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
    equity_id = col_list[0]
    
    #get returns when equity > 0 and equity < 0
    equity_up = (strategy_returns[strategy_returns[equity_id] > 0])
    equity_down = (strategy_returns[strategy_returns[equity_id] < 0])

    #TODO: fix bug in title
    dates = get_min_max_dates(strategy_returns)
    data_range = str(dates['start']).split()[0] + ' to ' + str(dates['end']).split()[0]
    title = 'Correlation of ' + str(len(strategy_returns)) + ' Historical Observations (' + data_range + ')'

    corr_dict = {
        "corr": [strategy_returns.corr(), title],
        "corr_up": [equity_up.corr(), title + ' where ' + equity_id + ' > 0'],
        "corr_down": [equity_down.corr(), title + ' where ' + equity_id + ' < 0']
        }
    
    return corr_dict

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
