# -*- coding: utf-8 -*-
"""
Created on Tue Oct  1 17:59:28 2019

@author: Powis Forjoe, Maddie Choi
"""

import pandas as pd
import os
from datetime import datetime as dt

CWD = os.getcwd()
RETURNS_DATA_FP = CWD +'\\EquityHedging\\data\\'
EQUITY_HEDGING_RETURNS_DATA = RETURNS_DATA_FP + 'ups_equity_hedge\\returns_data.xlsx'
NEW_DATA = RETURNS_DATA_FP + 'new_strats\\'
UPDATE_DATA = RETURNS_DATA_FP + 'update_strats\\'

def merge_dicts(main_dict, new_dict):
    """
    Merge new_dict to main_dict
    
    Parameters:
    main_dict -- dictionary
    new_dict -- dictionary

    Returns:
    dictionary
    """
    
    freq_list = ['Daily', 'Weekly', 'Monthly', 'Quarterly', 'Yearly']
    merged_dict = {}
    for freq in freq_list:
        df_main = main_dict[freq]
        df_new = new_dict[freq]
        merged_dict[freq] = merge_data_frames(df_main, df_new)
    return merged_dict

def merge_data_frames(df_main, df_new):
    """
    Merge df_new to df_main and drop na values
    
    Parameters:
    df_main -- dataframe
    df_new -- dataframe

    Returns:
    dataframe
    """
    
    df = pd.merge(df_main, df_new, left_index=True, right_index=True, how='outer')
    df.dropna(inplace=True)
    return df

def format_data(df_index, freq="1M"):
    """
    Format dataframe, by freq, to return dataframe
    
    Parameters:
    df_index -- dataframe
    freq -- string ('1M', '1W', '1D')
    
    Returns:
    dataframe
    """
    data = df_index.copy()
    data.index = pd.to_datetime(data.index)
    if not(freq == '1D'):
       data = data.resample(freq).ffill()
    data = data.pct_change(1)
    data.dropna(inplace=True)
    data = data.loc[(data!=0).any(1)]
    return data

def get_min_max_dates(df_returns):
    """
    Return a dict with the min and max dates of a dataframe.
    
    Parameters:
    df_returns -- dataframe with index dates
    
    Returns:
    dict(key (string), value(dates))
    """
    #get list of date index
    dates_list = list(df_returns.index.values)
    dates = {}
    dates['start'] = dt.utcfromtimestamp(dates_list[0].astype('O')/1e9)
    dates['end'] = dt.utcfromtimestamp(dates_list[len(dates_list) - 1].astype('O')/1e9)
    return dates

def compute_no_of_years(df_returns):
    """
    Returns number of years in a dataframe based off the min and max dates

    Parameters:
    df_returns -- dataframe with returns
    
    Returns:
    double
    """
    
    min_max_dates = get_min_max_dates(df_returns)
    no_of_years = (min_max_dates['end'] - min_max_dates['start']).days/365
    return no_of_years

def switch_freq_int(arg):
    """
    Return an integer equivalent to frequency in years
    
    Parameters:
    arg -- string ('1D', '1W', '1M')
    
    Returns:
    int of frequency in years
    """
    switcher = {
            "1D": 252,
            "1W": 52,
            "1M": 12,
            "1Q": 4,
            "1Y": 1,
    }
    return switcher.get(arg, 1)

def switch_freq_string(arg):
    """
    Return an string equivalent to frequency
    eg: swith_freq_string('1D') returns 'Daily'
    
    Parameters:
    arg -- string ('1D', '1W', '1M')
    
    Returns:
    string
    """
    switcher = {
            "1D": "Daily",
            "1W": "Weekly",
            "1M": "Monthly",
            "1Q": "Quarterly",
            "1Y": "Yearly",
    }
    return switcher.get(arg, 1)

def switch_string_freq(arg):
    """
    Return an string equivalent to freq
    eg: swith_freq_string('Daily') returns '1D'

    Parameters:
    arg -- string ('1D', '1W', '1M')
    
    Returns:
    string
    """
    switcher = {
            "Daily":"1D",
            "Weekly":"1W",
            "Monthly":"1M",
            "Quarterly":"1Q",
            "Yearly":"1Y",
    }
    return switcher.get(arg, 1)

def remove_na(df, col_name):
    """
    Remove na values from column
        
    Parameters:
    df -- dataframe
    col_name -- string (column name in dataframe)
    
    Returns:
    dataframe
    """
    clean_df = pd.DataFrame(df[col_name].copy())
    clean_df.dropna(inplace=True)
    return clean_df

def get_freq_ratio(freq1, freq2):
    """
    Returns ratio of 2 frequencies
        
    Parameters:
    freq1 -- string
    freq2 -- string
    
    Returns:
    int
    """
    
    return round(switch_freq_int(freq1)/switch_freq_int(freq2))

def convert_to_freq2(arg, freq1, freq2):
    """
    Converts number from freq1 to freq2
    
    Parameters:
    arg -- int
    freq1 -- string
    freq2 -- string

    Returns:
    int
    """
    
    return round(arg / get_freq_ratio(freq1, freq2))

def get_notional_weights(df_returns):
    """
    Returns list of notional values for stratgies
    
    Parameters:
    df_returns -- dataframe
    
    Returns:
    list
    """
    return [float(input('notional value (Billions) for ' + col + ': ')) for col in df_returns.columns]    

def create_copy_with_fi(df_returns, equity = 'SPTR', freq='1M', include_fi=False):
    """
    Combine columns of df_returns together to get:
    FI Benchmark (avg of Long Corps and STRIPS)
    VOLA (avg of VOLA I and VOLA II)
    Def Var (weighted avg Def Var (Fri): 60%, Def Var (Mon):20%, Def Var (Wed): 20%)
    
    Parameters:
    df_returns -- dataframe
    freq -- string
    
    Returns:
    dataframe
    """
    strategy_returns = df_returns.copy()
    
    if freq == '1W' or freq == '1M':
        strategy_returns['VOLA'] = (strategy_returns['VOLA I'] + strategy_returns['VOLA II'])/2
        strategy_returns['Def Var']=strategy_returns['Def Var (Fri)']*.6 + strategy_returns['Def Var (Mon)']*.2+strategy_returns['Def Var (Wed)']*.2
        if include_fi:
            strategy_returns['FI Benchmark'] = (strategy_returns['Long Corp'] + strategy_returns['STRIPS'])/2
            strategy_returns = strategy_returns[[equity, 'FI Benchmark', '99%/90% Put Spread', 
                                                 'Down Var', 'Vortex', 'VOLA','Dynamic Put Spread',
                                                 'VRR', 'GW Dispersion', 'Corr Hedge','Def Var']]
        else:
            strategy_returns = strategy_returns[[equity, '99%/90% Put Spread', 
                                                 'Down Var', 'Vortex', 'VOLA','Dynamic Put Spread',
                                                 'VRR', 'GW Dispersion', 'Corr Hedge','Def Var']]
    else:
        strategy_returns['VOLA'] = (strategy_returns['VOLA I'] + strategy_returns['VOLA II'])/2
        strategy_returns['Def Var']=strategy_returns['Def Var (Fri)']*.6 + strategy_returns['Def Var (Mon)']*.2+strategy_returns['Def Var (Wed)']*.2

        strategy_returns = strategy_returns[[equity, '99%/90% Put Spread', 'Down Var', 'Vortex',
                                             'VOLA','Dynamic Put Spread','VRR', 
                                             'GW Dispersion', 'Corr Hedge','Def Var']]
    
    return strategy_returns

def get_real_cols(df):
    """
    Removes empty columns labeled 'Unnamed: ' after importing data
    
    Parameters:
    df -- dataframe
    
    Returns:
    dataframe
    """
    real_cols = [x for x in df.columns if not x.startswith("Unnamed: ")]
    df = df[real_cols]
    return df

def get_equity_hedge_returns(equity='SPTR', include_fi=False, strat_drop_list=[],only_equity=False, all_data=False):
    """
    Returns a dictionary of dataframes containing returns data of 
    different frequencies
    
    Parameters:
    equity -- dataframe
    include_fi --boolean
    strat_drop_list -- list
    only_equity -- boolean
    
    Returns:
    dictionary
    """
    returns_dict = {}
    freqs = ['1D', '1W', '1M', '1Q', '1Y']
    for freq in freqs:
        freq_string = switch_freq_string(freq)
        temp_ret = pd.read_excel(EQUITY_HEDGING_RETURNS_DATA,
                                 sheet_name=freq_string,
                                 index_col=0)
        temp_ret = get_real_cols(temp_ret)
        if all_data:
            returns_dict[freq_string] = temp_ret.copy()
        else:
            returns_dict[freq_string] = create_copy_with_fi(temp_ret, equity, freq, include_fi)
        if strat_drop_list:
            returns_dict[freq_string].drop(strat_drop_list, axis=1, inplace=True)
        if only_equity:
            returns_dict[freq_string] = returns_dict[freq_string][[equity]]
        returns_dict[freq_string].index.names = ['Date']
    
    return returns_dict

def get_data_dict(data, data_type='index'):
    """
    Converts daily data into a dictionary of dataframes containing returns 
    data of different frequencies
    
    Parameters:
    data -- df
    data_type -- string
    
    Returns:
    dictionary
    """
    freq_list = ['Daily', 'Weekly', 'Monthly', 'Quarterly', 'Yearly']
    data_dict = {}
    if data_type != 'index':
        try:
            data.index = pd.to_datetime(data.index)
        except TypeError:
            pass
        data = get_prices_df(data)
    for freq_string in freq_list:
        data_dict[freq_string] = format_data(data, switch_string_freq(freq_string))
    return data_dict

def get_prices_df(df_returns):
    """"
    Converts returns dataframe to index level dataframe

    Parameters:
    df_returns -- returns dataframe

    Returns:
    index price level - dataframe
    """
    
    df_prices = df_returns.copy()
    
    for col in df_returns.columns:
        df_prices[col][0] = df_returns[col][0] + 1
    
    for i in range(1, len(df_returns)):
        for col in df_returns.columns:
            df_prices[col][i] = (df_returns[col][i] + 1) * df_prices[col][i-1]
    return df_prices

def get_new_strategy_returns_data(report_name, sheet_name, strategy_list=[]):
    """
    dataframe of stratgy returns
    
    Parameters:
    report_name -- string
    sheet_name -- string
    strategy_list -- list
    
    Returns:
    dataframe
    """
    df_strategy = pd.read_excel(NEW_DATA+report_name, sheet_name=sheet_name, index_col=0)
    df_strategy = get_real_cols(df_strategy)
    if strategy_list:
        df_strategy.columns = strategy_list
    try:
        df_strategy.index = pd.to_datetime(df_strategy.index)
    except TypeError:
        pass
    df_strategy = df_strategy.resample('1D').ffill()
    new_strategy_returns = df_strategy.copy()
    if 'Index' in sheet_name:
        new_strategy_returns = df_strategy.pct_change(1)
    new_strategy_returns.dropna(inplace=True)
    return new_strategy_returns
