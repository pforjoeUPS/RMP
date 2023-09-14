# -*- coding: utf-8 -*-
"""
Created on Thu Sep 14 10:47:57 2023

@author: Bloomberg
"""


#import libraries
from EquityHedging.datamanager import data_manager as dm
from EquityHedging.analytics.util import get_df_weights
from EquityHedging.analytics import summary
from EquityHedging.reporting.excel import reports as rp
from EquityHedging.reporting import formatter as plots


returns= dm.get_equity_hedge_returns(all_data=True)
strategy_list = ['ESPRSO']
filename = 'esprso.xlsx'
sheet_name = 'Sheet1'
new_strategy = dm.get_new_strategy_returns_data(filename, sheet_name, strategy_list)
new_strategy_dict = dm.get_data_dict(new_strategy, data_type='index')
returns_new = dm.merge_dicts(returns, new_strategy_dict)


#create new returns report
rp.get_returns_report('returns_data_new_strat', returns_new)

