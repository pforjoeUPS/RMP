# -*- coding: utf-8 -*-
"""
Created on Sun Aug 14 20:13:09 2022

@author: NVG9HXP
"""
import os
from .import data_manager as dm
from .import data_xformer as dxf
import pandas as pd
from ..reporting.excel import reports as rp

CWD = os.getcwd()
RETURNS_DATA_FP = CWD +'\\EquityHedging\\data\\returns_data\\'
UPDATE_DATA_FP = CWD +'\\EquityHedging\\data\\update_data\\'
BMK_COL_LIST = ['SPTR', 'SX5T', 'M1WD', 'MIMUAWON', 'Long Corp', 'STRIPS',
                    'HFRX Macro/CTA', 'HFRX Absolute Return', 'SG Trend']
HF_COL_LIST = ['HFRX Macro/CTA', 'SG Trend','HFRX Absolute Return','DM Equity',
               'EM Equity','Gov Bonds','Agg Bonds','EM Bonds','High Yield','BCOM',
               'S&P GSCI TR','Equity Volatility','EM FX','FX Carry','Commo Carry',
               'CTAs','HFRX Systematic Macro','HFRX Rel Val Arb','HFRX Global',
               'HFRX Eq Hedge','HFRX Event driven','HFRX Convert Arb','HFRX EM',
               'HFRX Commodities','HFRX RV']
FREQ_LIST = ['Daily', 'Weekly', 'Monthly', 'Quarterly', 'Yearly']
EQ_HEGDE_COL_LIST = ['SPTR', 'SX5T','M1WD', 'Long Corp', 'STRIPS', 'Down Var',
                     'Vortex', 'VOLA I', 'VOLA II','Dynamic VOLA','Dynamic Put Spread',
                     'GW Dispersion', 'Corr Hedge','Def Var (Mon)', 'Def Var (Fri)',
                     'Def Var (Wed)', 'Commodity Basket']

#TODO: get rid of this
def update_nexen_data(filename, report_name):
    nexen_dict = dxf.transform_nexen_data(UPDATE_DATA_FP+filename)
    rp.get_ret_mv_report(report_name, nexen_dict, data_file = True)

#TODO: get rid of this
def update_bbg_data(filename,sheet_name='data', report_name='bbg_data'):
    
    bbg_data = dxf.transform_bbg_data(UPDATE_DATA_FP+filename, sheet_name)
    bbg_dict = dxf.get_data_dict(bbg_data)
    rp.get_returns_report(report_name, bbg_dict, True)

def update_nexen_liq_alts_data(filename='Monthly Returns Liquid Alts.xls'):
    returns_dict = dxf.transform_nexen_data(UPDATE_DATA_FP+filename)
    rp.get_ret_mv_report('nexen_liq_alts_data-old', returns_dict, data_file = True)
    
def update_innocap_liq_alts_data(filename='1907_hf_data.xlsx'):
    innocap_dict = dxf.transform_innocap_data(UPDATE_DATA_FP+filename)
    old_col_list = ['1907 Campbell Trend Following LLC', '1907 III Class A','1907 Penso Class A',
                    '1907 Systematica Trend Following', 'UPS 1907 ARP Trend Following LLC',
                    '1907 ARP Trend Following LLC_Class EM', '1907 III Fund Ltd _ Class CV', '1907 Kepos']
    new_col_list = ['1907 Campbell TF', '1907 III Class A', '1907 Penso Class A', '1907 Systematica TF',
                    '1907 ARP TF', '1907 ARP EM', '1907 III CV','1907 Kepos RP']
    innocap_dict = update_df_dict_columns(innocap_dict, old_col_list, new_col_list)
    returns_dict = get_return_data('innocap_liq_alts_data.xlsx', ['returns', 'market_values'])
    returns_dict = update_data(returns_dict, innocap_dict, False)    
    
    rp.get_ret_mv_report('innocap_liq_alts_data-old', returns_dict, data_file = True)
    
def update_liq_alts_bmk_data(filename='liq_alts_bmk_data.xlsx'):
    bbg_data = dxf.transform_bbg_data(UPDATE_DATA_FP+filename, sheet_name='bbg_d', freq = '1D', col_list=HF_COL_LIST)
    bbg_data = bbg_data[['HFRX Macro/CTA', 'HFRX Absolute Return', 'SG Trend']]
    returns_dict = dxf.get_data_dict(bbg_data)
    for key in returns_dict:
        returns_dict[key] = returns_dict[key][['HFRX Macro/CTA', 'HFRX Absolute Return', 'SG Trend']]
    rp.get_returns_report('liq_alts_bmks-old', returns_dict, True)
    
def update_hf_bmk_data(filename='liq_alts_bmk_data.xlsx'):
    bbg_data = dxf.transform_bbg_data(UPDATE_DATA_FP+filename,sheet_name='bbg_d',freq='1D', col_list=HF_COL_LIST)
    returns_dict = dxf.get_data_dict(bbg_data)
    rp.get_returns_report('hf_bmks-old', returns_dict, True)
    
def update_bmk_data(filename='bmk_data.xlsx'):
    bbg_data = dxf.transform_bbg_data(UPDATE_DATA_FP+filename, freq = '1D', col_list=BMK_COL_LIST)
    bbg_dict = dxf.get_data_dict(bbg_data)
    returns_dict = get_return_data('bmk_returns.xlsx', FREQ_LIST, True)
    bbg_dict = match_dict_columns(returns_dict, bbg_dict)
    returns_dict = update_data(returns_dict, bbg_dict)
    rp.get_returns_report('bmk_returns-old', returns_dict, True)
    
def update_asset_class_data(filename='Historical Asset Class Returns.xls'):
    returns_dict = dxf.transform_nexen_data(UPDATE_DATA_FP+filename)
    old_col_list = ['Total EQ w/o Derivatives','Total Fixed Income',
                    'Total Liquid Alts','Total Real Estate','Total Private Equity',
                    'Total Credit','LDI ONLY-TotUSPenMinus401H']
    new_col_list = ['Public Equity', 'Fixed Income', 'Liquid Alts','Real Estate',
                    'Private Equity', 'Credit', 'Total Group Trust']
    returns_dict = update_df_dict_columns(returns_dict, old_col_list, new_col_list)
   
    rp.get_ret_mv_report('upsgt_returns-old', returns_dict, data_file = True)
    
def update_eq_hedge_returns():
    #get data from returns_data.xlsx into dictionary
    returns_dict = dm.get_equity_hedge_returns(all_data=True)

    #create dictionary that contains updated returns
    new_data_dict = create_update_dict()
    returns_dict = update_data(returns_dict, new_data_dict)
    rp.get_returns_report('eq_hedge_returns-old', returns_dict, data_file = True)
    
def get_return_data(filename, sheet_list=[], freq_data=False):
    if sheet_list:
        return_dict = {}
        for sheet in sheet_list:
            temp_ret = pd.read_excel(RETURNS_DATA_FP+filename,sheet_name=sheet,index_col=0)
            temp_ret = get_real_cols(temp_ret)  
            return_dict[sheet] = temp_ret.copy()
        return return_dict
    else:
        return_df = pd.read_excel(RETURNS_DATA_FP+filename,sheet_name=sheet,index_col=0)
        return_df = get_real_cols(temp_ret)  
        return return_df

def update_columns(df, old_col_list, new_col_list):
    df = df[old_col_list]
    df.columns = new_col_list
    return df

def update_df_dict_columns(df_dict, old_col_list, new_col_list):
    for key in df_dict:
        df_dict[key] = update_columns(df_dict[key], old_col_list, new_col_list)
    return df_dict
    
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
        data = dxf.get_prices_df(data)
    
    data_dict = dxf.get_data_dict(data)
    return data_dict

def add_bps(vrr_dict, strat_name, add_back=.0025):
    '''
    Adds bps back to the returns for the vrr strategy

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
        temp_df[strat_name] += add_back/(dm.switch_freq_int(freq))
        
        #add value to the temp dictionary
        temp_dict[key] = temp_df
    return temp_dict

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
    new_ups_data_dict = get_data_to_update(EQ_HEGDE_COL_LIST, 'ups_data.xlsx')
    
    #get vrr data
    vrr_dict = get_data_to_update(['VRR'], 'vrr_tracks_data.xlsx', sheet_name='VRR')
    vrr2_dict = get_data_to_update(['VRR 2'], 'vrr_tracks_data.xlsx', sheet_name='VRR2')
    vrr_trend_dict = get_data_to_update(['VRR Trend'], 'vrr_tracks_data.xlsx', sheet_name='VRR Trend')
    
    #add back 25 bps
    vrr_dict = add_bps(vrr_dict,'VRR')
    vrr2_dict = add_bps(vrr2_dict,'VRR 2', add_back= 0.005)
    vrr_trend_dict =add_bps(vrr_trend_dict, 'VRR Trend', add_back= 0.005)
    
    #get put spread data
    put_spread_dict = get_data_to_update(['99 Rep', 'Short Put', '99%/90% Put Spread'], 'put_spread_data.xlsx', 'Daily', put_spread = True)
    
    #merge vrr and put spread dicts to the new_data dict
    new_data_dict = dm.merge_dicts_list([new_ups_data_dict,put_spread_dict, vrr_dict, vrr2_dict, vrr_trend_dict], True)
    
    #get data from returns_data.xlsx into dictionary
    returns_dict = dm.get_equity_hedge_returns(all_data=True)
    
    #set columns in new_data_dict to be in the same order as returns_dict
    new_data_dict = match_dict_columns(returns_dict, new_data_dict)
        
    #return a dictionary
    return new_data_dict

def get_new_returns_df(new_returns_df,returns_df):
    #copy dataframes
    new_ret_df = new_returns_df.copy()
    ret_df = returns_df.copy()
    #reset both data frames index to make current index (dates) into a column
    new_ret_df.index.names = ['Date']
    ret_df.index.names = ['Date']
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

def update_data(main_dict, new_dict, freq_data = True):
    updated_dict = {}
    for key in main_dict:
        #create returns data frame
        new_ret_df = new_dict[key].copy()
        ret_df = main_dict[key].copy()
        
        #update current year returns 
        if key == 'Yearly':
            if ret_df.index[-1] == new_ret_df.index[-1]:
                ret_df = ret_df[:-1]
        #get new returns df       
        new_ret_df = get_new_returns_df(new_ret_df, ret_df)
        updated_dict[key] = pd.concat([ret_df,new_ret_df])
    
    if freq_data:
        updated_dict = check_returns(updated_dict)
    return updated_dict

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

