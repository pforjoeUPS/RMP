# -*- coding: utf-8 -*-
"""
Created on Thu Jun 30 09:34:35 2022

@author: GMS0VSB
"""
import os

os.chdir('..\..')
#import libraries
from EquityHedging.datamanager import data_manager as dm
from EquityHedging.analytics.util import get_df_weights
from EquityHedging.analytics import summary
from EquityHedging.reporting.excel import reports as rp
from EquityHedging.reporting import formatter as plots

#1

#import returns data
equity_bmk = 'SPTR'
include_fi = False
weighted = [True, False]
strat_drop_list = ['99%/90% Put Spread', 'Vortex']
new_strat = False
returns= dm.get_equity_hedge_returns(equity_bmk, include_fi, strat_drop_list)

new_strat = True
if new_strat:
    strategy_list = ['Defensive Skew']
    filename = 'Defensive_Skew_New.xlsx'
    sheet_name = 'Sheet1'
    new_strategy = dm.get_new_strategy_returns_data(filename, sheet_name, strategy_list)
    new_strategy_dict = dm.get_data_dict(new_strategy, data_type='index')
    returns = dm.merge_dicts(returns, new_strategy_dict)

#notional_weights = dm.get_notional_weights(returns['Monthly'])
notional_weights = [13,1,1,1,1,1,.25,.25,1]
df_weights = get_df_weights(notional_weights, list(returns['Monthly'].columns), include_fi)

check_corr = False
if check_corr:
    corr_freq_list = ['Daily', 'Weekly', 'Monthly']
    corr_dict = summary.get_corr_data(returns, corr_freq_list, weighted, notional_weights, include_fi)
    data = corr_dict['Monthly']
    corr_df = data[0]['full'][0]
    plots.draw_corrplot(corr_df)
    plots.draw_heatmap(corr_df, False)

#get quintile dataframe
check_quint = False
if check_quint:
    quintile_df = summary.get_grouped_data(returns, notional_weights, True, group='Quintile')

#get annual dollar returns dataframe
check_ann = False
if check_ann:
    annual_dollar_returns = summary.get_annual_dollar_returns(returns, notional_weights)

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


equity_hedge_report = 'equity_hedge_analysis_cs_def_skew'
selloffs = True

rp.get_equity_hedge_report(equity_hedge_report, returns,notional_weights, include_fi, new_strat, weighted[0], selloffs)



#2 

#import returns data
equity_bmk = 'M1WD'
include_fi = False
weighted = [True, False]
strat_drop_list = ['99%/90% Put Spread', 'Vortex']
new_strat = False
returns= dm.get_equity_hedge_returns(equity_bmk, include_fi, strat_drop_list)

new_strat = True
if new_strat:
    strategy_list = ['SMI Dispersion']
    filename = 'Defensive_Skew_New.xlsx'
    sheet_name = 'Sheet3'
    new_strategy = dm.get_new_strategy_returns_data(filename, sheet_name, strategy_list)
    new_strategy_dict = dm.get_data_dict(new_strategy, data_type='index')
    returns = dm.merge_dicts(returns, new_strategy_dict)

#notional_weights = dm.get_notional_weights(returns['Monthly'])
notional_weights = [13,1,1,1,1,1,.25,.25,.5]
df_weights = get_df_weights(notional_weights, list(returns['Monthly'].columns), include_fi)


equity_hedge_report = 'equity_hedge_analysis_cs_dispersion'
selloffs = True

rp.get_equity_hedge_report(equity_hedge_report, returns,notional_weights, include_fi, new_strat, weighted[0], selloffs)

#3a

#import returns data
equity_bmk = 'M1WD'
include_fi = False
weighted = [True, False]
strat_drop_list = ['99%/90% Put Spread', 'Vortex']
new_strat = False
returns= dm.get_equity_hedge_returns(equity_bmk, include_fi, strat_drop_list)

#SMI Dispersion

new_strat = True
if new_strat:
    strategy_list = ['SMI Dispersion']
    filename = 'Defensive_Skew_New.xlsx'
    sheet_name = 'Sheet3'
    new_strategy = dm.get_new_strategy_returns_data(filename, sheet_name, strategy_list)
    new_strategy_dict = dm.get_data_dict(new_strategy, data_type='index')
    returns = dm.merge_dicts(returns, new_strategy_dict)

#notional_weights = dm.get_notional_weights(returns['Monthly'])
notional_weights = [13,1,1,1,1,1,.25,.25,.5]
df_weights = get_df_weights(notional_weights, list(returns['Monthly'].columns), include_fi)

equity_hedge_report = 'equity_hedge_analysis_cs_dispersion'
selloffs = True

rp.get_equity_hedge_report(equity_hedge_report, returns,notional_weights, include_fi, new_strat, weighted[0], selloffs)

#3b

equity_bmk = 'M1WD'
include_fi = False
weighted = [True, False]
strat_drop_list = ['99%/90% Put Spread', 'Vortex']
new_strat = False
returns= dm.get_equity_hedge_returns(equity_bmk, include_fi, strat_drop_list)

new_strat = True
if new_strat:
    strategy_list = ['FVA']
    filename = 'FVA_Strategy_New.xlsx'
    sheet_name = 'Sheet1'
    new_strategy = dm.get_new_strategy_returns_data(filename, sheet_name, strategy_list)
    new_strategy_dict = dm.get_data_dict(new_strategy, data_type='index')
    returns = dm.merge_dicts(returns, new_strategy_dict)

#notional_weights = dm.get_notional_weights(returns['Monthly'])
notional_weights = [13,1,1,1,1,1,.25,.25,.5]
df_weights = get_df_weights(notional_weights, list(returns['Monthly'].columns), include_fi)

equity_hedge_report = 'equity_hedge_analysis_FVA'
selloffs = True

rp.get_equity_hedge_report(equity_hedge_report, returns,notional_weights, include_fi, new_strat, weighted[0], selloffs)

#3c

equity_bmk = 'M1WD'
include_fi = False
weighted = [True, False]
strat_drop_list = ['99%/90% Put Spread', 'Vortex']
new_strat = False
returns= dm.get_equity_hedge_returns(equity_bmk, include_fi, strat_drop_list)

new_strat = True
if new_strat:
    strategy_list = ['Def Term Premia']
    filename = 'FVA_Strategy_New.xlsx'
    sheet_name = 'Sheet2'
    new_strategy = dm.get_new_strategy_returns_data(filename, sheet_name, strategy_list)
    new_strategy_dict = dm.get_data_dict(new_strategy, data_type='index')
    returns = dm.merge_dicts(returns, new_strategy_dict)

#notional_weights = dm.get_notional_weights(returns['Monthly'])
notional_weights = [13,1,1,1,1,1,.25,.25,.5]
df_weights = get_df_weights(notional_weights, list(returns['Monthly'].columns), include_fi)

equity_hedge_report = 'equity_hedge_analysis_Def_Term_Premia_Davis'
selloffs = True

rp.get_equity_hedge_report(equity_hedge_report, returns,notional_weights, include_fi, new_strat, weighted[0], selloffs)

#3d

equity_bmk = 'M1WD'
include_fi = False
weighted = [True, False]
strat_drop_list = ['99%/90% Put Spread', 'Vortex']
new_strat = False
returns= dm.get_equity_hedge_returns(equity_bmk, include_fi, strat_drop_list)

new_strat = True
if new_strat:
    strategy_list = ['FVA + Def Term Premia']
    filename = 'FVA_Strategy_New.xlsx'
    sheet_name = 'Sheet3'
    new_strategy = dm.get_new_strategy_returns_data(filename, sheet_name, strategy_list)
    new_strategy_dict = dm.get_data_dict(new_strategy, data_type='index')
    returns = dm.merge_dicts(returns, new_strategy_dict)

#notional_weights = dm.get_notional_weights(returns['Monthly'])
notional_weights = [13,1,1,1,1,1,.25,.25,.5]
df_weights = get_df_weights(notional_weights, list(returns['Monthly'].columns), include_fi)

equity_hedge_report = 'equity_hedge_analysis_FVA_and_Def_Term_Premia_Davis'
selloffs = True

rp.get_equity_hedge_report(equity_hedge_report, returns,notional_weights, include_fi, new_strat, weighted[0], selloffs)