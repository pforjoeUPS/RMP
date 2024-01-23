# -*- coding: utf-8 -*-
"""
Created on Sat Jan 24 2023

@author: Powis Forjoe, Zach Wells and Maddie Choi
"""
# import os
#
# os.chdir('..\..')

# import libraries
from EquityHedging.datamanager import data_manager_new as dm
from EquityHedging.datamanager import data_handler as dh
from EquityHedging.datamanager import data_xformer_new as dxf
from EquityHedging.analytics import returns_analytics as ra
from EquityHedging.reporting.excel import new_reports as rp

# import returns data
eq_bmk = 'S&P 500'
include_fi = False
weighted = True
strat_drop_list = []
new_strat = False

eq_hedge_dh = dh.eqHedgeHandler(eq_bmk=eq_bmk, eq_mv=11.0,
                                include_fi=include_fi, fi_mv=20.0,
                                strat_drop_list=[])

# Add new strat
new_strat = True
if new_strat:
    strategy_list = ['esprso']
    filename = 'esprso.xlsx'
    sheet_name = 'Sheet1'
    notional_list = [1]
    new_strategy = dm.get_new_strategy_returns_data(filename, sheet_name, strategy_list)
    new_strategy_dict = dxf.get_data_dict(new_strategy, index_data=True)

eq_hedge_dh.add_strategy(new_strategy_dict, notional_list)

eq_hedge_dh.get_weighted_returns(new_strat=new_strat)

returns_dict = eq_hedge_dh.weighted_returns if weighted else eq_hedge_dh.returns
eq_hedge_analytics = ra.eqHedgeReturnsDictAnalytic(returns_dict, include_fi=include_fi,
                                                   mkt_data=eq_hedge_dh.mkt_returns, mkt_key=eq_hedge_dh.mkt_key)

# compute correlations
check_corr = True
if check_corr:
    corr_freq_list = ['Daily', 'Weekly', 'Monthly']
    eq_hedge_analytics.get_corr_stats_dict(corr_freq_list)
    corr_dict = dxf.copy_data(eq_hedge_analytics.corr_stats_dict)

# compute analytics
# import time
# start = time.time()
check_analysis = True
if check_analysis:
    analytics_freq_list = ['Weekly', 'Monthly']
    eq_hedge_analytics.get_returns_stats_dict(analytics_freq_list)
    eq_hedge_analytics.get_hedge_metrics_dict(analytics_freq_list)
    analytics_dict = {'return_stats': dxf.copy_data(eq_hedge_analytics.returns_stats_dict),
                      'hedge_metrics': dxf.copy_data(eq_hedge_analytics.hedge_metrics_dict)
                      }
# end = time.time()
# print(end - start)

# compute historical selloffs
check_hs = True
if check_hs:
    eq_hedge_analytics.get_hist_selloff()
    hist_selloff_df = dxf.copy_data(eq_hedge_analytics.historical_selloff_data)

# get quantile dataframe
check_quantile = True
if check_quantile:
    eq_hedge_analytics.get_quantile_stats()
    quantile_dict = dxf.copy_data(eq_hedge_analytics.quantile_stats_data)

# # get annual dollar returns dataframe
# check_ann = False
# if check_ann:
#     annual_dollar_returns = summary.get_annual_dollar_returns(returns, notional_weights)

# run report
report_name = 'equity_hedge_analysis_testNew'
selloffs = True
eq_hedge_rp = rp.equityHedgeReport(report_name=report_name, data_handler=eq_hedge_dh, weighted=weighted,
                                   new_strat=new_strat, selloffs=selloffs)
eq_hedge_rp.run_report(report_name=report_name)
# start = time.time()
# end = time.time()
# print(end - start)

hs_report = 'historical_selloff_test_new'
hs_rp = rp.histSelloffReport(report_name=hs_report, data_handler=eq_hedge_dh, weighted=weighted, new_strat=new_strat)
