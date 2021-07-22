# -*- coding: utf-8 -*-
"""
Created on Tue Oct  1 17:59:28 2019

@author: Powis Forjoe, Maddie Choi, and Zach Wells
"""

import pandas as pd
from ..datamanager import data_manager as dm
from .hedge_metrics import get_hedge_metrics
from EquityHedging.analytics import hedge_metrics as hm
from .import util
from .returns_stats import get_return_stats
from .corr_stats import get_corr_analysis
from .historical_selloffs import get_hist_sim_table
from .rolling_cum import get_rolling_cum


def get_analysis(df_returns, notional_weights=[], include_fi=False, new_strat=False, freq='1M', weighted = False):
    """
    Returns a dictionary of dataframes containing:
    1. Return Statistics
    2. Hedge Framework Metrics
    
    Parameters
    ----------
    df_returns : dataframe
        dataframe of returns
    notional_weights : list, optional
        notional weights of strategies. The default is [].
    include_fi : boolean, optional
        Include Fixed Income benchmark. The default is False.
    new_strat : boolean, optional
        Does analysis involve a new strategy. The default is False.
    freq : string, optional
        frequency. The default is '1M'.
    weighted : boolean, optional
        Include weighgted hedges and weighgted strats. The default is False.

    Returns
    -------
    dict
        dictionary containing:
           return_stats: dataframe
               dataframe containg returns stats of each strategy from df_returns
           hedge_metrics: dataframe
               dataframe containg hedge metrics of each strategy from df_returns

    """
    
    col_list = list(df_returns.columns)
    # analysis_dict = {}
    
    #if weighted, compute weighted hedges and strats
    if weighted:
        df_weighted_returns = get_weighted_data(df_returns,notional_weights,include_fi,new_strat)
        
        # Create pandas DataFrame for return statistics
        df_return_stats = get_return_stats(df_weighted_returns, freq)
    else:
        # Create pandas DataFrame for return statistics
        df_return_stats = get_return_stats(df_returns, freq)
        
        
    # remove the weighted strats from the dataframe
    if weighted:
        df_weighted_strats = util.get_weighted_strats_df(df_returns, notional_weights, include_fi, new_strat)
        hedge_returns = df_weighted_returns.copy()
    
        #remove weighted strats col
        hedge_returns.drop([df_weighted_strats.columns[0]],axis=1,inplace=True)
    
    #remove weighted strats w/o new strat cols if in the df
        if new_strat:
            hedge_returns.drop([df_weighted_strats.columns[1]],axis=1,inplace=True)
    else:
        hedge_returns = df_returns.copy()
        
    #remove fi benchmark col if in the df
    if include_fi:
        hedge_returns.drop([col_list[1]],axis=1,inplace=True)
    
    # Create pandas DataFrame for hedge metrics
    df_hedge_metrics = get_hedge_metrics(hedge_returns,freq)
    
    #remove equity col
    df_hedge_metrics.drop([col_list[0]],axis=1,inplace=True)
    
    #remove decay metrics if frequency is 1M, 1Q, 1Y
    if dm.switch_freq_int(freq) <= 12:
        df_hedge_metrics.drop(['Decay Days (50% retrace)','Decay Days (25% retrace)',
                             'Decay Days (10% retrace)'],inplace=True)
        
    return {'return_stats':df_return_stats, 'hedge_metrics':df_hedge_metrics}

def get_analysis_sheet_data(df_returns, notional_weights=[], include_fi=False, new_strat=False,freq='1M', weighted=False):
    """
    Returns data for analysis excel sheet into a dictionary

    Parameters
    ----------
    df_returns : dataframe
        dataframe of returns
    notional_weights : list, optional
        notional weights of strategies. The default is [].
    include_fi : boolean, optional
        Include Fixed Income benchmark. The default is False.
    new_strat : boolean, optional
        Does analysis involve a new strategy. The default is False.
    freq : string, optional
        frequency. The default is '1M'.
    weighted : boolean, optional
        Include weighgted hedges and weighgted strats. The default is False.

    Returns
    -------
    dict
       dictionary containing:
           df_list: list
               a list of dataframes:
                   correlations, portfolio weightings, returns_stats, hedge_metrics
           title_list: list
               a list containing titles of each of the dataframes

    """
    #create list of df_returns column names
    col_list = list(df_returns.columns)
    
    #convert freq to string
    freq_string = dm.switch_freq_string(freq)
    
    #get notional weights for weighted strategy returns if not accurate
    if weighted:
        notional_weights = util.check_notional(df_returns, notional_weights)
    
    #compute correlations
    corr_dict = get_corr_analysis(df_returns, notional_weights, include_fi, weighted)
    
    #compute return stats and hedge metrics
    analytics_dict = get_analysis(df_returns, notional_weights, include_fi, new_strat, freq,weighted)
    
    #compute portfolio weightings    
    df_weights = []
    weightings_title = ''
    if weighted:
        df_weights = util.get_df_weights(notional_weights, col_list, include_fi)
        weightings_title = 'Portfolio Weightings'
    
    #store analytics and respective titles in lists
    df_list = [corr_dict['corr'][0], corr_dict["corr_down"][0], 
               corr_dict["corr_up"][0], df_weights, analytics_dict['return_stats'],analytics_dict['hedge_metrics']]
    
    title_list = [corr_dict['corr'][1], corr_dict["corr_down"][1], 
               corr_dict["corr_up"][1], weightings_title,
               'Return Statistics ({} Returns)'.format(freq_string),
               'Hedging Framework Metrics ({} Returns)'.format(freq_string)]
    
    return {'df_list': df_list,'title_list': title_list}



def get_normal_sheet_data(df_returns,equity_bmk,  notional_weights=[], weighted=False, weighted_hedge = False):

    #get notional weights for weighted strategy returns if not accurate
    if weighted:
        notional_weights = util.check_notional(df_returns, notional_weights)
    
    if weighted_hedge == False:
        #normal data
        normal_dict = get_normalized_hedge_metrics(df_returns, equity_bmk, notional_weights, weighted_hedge=False)
        #store analytics and respective titles in lists
        df_list = [normal_dict['Hedge Metrics'], normal_dict['Normalized Data']]
    
    elif weighted_hedge == True:
       #normal data
       normal_dict = get_normalized_hedge_metrics(df_returns, equity_bmk, notional_weights, weighted_hedge=True)
       #store analytics and respective titles in lists
       df_list = [normal_dict['Hedge Metrics'], normal_dict['Normalized Data']]
    
    title_list = ['Hedging Framework Metrics', 'Normalized Hedge Metrics']
    
    return {'df_list': df_list,'title_list': title_list}



def get_data(returns_dict, notional_weights,weighted,freq_list=['Monthly', 'Weekly'],include_fi=False, new_strat=False):
    """
    Returns a dictionary containing:
        correlation data
        analytics data
        historical selloffs data
        quintile data
        annual $ returns data
        
    Parameters
    ----------
    returns_dict : dict
        dictionary of returns data by frequencies.
    notional_weights : list
        notional weights of strategies.
    weighted : list
        [True,False].
    freq_list : list, optional
        list of frequencies:
            'Daily', 'Weekly', 'Monthly'. The default is ['Monthly', 'Weekly']
    include_fi : boolean, optional
        Include Fixed Income benchmark. The default is False.
    new_strat : boolean, optional
        Does analysis involve a new strategy. The default is False.
    
    Returns
    -------
    dictionary containing:
           corr_dict: dictionary
           analytics_dict: dictionary
           hist_dict: dictionary
           quintile_df: dataframe
           annual_df: dataframe
           
    """
    
    #compute correation, analytics, historical selloffs, quintile and annual dollar returns datasets
    corr_dict = get_corr_data(returns_dict, freq_list, weighted, notional_weights, include_fi)
    analytics_dict = get_analytics_data(returns_dict,['Monthly', 'Weekly'],weighted,notional_weights, include_fi,new_strat)
    hist_dict = get_hist_data(returns_dict,notional_weights, weighted)
    quintile_df = get_grouped_data(returns_dict, notional_weights)
    annual_df = get_annual_dollar_returns(returns_dict, notional_weights)
    
    #return a dictionary containing the data
    return {'corr':corr_dict, 'analytics':analytics_dict, 'hist':hist_dict,
            'quintile': quintile_df, 'annual_returns':annual_df}


def get_percentile(df , bucket_format , group='Quintile', bucket_size = 5):
    """
    Computes Quintile or Decile based  on the given input. 
    
    Parameters
    ----------
    df : data frame
        returns data for given frequency 
    group : string
        Quintile or Decile
    bucket_format : method
        which formatting method to use when computing quintile or decile
    bucket_size : int
        how many buckets will returns data be divided into

    Returns
    -------
    groups : TYPE
        DESCRIPTION.

    """
    col_list = list(df.columns)
    equity = col_list[0]
    df['percentile'] = df[equity].rank(pct = True).mul(bucket_size)
    df[group] = df['percentile'].apply(bucket_format)
    groups= df.groupby(group).mean()
    groups = groups.sort_values(by=[equity], ascending=True)
    groups.drop(['percentile'], axis=1, inplace=True)
    groups.index.names = [equity + ' Monthly Returns Ranking']
    return groups

#TODO: Add frequency (Monthly, Weekly)  
def get_grouped_data(returns_dict, notional_weights=[], weighted=False, group='Quintile'):
    """
    Returns a dataframe containing average returns of each strategy grouped 
    into quintiles based on the equity returns ranking.
    
    Parameters
    ----------
    returns_dict : dict
        dictionary of returns data by frequencies.
    notional_weights : list, optional
        notional weights of strategies. The default is [].
    weighted : boolean, optional
        Include weighgted hedges and weighgted strats. The default is False.
    
    Returns
    -------
    quintile: dataframe
        quinitle analysis data

    """
    
    df = returns_dict['Monthly'].copy()
    
    if weighted == True:
        util.check_notional(df, notional_weights)
        df = util.get_weighted_hedges(df, notional_weights)
            
    if group == 'Quintile':       
        quintile = get_percentile(df, util.bucket, group, 5)
        return quintile
    
    elif group == 'Decile':
        decile = get_percentile(df, util.decile_bucket , group, 10)
        return decile
    
    

def get_corr_data(returns_dict, freq_list=['Monthly', 'Weekly'], weighted=[False], notional_weights=[], include_fi = False):
    """
    Returns a dataframe containing correlations data
    
    Parameters
    ----------
    returns_dict : dict
        dictionary of returns data by frequencies.
   freq_list : list, optional
        list of frequencies:
            'Daily', 'Weekly', 'Monthly'. The default is ['Monthly', 'Weekly']
    weighted : list, optional
        [True,False]. The default is [False].
     notional_weights : list
        notional weights of strategies. The default is [].
    include_fi : boolean, optional
        Include Fixed Income benchmark. The default is False.

    Returns
    -------
    corr_data : dataframe
        correlation data.

    """
    
    corr_data = {}

    if True in weighted:
        notional_weights = util.check_notional(returns_dict['Monthly'], notional_weights)
    
    for freq in freq_list:
        return_df = returns_dict[freq].copy()
        temp_corr_data = {}
        for w in weighted:
            temp_corr_data[w] = get_corr_analysis(return_df, notional_weights, include_fi, w)
        corr_data[freq] = temp_corr_data
    return corr_data

def get_analytics_data(returns_dict, freq_list=['Monthly', 'Weekly'], weighted=[False], notional_weights=[], include_fi = False, new_strat=False):
    """
    Returns a dataframe containing analytics data
    
    Parameters
    ----------
    returns_dict : dict
        dictionary of returns data by frequencies.
    freq_list : list, optional
        list of frequencies:
            'Daily', 'Weekly', 'Monthly'. The default is ['Monthly', 'Weekly']
    weighted : list, optional
        [True,False]. The default is [False].
    notional_weights : list, optional
        notional weights of strategies. The default is [].
    include_fi : boolean, optional
        Include Fixed Income benchmark. The default is False.
    new_strat : boolean, optional
        Does analysis involve a new strategy. The default is False.

    Returns
    -------
    analytics_data : dictionary
        analytics data.

    """
    
    analytics_data = {}
    

#TODO: fix to run when weighted has a true element is in the list and when weighted is true and false

    if True in weighted:
        notional_weights = util.check_notional(returns_dict['Monthly'], notional_weights)
    
    for freq in freq_list:
        return_df = returns_dict[freq].copy()
        temp_analytics_data = {}
        
        for w in weighted:
            temp_analytics_data[w] = get_analysis(return_df, notional_weights, include_fi, new_strat,
                                                       dm.switch_string_freq(freq),w)
        analytics_data[freq] = temp_analytics_data
    return analytics_data

def get_hist_data(returns_dict, notional_weights=[], weighted=[False]):
    """
    Returns a dictionary containing historical selloff data

    Parameters
    ----------
    returns_dict : dictionary
        dictionary of returns data by frequencies.
    notional_weights : list, optional
        notional weights of strategies. The default is [].
    weighted : list, optional
        [True,False]. The default is [False].

    Returns
    -------
    hist_data : dictionary
        historical selloff data.

    """
    daily = returns_dict['Daily'].copy()
    hist_data = {}
    for w in weighted:
        hist_data[w] = get_hist_sim_table(daily, notional_weights, w)
    
    return hist_data

def get_annual_dollar_returns(returns_dict, notional_weights, new_strat=False):
    """
    Returns a dataframe containing annual $ returns for each strategy.
    
    Parameters
    ----------
    returns_dict : dict
        dictionary of returns data by frequencies.
    notional_weights : list, optional
        notional weights of strategies. The default is [].
    new_strat : boolean, optional
        Does analysis involve a new strategy. The default is False.
    
    Returns
    -------
    annual_returns: dataframe
        annual $ returns data

    """
    
    #get annual returns data
    annual_returns = returns_dict['Yearly'].copy()
    
    #confirm notional weights is correct len
    notional_weights = util.check_notional(annual_returns, notional_weights)
    
    #compute annual returns for strategies
    col_list = annual_returns.columns.to_list()
    for i in range(len(notional_weights)):
        annual_returns[annual_returns.columns[i]] *= notional_weights[i]*1E9
    annual_returns = annual_returns[(annual_returns.select_dtypes('float').columns)[1:]]
    
    #compute annual returns for Tail Risk Program and add to annual_returns dataframe
    sum_column = 0
    col_list = col_list[1:]
    for col in col_list:
        sum_column += annual_returns[col]
    if new_strat:
        sum_column -= annual_returns[col_list[len(col_list)-1]]
    annual_returns['Tail Risk Program'] = sum_column
    col_list.insert(0,'Tail Risk Program')
    annual_returns = annual_returns[col_list]
    annual_returns.index.names = ['Year']
    return annual_returns

def get_dollar_returns_data(returns_dict, notional_weights, new_strat_bool):
    """
    """
    
    ann_ret_dict = {}
    for s in new_strat_bool:
        ann_ret_dict[s] = get_annual_dollar_returns(returns_dict, notional_weights, s)
    return ann_ret_dict

#TODO: make flexible to compute corrs w/o weighted strats/hedges
def get_rolling_cum_data(df_returns, freq='1W', notional_weights=[]):
    """
    Returns a dictionary of rolling cumulatiuve returns for different intervals

    Parameters
    ----------
    df_returns : dataframe
        DESCRIPTION.
    freq : string, optional
        '1W' or '1D'. The default is '1W'
    notional_weights : list, optional
        notional weights of strategies. The default is [].

    Returns
    -------
    dict
        dictionary containing dataframes

    """

    if freq == '1W' or freq == '1D':
        strategy_returns = df_returns.copy()
        
        #confirm notional weights is correct len
        notional_weights = util.check_notional(df_returns, notional_weights)
        
        #compute weighted hedges
        strat_weights = [weight/notional_weights[0] for weight in notional_weights]
        strat_weights[0] = 0
        strategy_returns['Weighted Hedges'] = strategy_returns.dot(tuple(strat_weights))
        
        #get rolling cumulative returns
        rolling_cum_threemonths = get_rolling_cum(strategy_returns, interval=13)
        rolling_cum_sixmonths = get_rolling_cum(strategy_returns, interval=26)
        rolling_cum_annual = get_rolling_cum(strategy_returns, interval=52)
        
        return {'3M': rolling_cum_threemonths,
                '6M': rolling_cum_sixmonths,
                '1Y': rolling_cum_annual}
    else:
        print('Frequency of data has to be weekly to run this function')
        
def get_weighted_data(df_returns, notional_weights=[], include_fi=False, new_strat=False):
    """
    Returns dataframe containg df_returns plus the weighted strats and hedges data

    Parameters
    ----------
    df_returns : dataframe
        dataframe of returns
    notional_weights : list, optional
        notional weights of strategies. The default is [].
    include_fi : boolean, optional
        Include Fixed Income benchmark. The default is False.
    new_strat : boolean, optional
        Does analysis involve a new strategy. The default is False.

    Returns
    -------
    df_weighted_returns : dataframe

    """
    
    #confirm notional weights is correct len
    notional_weights = util.check_notional(df_returns, notional_weights)
    
    #Get weighted strategies with and without new strategy (if new_strat = True)
    df_weighted_strats = util.get_weighted_strats_df(df_returns, notional_weights, include_fi,
                                                  new_strat)

    #merge weighted_strats with returns with and 
    #without new strategy (weighted_strats_old)
    df_weighted_returns = pd.merge(df_returns, df_weighted_strats, left_index=True, 
                                   right_index=True, how='outer')
    
    #Get weighted hedges with and without new strategy (if new_strat = True)
    df_weighted_hedges = util.get_weighted_hedges(df_returns, notional_weights, include_fi,new_strat)
    
    #merge weighted hedges with weighted returns
    df_weighted_hedges.drop(list(df_returns.columns), axis=1, inplace=True)
    df_weighted_returns = pd.merge(df_weighted_returns, df_weighted_hedges, left_index=True, 
                                   right_index=True, how='outer')
    return df_weighted_returns



def get_normalized_hedge_metrics(df_returns, equity_bmk, notional_weights, weighted_hedge = False):
    '''
    

    Parameters
    ----------
    returns : dict
        returns data
    equity_bmk : string
        choose a bmk: SPTR, M1WD, SPX
    notional_weights : list
        list with notional weights for each strategu

    Returns
    -------
    norm : data frame
        includes the normalized data for all strategies in the Strategy and Allocation Equity Hedge Portfolio

    '''
    
    if weighted_hedge == True:
         df_returns = util.get_weighted_hedges(df_returns, notional_weights)
         
    #calculates hedgemetrics 
    df_hm = get_hedge_metrics(df_returns, freq="1M", full_list=False)
    df_hm.drop(equity_bmk, axis = 1, inplace = True)
    df_hm= df_hm.transpose()
    
    #converts down reliability metrics from negative to positive in order to correctly rank them
    df_reverse = util.reverse_signs_in_col(df_hm,'Downside Reliability')

    #normalizes the data
    norm = util.get_normalized_data(df_reverse)
    #create dict with hedge met and normalized data
    return {'Hedge Metrics': df_hm, 'Normalized Data': norm}