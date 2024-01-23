# -*- coding: utf-8 -*-
"""
Created on Wed Nov 18 17:15:17 2020

@author: Powis Forjoe
"""

from . import util_new
from ..datamanager import data_manager_new as dm

SPTR_MAXDD = {'period':'SPTR Max DD',
              'start': '2008-01-01', 
              'end':'2009-03-09'}

GFC = {'period':'Financial Crisis', 
       'start': '2008-05-19', 
       'end':'2009-03-09'}

EURO_DEBT = {'period':'European Sovereign Debt Crisis', 
             'start': '2010-04-23', 
             'end':'2010-07-02'}

US_DEBT = {'period':'US Debt Downgrade', 
           'start': '2011-07-07', 
           'end':'2011-10-03'}

CHINA_WEAKNESS = {'period':'China weakness concerns', 
                  'start': '2015-08-10', 
                  'end':'2015-08-25'}

OIL_DROP = {'period':'Drop in oil prices, China Instability', 
            'start': '2015-12-29', 
            'end':'2016-02-11'}

FEB_2018 = {'period':'Feb 2018 Flash Crash', 
            'start': '2018-01-26', 
            'end':'2018-02-08'}

Q4_2018 = {'period':'Q4 2018', 
           'start': '2018-09-20', 
           'end':'2018-12-24'}

COVID_19 = {'period':'Coronavirus Pandemic', 
            'start': '2020-02-19', 
            'end':'2020-03-23'}

EVENTS = [SPTR_MAXDD, GFC, EURO_DEBT, US_DEBT, CHINA_WEAKNESS,
          OIL_DROP, FEB_2018, Q4_2018, COVID_19]


def compute_event_ret(df_index, col, start, end):
    """
    Returns the return of an event

    Parameters
    ----------
    df_index : dataframe
        index dataframe.
    col : string
        column name (strategy name) in df_index.
    start : string
        start date.
    end : string
        end date.

    Returns
    -------
    double
        returns.

    """    
    return df_index[col].loc[end] / df_index[col].loc[start] - 1

def separate_events(events):
    """
    separate the list of dictionarries into a dictionary

    Parameters
    ----------
    events : list
        list of dictionaries containing historical event data.

    Returns
    -------
    dictionary
        
    """
    
    #define 3 lists to contain period, start and end values
    period = []
    start = []
    end = []
    
    #lopp through event dictionary to get data for each list
    for event in events:
        period.append(event['period'])
        start.append(event['start'])
        end.append(event['end'])
    
    #return dictionary
    return {'Period': period, 'Start': start, 'End': end}

def get_hist_sim_table(df_returns, notional_weights=[], weighted=False):
    """
    Returns historical selloffs dataframe

    Parameters
    ----------
    df_returns : dataframe
        dataframe of returns.
    notional_weights : list, optional
        notional weights of strategies. The default is [].
    weighted : boolean, optional
         Include weighgted hedges. The default is False.

    Returns
    -------
    df_hist : dataframe

    """
    
    #get index level data
    df_index = dm.get_prices_df(df_returns)
    
    #computed weighted hedges
    if weighted:
        notional_weights = util.check_notional(df_returns, notional_weights)
        df_index = util.get_weighted_hedges(df_index, notional_weights)
    
    #create dictionary 
    hist_dict = {}
    
    periods = separate_events(EVENTS)['Period']
    hist_dict['Start'] = separate_events(EVENTS)['Start']
    hist_dict['End'] = separate_events(EVENTS)['End']
    
    #loop through columns to create dictionary
    for col in df_index:
        strat_df = dm.remove_na(df_index, col)
        
        #temp_col to store strategy selloff data
        temp_col = []
        temp_dict = {}
        for event in EVENTS:
            start = event['start']
            end = event['end']
            period = event['period']
            try:
                event_return = compute_event_ret(strat_df, col, start, end)
                temp_col.append(event_return)
                temp_dict[period] = event_return
            except KeyError:
                print(f'\t\tSkipping {period} selloff event for {col}')
                temp_col.append(float("nan"))
                pass
        hist_dict[col] = temp_col

    #convert dictionary to dataframe
    df_hist = util.convert_dict_to_df(hist_dict, periods)
    return df_hist