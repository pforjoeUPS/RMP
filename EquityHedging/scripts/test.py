# -*- coding: utf-8 -*-
"""
Created on Wed Jul  7 13:49:08 2021

@author: SQY5SPK
"""
from EquityHedging.datamanager import data_manager as dm
from EquityHedging.analytics import  util
from EquityHedging.analytics.util import get_df_weights
from EquityHedging.analytics import summary
from EquityHedging.reporting.excel import reports as rp
from EquityHedging.reporting import formatter as fmt, plots
from EquityHedging.analytics import hedge_metrics as hm
import pandas as pd
    
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
df = hm.get_hedge_metrics_to_normalize(returns, equity_bmk, notional_weights)


df_normal = summary.get_normalized_data(df)

import plotly.graph_objects as go
met= list(df_normal.index)

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=met,
    y=df_normal['Def Var'],
    marker=dict(color="blue",size=12),
    mode="markers",
    name="Def var"
    ))
fig.show()



import plotly.graph_objects as go

schools = ["Brown", "NYU", "Notre Dame", "Cornell", "Tufts", "Yale",
           "Dartmouth", "Chicago", "Columbia", "Duke", "Georgetown",
           "Princeton", "U.Penn", "Stanford", "MIT", "Harvard"]

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=[72, 67, 73, 80, 76, 79, 84, 78, 86, 93, 94, 90, 92, 96, 94, 112],
    y=schools,
    marker=dict(color="crimson", size=12),
    mode="markers",
    name="Women",
))

fig.add_trace(go.Scatter(
    x=[92, 94, 100, 107, 112, 114, 114, 118, 119, 124, 131, 137, 141, 151, 152, 165],
    y=schools,
    marker=dict(color="gold", size=12),
    mode="markers",
    name="Men",
))

fig.update_layout(title="Gender Earnings Disparity",
                  xaxis_title="Annual Salary (in thousands)",
                  yaxis_title="School")

fig.show()