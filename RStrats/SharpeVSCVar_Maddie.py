# -*- coding: utf-8 -*-
"""
Created on Tue Oct  3 15:45:57 2023

@author: pcr7fjw
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from EquityHedging.datamanager import data_manager as dm
from EquityHedging.analytics import returns_stats  as rs
from EquityHedging.analytics.util import get_df_weights
from EquityHedging.analytics import summary
from matplotlib.ticker import FuncFormatter

import os

CWD = os.getcwd()

#Moments only
index_prices = pd.read_excel(CWD+'\\RStrats\\' + 'JPMMomentsAnalysis.xlsx', sheet_name = 'Index', index_col=0)
ol_weights = [0,.01,.02,.03,.04,.05,.06,.07,.08,.09,.1,.11,.12,.13,.14,.15]
for i in ol_weights:
    index_prices[str(i)] = index_prices['M1WD']+(index_prices['Moments']*i)
index_prices = index_prices.drop('Moments',axis=1)
returns_moments_only = dm.get_data_dict(index_prices)['Daily']

cvar_list = []
sharpe_list = []
trackerror_list = []
ir_list = []
corr_list = []
max_dd_list = []

for col in returns_moments_only:
    ret_vol = rs.get_ret_vol_ratio(returns_moments_only[col],'1D')
    cvar = rs.get_cvar(returns_moments_only[col], p = 0.05)
    excess_return = (returns_moments_only[col]- returns_moments_only['M1WD'])
    track_error = excess_return.std()
    if track_error == 0:
        information_ratio = 0
    else:     
        information_ratio = excess_return.mean()/ track_error
    correlation = returns_moments_only['M1WD'].corr(returns_moments_only[col])
    max_dd = rs.get_max_dd(index_prices[col])
    
    cvar_list.append(cvar)
    sharpe_list.append(ret_vol)
    trackerror_list.append(track_error)
    ir_list.append(information_ratio)
    corr_list.append(correlation)
    max_dd_list.append(max_dd)
    
df_metrics = pd.DataFrame()
df_metrics['Sharpe'] = sharpe_list
df_metrics['CVaR'] = cvar_list
df_metrics['Tracking Error'] = trackerror_list
df_metrics['IR'] = ir_list
df_metrics['Corr'] = corr_list
df_metrics['Max DD'] = max_dd_list 
df_metrics.set_index(returns_moments_only.columns,inplace=True)
df_metrics['Rank'] = df_metrics['Tracking Error'].rank()
df_metrics['Rank'] = df_metrics['Rank'] * 50



def percent_formatter(x, pos):
    return f'{x * 100:.2f}%'

fig, ax = plt.subplots(figsize=(20, 20))

plt.scatter(df_metrics['CVaR'], df_metrics['Sharpe'], s= df_metrics['Rank'], c = 'blue', marker='o', label='')
labels = ['','0%','1%','2%','3%','4%','5%','6%','7%','8%','9%','10%','11%','12%','13%','14%','15%']
# Add labels to each data point
for i, label in enumerate(labels):
    plt.annotate(label, (df_metrics['CVaR'][i], df_metrics['Sharpe'][i]), textcoords="offset points", xytext=(-5,20), ha='center', fontsize = 20)

ax.xaxis.set_major_formatter(FuncFormatter(percent_formatter))

# Customize the plot
plt.xticks(rotation=-45, fontsize = 14)
plt.yticks( fontsize = 14)
plt.xlabel('CVaR', fontsize = 20)
plt.ylabel('Sharpe', fontsize = 20)
plt.title('M1WD w Moments', fontsize = 20)
plt.show()




file_path = CWD +'\\RStrats\\moments_metrics.xlsx'
excel_writer = pd.ExcelWriter(file_path, engine='xlsxwriter')
# Export the DataFrame to an Excel file
df_metrics.to_excel(excel_writer,sheet_name = "Sheet1" ,index=True)  # Set index=False to exclude the DataFrame index in the Excel file
print(f"DataFrame exported to {file_path}")



################################################################################################################################
#Program w Moments
strat_returns = pd.read_excel(CWD+'\\RStrats\\' + 'JPMMomentsAnalysis.xlsx', sheet_name = 'Strat Returns', index_col=0)
moments_returns = pd.read_excel(CWD+'\\RStrats\\' + 'JPMMomentsAnalysis.xlsx', sheet_name = 'Moments Return', index_col=0)

strat_returns_w_moments = pd.merge(moments_returns,strat_returns, left_index=True, right_index=True, how="inner")

#rearrange columns
strat_returns_cols = list(strat_returns.columns)
col_list_moments  = strat_returns_cols+["Moments"]
strat_returns_w_moments = strat_returns_w_moments[col_list_moments]
#set notional weights
notional_weights_moments = [11, 1, 1, 1, 1, 1, .25, 1, 1, 0.4, 1, 0.5]
notional_weights =[11, 1, 1, 1, 1, 1, .25, 1, 1, 0.4, 1]

#get weights
weights_w_moments = get_df_weights(notional_weights_moments, col_list_moments)
#drop notional weight for moments
weights_no_moments = get_df_weights(notional_weights, strat_returns_cols)


weighted_data = strat_returns_w_moments.copy()
weighted_data['Weighted Strats w/ Moments'] = strat_returns_w_moments.multiply(weights_w_moments.iloc[1,:].tolist()).sum(axis = 1).to_frame()
weighted_data['Weighted Strats w/o Moments']  = strat_returns_w_moments[strat_returns_cols].multiply(weights_no_moments.iloc[1,:].tolist()).sum(axis = 1).to_frame()
weighted_strats = weighted_data[['M1WD', 'Weighted Strats w/ Moments', 'Weighted Strats w/o Moments']]


# for i, notional in enumerate(notional_weights):
#     if i == 0:
#         weights.append(1)
#     else:
#         weights.append(notional / sum(notional_weights[1:12]))

# for i in range(0,len(notional_weights)):
#     strat_returns[strat_returns.columns[i]] = strat_returns[strat_returns.columns[i]]*weights[i]

# for col in strat_returns.columns:
#     if col == 'M1WD':
#         strat_returns['Weighted_Strat_Returns'] = strat_returns['M1WD']*0
#     else:
#         strat_returns['Weighted_Strat_Returns'] += strat_returns[col]
#         strat_returns = strat_returns.drop(columns=[col])

strat_return_index_prices = dm.get_prices_df(weighted_strats)

ol_weights = [0,.05,.1,.15,.2,.25,.3,.35,.4,.45,.5]
overlay_w_moments = strat_return_index_prices['M1WD'].copy().to_frame()
overlay =  strat_return_index_prices['M1WD'].copy().to_frame()

for i in ol_weights:
    overlay_w_moments[str(i)] = strat_return_index_prices['M1WD']+(strat_return_index_prices['Weighted Strats w/ Moments']*i)
    
    overlay[str(i)] = strat_return_index_prices['M1WD']+(strat_return_index_prices['Weighted Strats w/o Moments']*i)
    
#dm.get_data_dict(strat_return_index_prices.reset_index(drop=True))['Daily']


#Program w/o Moments
# #strat_returns = pd.read_excel(CWD+'\\RStrats\\' + 'JPMMomentsAnalysis.xlsx', sheet_name = 'Strat Returns', index_col=0)
# notional_weights = [11, 1, 1.25, 1, 1, 1, .25, 1, 1, 0.4, 1]
# weights = []
# for i, notional in enumerate(notional_weights):
#     if i == 0:
#         weights.append(1)
#     else:
#         weights.append(notional / sum(notional_weights[1:11]))

# for i in range(0,len(notional_weights)):
#     strat_returns[strat_returns.columns[i]] = strat_returns[strat_returns.columns[i]]*weights[i]

# for col in strat_returns.columns:
#     if col == 'M1WD':
#         strat_returns['Weighted_Strat_Returns'] = strat_returns['M1WD']*0
#     else:
#         strat_returns['Weighted_Strat_Returns'] += strat_returns[col]
#         strat_returns = strat_returns.drop(columns=[col])

# strat_return_index_prices = dm.get_prices_df(strat_returns)

# ol_weights = [0,.05,.1,.15,.2,.25,.3,.35,.4,.45,.5]
# for i in ol_weights:
#     strat_return_index_prices[str(i)] = strat_return_index_prices['M1WD']+(strat_return_index_prices['Weighted_Strat_Returns']*i)
# strat_return_index_prices = strat_return_index_prices.drop('Weighted_Strat_Returns',axis=1)
# returns_program_wo_moments = dm.get_data_dict(strat_return_index_prices.reset_index(drop=True))['Daily']



def get_metrics(index_prices):
    df_returns = dm.format_data(index_prices,'1D')
    cvar_list = []
    sharpe_list = []
    trackerror_list = []
    ir_list = []
    corr_list = []
    max_dd_list = []

    for col in df_returns:
        ret_vol = rs.get_ret_vol_ratio(df_returns[col],'1D')
        cvar = rs.get_cvar(df_returns[col], p = 0.05)
        excess_return = (df_returns[col]- df_returns['M1WD'])
        track_error = excess_return.std()
        if track_error == 0:
            information_ratio = 0
        else:     
            information_ratio = excess_return.mean()/ track_error
        correlation = df_returns['M1WD'].corr(df_returns[col])
        max_dd = rs.get_max_dd(index_prices[col])
        
        cvar_list.append(cvar)
        sharpe_list.append(ret_vol)
        trackerror_list.append(track_error)
        ir_list.append(information_ratio)
        corr_list.append(correlation)
        max_dd_list.append(max_dd)
        
    df_metrics = pd.DataFrame()
    df_metrics['Sharpe'] = sharpe_list
    df_metrics['CVaR'] = cvar_list
    df_metrics['Tracking Error'] = trackerror_list
    df_metrics['IR'] = ir_list
    df_metrics['Corr'] = corr_list
    df_metrics['Max DD'] = max_dd_list 
    df_metrics.set_index(index_prices.columns,inplace=True)
    df_metrics['Rank'] = df_metrics['Tracking Error'].rank()
    df_metrics['Rank'] = df_metrics['Rank'] * 50

    return df_metrics

data_sets_dict={}
data_sets_dict['Program w Moments'] = get_metrics(overlay_w_moments)
data_sets_dict['Program wo Moments'] = get_metrics(overlay)

fig, ax = plt.subplots(figsize=(20, 20))

plt.scatter(data_sets_dict['Program w Moments']['CVaR'], data_sets_dict['Program w Moments']['Sharpe'], s= data_sets_dict['Program w Moments']['Rank'],
            c='blue', marker='o', label='With Moments')
plt.scatter(data_sets_dict['Program wo Moments']['CVaR'], data_sets_dict['Program wo Moments']['Sharpe'], s= data_sets_dict['Program wo Moments']['Rank'], 
            c='green', marker='o', label='Without Moments')


labels = ['','0%','5%','10%','15%','20%','25%','30%','35%','40%','45%','50%']
# Add labels to each data point
for i, label in enumerate(labels):
    plt.annotate(label, (data_sets_dict['Program w Moments']['CVaR'][i], data_sets_dict['Program w Moments']['Sharpe'][i]), 
                 textcoords="offset points", xytext=(-5,20), ha='center',fontsize = 20)


ax.xaxis.set_major_formatter(FuncFormatter(percent_formatter))

# Customize the plot
plt.xticks(rotation=-45, fontsize = 14)
plt.yticks( fontsize = 14)
plt.xlabel('CVaR', fontsize = 20)
plt.ylabel('Sharpe', fontsize = 20)
plt.title('Hedging Program', fontsize = 20)
plt.show()


# Specify the file path where you want to save the Excel file

# Export the DataFrame to an Excel file
data_sets_dict['Program w Moments'].to_excel(excel_writer, index=True,sheet_name ='Program w Moments')  # Set index=False to exclude the DataFrame index in the Excel file
data_sets_dict['Program wo Moments'].to_excel(excel_writer, index=True,sheet_name = 'Program wo Moments')  # Set index=False to exclude the DataFrame index in the Excel file
excel_writer.save()

print(f"DataFrame exported to {file_path}")




