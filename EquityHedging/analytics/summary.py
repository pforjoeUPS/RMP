# -*- coding: utf-8 -*-
"""
Created on Tue Oct  1 17:59:28 2019

@author: Powis Forjoe and Maddie Choi
"""

import pandas as pd
from ..datamanager import data_manager as dm
from .hedge_metrics import get_hedge_metrics
from .import util
from .returns_stats import get_return_stats
from .corr_stats import get_corr_analysis
from .historical_selloffs import get_hist_sim_table
from .rolling_cum import get_rolling_cum

def get_analysis(df_returns, notional_weights=[], include_fi=False, new_strat=False, freq='1M', weighted = False):
    """
    Returns a tuple of dataframes containing:
    1. Return Statistics
    2. Hedge Framework Metrics
    
    Parameters:
    df_returns -- dataframe
    notional_weights -- list
    include_fi -- boolean
    new_strat -- boolean
    freq -- string
    
    Returns:
    tuple(datframe, dataframe)
        
    """
    col_list = list(df_returns.columns)
    analysis_dict = {}
    if weighted:
        notional_weights = util.check_notional(df_returns, notional_weights)
        
        #Get weighted strategies (weighted_strats) with and 
        #without new strategy (weighted_strats_old)
        df_weighted_strats = util.get_weighted_strats_df_1(df_returns, notional_weights, include_fi, new_strat)
    
        #merge wighted_strats with returns
        df_weighted_returns = dm.merge_data_frames(df_returns, df_weighted_strats)
        strat_weights = util.get_strat_weights(notional_weights, include_fi)
        #compute weighted hedges returns
        df_weighted_returns['Weighted Hedges'] = df_returns.dot(tuple(strat_weights))
        #generate return statistics for each strategy
        analysis_dict = get_return_stats(df_weighted_returns, freq)
    else:
        analysis_dict = get_return_stats(df_returns, freq)
        
    # Create pandas DataFrame for return statistics
    df_return_stats = pd.DataFrame(analysis_dict, 
                               index = ['Annualized Ret', 
                                        'Annualized Vol','Ret/Vol', 
                                        'Max DD','Ret/Max DD','Max 1M DD',
                                        'Max 1M DD Date', 'Ret/Max 1M DD','Max 3M DD', 
                                        'Max 3M DD Date','Ret/Max 3M DD', 'Skew',
                                        'Avg Pos Ret/Avg Neg Ret',
                                        'Downside Deviation',
                                        'Sortino Ratio'])
        
    # copy weighted returns df
    #we want the weighted hedge returns
    if weighted:
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
    
    #generate hedge metrics for each strategy
    hedge_dict = get_hedge_metrics(hedge_returns,freq)
    # Create pandas DataFrame for hedge metrics
    df_hedge_metrics = pd.DataFrame(hedge_dict, 
                                  index = ['Benefit Count', 'Benefit Median', 
                                           'Benefit Mean','Benefit Cumulative', 'Reliabitlity (BMK>0)','Reliabitlity (BMK<0)',
                                           'Convexity Count', 'Convexity Median',
                                           'Convexity Mean','Convexity Cumulative','Cost Count',
                                           'Cost Median','Cost Mean','Cost Cumulative', 'Decay Days (50% retrace)',
                                            'Decay Days (25% retrace)', 'Decay Days (10% retrace)'])
    
    #remove equity col
    df_hedge_metrics.drop([col_list[0]],axis=1,inplace=True)
    
    #remove decay metrics if frequency is 1M, 1Q, 1Y
    if dm.switch_freq_int(freq) <= 12:
        df_hedge_metrics.drop(['Decay Days (50% retrace)','Decay Days (25% retrace)',
                             'Decay Days (10% retrace)'],inplace=True)
        
    return {'return_stats':df_return_stats, 'hedge_metrics':df_hedge_metrics}

def get_analysis_sheet_data(df_returns, notional_weights=[], include_fi=False, new_strat=False,freq='1M', weighted=False):
    """
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
    
    #Save to excel file
    df_weights = []
    weightings_title = ''
    if weighted:
        df_weights = util.get_df_weights(notional_weights, col_list, include_fi)
        weightings_title = 'Portfolio Weightings'
    
    df_list = [corr_dict['corr'][0], corr_dict["corr_down"][0], 
               corr_dict["corr_up"][0], df_weights, analytics_dict['return_stats'],analytics_dict['hedge_metrics']]
    
    title_list = [corr_dict['corr'][1], corr_dict["corr_down"][1], 
               corr_dict["corr_up"][1], weightings_title,
               'Return Statistics ({} Returns)'.format(freq_string),
               'Hedging Framework Metrics ({} Returns)'.format(freq_string)]
    
    return {'df_list': df_list,'title_list': title_list}

def get_data(returns_dict, notional_weights,weighted,freq_list,include_fi=False, new_strat=False):
    """
    """
    
    corr_dict = get_corr_data(returns_dict, freq_list, weighted, notional_weights, include_fi)
    analytics_dict = get_analytics_data(returns_dict,['Monthly', 'Weekly'],weighted,notional_weights, include_fi,new_strat)
    hist_dict = get_hist_data(returns_dict,notional_weights, weighted)
    quintile_df = get_quintile_data(returns_dict, notional_weights)
    annual_df = get_annual_dollar_returns(returns_dict, notional_weights)
    
    return {'corr':corr_dict, 'analytics':analytics_dict, 'hist':hist_dict,
            'quintile': quintile_df, 'annual_returns':annual_df}

#TODO: Make it flexible to change the breakdowns (quintile, decile)
#TODO: Add frequency (Monthly, Weekly)
def get_quintile_data(returns_dict, notional_weights=[], weighted=False):
    """
    """
    
    df = returns_dict['Monthly'].copy()
    col_list = list(df.columns)
    equity = col_list[0]
    if weighted:
        if len(col_list) != len(notional_weights):
            notional_weights = []
            notional_weights = dm.get_notional_weights(df)
            df = util.get_weighted_hedges(df, notional_weights)
    df['percentile'] = df[equity].rank(pct = True).mul(5)
    df['Quintile'] = df['percentile'].apply(util.bucket)
    quintile = df.groupby('Quintile').mean()
    quintile = quintile.sort_values(by=[equity], ascending=True)
    quintile.drop(['percentile'], axis=1, inplace=True)
    quintile.index.names = [equity + ' Monthly Returns Ranking']
    return quintile

def get_corr_data(returns_dict, frequency, weighted=[False], notional_weights=[], include_fi = False):
    """
    """
    
    corr_data = {}
    
    if weighted:
        notional_weights = util.check_notional(returns_dict['Monthly'], notional_weights)
    
    for freq in frequency:
        return_df = returns_dict[freq].copy()
        temp_corr_data = {}
        for w in weighted:
            temp_corr_data[w] = get_corr_analysis(return_df, notional_weights, include_fi, w)
        corr_data[freq] = temp_corr_data
    return corr_data

def get_analytics_data(returns_dict, frequency, weighted=[False], notional_weights=[], include_fi = False, new_strat=False):
    """
    """
    
    analytics_data = {}
    
    if weighted:
        notional_weights = util.check_notional(returns_dict['Monthly'], notional_weights)
    
    for freq in frequency:
        return_df = returns_dict[freq].copy()
        temp_analytics_data = {}
        for w in weighted:
            temp_analytics_data[w] = get_analysis(return_df, notional_weights, include_fi, new_strat,
                                                       dm.switch_string_freq(freq),w)
        analytics_data[freq] = temp_analytics_data
    return analytics_data

def get_hist_data(returns_dict, notional_weights=[], weighted=[False]):
    """
    """
    daily = returns_dict['Daily'].copy()
    hist_data = {}
    for w in weighted:
        hist_data[w] = get_hist_sim_table(daily, notional_weights, w)
    
    return hist_data

def get_annual_dollar_returns(returns_dict, notional_weights, new_strat=False):
    """
    """
    annual_returns = returns_dict['Yearly'].copy()
    col_list = annual_returns.columns.to_list()
    if len(col_list) != len(notional_weights):
        notional_weights = []
        notional_weights = dm.get_notional_weights(annual_returns)
    for i in range(len(notional_weights)):
        annual_returns[annual_returns.columns[i]] *= notional_weights[i]*1E9
    annual_returns = annual_returns[(annual_returns.select_dtypes('float').columns)[1:]]
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
def get_rolling_cum_data(df_returns, freq, notional_weights=[]):
    """
    Return dict of rolling cumulatiuve returns for different intervals

    Parameters:
    returns_df -- dataframe
    freq -- string
    notional weights -- list
    
    Returns:
    dict
    """
    if freq == '1W':
        strategy_returns = df_returns.copy()
        #confirm notional weights is correct len
        notional_weights = util.check_notional(df_returns, notional_weights)
        
        strat_weights = [weight/notional_weights[0] for weight in notional_weights]
        strat_weights[0] = 0
        
        strategy_returns['Weighted Hedges'] = strategy_returns.dot(tuple(strat_weights))
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
    """
    
    #confirm notional weights is correct len
    notional_weights = util.check_notional(df_returns, notional_weights)
    
    #Get weighted strategies (weighted_strats) with and 
    #without new strategy (weighted_strats_old)
    df_weighted_strats = util.get_weighted_strats_df_1(df_returns, notional_weights, include_fi,
                                                  new_strat)

    #merge wighted_strats with returns
    df_weighted_returns = pd.merge(df_returns, df_weighted_strats, left_index=True, 
                                   right_index=True, how='outer')
    strat_weights = util.get_strat_weights(notional_weights, include_fi)
    
    #compute weighted hedges returns
    df_weighted_returns['Weighted Hedges'] = df_returns.dot(tuple(strat_weights))
    return df_weighted_returns

