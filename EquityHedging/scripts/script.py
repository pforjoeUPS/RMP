# -*- coding: utf-8 -*-
"""
Created on Sat Apr 24 00:21:46 2021

@author: Powis Forjoe
"""


from EquityHedging.datamanager import data_manager as dm
from EquityHedging.analytics.util import get_df_weights
from EquityHedging.analytics import summary
from EquityHedging.reporting.excel import reports as rp
from EquityHedging.reporting import formatter as fmt, plots

equity_bmk = 'SPTR'
include_fi = False
weighted = [True, False]
strat_drop_list = ['99%/90% Put Spread', 'Vortex']
new_strat = False
returns = dm.get_equity_hedge_returns(equity_bmk, include_fi, strat_drop_list)

notional_weights = dm.get_notional_weights(returns['Monthly'])
df_weights = get_df_weights(notional_weights, list(returns['Monthly'].columns), include_fi)
fmt.get_notional_styler(df_weights)

corr_freq_list = ['Daily', 'Weekly', 'Monthly']
corr_dict = summary.get_corr_data(returns, corr_freq_list, weighted, notional_weights, include_fi)
data = corr_dict['Monthly']
corr_df = data[0]['corr'][0]
plots.draw_corrplot(corr_df)
plots.draw_heatmap(corr_df, False)

analytics_freq_list = ['Weekly', 'Monthly']
analytics_dict = summary.get_analytics_data(returns,analytics_freq_list,weighted,notional_weights,include_fi,new_strat)

hist_dict = summary.get_hist_data(returns,notional_weights=notional_weights, weighted=weighted)

quintile_df = summary.get_quintile_data(returns, notional_weights,weighted=True)

annual_dollar_returns = summary.get_annual_dollar_returns(returns, notional_weights)

equity_hedge_report = 'equity_hedge_analysis_052021'
selloffs = False
rp.get_equity_hedge_report(equity_hedge_report, returns, notional_weights, include_fi, new_strat, weighted[0], selloffs)
