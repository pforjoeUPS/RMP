# -*- coding: utf-8 -*-
"""
Created on Wed Jul  7 13:49:08 2021

@author: Maddie Choi
"""
from EquityHedging.datamanager import data_manager as dm
from EquityHedging.analytics import  util
from EquityHedging.analytics.util import get_df_weights
from EquityHedging.analytics import summary
from EquityHedging.reporting.excel import reports as rp
from EquityHedging.reporting import formatter as fmt, plots
from EquityHedging.analytics import hedge_metrics as hm
import pandas as pd
from EquityHedging.reporting import formatter as fmt

equity_bmk = 'M1WD'
include_fi = False
weighted = [True, False]
strat_drop_list = ['99%/90% Put Spread', 'Vortex']
new_strat = True
returns = dm.get_equity_hedge_returns(equity_bmk, include_fi, strat_drop_list)

notional_weights = dm.get_notional_weights(returns['Monthly'])
df_weights = get_df_weights(notional_weights, list(returns['Monthly'].columns), include_fi)
fmt.get_notional_styler(df_weights)

#get hedge metrics data frame
import time

start = time.time()
df = hm.get_hedge_metrics_to_normalize(returns, equity_bmk, notional_weights,True)
end = time.time()
print(end - start)

start = time.time()
df_returns = returns['Weekly'].copy()
df_weighted_ret = util.get_weighted_hedges(df_returns, notional_weights)
df_1 = hm.get_hedge_metrics(df_weighted_ret,'1W', False)
end = time.time()
print(end - start)

# df


df_normal = util.get_normalized_data(df)

df_normal= summary.get_normalized_hedge_metrics(returns, equity_bmk, notional_weights, weighted_hedge=True)
df_normal = df_normal['Normalized Data']

fmt.format_normalized_data(df_normal)

symbols = util.get_symbols(df_normal, weighted_hedge = True)
symbols['Down Var']
