# -*- coding: utf-8 -*-
"""
Created on Sat Apr 24 00:21:46 2021

@author: Powis Forjoe, Zach Wells and Maddie Choi
"""

#import libraries
from EquityHedging.datamanager import data_manager as dm
from EquityHedging.analytics.util import get_df_weights
from EquityHedging.analytics import summary
from EquityHedging.reporting.excel import reports as rp
from EquityHedging.reporting import formatter as fmt, plots

#import returns data
equity_bmk = 'SPTR'
include_fi = False
weighted = [True, False]
strat_drop_list = ['99%/90% Put Spread', 'Vortex']
new_strat = False
returns_ups = dm.get_equity_hedge_returns(equity_bmk, include_fi, strat_drop_list)

#Add new strat
strategy_list = ['Dynamic VOLA', 'Original VOLA']
filename = 'vola.xlsx'
sheet_name = 'Sheet1'
new_strategy = dm.get_new_strategy_returns_data(filename, sheet_name, strategy_list)
new_strategy=new_strategy[['Dynamic VOLA']]
new_strategy_dict = dm.get_data_dict(new_strategy, data_type='index')
returns = dm.merge_dicts(returns_ups, new_strategy_dict)
new_strat=True
#returns['Weekly'] = returns['Weekly'][:-1]

#get notional weights
notional_weights = dm.get_notional_weights(returns['Monthly'])
df_weights = get_df_weights(notional_weights, list(returns['Monthly'].columns), include_fi)
fmt.get_notional_styler(df_weights)

#compute correlations
corr_freq_list = ['Daily', 'Weekly', 'Monthly']
corr_dict = summary.get_corr_data(returns, corr_freq_list, weighted, notional_weights, include_fi)
data = corr_dict['Monthly']
corr_df = data[0]['corr'][0]
plots.draw_corrplot(corr_df)
plots.draw_heatmap(corr_df, False)

#compute analytics
analytics_freq_list = ['Weekly', 'Monthly']
analytics_dict = summary.get_analytics_data(returns,analytics_freq_list,weighted,notional_weights,include_fi,new_strat)

#compute historical selloffs
hist_dict = summary.get_hist_data(returns,notional_weights, weighted)

#get quintile dataframe
quintile_df = summary.get_quintile_data(returns, notional_weights,weighted=True)

#get annual dollar returns dataframe
annual_dollar_returns = summary.get_annual_dollar_returns(returns, notional_weights)

#run report
equity_hedge_report = 'equity_hedge_analysis_test'
selloffs = True
rp.get_equity_hedge_report(equity_hedge_report, returns, notional_weights, include_fi, new_strat, weighted[0], selloffs)
