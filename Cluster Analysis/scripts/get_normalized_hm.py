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

# To run all HMs at once uncommented the code below and comment the Individual HM calc code

# # Iterate over the remaining DataFrames in qis_returns and merge them with the merged_df
# for key, df in qis_returns.items():
#     if key != 'UBS':
#         merged_df = pd.merge(merged_df, df, left_index=True, right_index=True, how='left')
#         merged_df.fillna(method='ffill', inplace=True)
# # Rename the index column to 'Date'
# merged_df.index.name = 'Date'
# def_df = pd.DataFrame()
# sp_returns = merged_df.iloc[:,0]
# dates_index = merged_df.index

# # Iterate over the columns from the second column onwards
# for column in merged_df.columns[1:]:
#     # Create a temporary DataFrame with dates as the index and SPTR returns and current column returns
#   if column not in ['SPTR_y','SPTR_x']:  
#     temp_df = pd.DataFrame(index=dates_index)
#     temp_df['SPTR_returns'] = sp_returns
#     temp_df[column] = merged_df[column]
#     hm = summary.get_hedge_metrics(temp_df, freq='1W', full_list=False, for_qis=True)
#     hm.drop(hm.columns[0], axis = 1,inplace=True)
#     hm = hm.transpose()
#     hm.index = [column]  # Set the row name as the column name
#     def_df = def_df.append(hm)
#     def_df = def_df.append(hm.transpose(), ignore_index=True)
#     #def_dict[column]=hm.transpose()


# To update individual bank QIS, uncomment the following lines and change the name of the bank respectively and comment the All HMs code
# Individual HM calc code starts

def_df = pd.DataFrame()

# Get the dates from the UBS dataframe
ubs_dates = ubs_df.index

# Demerge the dataframes using the UBS dates
demerged_dfs = {}
for key, df in qis_returns.items():
    if key != 'UBS':
        #demerged_df = df.reindex(ubs_dates)
        demerged_df = pd.DataFrame(index=ubs_dates)
        demerged_df = pd.merge(demerged_df, df, left_index=True, right_index=True, how='left')
        demerged_dfs[key] = demerged_df

demerged_dfs['UBS'] = ubs_df        
#compute raw hedge metrics
print('compute hedge metrics')
#def_df = pd.DataFrame()

# Get the SPTR returns column
sptr_returns = demerged_dfs['UBS']['SPTR']

# Iterate over the columns from the second column onwards
for column in demerged_dfs['BofA'].columns[1:]:
    # Create a temporary DataFrame with dates as the index and SPTR returns and current column returns
    temp_df = pd.DataFrame(index=demerged_dfs['BofA'].index)
    temp_df['SPTR_returns'] = sptr_returns
    temp_df[column] = demerged_dfs['BofA'][column]
    hm = summary.get_hedge_metrics(temp_df, freq='1W', full_list=False, for_qis=True)
    hm.drop(hm.columns[0], axis = 1,inplace=True)
    hm = hm.transpose()
    hm.index = [column]  # Set the row name as the column name
    #def_df = def_df.append(hm)
    def_df = def_df.append(hm.transpose(), ignore_index=True)


#Save the DataFrame to an Excel file
def_df.to_excel("BofA_hm.xlsx", index=True)
 
# Individual HM calc code ends
   
#merge dicts
print('merge hedge metric data frames')
#hm_df = util.append_dict_dfs(def_dict)
hm_df = pd.read_excel('HM_Universe.xlsx',  index_col=0,header = 0)
normalized_hm = util.get_normalized_data(hm_df)

#store in excel
print('store in excel')
file_path = dm.QIS_UNIVERSE + "Normalized_Hedge_Metrics.xlsx"
writer = pd.ExcelWriter(file_path,engine='xlsxwriter')
normalized_hm.to_excel(writer,sheet_name='Hedge Metrics')
writer.save()