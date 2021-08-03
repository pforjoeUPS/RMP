# -*- coding: utf-8 -*-
"""
Created on Fri Jul 23 13:32:53 2021

@author: SQY5SPK
"""

from EquityHedging.datamanager import data_manager as dm
from EquityHedging.analytics import  util
from EquityHedging.analytics import summary 
from EquityHedging.reporting.excel import reports as rp
from EquityHedging.reporting import formatter as fmt, plots
from EquityHedging.analytics import hedge_metrics as hm
import pandas as pd
from sklearn.preprocessing import MinMaxScaler

equity_bmk = 'SPTR'
weighted = [True, False]
strat_drop_list = ['99%/90% Put Spread', 'Vortex']
returns = dm.get_equity_hedge_returns(equity_bmk, strat_drop_list = strat_drop_list)
weekly_ret=returns['Weekly'].copy()

#notional_weights = dm.get_notional_weights(returns['Monthly'])
notional_weights = [19.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.25, 1.0]
df_weights = util.get_df_weights(notional_weights, list(returns['Weekly'].columns))
fmt.get_notional_styler(df_weights)

data = summary.get_normalized_hedge_metrics(weekly_ret, equity_bmk=True, notional_weights = notional_weights, weighted = True)
df_norm = data['Normalized Data']
df_normal = df_norm.transpose()

symbols = plots.get_symbols(df_normal, unique=True)
color = plots.get_colors(df_normal, grey=True)


