# -*- coding: utf-8 -*-
"""
Created on Sat Apr 24 00:21:46 2021

@author: Powis Forjoe, Zach Wells and Maddie Choi
"""
import os

os.chdir('..\..')

#import libraries
from EquityHedging.datamanager import data_manager as dm
from EquityHedging.datamanager import data_handler as dh
from EquityHedging.analytics.util import get_df_weights
from EquityHedging.analytics import summary
#from EquityHedging.reporting.excel import reports as rp
from EquityHedging.reporting.excel import new_reports as rp
from EquityHedging.reporting import formatter as plots

#import returns data
equity_bmk = 'SPTR'
include_fi = False
weighted = [True, False]
strat_drop_list = ['99%/90% Put Spread', 'Vortex']
new_strat = False
returns= dm.get_equity_hedge_returns(equity_bmk, include_fi, strat_drop_list)

# eq_hedge_dh = dh.eqHedgeHandler(equity_bmk='SPTR', include_fi=True, strat_drop_list=['99%/90% Put Spread', 'Vortex'])

#Add new strat
new_strat = False
if new_strat:
    strategy_list = ['JPM Skew','CITI Put Ratio']
    filename = 'JPM_Skew_and_CITI_Put.xlsx'
    sheet_name = 'Sheet1'
    new_strategy = dm.get_new_strategy_returns_data(filename, sheet_name, strategy_list)
    new_strategy_dict = dm.get_data_dict(new_strategy, data_type='index')
    returns = dm.merge_dicts(returns, new_strategy_dict)

# eq_hedge_dh.add_new_strat()




#get notional weights
notional_weights = dm.get_notional_weights(returns['Monthly'])
returns_vrr = dm.create_vrr_portfolio(returns,notional_weights)
notional_weights[4:6] = [notional_weights[4] + notional_weights[5]]


df_weights = get_df_weights(notional_weights, list(returns['Monthly'].columns), include_fi)


#returns = eq_hedge_dh.returns

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
equity_hedge_report = 'equity_hedge_analysis_testNew'
selloffs = True
# start = time.time()
rp.generateEquityHedgeReport(equity_hedge_report, returns, notional_weights, include_fi, new_strat, weighted[0], selloffs)
#rp.get_equity_hedge_report(equity_hedge_report, returns,notional_weights, include_fi, new_strat, weighted[0], selloffs)
# end = time.time()
# print(end - start)

hs_report = 'historical_selloff_test_new'
rp.generateHSReport(hs_report, returns)
