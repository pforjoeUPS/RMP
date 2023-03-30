# -*- coding: utf-8 -*-
"""
Created on Thu Mar 30 15:39:05 2023

@author: PCR7FJW
"""

#import libraries
from EquityHedging.datamanager import data_manager as dm
from EquityHedging.analytics.util import get_df_weights
from EquityHedging.analytics import summary
from EquityHedging.reporting.excel import reports as rp
from EquityHedging.reporting import formatter as plots
from EquityHedging.analytics import returns_stats as rs

import pandas as pd

equity_bmk = 'SPTR'
include_fi = False
weighted = [True, False]
strat_drop_list = ['99%/90% Put Spread', 'Vortex']
new_strat = True
returns= dm.get_equity_hedge_returns(equity_bmk, include_fi, strat_drop_list)

new_strategy = returns['Weekly']

price_series = new_strategy.copy()
return_series = price_series.copy()

#finds drawdown series
def get_drawdown_series(price_series):
    window = len(price_series)
    roll_max = price_series.rolling(window, min_periods=1).max()
    drawdown = price_series/roll_max - 1.0
    return drawdown


def find_dd_dates(price_series):
    max_dd = pd.DataFrame(rs.get_max_dd(price_series)).transpose()
    drawdown = get_drawdown_series(price_series)
    strats = list(drawdown.columns)
    dd_dates = pd.DataFrame()
    
    for i in strats:
        dd_dates[i] = drawdown.index[drawdown[i] == float(max_dd[i])]
    return dd_dates
    

def find_zero_dd_dates(price_series):
    drawdown = get_drawdown_series(price_series)
    strats = list(drawdown.columns)
    zero_dd_dates = pd.DataFrame()
    
    for i in strats:
        drawdown_reverse = drawdown.loc[::-1]
        x = find_dd_dates(price_series)[i][0]
        strat_drawdown = drawdown_reverse[i].loc[x:]
        
        for dd_index, dd_value in enumerate(strat_drawdown):
            if dd_value == 0:
                zero_dd_dates[i] = [strat_drawdown.index[dd_index]]
                break
    return zero_dd_dates


def get_recovery(price_series):
    drawdown = get_drawdown_series(price_series)
    strats = list(drawdown.columns)

    recovery = pd.DataFrame(columns = strats)    
    for i in strats:
        zero_dd_dates = find_zero_dd_dates(price_series)[i][0]
        #find where max dd zero
        count_price_series = price_series[i].loc[zero_dd_dates:]
        recovery_days = 0
        for price in count_price_series[1:]:
            if price < count_price_series[0]:
                recovery_days += 1
            else:
                break
        recovery[i] = [recovery_days]
    return recovery

x = get_recovery(price_series)
