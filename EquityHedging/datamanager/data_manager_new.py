# -*- coding: utf-8 -*-
"""
Created on Tue Oct  1 17:59:28 2019

@author: Powis Forjoe, Maddie Choi
"""


import pandas as pd
import numpy as np
import os
from datetime import datetime as dt
from math import prod
# from EquityHedging.analytics import util
from openpyxl import load_workbook
from .import data_xformer_new as dxf


CWD = os.getcwd()
DATA_FP = CWD +'\\EquityHedging\\data\\'
RETURNS_DATA_FP = DATA_FP +'returns_data\\'
EQUITY_HEDGING_RETURNS_DATA = RETURNS_DATA_FP + 'eq_hedge_returns.xlsx'
# RETURNS_DATA_FP = CWD +'\\EquityHedging\\data\\'
# EQUITY_HEDGING_RETURNS_DATA = DATA_FP + 'ups_equity_hedge\\returns_data.xlsx'
NEW_DATA = RETURNS_DATA_FP + 'new_strats\\'
# UPDATE_DATA = RETURNS_DATA_FP + 'update_strats\\'
UPDATE_DATA = DATA_FP + 'update_data\\'
EQUITY_HEDGE_DATA = DATA_FP + 'ups_equity_hedge\\'

QIS_UNIVERSE = CWD + '\\Cluster Analysis\\data\\'

NEW_DATA_COL_LIST = ['SPTR', 'SX5T','M1WD', 'Long Corp', 'STRIPS', 'Down Var',
 'Vortex', 'VOLA I', 'VOLA II','Dynamic VOLA','Dynamic Put Spread',
                    'GW Dispersion', 'Corr Hedge','Def Var (Mon)', 'Def Var (Fri)', 'Def Var (Wed)', 
                    'Commodity Basket']

def merge_dicts(main_dict, new_dict, fillzeros = False):

    """
    Merge new_dict to main_dict
    
    Parameters:
    main_dict -- dictionary
    new_dict -- dictionary

    Returns:
    dictionary
    """
    
    # freq_list = ['Daily', 'Weekly', 'Monthly', 'Quarterly', 'Yearly']
    merged_dict = {}
    for key in main_dict:
        df_main = main_dict[key]
        df_new = new_dict[key]
        if key == 'Daily':
            merged_dict[key] = merge_data_frames(df_main, df_new, True)
        else:
            merged_dict[key] = merge_data_frames(df_main, df_new)
    return merged_dict

def merge_data_frames(df_main, df_new,fillzeros=False):
    """
    Merge df_new to df_main and drop na values
    
    Parameters:
    df_main -- dataframe
    df_new -- dataframe

    Returns:
    dataframe
    """
    
    df = pd.merge(df_main, df_new, left_index=True, right_index=True, how='left')
    if fillzeros:
        df = df.fillna(0)
    else:
        df.dropna(inplace=True)
    return df

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

#TODO: move 
def get_vrr_weights(weights):
    """
    Returns VRR weights from notional weights
    
    Parameters:
    notional weights -- list

    Returns:
    list
    """   
    notional_vrr_weights = [weights[4],weights[5]]
    port_total = float(sum(notional_vrr_weights))
    vrr_weights = [weight / port_total for weight in notional_vrr_weights]
    return vrr_weights

#TODO: move 
def create_vrr_portfolio(returns, weights):
    """
    Updates returns to combine VRR2 and VRRTrend returns into VRRPortfolio
    
    Parameters:
    df_returns -- dataframe
    weights -- list

    Returns:
    dataframe
    """   
    returns_dict = returns.copy()
    vrr_weights = get_vrr_weights(weights)
    freqs = ['Daily', 'Weekly', 'Monthly', 'Quarterly', 'Yearly']
    for freq in freqs:
        vrr_portfolio = returns_dict[freq]['VRR 2']*vrr_weights[0]+returns_dict[freq]['VRR Trend']*vrr_weights[1]
        returns_dict[freq].insert(loc = 4, column = 'VRR Portfolio',value = vrr_portfolio)
        returns_dict[freq].drop(['VRR Trend'],inplace=True,axis=1)
        returns_dict[freq].drop(['VRR 2'],inplace=True,axis=1)
    return returns_dict

def drop_nas(data):
    if type(data) == dict:
        for key in data:
            data[key].drop.dropna(inplace=True)
    else:
        data.dropna(inplace=True)
    return data

def check_col_len(df, col_list):
    if len(col_list) != len(df.columns):
        return list(df.columns)
    else:
        return col_list

def rename_columns(data, col_list):
    if type(data) == dict:
        for key in data:
            data[key].columns = check_col_len(data[key], col_list)
    else:
        data.columns = check_col_len(data, col_list)
    return data
        
def get_notional_weights(df_returns):
    """
    Returns list of notional values for stratgies
    
    Parameters:
    df_returns -- dataframe
    
    Returns:
    list
    """
    weights = [float(input('notional value (Billions) for ' + col + ': ')) for col in df_returns.columns]
    #df_returns = create_vrr_portfolio(df_returns, weights)
    #weights.append(weights[4]+weights[5])
    #del weights[4:6]
    return weights

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
    
    strategy_returns['VOLA 3'] = strategy_returns['Dynamic VOLA']
    strategy_returns['Def Var']=strategy_returns['Def Var (Fri)']*.4 + strategy_returns['Def Var (Mon)']*.3+strategy_returns['Def Var (Wed)']*.3
        
    if freq == '1W' or freq == '1M':
        if include_fi:
            strategy_returns['FI Benchmark'] = (strategy_returns['Long Corp'] + strategy_returns['STRIPS'])/2
            strategy_returns = strategy_returns[[equity, 'FI Benchmark', '99%/90% Put Spread', 

                                                 'Down Var', 'Vortex', 'VOLA 3','Dynamic Put Spread',
                                                  'VRR 2', 'VRR Trend', 'GW Dispersion', 'Corr Hedge','Def Var','Commodity Basket']]
        else:
            strategy_returns = strategy_returns[[equity, '99%/90% Put Spread', 
                                                 'Down Var', 'Vortex', 'VOLA 3','Dynamic Put Spread',
                                                 'VRR 2', 'VRR Trend', 'GW Dispersion', 'Corr Hedge','Def Var','Commodity Basket']]
    else:
        strategy_returns = strategy_returns[[equity, '99%/90% Put Spread', 'Down Var', 'Vortex',
                                             'VOLA 3','Dynamic Put Spread', 'VRR 2', 'VRR Trend', 
                                             'GW Dispersion', 'Corr Hedge','Def Var','Commodity Basket']]

    return strategy_returns

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

def merge_dicts_list(dict_list, fillzeros = True):
    '''
    merge main dictionary with a dictionary list

    Parameters
    ----------
    dict_list : list

    Returns
    -------
    main_dict : dictionary
        new dictionary created upon being merged with a list

    '''
    main_dict = dict_list[0]
    dict_list.remove(main_dict)
    #iterate through dictionary 
    for dicts in dict_list:
        
        #merge each dictionary in the list of dictionaries to the main
        main_dict = merge_dicts(main_dict,dicts, fillzeros = fillzeros )
    return main_dict

def compound_ret_from_monthly(strat_monthly_returns, strategy):
    monthly_ret = strat_monthly_returns.copy()
    monthly_ret["Year"] = monthly_ret.index.get_level_values('year')
    
    years = np.unique(monthly_ret["Year"])
    yr_ret = []
    for i in range(0, len(years)):
        #isolate monthly returns for single year
        monthly_ret_by_yr = monthly_ret.loc[monthly_ret.Year == years[i]][strategy]
        #calculate compound return
        comp_ret = prod(1 + monthly_ret_by_yr) - 1
        yr_ret.append(comp_ret)
        
    yr_ret = pd.DataFrame( yr_ret, columns = ["Year"], index = list(years)) 
    return yr_ret
    
def month_ret_table(returns_df, strategy):
    '''

    Parameters
    ----------
    returns_df : Data Frame
        
    strategy : String
        Strategy name

    Returns
    -------
    Data Frame

    '''
    #pull monthly returns from dictionary 
    month_ret = pd.DataFrame(returns_df[strategy])
    
    #create monthly return data frame with index of years 
    month_ret['year'] = month_ret.index.year
    month_ret['month'] = month_ret.index.month_name().str[:3]
    
    #change monthly returns into a table with x axis as months and y axis as years
    strat_monthly_returns = month_ret.groupby(['year', 'month']).sum()
    yr_ret = compound_ret_from_monthly(strat_monthly_returns, strategy)
       
    month_table = strat_monthly_returns.unstack()
    
    #drop first row index
    month_table = month_table.droplevel(level = 0, axis = 1)
    
    #re order columns
    month_table = month_table[["Jan", "Feb", "Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]]
    
    #Join yearly returns to the monthly returns table
    table = pd.concat([month_table, yr_ret],  axis=1)
    table.index.names = [strategy]

    return table

def get_sheetnames_xlsx(filepath):
    wb = load_workbook(filepath, read_only=True, keep_links=False)
    return wb.sheetnames

def get_qis_uni_dict():
    qis_uni = {}
    sheet_names = get_sheetnames_xlsx(QIS_UNIVERSE + "QIS Universe Time Series TEST.xlsx")
    for sheet in sheet_names:
        index_price = pd.read_excel(QIS_UNIVERSE + "QIS Universe Time Series TEST.xlsx", sheet_name = sheet, index_col=0,header = 1)
        qis_uni[sheet] = dxf.format_data(index_price, freq = '1W')
    return qis_uni

def check_notional(df_returns, notional_weights=[]):
    """
    Get notional weights if some weights are missing

    Parameters
    ----------
    df_returns : dataframe
        dataframe of returns
    notional_weights : list, optional
        notional weights of strategies. The default is [].
    
    Returns
    -------
    notional_weights : list

    """
    #create list of df_returns column names
    col_list = list(df_returns.columns)
    
    #get notional weights for weighted strategy returns if not accurate
    if len(col_list) != len(notional_weights):
        notional_weights = []
        notional_weights = get_notional_weights(df_returns)
    
    return notional_weights