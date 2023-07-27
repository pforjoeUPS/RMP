# -*- coding: utf-8 -*-
"""
Created on Sun Aug 14 2022

@author: Powis Forjoe
"""

import pandas as pd
import os
# from .import data_importer as di
from .import data_manager as dm

CWD = os.getcwd()
DATA_FP = CWD +'\\EquityHedging\\data\\'

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
    bbg_df = dm.resample_data(bbg_df, freq)
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
    returns_df = dm.resample_data(returns_df, freq)
    returns_df /=100
    mv_df = innocap_df.pivot_table(values='Market Value', index='Dates', columns='Name')
    mv_df = dm.resample_data(mv_df, freq)
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
        exposure_dict[name] = dm.resample_data(exposure_dict[name], freq)
    return exposure_dict