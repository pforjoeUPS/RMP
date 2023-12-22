# -*- coding: utf-8 -*-
"""
Created on Sun Aug 14 2022

@author: Powis Forjoe
"""

import pandas as pd
import os
from .import data_manager as dm

CWD = os.getcwd()
DATA_FP = CWD +'\\EquityHedging\\data\\'

def copy_data(data):
    if type(data) == dict:
        dict_copy = {}
        for key in data:
            dict_copy[key] = data[key].copy()
        return dict_copy
    else:
        return data.copy()
    
def resample_data(df, freq="1M"):
    data = df.copy()
    data.index = pd.to_datetime(data.index)
    if not(freq == '1D'):
       data = data.resample(freq).ffill()
    return data

def format_data(df_index, freq="1M", dropna=True, drop_zero=False):
    """
    Format dataframe, by freq, to return dataframe
    
    Parameters:
    df_index -- dataframe
    freq -- string ('1M', '1W', '1D')
    
    Returns:
    dataframe
    """
    data = resample_data(df_index, freq)
    data = data.pct_change(1)
    data = data.iloc[1:,]
    if dropna:
        data.dropna(inplace=True)
        
    if drop_zero:
        data = data.loc[(data!=0).any(1)]
    return data

def get_data_dict(data, data_type='index', dropna=True, drop_zero=True):
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
        data_dict[freq_string] = format_data(data, dm.switch_string_freq(freq_string),dropna, drop_zero)
    return data_dict

def get_prices_df(df_returns):
    """"
    Converts returns dataframe to index level dataframe

    Parameters:
    df_returns -- returns dataframe

    Returns:
    index price level - dataframe
    """
    
    df_index = 100*(1 + df_returns).cumprod()
    
    return update_df_index(df_index)

def update_df_index(df_index):
    
    #insert extra row at top for first month of 100
    data = []
    data.insert(0,{})
    df_prices = pd.concat([pd.DataFrame(data), df_index])
    
    #fill columns with 100 for row 1
    for col in df_prices.columns:
        df_prices[col][0] = 100

    #update index to prior month    
    df_prices.index.names = ['Dates']
    df_prices.reset_index(inplace=True)
    df_prices['Dates'][0] = df_index.index[0] - pd.DateOffset(months=1)
    df_prices.set_index('Dates', inplace=True)
    
    return df_prices

def get_price_series(return_series):
    price_series = return_series.copy()
    price_series[0] = return_series[0] + 1
    for i in range(1, len(return_series)):
        price_series[i] = (return_series[i] + 1) * price_series[i-1]
    return price_series

def transform_nexen_data(filepath):
    """
    converts nexen .xls file into dictionary of dataframes  

    Parameters
    ----------
    filepath : string
        DESCRIPTION.
    fillna : TYPE, optional
        DESCRIPTION. The default is False.

    Returns
    -------
    dict
        DESCRIPTION.

    """
    
    nexen_df = pd.read_excel(filepath)
    nexen_df = nexen_df[['Account Name\n', 'Account Id\n', 'Return Type\n', 'As Of Date\n',
                            'Market Value\n', 'Account Monthly Return\n']]
    nexen_df.columns = ['Name', 'Account Id', 'Return Type', 'Date', 'Market Value', 'Return']
    # nexen_df = di.nexenDataImporter(filepath).data
    returns_df = nexen_df.pivot_table(values='Return', index='Date', columns='Name')
    returns_df /=100
    mv_df = nexen_df.pivot_table(values='Market Value', index='Date', columns='Name')
    return {'returns': returns_df, 'market_values': mv_df}
    
def transform_bbg_data(filepath, sheet_name='data', freq='1M', col_list=[]):
    """
    

    Parameters
    ----------
    filepath : TYPE
        DESCRIPTION.
    sheet_name : TYPE, optional
        DESCRIPTION. The default is 'data'.
    freq : TYPE, optional
        DESCRIPTION. The default is '1M'.
    col_list : TYPE, optional
        DESCRIPTION. The default is [].

    Returns
    -------
    bbg_df : TYPE
        DESCRIPTION.

    """
    bbg_df = pd.read_excel(filepath, sheet_name=sheet_name, 
                            index_col=0,skiprows=[0,1,2,4,5,6])
    bbg_df.index.names = ['Dates']
    # bbg_df = di.bbgDataImporter(filepath, sheet_name,col_list=col_list)
    if col_list:
        bbg_df.columns = col_list
    bbg_df = resample_data(bbg_df, freq)
    return bbg_df

def transform_innocap_data(filepath, sheet_name='Default', freq = '1M'):
    """
    

    Parameters
    ----------
    filepath : TYPE
        DESCRIPTION.
    sheet_name : TYPE, optional
        DESCRIPTION. The default is 'Default'.
    freq : TYPE, optional
        DESCRIPTION. The default is '1M'.

    Returns
    -------
    dict
        DESCRIPTION.

    """
    innocap_df = pd.read_excel(filepath, sheet_name=sheet_name, skiprows=[0,1])
    innocap_df.columns = ['Dates', 'Name', 'Market Value', 'Return']
    
    returns_df = innocap_df.pivot_table(values='Return', index='Dates', columns='Name')
    returns_df = resample_data(returns_df, freq)
    returns_df /=100
    mv_df = innocap_df.pivot_table(values='Market Value', index='Dates', columns='Name')
    mv_df = resample_data(mv_df, freq)
    return {'returns': returns_df, 'market_values': mv_df}

def transform_innocap_exposure_data(filepath, sheet_name='Default', freq = '1M'):
    """
    Return dictionary of asset exposures for individual funds

    Parameters
    ----------
    filepath : TYPE
        excel spreadsheet with asset class exposure by fund
    sheet_name : TYPE, optional
        DESCRIPTION. The default is 'Default'.
    freq : TYPE, optional
        DESCRIPTION. The default is '1M'.

    Returns
    -------
    exposure_dict : TYPE
        DESCRIPTION.

    """
    innocap_df = pd.read_excel(filepath, sheet_name=sheet_name, skiprows=[0,1])
    innocap_df.columns = ['Dates', 'Name', 'Asset Class','10 Yr Equiv Net % Notional']
    names_list = [x for x in list(innocap_df.Name.unique()) if x == x]
    exposure_dict = {}
    for name in names_list:
        name_df = innocap_df.loc[innocap_df['Name'] == name]
        exposure_dict[name] = name_df.pivot_table(values='10 Yr Equiv Net % Notional', index='Dates', columns='Asset Class')
        exposure_dict[name] = resample_data(exposure_dict[name], freq)
    return exposure_dict