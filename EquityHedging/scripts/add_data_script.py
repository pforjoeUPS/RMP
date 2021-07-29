# -*- coding: utf-8 -*-
"""
Created on Mon Jul 26 22:35:26 2021

@author: gcz5chn
"""
import os
os.chdir("..\..")
from EquityHedging.datamanager import data_manager as dm
from EquityHedging.reporting.excel import reports as rp

new_data_col_list = ['SPTR', 'SX5T','M1WD', 'Long Corp', 'STRIPS', 'Down Var',
                    'Vortex', 'VOLA I', 'VOLA II','Dynamic Put Spread',
                    'GW Dispersion', 'Corr Hedge','Def Var (Mon)', 'Def Var (Fri)', 'Def Var (Wed)']

#Import data from bloomberg into dataframe and create dictionary with different frequencies
new_data_dict = dm.get_data_to_update(new_data_col_list, 'ups_data.xlsx')

#get vrr data
vrr_dict = dm.get_data_to_update(['VRR'], 'vrr_tracks_data.xlsx')

#add back 25 bps
vrr_dict = dm.add_bps(vrr_dict)

#get put spread data
ps_col_list = ['99 Rep', 'Short Put', '99%/90% Put Spread']
put_spread_dict = dm.get_data_to_update(ps_col_list, 'put_spread_data.xlsx', 'Daily', put_spread = True)

#merge vrr and put spread dicts to the new_data dict
new_data_dict =dm.merge_data_dicts(new_data_dict,[put_spread_dict, vrr_dict])

#get data from returns_data.xlsx into dictionary
returns_dict = dm.get_equity_hedge_returns(all_data=True)

#set columns in new_data_dict to be in the same order as returns_dict
new_data_dict = dm.match_dict_columns(returns_dict, new_data_dict)    

# #remove first n rows from daily dataframe
# n = 64
# new_data_dict['Daily'] = new_data_dict['Daily'].iloc[n:,]

# #remove first n rows from weekly dataframe
# n = 7
# new_data_dict['Weekly'] = new_data_dict['Weekly'].iloc[n:,]

# #remove last row from weekly dataframe
# n =1
# new_data_dict['Weekly'] = new_data_dict['Weekly'][:-n]

# #remove first n rows from monthly dataframe
# n = 3
# new_data_dict['Monthly'] = new_data_dict['Monthly'].iloc[n:,]

# #remove first n rows from quarterly dataframe
# n = 1
# new_data_dict['Quarterly'] = new_data_dict['Quarterly'].iloc[n:,]

# #remove yearly dataframe from dict
# new_data_dict.pop('Yearly')


#update returns_dict with new_data
returns_dict = dm.append_dict(returns_dict, new_data_dict)

#create new returns report
rp.get_returns_report('returns_data_new', returns_dict)
