# -*- coding: utf-8 -*-
"""
Created on Fri Apr 30 14:23:35 2021

@author: Powis Forjoe
"""
import pandas as pd
from EquityHedging.datamanager import data_manager as dm
from EquityHedging.reporting.excel import reports as rp

ADD_BACK = .0025
#TODO: need to automate this
#TODO: incorporate bloomberg api code as well

#Import data from bloomberg into dataframe and create dictionary with different frequencies
new_data = pd.read_excel(dm.UPDATE_DATA +'ups_data.xlsx', sheet_name='data', index_col=0)
new_data.columns
new_data.columns = ['SPTR', 'SX5T','M1WD', 'Long Corp', 'STRIPS', 'Down Var',
                    'Vortex', 'VOLA I', 'VOLA II','Dynamic Put Spread',
                    'GW Dispersion', 'Corr Hedge','Def Var (Mon)', 'Def Var (Fri)', 'Def Var (Wed)']

new_data_dict = dm.get_data_dict(new_data)

#get vrr data
vrr = pd.read_excel(dm.UPDATE_DATA+'vrr_tracks_data.xlsx', sheet_name='data', index_col=0)
vrr.columns =['VRR']
vrr_dict = dm.get_data_dict(vrr)

#add back 25 bps
for key in vrr_dict:
    freq = dm.switch_string_freq(key)
    vrr_dict[key]['VRR'] += ADD_BACK/(dm.switch_freq_int(freq))

#get put spread data
put_spread = pd.read_excel(dm.UPDATE_DATA+'put_spread_data.xlsx',
                             sheet_name='Daily', index_col=0)
put_spread.columns = ['99 Rep', 'Short Put', '99%/90% Put Spread']
put_spread = put_spread.iloc[1:,]
put_spread = put_spread[['99%/90% Put Spread']]
# put_spread.drop(['99 Rep', 'Short Put'], axis=1, inplace=True)

put_spread_price = dm.get_prices_df(put_spread)
put_spread_dict = dm.get_data_dict(put_spread_price)

#merge vrr and put spread dicts to the new_data dict
new_data_dict = dm.merge_dicts(new_data_dict, put_spread_dict)
new_data_dict = dm.merge_dicts(new_data_dict, vrr_dict)

#get data from returns_data.xlsx into dataframe
returns_dict = dm.get_equity_hedge_returns(all_data=True)

#set columns in new_data_dict to be in the same order as returns_dict
for key in new_data_dict:
    new_data_dict[key] = new_data_dict[key][list(returns_dict[key].columns)]
    
#clean up new_data_dict before adding to returns    

#remove first 3 rows from daily dataframe
new_data_dict['Daily'] = new_data_dict['Daily'].iloc[3:,]

#remove yearly dataframe from dict
new_data_dict.pop('Yearly')

#remove last row from weekly dataframe
new_data_dict['Weekly'] = new_data_dict['Weekly'][:-1]

#update returns_dict with new_data
for key in new_data_dict:
    returns_dict[key] = returns_dict[key].append(new_data_dict[key])

#create new returns report
rp.get_returns_report('returns_data_new', returns_dict)

