# -*- coding: utf-8 -*-
"""
Created on Tue Feb 28 10:01:32 2023

@author: PCR7FJW
"""
import pandas as pd
from EquityHedging.analytics import returns_stats as rs
from EquityHedging.datamanager import data_manager as dm

price_series = dm.get_prices_df(returns["Monthly"])
return_series = price_series.copy()

#finds drawdown series
window = len(price_series)
roll_max = price_series.rolling(window, min_periods=1).max()
drawdown = price_series/roll_max - 1.0

max_dd = rs.get_max_dd(return_series)
max_dd1 = pd.DataFrame(max_dd)
max_dd1 = max_dd1.transpose()
strats = list(drawdown.columns)
    
#find dates of when max drawdown occurs for each strat
dd_dates = pd.DataFrame()
for i in strats:
    dd_dates[i] = drawdown.index[drawdown[i] == float(max_dd1[i])]

#find dates of when drawdown was zero before the max drawdown    
zero_dd_dates = pd.DataFrame()
for i in strats:
    drawdown_reverse = drawdown.loc[::-1]
    x = dd_dates[i][0]
    strat_drawdown = drawdown_reverse[i].loc[x:]
    for dd_index, dd_value in enumerate(strat_drawdown):
        if dd_value == 0:
            zero_dd_dates[i] = [strat_drawdown.index[dd_index]]
            break

#starts calculating recovery 'days'
recovery_days_list = []
for i in strats:
    count_price_series = price_series[i].loc[zero_dd_dates[i][0]:]
    recovery_days = 0
    recovery_date = ''
    for price in count_price_series[1:]:
        if price < count_price_series[0]:
            recovery_days += 1
        else:
            recovery_date = count_price_series.index[count_price_series == price]
            break
    recovery_days_list.append((i,recovery_days,recovery_date))

print(recovery_days_list)

#psuedo/test code
# =============================================================================
# zero_return_dates = pd.DataFrame()            
# temp = strat_drawdown.loc[x:]
# for j, drawdown_value in enumerate(temp):
#     if drawdown_value == 0:
#         print(j)
#         zero_return_dates['SPTR'] = temp.index[j]
#         break          
# =============================================================================

exampleloc = drawdown.loc['2008-01-31':'2008-09-30']['SPTR']
