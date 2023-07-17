# -*- coding: utf-8 -*-
"""
Created on Mon Nov 21 21:02:27 2022

@author:  Powis Forjoe, Maddie Choi
"""

import os

os.chdir('..\..')

from EquityHedging.datamanager import data_manager as dm
from EquityHedging.analytics import  util
from EquityHedging.analytics import summary 
import pandas as pd
from functools import reduce

#get equity portfolio daily data
print('get equity portfolio weekly data')
equity_bmk = 'SPTR'
strat_drop_list = ['99%/90% Put Spread', 'Vortex']
returns = dm.get_equity_hedge_returns(equity_bmk, strat_drop_list = strat_drop_list)
weekly_ret=returns['Daily'].copy()

#compute weighted hedges
print('compute weighted hedges')
notional_weights = dm.get_notional_weights(returns['Daily'])
df_weighted_hedges = util.get_weighted_hedges(weekly_ret, notional_weights)
df_weighted_hedges = df_weighted_hedges.drop(['VOLA 3', 'GW Dispersion', 'Dynamic Put Spread'], axis=1)
#get def universe
print('get QIS universe')
qis_uni = dm.get_qis_uni_dict()
#add benchmark data to each strat universe to compute hm
sp_dict = {}
for key in qis_uni:
    sp_dict[key] = pd.DataFrame(weekly_ret['SPTR'])
    
qis_returns = dm.merge_dicts(sp_dict,qis_uni)

qis_returns['Weighted Hedges'] = df_weighted_hedges

# Get the dataframe from the 'UBS' key in qis_returns
ubs_df = qis_returns['UBS']

# Initialize the merged DataFrame with the UBS DataFrame
merged_df = ubs_df

# Iterate over the remaining DataFrames in qis_returns and merge them with the merged_df
for key, df in qis_returns.items():
    if key != 'UBS':
        merged_df = pd.merge(merged_df, df, left_index=True, right_index=True, how='left')
        merged_df.fillna(method='ffill', inplace=True)
# Rename the index column to 'Date'
merged_df.index.name = 'Date'

# Get the dates from the UBS dataframe
ubs_dates = ubs_df.index

# Demerge the dataframes using the UBS dates
demerged_dfs = {}
for key, df in qis_returns.items():
    if key != 'UBS':
        demerged_df = pd.DataFrame(index=ubs_dates)
        demerged_df = pd.merge(demerged_df, df, left_index=True, right_index=True, how='left')
        demerged_dfs[key] = demerged_df

demerged_dfs['UBS'] = ubs_df        
#compute raw hedge metrics
print('compute hedge metrics')
def_dict = {}
for key in qis_uni:
      print(key)
      hm = summary.get_hedge_metrics(demerged_dfs[key], freq='1W', full_list=False, for_qis=True)
      hm.drop(hm.columns[0], axis = 1,inplace=True)
      def_dict[key]=hm.transpose()

    
#merge dicts
print('merge hedge metric data frames')
hm_df = util.append_dict_dfs(def_dict)
normalized_hm = util.get_normalized_data(hm_df)

#store in excel
print('store in excel')
file_path = dm.QIS_UNIVERSE + "Normalized_Hedge_Metrics.xlsx"
writer = pd.ExcelWriter(file_path,engine='xlsxwriter')
normalized_hm.to_excel(writer,sheet_name='Hedge Metrics')
writer.save()