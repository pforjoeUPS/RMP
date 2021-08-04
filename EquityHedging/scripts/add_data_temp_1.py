# -*- coding: utf-8 -*-
"""
Created on Fri Apr 30 14:23:35 2021

@author: Powis Forjoe
"""
import pandas as pd
from EquityHedging.datamanager import data_manager as dm
from EquityHedging.reporting.excel import reports as rp

#import analytics
#TODO: need to automate this, by incorporating bloomberg code
new_data = pd.read_excel(dm.UPDATE_DATA +'ups_data_1.xlsx', sheet_name='Data', index_col=0)
new_data.columns
new_data.columns = ['SPTR', 'SX5T','M1WD', 'Long Corp', 'STRIPS', 'Down Var',
                    'Vortex', 'VOLA I', 'VOLA II','Dynamic Put Spread',
                    'GW Dispersion', 'Corr Hedge','Def Var (Mon)', 'Def Var (Fri)', 'Def Var (Wed)']

new_data_dict = dm.get_data_dict(new_data)

vrr = pd.read_excel(dm.UPDATE_DATA+'SGI VRR USD Official Chained Tracks.xlsx', sheet_name='data', index_col=0)
vrr.columns =['VRR']
vrr_dict = dm.get_data_dict(vrr)

put_spread = pd.read_excel(dm.UPDATE_DATA+'Put Spread - Return Series 3-31-21.xlsx',
                             sheet_name='Daily', index_col=0)
put_spread.columns = ['99 Rep', 'Short Put', '99%/90% Put Spread']
put_spread = put_spread.iloc[1:,]
put_spread.drop(['99 Rep', 'Short Put'], axis=1, inplace=True)

put_spread_price = dm.get_prices_df(put_spread)
put_spread_dict = dm.get_data_dict(put_spread_price)

new_data_dict = dm.merge_dicts(new_data_dict, put_spread_dict)
new_data_dict = dm.merge_dicts(new_data_dict, vrr_dict)

returns_dict = dm.get_equity_hedge_returns(all_data=True)
returns_dict = {}
for key in new_data_dict:
    returns_dict[key] = pd.read_excel(dm.RETURNS_DATA_FP+'ups_equity_hedge//returns_data_1.xlsx',sheet_name=key, index_col=0)

for key in new_data_dict:
    new_data_dict[key] = new_data_dict[key][list(returns_dict[key].columns)]
    add_back = .0025
    freq = dm.switch_string_freq(key)
    new_data_dict[key]['VRR'] += add_back/(dm.switch_freq_int(freq))

new_data_dict['Daily'] = new_data_dict['Daily'].iloc[10:,]
new_data_dict.pop('Yearly')
new_data_dict['Weekly'] = new_data_dict['Weekly'][:-1]

for key in new_data_dict:
    returns_dict[key] = returns_dict[key].append(new_data_dict[key])

rp.get_returns_report('returns_data_2', returns_dict)

