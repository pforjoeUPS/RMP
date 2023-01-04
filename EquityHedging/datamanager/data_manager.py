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
from EquityHedging.analytics import summary 
from EquityHedging.analytics import  util

CWD = os.getcwd()
RETURNS_DATA_FP = CWD +'\\EquityHedging\\data\\'
EQUITY_HEDGING_RETURNS_DATA = RETURNS_DATA_FP + 'ups_equity_hedge\\returns_data.xlsx'
NEW_DATA = RETURNS_DATA_FP + 'new_strats\\'
UPDATE_DATA = RETURNS_DATA_FP + 'update_strats\\'
EQUITY_HEDGE_DATA = RETURNS_DATA_FP + 'ups_equity_hedge\\'
QIS_UNIVERSE = CWD + '\\Cluster Analysis\\data\\'
NEW_DATA_COL_LIST = ['SPTR', 'SX5T','M1WD', 'Long Corp', 'STRIPS', 'Down Var', 'VRR 2', 'VRR Trend',
 'Vortex', 'VOLA I', 'VOLA II','Dynamic VOLA','Dynamic Put Spread',
                    'GW Dispersion', 'Corr Hedge','Def Var (Mon)', 'Def Var (Fri)', 'Def Var (Wed)']

def merge_dicts(main_dict, new_dict, fillzeros = True):
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
            merged_dict[key] = merge_data_frames(df_main, df_new, fillzeros = fillzeros)
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
    
    df = pd.merge(df_main, df_new, left_index=True, right_index=True, how='outer')
    if fillzeros:
        df = df.fillna(0)
    else:
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
    ***Change to VOLA (Dynamic VOLA) ????????
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
                                                 'VRR', 'GW Dispersion', 'Corr Hedge','Def Var']]
        else:
            strategy_returns = strategy_returns[[equity, '99%/90% Put Spread', 
                                                 'Down Var', 'Vortex', 'VOLA 3','Dynamic Put Spread',
                                                 'VRR', 'GW Dispersion', 'Corr Hedge','Def Var']]
    else:
        strategy_returns = strategy_returns[[equity, '99%/90% Put Spread', 'Down Var', 'Vortex',
                                             'VOLA 3','Dynamic Put Spread','VRR', 
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

def get_new_strategy_returns_data(report_name, sheet_name, strategy_list=[], freq = '1D'):
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
    df_strategy = df_strategy.resample(freq).ffill()
    new_strategy_returns = df_strategy.copy()
    if 'Index' in sheet_name:
        new_strategy_returns = df_strategy.pct_change(1)
    new_strategy_returns.dropna(inplace=True)
    return new_strategy_returns

def get_data_to_update(col_list, filename, sheet_name = 'data', put_spread=False):
    '''
    Update data to dictionary

    Parameters
    ----------
    col_list : list
        List of columns for dict
    filename : string        
    sheet_name : string
        The default is 'data'.
    put_spread : boolean
        Describes whether a put spread strategy is used. The default is False.

    Returns
    -------
    data_dict : dictionary
        dictionary of the updated data.

    '''
    #read excel file to dataframe
    data = pd.read_excel(UPDATE_DATA + filename, sheet_name= sheet_name, index_col=0)
    
    #rename column(s) in dataframe
    data.columns = col_list
    
    if put_spread:
        #remove the first row of dataframe
        data = data.iloc[1:,]
    
        #add column into dataframe
        data = data[['99%/90% Put Spread']]
    
        #add price into dataframe
        data = get_prices_df(data)
    
    data_dict = get_data_dict(data)
    return data_dict

def add_bps(vrr_dict, add_back=.0025):
    '''
    Adds bips back to the returns for the vrr strategy

    Parameters
    ----------
    vrr_dict : dictionary
        DESCRIPTION.
    add_back : float
        DESCRIPTION. The default is .0025.

    Returns
    -------
    temp_dict : dictionary
        dictionary of VRR returns with bips added to it

    '''
    #create empty dictionary
    temp_dict = {}
    
    #iterate through keys of a dictionary
    for key in vrr_dict:
        
        #set dataframe equal to dictionary's key
        temp_df = vrr_dict[key].copy()
        
        #set variable equaly to the frequency of key
        freq = switch_string_freq(key)
        
        #add to dataframe
        temp_df['VRR'] += add_back/(switch_freq_int(freq))
        
        #add value to the temp dictionary
        temp_dict[key] = temp_df
    return temp_dict

def merge_dicts_list(dict_list):
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
        main_dict = merge_dicts(main_dict,dicts)
    return main_dict

def match_dict_columns(main_dict, new_dict):
    '''
    

    Parameters
    ----------
    main_dict : dictionary
    original dictionary
    new_dict : dictionary
    dictionary that needs to have columns matched to main_dict
    Returns
    -------
    new_dict : dictionary
        dictionary with matched columns

    '''
    
    #iterate through keys in dictionary
    for key in new_dict:
        
        #set column in the new dictionary equal to that of the main
        new_dict[key] = new_dict[key][list(main_dict[key].columns)]
    return new_dict  

def append_dict(main_dict, new_dict):
    '''
    update an original dictionary by adding information from a new one

    Parameters
    ----------
    main_dict : dictionary      
    new_dict : dictionary        

    Returns
    -------
    main_dict : dictionary

    '''
    #iterate through keys in dictionary
    for key in new_dict:
        
        #add value from new_dict to main_dict
        main_dict[key] = main_dict[key].append(new_dict[key])
    return main_dict

def create_update_dict():
    '''
    Create a dictionary that updates returns data

    Returns
    -------
    new_data_dict : Dictionary
        Contains the updated information after adding new returns data

    '''
    #Import data from bloomberg into dataframe and create dictionary with different frequencies
    new_ups_data_dict = get_data_to_update(NEW_DATA_COL_LIST, 'ups_data.xlsx')
    
    #get vrr data
    vrr_dict = get_data_to_update(['VRR'], 'vrr_tracks_data.xlsx')
    
    #add back 25 bps
    vrr_dict = add_bps(vrr_dict)

    #get put spread data
    put_spread_dict = get_data_to_update(['99 Rep', 'Short Put', '99%/90% Put Spread'], 'put_spread_data.xlsx', 'Daily', put_spread = True)
    
    #merge vrr and put spread dicts to the new_data dict
    new_data_dict = merge_dicts(new_ups_data_dict, put_spread_dict, False)
    new_data_dict =  merge_dicts(new_data_dict, vrr_dict)   


    #get data from returns_data.xlsx into dictionary
    returns_dict = get_equity_hedge_returns(all_data=True)
    
    #set columns in new_data_dict to be in the same order as returns_dict
    new_data_dict = match_dict_columns(returns_dict, new_data_dict)
        
    #return a dictionary
    return new_data_dict


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

    

def all_strat_month_ret_table(returns_df, notional_weights = [], include_fi = False, new_strat = False, weighted = False):
    '''
    

    Parameters
    ----------
    returns_df : Data Frame
        Data Frame containing monthly returns data
    strat_list : List
        DESCRIPTION. The default is ['Down Var','VOLA', 'Dynamic Put Spread', 'VRR', 'GW Dispersion','Corr Hedge','Def Var'].

    Returns
    -------
    month_table : TYPE
        DESCRIPTION.

    '''
    #make strat list the columns of returns_df
    
    if weighted == True:
        
        #get weighted strats and weighted hedges 
        returns_df = summary.get_weighted_data(returns_df,notional_weights,include_fi, new_strat)
        
    
    #create strat list from the columns of the returns data
    strat_list = returns_df.columns
    
    #create moth table dict
    month_table_dict = {}
    
    #loop through each strategy in the list and get the monthly returns table
    for strat in strat_list:
       month_table_dict[strat] = month_ret_table(returns_df, strat)
       #month_table_dict[strat] = month_table_dict[strat][:-1]
    return month_table_dict


def get_new_returns_df(new_ret_df,ret_df):
    #reset both data frames index to make current index (dates) into a column
    new_ret_df.index.names = ['Date']
    new_ret_df.reset_index(inplace = True)
    ret_df.reset_index(inplace=True)
   
    #find difference in dates
    difference = set(new_ret_df.Date).difference(ret_df.Date)
    #find which dates in the new returns are not in the current returns data
    difference_dates = new_ret_df['Date'].isin(difference)
    
    #select only dates not included in original returns df
    new_ret_df = new_ret_df[difference_dates]
    
    #set 'Date' column as index for both data frames
    new_ret_df.set_index('Date', inplace = True)
    ret_df.set_index('Date', inplace = True)
    
    return new_ret_df

def check_returns(returns_dict):
    #if the last day of the month is earlier than the last row in weekly returns then drop last row of weekly returns
    if returns_dict['Monthly'].index[-1] < returns_dict['Weekly'].index[-1] :
        returns_dict['Weekly'] = returns_dict['Weekly'][:-1]
    
    
    if returns_dict['Monthly'].index[-1] < returns_dict['Quarterly'].index[-1] :
        returns_dict['Quarterly'] = returns_dict['Quarterly'][:-1]
        
    return returns_dict    


def update_returns_data():
    
    #get data from returns_data.xlsx into dictionary
    returns_dict = get_equity_hedge_returns(all_data=True)

    #create dictionary that contains updated returns
    new_data_dict = create_update_dict()

    for key in returns_dict:
        #create returns data frame
        new_ret_df = new_data_dict[key].copy()
        ret_df = returns_dict[key].copy()
        
        #update current year returns 
        if key == 'Yearly':
            if ret_df.index[-1] == new_ret_df.index[-1]:
                ret_df = ret_df[:-1]
        #get new returns df       
        new_ret_df = get_new_returns_df(new_ret_df, ret_df)
        returns_dict[key] = ret_df.append(new_ret_df)
    
    returns_dict = check_returns(returns_dict)
    return returns_dict


def get_qis_uni_dict():
    qis_uni = {}
    sheet_names = util.get_sheetnames_xlsx(QIS_UNIVERSE + "QIS Universe Time Series TEST.xlsx")
    for sheet in sheet_names:
        index_price = pd.read_excel(QIS_UNIVERSE + "QIS Universe Time Series TEST.xlsx", sheet_name = sheet, index_col=0,header = 1)
        qis_uni[sheet] = format_data(index_price, freq = '1W')
    return qis_uni