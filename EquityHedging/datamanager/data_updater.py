# -*- coding: utf-8 -*-
"""
Created on Sun Aug 14 20:13:09 2022

@author: NVG9HXP
"""

"""
Created on Sun Aug  7 22:18:15 2022

@author: NVG9HXP
"""

import os
from .import data_manager as dm
import pandas as pd
from ..reporting.excel import reports as rp

CWD = os.getcwd()
# RETURNS_DATA_FP = CWD +'\\EquityHedging\\data\\'
UPDATE_DATA_FP = CWD +'\\EquityHedging\\data\\update_data\\'

def update_nexen_data(filename, report_name):
    nexen_dict = dm.transform_nexen_data_1(UPDATE_DATA_FP+filename)
    rp.get_nexen_report(report_name, nexen_dict, data_file = True)

def update_bbg_data(filename, report_name,sheet_name='data'):
    
    bbg_data = dm.transform_bbg_data(UPDATE_DATA_FP+filename, sheet_name)
    bbg_dict = dm.get_data_dict(bbg_data)
    rp.get_returns_report(report_name, bbg_dict, True)

def update_liq_alts_port_data(filename='Monthly Returns Liquid Alts.xls'):
    return update_nexen_data(filename,'liq_alts_data')

def update_liq_alts_bmk_data(filename='bmk_data.xlsx'):
    bbg_data = dm.transform_bbg_data(UPDATE_DATA_FP+filename)
    bbg_data = bbg_data[['HFRXM Index', 'HFRXAR Index','NEIXCTAT Index']]
    bbg_data.columns = ['HFRX Macro/CTA', 'HFRX Absolute Return', 'SG Trend']
    bbg_dict = dm.get_data_dict(bbg_data)
    rp.get_returns_report('liq_alts_bmks', bbg_dict, True)

def update_bmk_data(filename='bmk_data.xlsx'):
    bbg_data = dm.transform_bbg_data(UPDATE_DATA_FP+filename)
    # bbg_data.columns = ['HFRX Macro/CTA', 'HFRX Absolute Return', 'SG Trend']
    bbg_dict = dm.get_data_dict(bbg_data)
    rp.get_returns_report('liq_alts_bmks', bbg_dict, True)

    
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
    data = pd.read_excel(UPDATE_DATA_FP + filename, sheet_name= sheet_name, index_col=0)
    
    #rename column(s) in dataframe
    data.columns = col_list
    
    if put_spread:
        #remove the first row of dataframe
        data = data.iloc[1:,]
    
        #add column into dataframe
        data = data[['99%/90% Put Spread']]
    
        #add price into dataframe
        data = dm.get_prices_df(data)
    
    data_dict = dm.get_data_dict(data)
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
        freq = dm.switch_string_freq(key)
        
        #add to dataframe
        temp_df['VRR'] += add_back/(dm.switch_freq_int(freq))
        
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
        main_dict = dm.merge_dicts(main_dict,dicts)
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
    new_data_dict = dm.get_data_to_update(dm.NEW_DATA_COL_LIST, 'ups_data.xlsx')
    
    #get vrr data
    vrr_dict = get_data_to_update(['VRR'], 'vrr_tracks_data.xlsx')
    
    #add back 25 bps
    vrr_dict = add_bps(vrr_dict)
    
    #get put spread data
    put_spread_dict = get_data_to_update(['99 Rep', 'Short Put', '99%/90% Put Spread'], 'put_spread_data.xlsx', 'Daily', put_spread = True)
    
    #merge vrr and put spread dicts to the new_data dict
    new_data_dict = merge_dicts_list([new_data_dict,put_spread_dict, vrr_dict])
    
    #get data from returns_data.xlsx into dictionary
    returns_dict = dm.get_equity_hedge_returns(all_data=True)
    
    #set columns in new_data_dict to be in the same order as returns_dict
    new_data_dict = match_dict_columns(returns_dict, new_data_dict)
        
    #return a dictionary
    return new_data_dict

