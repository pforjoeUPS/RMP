# -*- coding: utf-8 -*-
"""
Created on Sat Apr 24 00:21:46 2021

@author: Powis Forjoe, Zach Wells and Maddie Choi
"""
import os

os.chdir('..\..')

#import libraries
from EquityHedging.datamanager import data_manager as dm
from EquityHedging.analytics.util import get_df_weights
from EquityHedging.analytics import summary
from EquityHedging.reporting.excel import reports as rp
from EquityHedging.reporting import formatter as plots
from EquityHedging.reporting import plots as plt2

#import returns data
equity_bmk = 'SPTR'
include_fi = False
weighted = [True, False]
strat_drop_list = ['99%/90% Put Spread', 'Vortex']
new_strat = True
returns= dm.get_equity_hedge_returns(equity_bmk, include_fi, strat_drop_list)

#Add new strat
new_strat = True
if new_strat:
    strategy_list1 = ['JPM Moments']
    strategy_list2 = ['CS Def Skew']
    filename1 = 'JPM Moments.xlsx'
    filename2 = 'CS Def Skew.xlsx'
    sheet_name1 = 'Sheet2'
    sheet_name2 = 'data'
    new_strategy1 = dm.get_new_strategy_returns_data(filename1, sheet_name1, strategy_list1)
    new_strategy2 = dm.get_new_strategy_returns_data(filename2, sheet_name2, strategy_list2)
    new_strategy_dict1 = dm.get_data_dict(new_strategy1, data_type='index')
    new_strategy_dict2 = dm.get_data_dict(new_strategy2, data_type='index')
    returns = dm.merge_dicts(returns, new_strategy_dict1)
    returns = dm.merge_dicts(returns, new_strategy_dict2)

#get notional weights

notional_weights = dm.get_notional_weights(returns['Monthly'])
returns = dm.create_vrr_portfolio(returns,notional_weights)
notional_weights[4:6] = [notional_weights[4] + notional_weights[5]]

df_weights = get_df_weights(notional_weights, list(returns['Monthly'].columns), include_fi)


#compute correlations
check_corr = False
if check_corr:
    corr_freq_list = ['Daily', 'Weekly', 'Monthly']
    corr_dict = summary.get_corr_data(returns, corr_freq_list, weighted, notional_weights, include_fi)
    data = corr_dict['Monthly']
    corr_df = data[0]['full'][0]
    plots.draw_corrplot(corr_df)
    plots.draw_heatmap(corr_df, False)

#compute analytics
# import time
# start = time.time()
check_analysis = False
if check_analysis:
    analytics_freq_list = ['Weekly', 'Monthly']
    analytics_dict = summary.get_analytics_data(returns,analytics_freq_list,weighted,notional_weights,include_fi,new_strat)

# end = time.time()
# print(end - start)

#compute historical selloffs
check_hs = False
if check_hs:
    hist_dict = summary.get_hist_data(returns,notional_weights, weighted)

#get quintile dataframe
check_quint = False
if check_quint:
    quintile_df = summary.get_grouped_data(returns, notional_weights, True, group='Quintile')

#get annual dollar returns dataframe
check_ann = False
if check_ann:
    annual_dollar_returns = summary.get_annual_dollar_returns(returns, notional_weights)
    
strategy = "VOLA 3"
monthly_ret_table = True
if monthly_ret_table:
    month_returns_table = dm.month_ret_table(returns['Monthly'], strategy = strategy)
    full_month_returns_table = dm.all_strat_month_ret_table(returns['Monthly'])

#runs linear regression
plt2.get_regression_plot(returns, notional_weights, 'Daily', 'Down Var') 

#run report
equity_hedge_report = 'JPM Moments & CS Def Skew'
selloffs = True
grouped = True
# start = time.time()
rp.get_equity_hedge_report(equity_hedge_report, returns,notional_weights, include_fi, new_strat, weighted[0], selloffs, grouped, monthly_ret_table)
# end = time.time()
# print(end - start)

