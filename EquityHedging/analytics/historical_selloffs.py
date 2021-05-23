# -*- coding: utf-8 -*-
"""
Created on Wed Nov 18 17:15:17 2020

@author: Powis Forjoe
"""

import pandas as pd
from ..datamanager import data_manager as dm
from .import util

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


EVENTS = [GFC, EURO_DEBT, US_DEBT, CHINA_WEAKNESS,
          OIL_DROP, FEB_2018, Q4_2018, COVID_19]


#TODO: Add definitions
def compute_event_ret(df_index, col, start, end):
    """ 
    """
    
    return df_index[col].loc[end] / df_index[col].loc[start] - 1

def separate_events(events):
    """ 
    """
    
    period = []
    start = []
    end = []
    for event in events:
        period.append(event['period'])
        start.append(event['start'])
        end.append(event['end'])
        
    return {'Period': period, 'Start': start, 'End': end}

def get_index_df(df_returns, notional_weights=[], weighted=False):
    """ 
    """
    
    df_index = dm.get_prices_df(df_returns)
    
    if weighted:
        notional_weights = util.check_notional(df_returns, notional_weights)
        strat_weights = util.get_strat_weights(notional_weights)
        
        #compute weighted hedges returns
        df_index['Weighted Hedges'] = df_index.dot(tuple(strat_weights))
    return df_index

def get_hist_sim_table(df_returns, notional_weights=[], weighted=False):
    """ 
    """
    
    df_index = get_index_df(df_returns, notional_weights, weighted)
    hist_dict = {}
    
    periods = separate_events(EVENTS)['Period']
    hist_dict['Start'] = separate_events(EVENTS)['Start']
    hist_dict['End'] = separate_events(EVENTS)['End']
    
    for col in df_index.columns:
        strat_df = dm.remove_na(df_index, col)
        temp_col = []
        for event in EVENTS:
            start = event['start']
            end = event['end']
            event_return = compute_event_ret(strat_df, col, start, end)
            temp_col.append(event_return)
        hist_dict[col] = temp_col
    df_hist = pd.DataFrame(hist_dict, index = periods)
    return df_hist