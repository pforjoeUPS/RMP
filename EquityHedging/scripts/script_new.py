# -*- coding: utf-8 -*-
"""
Created on Sat Apr 24 00:21:46 2021

@author: Powis Forjoe, Zach Wells and Maddie Choi
"""
import os

os.chdir('..\..')

# import libraries
from EquityHedging.datamanager import data_manager_new as dm
from EquityHedging.datamanager import data_handler as dh
from EquityHedging.datamanager.data_xformer_new import copy_data, get_data_dict
from EquityHedging.analytics import returns_analytics as ra
from EquityHedging.reporting.excel import new_reports as rp

# import returns data
eq_bmk = 'S&P 500'
include_fi = False
weighted = True
strat_drop_list = []
new_strat = False

eq_hedge_dh = dh.EQHedgeDataHandler1(eq_bmk=eq_bmk, eq_mv=11.0,
                                     include_fi=include_fi, fi_mv=20.0,
                                     strat_drop_list=[])

# Add new strat
new_strat = True
if new_strat:
    strategy_list = ['esprso']
    filename = 'esprso.xlsx'
    sheet_name = 'Sheet1'
    notional_list = [1]
    new_strategy = dm.get_new_strategy_returns_data(filename=filename, sheet_name=sheet_name, return_data=False,
                                                    strategy_list=strategy_list)
    new_strategy_dict = get_data_dict(new_strategy, index_data=False)

eq_hedge_dh.add_strategy(new_strategy_dict, notional_list)

eq_hedge_dh.get_weighted_returns(new_strat=new_strat)

returns_dict = eq_hedge_dh.weighted_returns if weighted else eq_hedge_dh.returns
mkt_data = eq_hedge_dh.mkt_returns
mkt_key = eq_hedge_dh.mkt_key
include_fi = eq_hedge_dh.include_fi

eq_hedge_analytics = ra.EqHedgeReturnsDictAnalytic(returns_dict, include_fi=include_fi,
                                                   mkt_data=mkt_data, mkt_key=mkt_key)

# compute correlations
check_corr = False
if check_corr:
    corr_freq_list = ['Daily', 'Weekly', 'Monthly']
    eq_hedge_analytics.get_corr_stats_dict(corr_freq_list)
    corr_dict = copy_data(eq_hedge_analytics.corr_stats_dict)

# compute analytics
# import time
# start = time.time()
check_analysis = False
if check_analysis:
    analytics_freq_list = ['Weekly', 'Monthly']
    eq_hedge_analytics.get_returns_stats_dict(analytics_freq_list)
    eq_hedge_analytics.get_hedge_metrics_dict(analytics_freq_list)
    analytics_dict = {'return_stats': copy_data(eq_hedge_analytics.returns_stats_dict),
                      'hedge_metrics': copy_data(eq_hedge_analytics.hedge_metrics_dict)
                      }

# end = time.time()
# print(end - start)

# compute historical selloffs
check_hs = False
if check_hs:
    eq_hedge_analytics.get_hist_selloff()
    hist_df = copy_data(eq_hedge_analytics.historical_selloff_data)

# get quantile dataframe
check_quantile = False
if check_quantile:
    eq_hedge_analytics.get_quantile_stats()
    quantile_dict = copy_data(eq_hedge_analytics.quantile_stats_data)

# #get annual dollar returns dataframe
# check_ann = False
# if check_ann:
#     annual_dollar_returns = summary.get_annual_dollar_returns(returns, notional_weights)

# run report
report_name = 'equity_hedge_analysis_testNew'
selloffs = True
# start = time.time()
rp.EquityHedgeReport(report_name=report_name, data_handler=eq_hedge_dh, weighted=weighted,
                     new_strat=new_strat, selloffs=selloffs).run_report()

# end = time.time()
# print(end - start)

hs_report = 'historical_selloff_test'
rp.HistSelloffReport(report_name=hs_report, data_handler=eq_hedge_dh, weighted=weighted,
                     new_strat=new_strat).run_report()
