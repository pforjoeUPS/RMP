# -*- coding: utf-8 -*-
"""
Created on Fri Jun  9 12:03:49 2023

@author: HQP6CBS
"""


import os

os.chdir('..\..')

#import libraries
from EquityHedging.datamanager import data_manager as dm
from EquityHedging.analytics.util import get_df_weights
from EquityHedging.analytics import summary
from EquityHedging.reporting.excel import reports as rp
from EquityHedging.reporting import formatter as plots

#import returns data
equity_bmk = 'SPTR'
include_fi = False
weighted = [False]
strat_drop_list = []
new_strat = False
sptr_dict= dm.get_equity_hedge_returns(equity_bmk, include_fi, strat_drop_list,True,False)



new_strat = True
if new_strat:
    strategy_list = ['CSDefensiveSkew']
    filename = 'CS_Data.xlsx'
    sheet_name1 = 'CS_Defensive_Skew'
    cs_data = dm.get_new_strategy_returns_data(filename, sheet_name1, strategy_list)
    cs_dict = dm.get_data_dict(cs_data,data_type='index')
    ret_dict = dm.merge_dicts(sptr_dict,cs_dict)
    
strat_report = rp.generate_strat_report('strat_report_Devang', ret_dict,False)

    
