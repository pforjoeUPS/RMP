# -*- coding: utf-8 -*-
"""
Created on Wed Jun  7 15:49:38 2023

@author: rrq1fyq
"""


#import libraries
from EquityHedging.datamanager import data_manager as dm
from EquityHedging.analytics.util import get_df_weights
from EquityHedging.analytics import summary
from EquityHedging.reporting.excel import reports as rp
from EquityHedging.reporting import formatter as plots
import matplotlib.pyplot as plt

#import returns data
equity_bmk = 'SPTR'
include_fi = False
weighted = [True, False]
strat_drop_list = ['99%/90% Put Spread', 'Vortex']
new_strat = False
returns= dm.get_equity_hedge_returns(equity_bmk, include_fi, strat_drop_list)


#get notional weights

notional_weights = dm.get_notional_weights(returns['Monthly'])
returns = dm.create_vrr_portfolio(returns,notional_weights)
notional_weights[4:6] = [notional_weights[4] + notional_weights[5]]

df_weights = get_df_weights(notional_weights, list(returns['Monthly'].columns), include_fi)

plt.scatter(returns['Daily']['SPTR'], returns['Daily']['Down Var'])


# Generate data
x = returns['Daily']['SPTR']
y = returns['Daily']['Down Var']

import matplotlib.pyplot as plt

x1 = list(x.index[x<0])
x2 = 
#create basic scatterplot
plt.plot(x, y, 'o')

#obtain m (slope) and b(intercept) of linear regression line
m, b = np.polyfit(x, y, 1)

#add linear regression line to scatterplot 
plt.plot(x, m*x+b)