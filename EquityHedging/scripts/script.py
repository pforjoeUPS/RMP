# -*- coding: utf-8 -*-
"""
Created on Sat Apr 24 00:21:46 2021

@author: Powis Forjoe, Zach Wells and Maddie Choi
"""
import os

#os.chdir('..\..')

#import libraries
from EquityHedging.datamanager import data_manager as dm
from EquityHedging.analytics.util import get_df_weights
from EquityHedging.analytics import summary
from EquityHedging.reporting.excel import reports as rp
from EquityHedging.reporting import formatter as plots

#import returns data
equity_bmk = 'SPTR'
include_fi = False
weighted = [True, False]
strat_drop_list = ['99%/90% Put Spread', 'Vortex']
new_strat = True
returns= dm.get_equity_hedge_returns(equity_bmk, include_fi, strat_drop_list)

#Add new strat
new_strat = False
if new_strat:
    strategy_list = ['Vortex_Gamma']
    filename = 'Barclays_Vortex_Gamma.xlsx'
    sheet_name = 'Sheet2'
    new_strategy = dm.get_new_strategy_returns_data(filename, sheet_name, strategy_list)
    new_strategy_dict = dm.get_data_dict(new_strategy, data_type='index')
    returns = dm.merge_dicts(returns, new_strategy_dict)




#get notional weights
#notional_weights = dm.get_notional_weights(returns['Monthly'])
notional_weights = [13.5, 0.86, 1.12, 1.01, 0.77, 0.28, 1, .23, 0.98]
returns = dm.get_returns_VRR_Portfolio(returns, notional_weights)

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

#run report
equity_hedge_report = 'equity_hedge_analysis_test'
selloffs = True
# start = time.time()
rp.get_equity_hedge_report(equity_hedge_report, returns,notional_weights, include_fi, new_strat, weighted[0], selloffs)
# end = time.time()
# print(end - start)

