# -*- coding: utf-8 -*-
"""
Created on Fri Apr 30 14:23:35 2021

@author: Powis Forjoe
"""
import pandas as pd
from EquityHedging.datamanager import data_manager as dm
from EquityHedging.reporting.excel import reports as rp

#TODO: need to automate this
#TODO: incorporate bloomberg api code as well

###############################
#METHODS
################################

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
    data = pd.read_excel(dm.UPDATE_DATA + filename, sheet_name= sheet_name, index_col=0)
    
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

def get_bloomberg_data(col_list, filename = 'ups_data.xlsx', sheet_name = 'data'):
    '''
    Imports bloomberg data from an excel sheet into a dictionary

    Parameters
    ----------
    col_list : list
        column names.
    filename : string, optional
        name of excel file. The default is 'ups_data.xlsx'.
    sheet_name : string, optional
        sheet name in excel file. The default is 'data'.

    Returns
    -------
    new_data_dict : dictionary
        dictionary of returns dataframes of different frequencies.

    '''
    #read excel file to dataframe
    new_data = pd.read_excel(dm.UPDATE_DATA + filename, sheet_name= sheet_name, index_col=0)
    
    #rename columns in dataframe
    new_data.columns = col_list
    
    #create dictionary
    new_data_dict = dm.get_data_dict(new_data)
    
    return new_data_dict

def get_vrr_data(col = 'VRR', filename = 'vrr_tracks_data.xlsx', sheet_name = 'data'):
    '''
    Imports VRR data from excel sheet into a dictionary

    Parameters
    ----------
    col : string
        DESCRIPTION. The default is 'VRR'.
    filename : string
        DESCRIPTION. The default is 'vrr_tracks_data.xlsx'.
    sheet_name : string
        DESCRIPTION. The default is 'data'.

    Returns
    -------
    vrr_dict : dictionary
        dictionary of VRR returns

    '''
    #read excel file into dataframe
    vrr = pd.read_excel(dm.UPDATE_DATA + filename, sheet_name = sheet_name, index_col=0)
    
    #rename columns into dataframe
    vrr.columns = [col]
    
    #create dictionary
    vrr_dict = dm.get_data_dict(vrr)
    
    return vrr_dict

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

def get_put_spread_data(col_list, col = '99%/90% Put Spread', filename = 'put_spread_data.xlsx', sheet_name = 'Daily'):
    '''
    Imports put spread data from excel sheet into dictionary

    Parameters
    ----------
    col_list : list
        column names
    col : string
        Data column needed. The default is '99%/90% Put Spread'.
    filename : string
        name of file. The default is 'put_spread_data.xlsx'.
    sheet_name : string
        name of sheet. The default is 'Daily'.

    Returns
    -------
    put_spread_dict : dictionary
        dictioinary of put spread strategy data

    '''
    #read excel file into dataframe
    put_spread = pd.read_excel(dm.UPDATE_DATA+filename,
                             sheet_name=sheet_name, index_col=0)
    
    #rename columns into dataframe
    put_spread.columns = col_list
    
    #remove the first row of dataframe
    put_spread = put_spread.iloc[1:,]
    
    #add column into dataframe
    put_spread = put_spread[[col]]
    
    #add price into dataframe
    put_spread_price = dm.get_prices_df(put_spread)
    
    #create dictionary
    put_spread_dict = dm.get_data_dict(put_spread_price)
    
    return put_spread_dict

def merge_data_dicts(main_dict, dict_list):
    '''
    merge main dictionary with a dictionary list

    Parameters
    ----------
    main_dict : dictionary
    dict_list : list

    Returns
    -------
    main_dict : dictionary
        new dictionary created upon being merged with a list

    '''
    #iterate through dictionary 
    for dicts in dict_list:
        
        #merge each dictionary in the list of dictionaries to the main
        main_dict = dm.merge_dicts(main_dict, dicts)
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
######################################################################################################################################

###############################
#SCRIPT
################################

new_data_col_list = ['SPTR', 'SX5T','M1WD', 'Long Corp', 'STRIPS', 'Down Var',
                    'Vortex', 'VOLA I', 'VOLA II','Dynamic Put Spread',
                    'GW Dispersion', 'Corr Hedge','Def Var (Mon)', 'Def Var (Fri)', 'Def Var (Wed)']

#Import data from bloomberg into dataframe and create dictionary with different frequencies
new_data_dict = get_data_to_update(new_data_col_list, 'ups_data.xlsx')
#new_data_dict_1 = get_data(new_data_col_list, 'ups_data.xlsx')

#get vrr data
vrr_dict = get_data_to_update(['VRR'], 'vrr_tracks_data.xlsx')
#vrr_dict_1 = get_data(['VRR'], 'vrr_tracks_data.xlsx')

#add back 25 bps
vrr_dict = add_bps(vrr_dict)

#get put spread data
ps_col_list = ['99 Rep', 'Short Put', '99%/90% Put Spread']
put_spread_dict = get_data_to_update(ps_col_list, 'put_spread_data.xlsx', 'Daily', put_spread = True)
#put_spread_dict_1 = get_data(ps_col_list,'put_spread_data.xlsx', 'Daily', put_spread=True)

#merge vrr and put spread dicts to the new_data dict
new_data_dict = merge_data_dicts(new_data_dict,[put_spread_dict, vrr_dict])

#get data from returns_data.xlsx into dataframe
returns_dict = dm.get_equity_hedge_returns(all_data=True)

#set columns in new_data_dict to be in the same order as returns_dict
new_data_dict = match_dict_columns(returns_dict, new_data_dict)    


#clean up new_data_dict before adding to returns    

#remove first n rows from daily dataframe
n = 64
new_data_dict['Daily'] = new_data_dict['Daily'].iloc[n:,]

#remove first n rows from weekly dataframe
n = 7
new_data_dict['Weekly'] = new_data_dict['Weekly'].iloc[n:,]

#remove last row from weekly dataframe
n =1
new_data_dict['Weekly'] = new_data_dict['Weekly'][:-n]

#remove first n rows from monthly dataframe
n = 3
new_data_dict['Monthly'] = new_data_dict['Monthly'].iloc[n:,]

#remove first n rows from quarterly dataframe
n = 1
new_data_dict['Quarterly'] = new_data_dict['Quarterly'].iloc[n:,]

#remove yearly dataframe from dict
new_data_dict.pop('Yearly')


#update returns_dict with new_data
returns_dict = append_dict(returns_dict, new_data_dict)

#create new returns report
rp.get_returns_report('returns_data_new', returns_dict)

